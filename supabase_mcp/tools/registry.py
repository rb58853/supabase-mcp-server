from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from supabase_mcp.core.container import Container
from supabase_mcp.exceptions import ConfirmationRequiredError
from supabase_mcp.logger import logger
from supabase_mcp.services.database.postgres_client import QueryResult
from supabase_mcp.services.safety.models import ClientType, SafetyMode
from supabase_mcp.tools.manager import ToolName


class ToolRegistry:
    """Responsible for registering tools with the MCP server"""

    def __init__(self, mcp: FastMCP, services_container: Container):
        self.mcp = mcp
        self.services_container = services_container

    def register_tools(self) -> FastMCP:
        """Register all tools with the MCP server"""
        mcp = self.mcp
        services_container = self.services_container

        tool_manager = services_container.tool_manager

        @mcp.tool(description=tool_manager.get_description(ToolName.GET_SCHEMAS))  # type: ignore
        async def get_schemas() -> QueryResult:
            """List all database schemas with their sizes and table counts."""
            query_manager = services_container.query_manager
            query = query_manager.get_schemas_query()
            return await query_manager.handle_query(query)

        @mcp.tool(description=tool_manager.get_description(ToolName.GET_TABLES))  # type: ignore
        async def get_tables(schema_name: str) -> QueryResult:
            """List all tables, foreign tables, and views in a schema with their sizes, row counts, and metadata."""
            query_manager = services_container.query_manager
            query = query_manager.get_tables_query(schema_name)
            return await query_manager.handle_query(query)

        @mcp.tool(description=tool_manager.get_description(ToolName.GET_TABLE_SCHEMA))  # type: ignore
        async def get_table_schema(schema_name: str, table: str) -> QueryResult:
            """Get detailed table structure including columns, keys, and relationships."""
            query_manager = services_container.query_manager
            query = query_manager.get_table_schema_query(schema_name, table)
            return await query_manager.handle_query(query)

        @mcp.tool(description=tool_manager.get_description(ToolName.EXECUTE_POSTGRESQL))  # type: ignore
        async def execute_postgresql(query: str) -> QueryResult:
            """Execute PostgreSQL statements against your Supabase database."""
            query_manager = services_container.query_manager
            return await query_manager.handle_query(query, has_confirmation=False)

        @mcp.tool(description=tool_manager.get_description(ToolName.CONFIRM_DESTRUCTIVE_OPERATION))  # type: ignore
        async def confirm_destructive_operation(
            operation_type: Literal["api", "database"], confirmation_id: str, user_confirmation: bool = False
        ) -> QueryResult | dict[str, Any]:
            """Execute a destructive operation after confirmation. Use this only after reviewing the risks with the user."""
            api_manager = services_container.api_manager
            query_manager = services_container.query_manager
            if not user_confirmation:
                raise ConfirmationRequiredError("Destructive operation requires explicit user confirmation.")

            if operation_type == "api":
                return await api_manager.handle_confirmation(confirmation_id)
            elif operation_type == "database":
                return await query_manager.handle_confirmation(confirmation_id)

        @mcp.tool(description=tool_manager.get_description(ToolName.RETRIEVE_MIGRATIONS))  # type: ignore
        async def retrieve_migrations() -> QueryResult:
            """Get all migrations from the supabase_migrations schema."""
            query_manager = services_container.query_manager
            query = query_manager.get_migrations_query()
            return await query_manager.handle_query(query)

        @mcp.tool(description=tool_manager.get_description(ToolName.SEND_MANAGEMENT_API_REQUEST))  # type: ignore
        async def send_management_api_request(
            method: str,
            path: str,
            path_params: dict[str, str],
            request_params: dict[str, Any],
            request_body: dict[str, Any],
        ) -> dict[str, Any]:
            """Execute a Supabase Management API request."""
            api_manager = services_container.api_manager
            return await api_manager.execute_request(method, path, path_params, request_params, request_body)

        @mcp.tool(description=tool_manager.get_description(ToolName.LIVE_DANGEROUSLY))  # type: ignore
        async def live_dangerously(
            service: Literal["api", "database"], enable_unsafe_mode: bool = False
        ) -> dict[str, Any]:
            """
            Toggle between safe and unsafe operation modes for API or Database services.

            This function controls the safety level for operations, allowing you to:
            - Enable write operations for the database (INSERT, UPDATE, DELETE, schema changes)
            - Enable state-changing operations for the Management API
            """
            safety_manager = services_container.safety_manager
            if service == "api":
                # Set the safety mode in the safety manager
                new_mode = SafetyMode.UNSAFE if enable_unsafe_mode else SafetyMode.SAFE
                safety_manager.set_safety_mode(ClientType.API, new_mode)

                # Return the actual mode that was set
                return {"service": "api", "mode": safety_manager.get_safety_mode(ClientType.API)}
            elif service == "database":
                # Set the safety mode in the safety manager
                new_mode = SafetyMode.UNSAFE if enable_unsafe_mode else SafetyMode.SAFE
                safety_manager.set_safety_mode(ClientType.DATABASE, new_mode)

                # Return the actual mode that was set
                return {"service": "database", "mode": safety_manager.get_safety_mode(ClientType.DATABASE)}

        @mcp.tool(description=tool_manager.get_description(ToolName.GET_MANAGEMENT_API_SPEC))  # type: ignore
        async def get_management_api_spec(params: dict[str, Any] = {}) -> dict[str, Any]:
            """Get the Supabase Management API specification.

            This tool can be used in four different ways (and then some ;)):
            1. Without parameters: Returns all domains (default)
            2. With path and method: Returns the full specification for a specific API endpoint
            3. With domain only: Returns all paths and methods within that domain
            4. With all_paths=True: Returns all paths and methods

            Args:
                params: Dictionary containing optional parameters:
                    - path: Optional API path (e.g., "/v1/projects/{ref}/functions")
                    - method: Optional HTTP method (e.g., "GET", "POST")
                    - domain: Optional domain/tag name (e.g., "Auth", "Storage")
                    - all_paths: If True, returns all paths and methods

            Returns:
                API specification based on the provided parameters
            """
            path = params.get("path")
            method = params.get("method")
            domain = params.get("domain")
            all_paths = params.get("all_paths", False)

            logger.debug(
                f"Getting management API spec with path: {path}, method: {method}, domain: {domain}, all_paths: {all_paths}"
            )
            api_manager = services_container.api_manager
            return await api_manager.handle_spec_request(path, method, domain, all_paths)

        @mcp.tool(description=tool_manager.get_description(ToolName.GET_MANAGEMENT_API_SAFETY_RULES))  # type: ignore
        async def get_management_api_safety_rules() -> str:
            """Get all safety rules for the Supabase Management API"""
            api_manager = services_container.api_manager
            return api_manager.get_safety_rules()

        @mcp.tool(description=tool_manager.get_description(ToolName.GET_AUTH_ADMIN_METHODS_SPEC))  # type: ignore
        async def get_auth_admin_methods_spec() -> dict[str, Any]:
            """Get Python SDK methods specification for Auth Admin."""
            sdk_client = services_container.sdk_client
            return sdk_client.return_python_sdk_spec()

        @mcp.tool(description=tool_manager.get_description(ToolName.CALL_AUTH_ADMIN_METHOD))  # type: ignore
        async def call_auth_admin_method(method: str, params: dict[str, Any]) -> dict[str, Any]:
            """Call an Auth Admin method from Supabase Python SDK."""
            sdk_client = services_container.sdk_client
            return await sdk_client.call_auth_admin_method(method, params)

        return mcp
