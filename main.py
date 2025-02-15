from mcp.server.fastmcp import FastMCP

from src.client import SupabaseClient
from src.logger import logger
from src.queries import PreBuiltQueries
from src.validators import validate_schema_name, validate_sql_query, validate_table_name

try:
    mcp = FastMCP("supabase")
    supabase = SupabaseClient.create()
except Exception as e:
    logger.error(f"Failed to create Supabase client: {e}")
    raise e


@mcp.tool(description="Get all schemas from Supabase.")
async def get_db_schemas():
    """Get all schemas from Supabase."""
    query = PreBuiltQueries.get_schemas_query()
    result = supabase.readonly_query(query)
    return result


@mcp.tool(description="Get all tables from a schema in Supabase.")
async def get_tables(schema_name: str):
    """Get all tables from a schema in Supabase."""
    schema_name = validate_schema_name(schema_name)
    query = PreBuiltQueries.get_tables_in_schema_query(schema_name)
    return supabase.readonly_query(query)


@mcp.tool(description="Get the schema of a table in Supabase.")
async def get_table_schema(schema_name: str, table: str):
    """Get the schema of a table in Supabase."""
    schema_name = validate_schema_name(schema_name)
    table = validate_table_name(table)
    query = PreBuiltQueries.get_table_schema_query(schema_name, table)
    return supabase.readonly_query(query)


@mcp.tool(description="Get the stats of a table in Supabase.")
async def get_table_stats(schema_name: str, table: str):
    """Get the stats of a table in Supabase."""
    schema_name = validate_schema_name(schema_name)
    table = validate_table_name(table)
    query = PreBuiltQueries.get_table_stats_query(schema_name, table)
    return supabase.readonly_query(query)


@mcp.tool(description="Get the indexes of a table in Supabase.")
async def get_table_indexes(schema_name: str, table: str):
    """Get the indexes of a table in Supabase."""
    schema_name = validate_schema_name(schema_name)
    table = validate_table_name(table)
    query = PreBuiltQueries.get_table_indexes_query(schema_name, table)
    return supabase.readonly_query(query)


@mcp.tool(description="Get the relationships of a table in Supabase.")
async def get_table_relationships(schema_name: str, table: str):
    """Get the relationships of a table in Supabase."""
    schema_name = validate_schema_name(schema_name)
    table = validate_table_name(table)
    query = PreBuiltQueries.get_table_relationships_query(schema_name, table)
    return supabase.readonly_query(query)


@mcp.tool(description="Query the database with a raw SQL query.")
async def query_db(query: str):
    """Query the database with a raw SQL query."""
    query = validate_sql_query(query)
    return supabase.readonly_query(query)


if __name__ == "__main__":
    logger.info("Starting Supabase MCP server...")
    mcp.run()
