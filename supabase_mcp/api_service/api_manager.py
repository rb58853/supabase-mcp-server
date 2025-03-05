from __future__ import annotations

from typing import Any

from supabase_mcp.api_service.api_client import APIClient
from supabase_mcp.api_service.api_spec_manager import ApiSpecManager
from supabase_mcp.logger import logger
from supabase_mcp.safety.core import ClientType
from supabase_mcp.safety.safety_manager import SafetyManager


class SupabaseApiManager:
    """
    Manages the Supabase Management API.
    """

    _instance: SupabaseApiManager | None = None

    def __init__(self):
        """Initialize the API manager."""
        self.spec_manager = None
        self.client: APIClient = None  # Type hint to fix linter error
        self.safety_manager = SafetyManager.get_instance()

    @classmethod
    async def create(cls) -> SupabaseApiManager:
        """Create a new API manager instance."""
        manager = cls()
        manager.spec_manager = await ApiSpecManager.create()  # Use the running event loop
        manager.client = APIClient()  # This is now properly typed
        return manager

    @classmethod
    async def get_manager(cls) -> SupabaseApiManager:
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = await cls.create()
        return cls._instance

    def get_spec(self) -> dict:
        """Retrieves enriched spec from spec manager"""
        return self.spec_manager.get_spec()

    def get_safety_rules(self) -> str:
        """
        Get safety rules with human-readable descriptions.

        Returns:
            str: Human readable safety rules explanation
        """
        # Get safety configuration from the safety manager
        safety_manager = self.safety_manager

        # Get risk levels and operations by risk level
        extreme_risk_ops = safety_manager.get_operations_by_risk_level("extreme", ClientType.API)
        high_risk_ops = safety_manager.get_operations_by_risk_level("high", ClientType.API)
        medium_risk_ops = safety_manager.get_operations_by_risk_level("medium", ClientType.API)

        # Create human-readable explanations
        extreme_risk_summary = (
            "\n".join([f"- {method} {path}" for method, paths in extreme_risk_ops.items() for path in paths])
            if extreme_risk_ops
            else "None"
        )

        high_risk_summary = (
            "\n".join([f"- {method} {path}" for method, paths in high_risk_ops.items() for path in paths])
            if high_risk_ops
            else "None"
        )

        medium_risk_summary = (
            "\n".join([f"- {method} {path}" for method, paths in medium_risk_ops.items() for path in paths])
            if medium_risk_ops
            else "None"
        )

        current_mode = safety_manager.get_current_mode(ClientType.API)

        return f"""MCP Server Safety Rules:

            EXTREME RISK Operations (never allowed by the server):
            {extreme_risk_summary}
            
            HIGH RISK Operations (require unsafe mode):
            {high_risk_summary}
            
            MEDIUM RISK Operations (require unsafe mode):
            {medium_risk_summary}
            
            All other operations are LOW RISK (always allowed).

            Current mode: {current_mode}
            In safe mode, only low risk operations are allowed.
            Use live_dangerously() to enable unsafe mode for medium and high risk operations.
            """

    def replace_path_params(self, path: str, path_params: dict[str, Any] | None = None) -> str:
        """
        Replace path parameters in the path string with actual values.
        """
        if path_params:
            for key, value in path_params.items():
                path = path.replace("{" + key + "}", str(value))
        return path

    async def execute_request(
        self,
        method: str,
        path: str,
        path_params: dict[str, Any] | None = None,
        request_params: dict[str, Any] | None = None,
        request_body: dict[str, Any] | None = None,
        has_confirmation: bool = False,
    ) -> dict[str, Any]:
        """
        Execute Management API request with safety validation.

        Args:
            method: HTTP method to use
            path: API path to call
            request_params: Query parameters to include
            request_body: Request body to send
            has_confirmation: Whether the operation has been confirmed by the user
        Returns:
            API response as a dictionary

        Raises:
            APIConnectionError: If there's a connection error
            APIResponseError: If the API returns an error
            SafetyError: If the operation is not allowed by safety rules
        """
        # Log the request
        logger.info(
            "Executing API request: %s %s",
            method,
            path,
            request_params,
            request_body,
        )

        # Create an operation object for validation
        operation = (method, path, path_params, request_params, request_body)

        # Use the safety manager to validate the operation
        self.safety_manager.validate_operation(ClientType.API, operation, has_confirmation=has_confirmation)

        # Replace path parameters in the path string with actual values
        path = self.replace_path_params(path, path_params)

        try:
            # Execute the request using the API client
            return await self.client.execute_request(method, path, request_params, request_body)
        except Exception as e:
            logger.error(f"Error executing API request: {str(e)}")
            raise

    async def handle_confirmation(self, confirmation_id: str) -> dict[str, Any]:
        """Handle a confirmation request."""
        # retrieve the operation from the confirmation id
        operation = self.safety_manager.get_stored_operation(confirmation_id)
        if not operation:
            raise ValueError("No operation found for confirmation id")

        # execute the operation
        return await self.execute_request(
            method=operation[0],
            path=operation[1],
            path_params=operation[2],
            request_params=operation[3],
            request_body=operation[4],
            has_confirmation=True,
        )
