from pathlib import Path

from mcp.server.fastmcp import FastMCP

from supabase_mcp.client import SupabaseClient
from supabase_mcp.logger import logger
from supabase_mcp.queries import PreBuiltQueries
from supabase_mcp.settings import settings
from supabase_mcp.validators import validate_schema_name, validate_sql_query, validate_table_name

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
