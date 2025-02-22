from __future__ import annotations

import logging
from json import JSONDecodeError
from typing import Literal

import httpx
from httpx import HTTPStatusError
from tenacity import (
    after_log,
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from supabase_mcp.api_manager.api_safety_config import SafetyConfig, SafetyLevel
from supabase_mcp.api_manager.spec_manager import SpecManager
from supabase_mcp.exceptions import (
    APIClientError,
    APIConnectionError,
    APIError,
    APIResponseError,
    SafetyError,
    UnexpectedError,
)
from supabase_mcp.logger import logger
from supabase_mcp.settings import settings


class SupabaseApiManager:
    """
    Manages the Supabase Management API.
    """

    _instance: SupabaseApiManager | None = None

    def __init__(self):
        self._mode: Literal[SafetyLevel.SAFE, SafetyLevel.UNSAFE] = SafetyLevel.SAFE  # Start in safe mode
        self.safety_config = SafetyConfig()
        self.spec_manager = None
        self.client = self.create_httpx_client()

    @classmethod
    async def create(cls) -> SupabaseApiManager:
        """Factory method to create and initialize an API manager"""
        manager = cls()
        manager.spec_manager = await SpecManager.create()  # Use the running event loop
        return manager

    @classmethod
    async def get_manager(cls) -> SupabaseApiManager:
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = await cls.create()
        return cls._instance

    def create_httpx_client(self) -> httpx.AsyncClient:
        """Creates a new httpx client"""
        client = httpx.AsyncClient(
            base_url="https://api.supabase.com",
            headers={"Authorization": f"Bearer {settings.supabase_access_token}", "Content-Type": "application/json"},
        )
        logger.info("Initialized Supabase Management API client")
        return client

    @property
    def mode(self) -> SafetyLevel:
        """Current operation mode"""
        return self._mode

    def switch_mode(self, mode: Literal[SafetyLevel.SAFE, SafetyLevel.UNSAFE]) -> None:
        """Switch between safe and unsafe operation modes"""
        self._mode = mode
        logger.info(f"Switched to {self._mode.value} mode")

    def get_spec(self) -> dict:
        """Retrieves enriched spec from spec manager"""
        return self.spec_manager.get_spec()

    def get_safety_rules(self) -> str:
        """
        Get safety rules with human-readable descriptions.

        Returns:
            str: Human readable safety rules explanation
        """
        blocked_ops = self.safety_config.BLOCKED_OPERATIONS
        unsafe_ops = self.safety_config.UNSAFE_OPERATIONS

        # Create human-readable explanations
        blocked_summary = "\n".join([f"- {method} {path}" for method, paths in blocked_ops.items() for path in paths])

        unsafe_summary = "\n".join([f"- {method} {path}" for method, paths in unsafe_ops.items() for path in paths])

        return f"""MCP Server Safety Rules:

            BLOCKED Operations (never allowed by the server):
            {blocked_summary}

            UNSAFE Operations (require unsafe mode):
            {unsafe_summary}

            Current mode: {self.mode}
            In safe mode, only read operations are allowed.
            Use live_dangerously() to enable unsafe mode for write operations.
            """

    @retry(
        retry=retry_if_exception_type(APIConnectionError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=15),
        before=before_log(logger, logging.DEBUG),
        after=after_log(logger, logging.DEBUG),
    )
    async def execute_request(
        self,
        method: str,
        path: str,
        request_params: dict | None = None,
        request_body: dict | None = None,
    ) -> dict:
        """
        Execute Management API request with safety validation.

        Args:
            method: HTTP method (GET, POST, etc)
            path: API path (/v1/projects etc)
            request_params: Optional query parameters as dict
            request_body: Optional request body as dict

        Returns:
            API response as dict

        Raises:
            SafetyError: If operation not allowed
            APIError: If request fails
        """
        # Replace project ref
        if "{ref}" in path:
            path = path.replace("{ref}", settings.supabase_project_ref)

        # Safety check
        allowed, reason, level = self.safety_config.is_operation_allowed(method, path)

        if level == SafetyLevel.BLOCKED:
            logger.warning(f"Blocked operation attempted: {method} {path}")
            raise SafetyError(
                f"Operation blocked: {reason}, check all safety rules here: {self.safety_config.list_all_rules()}"
            )

        if level == SafetyLevel.UNSAFE and self.mode == SafetyLevel.SAFE:
            logger.warning(f"Unsafe operation attempted in safe mode: {method} {path}")
            raise SafetyError(
                f"Operation requires YOLO mode: {reason}. Use live_dangerously() to enable YOLO mode. Check all safety rules here: {self.safety_config.list_all_rules()}"
            )

        # Execute request
        logger.info(
            "Executing API request: method=%s, url=%s, params=%s, request_body=%s",
            method,
            path,
            request_params,
            request_body,
        )
        try:
            # Build and send request
            request = self.client.build_request(method=method, url=path, params=request_params, json=request_body)
            response = await self.client.send(request)

            # Try to parse error response body if available
            error_body = None
            try:
                error_body = response.json() if response.content else None
            except JSONDecodeError:
                error_body = {"raw_content": response.text} if response.text else None

            # Handle API errors (4xx, 5xx)
            try:
                response.raise_for_status()
            except HTTPStatusError as e:
                error_message = f"API request failed: {e.response.status_code}"
                if error_body and isinstance(error_body, dict):
                    error_message = error_body.get("message", error_message)

                if 400 <= e.response.status_code < 500:
                    raise APIClientError(
                        message=error_message,
                        status_code=e.response.status_code,
                        response_body=error_body,
                    ) from e
            # Parse successful response
            try:
                return response.json()
            except JSONDecodeError as e:
                raise APIResponseError(
                    message=f"Failed to parse API response as JSON: {str(e)}",
                    status_code=response.status_code,
                    response_body={"raw_content": response.text},
                ) from e

        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
            raise APIConnectionError(message=f"Connection error: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (APIError, SafetyError)):
                raise
            logger.exception("Unexpected error during API request")
            raise UnexpectedError(message=f"Unexpected error during API request: {str(e)}") from e

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
