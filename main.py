from mcp.server.fastmcp import FastMCP

from src.client import SupabaseClient
from src.tools import PreBuiltQueries
from src.validators import validate_schema_name, validate_sql_query, validate_table_name

supabase_mcp = FastMCP("supabase")
supabase = SupabaseClient.create()


@supabase_mcp.tool(description="Get all schemas from Supabase.")
async def get_db_schemas():
    """Get all schemas from Supabase."""
    query = PreBuiltQueries.get_schemas_query()
    result = supabase.readonly_query(query)

    return result


@supabase_mcp.tool(description="Get all tables from a schema in Supabase.")
async def get_tables(schema: str):
    """Get all tables from a schema in Supabase."""
    schema = validate_schema_name(schema)
    query = PreBuiltQueries.get_tables_in_schema_query(schema)
    return supabase.readonly_query(query)


@supabase_mcp.tool(description="Get the schema of a table in Supabase.")
async def get_table_schema(schema: str, table: str):
    """Get the schema of a table in Supabase."""
    schema = validate_schema_name(schema)
    table = validate_table_name(table)
    query = PreBuiltQueries.get_table_schema_query(schema, table)
    return supabase.readonly_query(query)


@supabase_mcp.tool(description="Query the database with a raw SQL query.")
async def query_db(query: str):
    """Query the database with a raw SQL query."""
    query = validate_sql_query(query)
    return supabase.readonly_query(query)


if __name__ == "__main__":
    supabase_mcp.run()
