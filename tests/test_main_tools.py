# Database tools
# Needs postgres_clint integration fixture
# It needs in turn a query_manager integration fixture

# TESTS
# get_schemas
# get_tables
# get_table_schema
# execute_postgresql
# confirm_destructive_operation
# retrieve_migrations

# Each tests
# - non-error response for happy paths
# - postgressql tests:
#   - error response for invalid queries
#   - error if risky operation in safe mode
#   - confirmation error if risky operation in non-safe mode


import pytest

from supabase_mcp.database_service.postgres_client import QueryResult
from supabase_mcp.database_service.query_manager import QueryManager
from supabase_mcp.exceptions import ConfirmationRequiredError, SQLSafetyError
from supabase_mcp.main import (
    execute_postgresql,
    get_schemas,
    get_table_schema,
    get_tables,
    live_dangerously,
    retrieve_migrations,
)
from supabase_mcp.safety.core import ClientType, SafetyMode
from supabase_mcp.safety.safety_manager import SafetyManager


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_schemas_tool(query_manager_integration: QueryManager):
    """Test the get_schemas tool retrieves schema information properly."""
    # Execute the get_schemas tool
    result = await get_schemas()

    # Verify result structure
    assert isinstance(result, QueryResult), "Result should be a QueryResult"
    assert hasattr(result, "rows"), "Result should have rows attribute"
    assert hasattr(result, "count"), "Result should have count attribute"
    assert hasattr(result, "status"), "Result should have status attribute"

    # Verify we have schema data
    assert result.count > 0, "Should return at least one schema"

    # Verify the public schema is present (required in Supabase)
    public_schema = next((s for s in result.rows if s.get("schema_name") == "public"), None)
    assert public_schema is not None, "Public schema should be present"

    # Verify schema structure
    expected_fields = ["schema_name", "schema_size", "tables_count"]
    for field in expected_fields:
        assert field in public_schema, f"Schema result missing '{field}' field"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_tables_tool(query_manager_integration: QueryManager):
    """Test the get_tables tool retrieves table information from a schema."""
    # Execute the get_tables tool for the public schema
    result = await get_tables("public")

    # Verify result structure
    assert isinstance(result, QueryResult), "Result should be a QueryResult"
    assert hasattr(result, "rows"), "Result should have rows attribute"
    assert hasattr(result, "count"), "Result should have count attribute"
    assert hasattr(result, "status"), "Result should have status attribute"

    # If tables exist, verify their structure
    if result.count > 0:
        # Verify table structure
        first_table = result.rows[0]
        expected_fields = ["table_name", "table_type", "row_count", "size"]
        for field in expected_fields:
            assert field in first_table, f"Table result missing '{field}' field"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_table_schema_tool(query_manager_integration: QueryManager):
    """Test the get_table_schema tool retrieves column information for a table."""
    # First get tables to find one to test with
    tables_result = await get_tables("public")

    # Skip test if no tables available
    if tables_result.count == 0:
        pytest.skip("No tables available in public schema to test table schema")

    # Get the first table name to test with
    first_table = tables_result.rows[0]["table_name"]

    # Execute the get_table_schema tool
    result = await get_table_schema("public", first_table)

    # Verify result structure
    assert isinstance(result, QueryResult), "Result should be a QueryResult"
    assert hasattr(result, "rows"), "Result should have rows attribute"
    assert hasattr(result, "count"), "Result should have count attribute"

    # If columns exist, verify their structure
    if result.count > 0:
        # Verify column structure
        first_column = result.rows[0]
        expected_fields = ["column_name", "data_type", "is_nullable"]
        for field in expected_fields:
            assert field in first_column, f"Column result missing '{field}' field"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_postgresql_safe_query(query_manager_integration: QueryManager):
    """Test the execute_postgresql tool runs safe SQL queries."""
    # Test a simple SELECT query
    result = await execute_postgresql("SELECT 1 as number, 'test' as text")

    # Verify result structure
    assert isinstance(result, QueryResult), "Result should be a QueryResult"
    assert hasattr(result, "rows"), "Result should have rows attribute"
    assert hasattr(result, "count"), "Result should have count attribute"
    assert hasattr(result, "status"), "Result should have status attribute"

    # Verify data matches what we expect
    assert result.count == 1, "Expected exactly one row"
    assert result.rows[0]["number"] == 1, "First column should be 1"
    assert result.rows[0]["text"] == "test", "Second column should be 'test'"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_postgresql_unsafe_query(query_manager_integration: QueryManager):
    """Test the execute_postgresql tool handles unsafe queries properly."""
    # First, ensure we're in safe mode
    await live_dangerously(service="database", enable_unsafe_mode=False)

    # Try to execute an unsafe query (CREATE TABLE)
    unsafe_query = """
    CREATE TABLE IF NOT EXISTS test_table (
        id SERIAL PRIMARY KEY,
        name TEXT
    )
    """

    # This should raise a safety error
    with pytest.raises(SQLSafetyError):
        await execute_postgresql(unsafe_query)

    # Now switch to unsafe mode
    await live_dangerously(service="database", enable_unsafe_mode=True)

    # The query should now require confirmation
    with pytest.raises(ConfirmationRequiredError):
        await execute_postgresql(unsafe_query)

    # Switch back to safe mode for other tests
    await live_dangerously(service="database", enable_unsafe_mode=False)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_retrieve_migrations(query_manager_integration: QueryManager):
    """Test the retrieve_migrations tool retrieves migration information."""
    # Execute the retrieve_migrations tool
    result = await retrieve_migrations()

    # Verify result structure
    assert isinstance(result, QueryResult), "Result should be a QueryResult"
    assert hasattr(result, "rows"), "Result should have rows attribute"
    assert hasattr(result, "count"), "Result should have count attribute"
    assert hasattr(result, "status"), "Result should have status attribute"

    # Note: We don't assert on count because there might not be any migrations
    # But we can verify the query executed successfully
    assert result.status == "success", "Query should execute successfully"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_dangerously_database(query_manager_integration: QueryManager):
    """Test the live_dangerously tool toggles database safety mode."""
    # Get the safety manager
    safety_manager = SafetyManager.get_instance()

    # Start with safe mode
    await live_dangerously(service="database", enable_unsafe_mode=False)
    assert safety_manager.get_safety_mode(ClientType.DATABASE) == SafetyMode.SAFE, "Database should be in safe mode"

    # Switch to unsafe mode
    result = await live_dangerously(service="database", enable_unsafe_mode=True)
    assert result["service"] == "database", "Response should identify database service"
    assert safety_manager.get_safety_mode(ClientType.DATABASE) == SafetyMode.UNSAFE, "Database should be in unsafe mode"

    # Switch back to safe mode
    result = await live_dangerously(service="database", enable_unsafe_mode=False)
    assert result["service"] == "database", "Response should identify database service"
    assert safety_manager.get_safety_mode(ClientType.DATABASE) == SafetyMode.SAFE, "Database should be in safe mode"
