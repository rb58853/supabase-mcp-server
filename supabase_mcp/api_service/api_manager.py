from __future__ import annotations

from enum import Enum
from typing import Any

from supabase_mcp.api_service.api_client import APIClient
from supabase_mcp.api_service.api_spec_manager import ApiSpecManager
from supabase_mcp.logger import logger
from supabase_mcp.safety.core import ClientType
from supabase_mcp.safety.safety_manager import SafetyManager
from supabase_mcp.settings import settings


class PathPlaceholder(str, Enum):
    """Enum of all possible path placeholders in the Supabase Management API."""

    REF = "ref"
    FUNCTION_SLUG = "function_slug"
    ID = "id"
    SLUG = "slug"
    BRANCH_ID = "branch_id"
    PROVIDER_ID = "provider_id"
    TPA_ID = "tpa_id"


class SupabaseApiManager:
    """
    Manages the Supabase Management API.
    """

    _instance: SupabaseApiManager | None = None

    def __init__(self) -> None:
        """Initialize the API manager."""
        self.spec_manager: ApiSpecManager | None = None
        self.client: APIClient | None = None  # Type hint to fix linter error
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

    def get_spec(self) -> dict[str, Any]:
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

        This method:
        1. Automatically injects the project ref from settings
        2. Replaces all placeholders in the path with values from path_params
        3. Validates that all placeholders are replaced

        Args:
            path: The API path with placeholders (e.g., "/v1/projects/{ref}/functions/{function_slug}")
            path_params: Dictionary of path parameters to replace (e.g., {"function_slug": "my-function"})

        Returns:
            The path with all placeholders replaced

        Raises:
            ValueError: If any placeholders remain after replacement or if invalid placeholders are provided
        """
        # Create a working copy of path_params to avoid modifying the original
        working_params = {} if path_params is None else path_params.copy()

        # Check if user provided ref and raise an error
        if working_params and PathPlaceholder.REF.value in working_params:
            raise ValueError(
                "Do not provide 'ref' in path_params. The project reference is automatically injected from settings. "
                "If you need to change the project reference, modify the environment variables instead."
            )

        # Validate that all provided path parameters are known placeholders
        if working_params:
            for key in working_params:
                try:
                    PathPlaceholder(key)
                except ValueError as e:
                    raise ValueError(
                        f"Unknown path parameter: '{key}'. Valid placeholders are: "
                        f"{', '.join([p.value for p in PathPlaceholder])}"
                    ) from e

        # Get project ref from settings and add it to working_params
        working_params[PathPlaceholder.REF.value] = settings.supabase_project_ref

        logger.info(f"Replacing path parameters in path: {working_params}")

        # Replace all placeholders in the path
        for key, value in working_params.items():
            placeholder = "{" + key + "}"
            if placeholder in path:
                path = path.replace(placeholder, str(value))
                logger.debug(f"Replaced {placeholder} with {value}")

        # Check if any placeholders remain
        import re

        remaining_placeholders = re.findall(r"\{([^}]+)\}", path)
        if remaining_placeholders:
            raise ValueError(
                f"Missing path parameters: {', '.join(remaining_placeholders)}. "
                f"Please provide values for these placeholders in the path_params dictionary."
            )

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
            SafetyError: If the operation is not allowed by safety rules
        """
        # Log the request with proper formatting
        logger.info(
            f"API Request: {method} {path} | Path params: {path_params or {}} | Query params: {request_params or {}} | Body: {request_body or {}}"
        )

        # Create an operation object for validation
        operation = (method, path, path_params, request_params, request_body)

        # Use the safety manager to validate the operation
        logger.debug(f"Validating operation safety: {method} {path}")
        self.safety_manager.validate_operation(ClientType.API, operation, has_confirmation=has_confirmation)

        # Replace path parameters in the path string with actual values
        path = self.replace_path_params(path, path_params)

        # Execute the request using the API client
        return await self.client.execute_request(method, path, request_params, request_body)

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

    def handle_spec_request(
        self,
        path: str | None = None,
        method: str | None = None,
        domain: str | None = None,
        all_paths: bool | None = False,
    ) -> dict[str, Any]:
        """Handle a spec request.

        Args:
            path: Optional API path
            method: Optional HTTP method
            api_domain: Optional domain/tag name
            full_spec: If True, returns all paths and methods

        Returns:
            API specification based on the provided parameters
        """
        spec_manager = self.spec_manager

        if spec_manager is None:
            raise RuntimeError("API spec manager is not initialized")

        # Option 1: Get spec for specific path and method
        if path and method:
            method = method.lower()  # Normalize method to lowercase
            result = spec_manager.get_spec_for_path_and_method(path, method)
            if result is None:
                return {"error": f"No specification found for {method.upper()} {path}"}
            return result

        # Option 2: Get all paths and methods for a specific domain
        elif domain:
            result = spec_manager.get_paths_and_methods_by_domain(domain)
            if not result:
                # Check if the domain exists
                all_domains = spec_manager.get_all_domains()
                if domain not in all_domains:
                    return {"error": f"Domain '{domain}' not found", "available_domains": all_domains}
            return {"domain": domain, "paths": result}

        # Option 4: Get all paths and methods
        elif all_paths:
            return {"paths": spec_manager.get_all_paths_and_methods()}

        # Option 3: Get all domains (default)
        else:
            return {"domains": spec_manager.get_all_domains()}
