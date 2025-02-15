from mcp.server.fastmcp import FastMCP

from src.client import SupabaseClient
from src.logger import logger
from src.queries import PreBuiltQueries
from src.settings import settings
from src.validators import validate_schema_name, validate_sql_query, validate_table_name

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


if __name__ == "__main__":
    logger.info("Starting Supabase MCP server to connect to project ref: %s", settings.supabase_project_ref)
    mcp.run()
