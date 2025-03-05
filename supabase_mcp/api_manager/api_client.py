"""API client for Supabase Management API.

This module provides a client for interacting with the Supabase Management API.
It handles the low-level HTTP requests and response parsing.
"""

from json.decoder import JSONDecodeError
from typing import Any

import httpx
from httpx import HTTPStatusError

from supabase_mcp.api_manager.errors import (
    APIClientError,
    APIConnectionError,
    APIError,
    APIResponseError,
    UnexpectedError,
)
from supabase_mcp.logger import logger
from supabase_mcp.settings import settings


class APIClient:
    """
    Client for Supabase Management API.

    Handles low-level HTTP requests to the Supabase Management API.
    """

    def __init__(self):
        """Initialize the API client with default settings."""
        self.client = self.create_httpx_client()

    def create_httpx_client(self) -> httpx.AsyncClient:
        """Create and configure an httpx client for API requests."""
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "Content-Type": "application/json",
        }

        return httpx.AsyncClient(
            base_url=settings.supabase_api_url,
            headers=headers,
            timeout=30.0,
        )

    async def execute_request(
        self,
        method: str,
        path: str,
        request_params: dict[str, Any] | None = None,
        request_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an HTTP request to the Supabase Management API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            request_params: Query parameters
            request_body: Request body

        Returns:
            API response as a dictionary

        Raises:
            APIClientError: For client errors (4xx)
            APIConnectionError: For connection issues
            APIResponseError: For response parsing errors
            UnexpectedError: For unexpected errors
        """
        logger.info(
            "Executing API request",
            method=method,
            path=path,
            request_params=request_params,
            request_body=request_body,
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
            if isinstance(e, APIError):
                raise
            logger.exception("Unexpected error during API request")
            raise UnexpectedError(message=f"Unexpected error during API request: {str(e)}") from e

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
