from mcp.server.fastmcp import FastMCP

from src.client import SupabaseClient
from src.tools import PreBuiltQueries

supabase_mcp = FastMCP("supabase")
supabase = SupabaseClient.create()


@supabase_mcp.tool(description="Get all schemas from Supabase.")
async def get_db_schemas():
    """Get all schemas from Supabase."""
    query = PreBuiltQueries.get_schemas_query()
    result = supabase.query(query)

    return result


@supabase_mcp.tool(description="Get all tables from a schema in Supabase.")
async def get_tables(schema: str):
    """Get all tables from a schema in Supabase."""
    query = PreBuiltQueries.get_tables_in_schema_query(schema)
    result = supabase.query(query)

    return result


@supabase_mcp.tool(description="Get the schema of a table in Supabase.")
async def get_table_schema(schema: str, table: str):
    """Get the schema of a table in Supabase."""
    query = PreBuiltQueries.get_table_schema_query(schema, table)
    result = supabase.query(query)

    return result


@supabase_mcp.tool(description="Query the database with a raw SQL query.")
async def query_db(query: str):
    """Query the database with a raw SQL query."""
    result = supabase.query(query)

    return result


if __name__ == "__main__":
    supabase_mcp.run()
