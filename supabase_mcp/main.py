from pathlib import Path

from mcp.server.fastmcp import FastMCP

from supabase_mcp.api_manager.api_manager import SupabaseApiManager
from supabase_mcp.api_manager.safety_config import SafetyLevel
from supabase_mcp.client import SupabaseClient
from supabase_mcp.logger import logger
from supabase_mcp.queries import PreBuiltQueries
from supabase_mcp.settings import settings
from supabase_mcp.validators import (
    validate_schema_name,
    validate_sql_query,
    validate_table_name,
)

try:
    mcp = FastMCP("supabase")
    supabase = SupabaseClient.create()
except Exception as e:
    logger.error(f"Failed to create Supabase client: {e}")
    raise e


@mcp.tool(description="List all database schemas with their sizes and table counts.")
async def get_db_schemas():
    """Get all accessible database schemas with their total sizes and number of tables."""
    query = PreBuiltQueries.get_schemas_query()
    result = supabase.readonly_query(query)
    return result


@mcp.tool(description="List all tables in a schema with their sizes, row counts, and metadata.")
async def get_tables(schema_name: str):
    """Get all tables from a schema with size, row count, column count, and index information."""
    schema_name = validate_schema_name(schema_name)
    query = PreBuiltQueries.get_tables_in_schema_query(schema_name)
    return supabase.readonly_query(query)


@mcp.tool(description="Get detailed table structure including columns, keys, and relationships.")
async def get_table_schema(schema_name: str, table: str):
    """Get table schema including column definitions, primary keys, and foreign key relationships."""
    schema_name = validate_schema_name(schema_name)
    table = validate_table_name(table)
    query = PreBuiltQueries.get_table_schema_query(schema_name, table)
    return supabase.readonly_query(query)


@mcp.tool(description="Query the database with a raw SQL query.")
async def query_db(query: str):
    """Execute a read-only SQL query with validation."""
    query = validate_sql_query(query)
    return supabase.readonly_query(query)


# Core Tools
@mcp.tool(
    description="""
Execute a Supabase Management API request. Use paths exactly as defined in the API spec -
the {ref} parameter will be automatically injected from settings.

Parameters:
- method: HTTP method (GET, POST, PUT, PATCH, DELETE)
- path: API path (e.g. /v1/projects/{ref}/functions)
- request_params: Query parameters as dict (e.g. {"key": "value"}) - use empty dict {} if not needed
- request_body: Request body as dict (e.g. {"name": "test"}) - use empty dict {} if not needed

Examples:
1. GET request with params:
   method: "GET"
   path: "/v1/projects/{ref}/functions"
   request_params: {"name": "test"}
   request_body: {}

2. POST request with body:
   method: "POST"
   path: "/v1/projects/{ref}/functions"
   request_params: {}
   request_body: {"name": "test-function", "slug": "test-function"}
"""
)
async def send_management_api_request(
    method: str,
    path: str,  # URL path
    request_params: dict,  # Query parameters as dict
    request_body: dict,  # Request body as dict
) -> dict:
    """
    Execute a Management API request.

    Args:
        method: HTTP method (GET, POST, etc)
        path: API path exactly as in spec, {ref} will be auto-injected
        request_params: Query parameters as dict if needed (e.g. {"key": "value"})
        request_body: Request body as dict for POST/PUT/PATCH (e.g. {"name": "test"})

    Example:
        To get a function details, use:
        path="/v1/projects/{ref}/functions/{function_slug}"
        The {ref} will be auto-injected, only function_slug needs to be provided
    """
    api_manager = await SupabaseApiManager.get_manager()
    return await api_manager.execute_request(method, path, request_params, request_body)


@mcp.tool(
    description="""
Toggle unsafe mode for Management API operations.
In safe mode (default), only read operations are allowed.
In unsafe mode, state-changing operations are permitted except blocked ones.
"""
)
async def live_dangerously(enable: bool = False) -> dict:
    """
    Toggle between safe and unsafe operation modes.

    Args:
        enable: True to enable unsafe mode, False for safe mode

    Returns:
        dict: Current mode status and available operations
    """
    api_manager = await SupabaseApiManager.get_manager()
    api_manager.switch_mode(SafetyLevel.UNSAFE if enable else SafetyLevel.SAFE)
    return {"mode": api_manager.mode}


@mcp.tool(
    description="""
Get the complete Management API specification enriched with safety metadata.
Each operation includes safety level (safe/unsafe/blocked) and reasoning.
Use this to understand available operations and their requirements.
"""
)
async def get_management_api_spec() -> dict:
    """
    Get enriched API specification with safety information.

    Returns:
        dict: OpenAPI spec with added safety metadata per operation
    """
    api_manager = await SupabaseApiManager.get_manager()
    return api_manager.get_spec()


@mcp.tool(description="Get all safety rules for the Supabase Management API")
async def get_management_api_safety_rules() -> dict:
    """Returns all safety rules including blocked and unsafe operations with human-readable explanations"""
    api_manager = await SupabaseApiManager.get_manager()
    return api_manager.get_safety_rules()


def run():
    """Run the Supabase MCP server."""
    if settings.supabase_project_ref.startswith("127.0.0.1"):
        logger.info(
            "Starting Supabase MCP server to connect to local project: %s",
            settings.supabase_project_ref,
        )
    else:
        logger.info(
            "Starting Supabase MCP server to connect to project ref: %s (region: %s)",
            settings.supabase_project_ref,
            settings.supabase_region,
        )
    if settings.supabase_access_token:
        logger.info("Personal access token detected - using for Management API")
    mcp.run()


if __name__ == "__main__":
    run()


def inspector():
    """Inspector mode - same as mcp dev"""
    logger.info("Starting Supabase MCP server inspector")

    import importlib.util

    from mcp.cli.cli import dev  # Import from correct module

    # Get the package location
    spec = importlib.util.find_spec("supabase_mcp")
    if spec and spec.origin:
        package_dir = str(Path(spec.origin).parent)
        file_spec = str(Path(package_dir) / "main.py")
        logger.info(f"Using file spec: {file_spec}")
        return dev(file_spec=file_spec)
    else:
        raise ImportError("Could not find supabase_mcp package")
