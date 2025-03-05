"""API Request Manager for Supabase Management API.

This module provides a manager for interacting with the Supabase Management API
with safety validation and request handling.
"""

from typing import Any

from supabase_mcp.api_manager.api_client import APIClient
from supabase_mcp.api_manager.errors import SafetyError
from supabase_mcp.logger import logger
from supabase_mcp.safety.configs.api_safety_config import APISafetyConfig
from supabase_mcp.safety.core import ClientType, OperationRiskLevel, SafetyMode
from supabase_mcp.safety.safety_manager import SafetyManager


class APIRequestManager:
    """
    Manages API requests with safety validation.

    This class is responsible for:
    1. Validating API requests for safety
    2. Executing requests through the API client
    3. Managing API specifications and safety rules

    It acts as a central point for all API operations, ensuring consistent
    validation and execution patterns.
    """

    _instance = None

    def __init__(self, api_client: APIClient):
        """Initialize the API manager with a client."""
        self.api_client = api_client
        self.safety_manager = SafetyManager.get_instance()
        self.safety_config = APISafetyConfig()

    @classmethod
    async def create(cls) -> "APIRequestManager":
        """Create and initialize the API manager."""
        if cls._instance is None:
            api_client = APIClient()
            cls._instance = cls(api_client)
        return cls._instance

    @classmethod
    async def get_manager(cls) -> "APIRequestManager":
        """Get the singleton instance of the API manager."""
        if cls._instance is None:
            return await cls.create()
        return cls._instance

    async def handle_request(
        self,
        method: str,
        path: str,
        request_params: dict[str, Any] | None = None,
        request_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Handle an API request with safety validation.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            request_params: Query parameters
            request_body: Request body

        Returns:
            API response as a dictionary

        Raises:
            SafetyError: If the operation is not allowed based on safety rules
            APIError: For various API-related errors
        """
        # Validate the request for safety
        risk_level = self._get_risk_level(method, path)
        client_type = ClientType.API

        # Check if the operation is allowed based on the current safety mode
        if not self.safety_manager.validate_operation(client_type, risk_level):
            operation_desc = f"{method} {path}"
            mode = self.safety_manager.get_safety_mode(client_type)

            if risk_level == OperationRiskLevel.EXTREME:
                raise SafetyError(
                    f"Operation '{operation_desc}' is blocked for safety reasons. "
                    f"This operation is too risky and cannot be performed."
                )

            if mode == SafetyMode.SAFE and risk_level > OperationRiskLevel.LOW:
                raise SafetyError(
                    f"Operation '{operation_desc}' requires unsafe mode. "
                    f"Use live_dangerously('api', True) to enable unsafe mode."
                )

        # Check if the operation needs confirmation based on risk level
        if risk_level >= OperationRiskLevel.HIGH:
            # For now, we'll just log a warning
            # In the future, we could implement a confirmation mechanism
            logger.warning(f"High-risk operation: {method} {path}. This operation is potentially destructive.")

        # Execute the request
        return await self.api_client.execute_request(
            method=method,
            path=path,
            request_params=request_params,
            request_body=request_body,
        )

    def _get_risk_level(self, method: str, path: str) -> OperationRiskLevel:
        """
        Get the risk level for an API operation.

        Args:
            method: HTTP method
            path: API path

        Returns:
            The risk level for the operation
        """
        return self.safety_config.get_risk_level((method, path))

    def get_safety_rules(self) -> str:
        """
        Get a human-readable description of the safety rules.

        Returns:
            A string describing the safety rules
        """
        client_type = ClientType.API
        mode = self.safety_manager.get_safety_mode(client_type)

        return (
            f"API Safety Rules:\n"
            f"Current mode: {mode.value}\n"
            f"In safe mode, only low-risk operations (mostly GET requests) are allowed.\n"
            f"Use live_dangerously('api', True) to enable unsafe mode for higher-risk operations."
        )

    async def close(self):
        """Close the API client."""
        await self.api_client.close()
