import asyncio
import os
import subprocess
from unittest.mock import ANY, patch

import pytest

from supabase_mcp.logger import logger
from supabase_mcp.main import inspector, mcp, run

# === UNIT TESTS ===


@pytest.mark.unit
def test_mcp_server_initializes():
    """Test that MCP server initializes with default configuration and tools"""
    # Verify server name
    assert mcp.name == "supabase"

    # Verify tools are properly registered using the actual MCP protocol
    tools = asyncio.run(mcp.list_tools())
    assert len(tools) >= 4, "Expected at least 4 tools to be registered"

    # Verify each tool has proper MCP protocol structure
    for tool in tools:
        assert tool.name, "Tool must have a name"
        assert tool.description, "Tool must have a description"
        assert tool.inputSchema, "Tool must have an input schema"

    # Verify our core tools are registered
    tool_names = {tool.name for tool in tools}
    required_tools = {"get_db_schemas", "get_tables", "get_table_schema", "execute_sql_query"}
    assert required_tools.issubset(tool_names), f"Missing required tools. Found: {tool_names}"


@pytest.mark.unit
def test_run_server_starts():
    """Test that server run function executes without errors"""
    with patch("supabase_mcp.main.mcp.run") as mock_run:
        run()
        mock_run.assert_called_once()


@pytest.mark.unit
def test_inspector_mode():
    """Test that inspector mode initializes correctly"""
    with patch("mcp.cli.cli.dev") as mock_dev:
        inspector()
        mock_dev.assert_called_once_with(file_spec=ANY)


@pytest.mark.unit
def test_server_command_starts():
    """Test that the server command executes without errors"""
    result = subprocess.run(
        ["supabase-mcp-server"],
        capture_output=True,
        text=True,
        timeout=2,  # Kill after 2 seconds since it's a server
    )
    assert result.returncode == 0, f"Server command failed: {result.stderr}"


@pytest.mark.unit
def test_mcp_server_tools():
    """Test that all expected tools are registered and accessible"""
    tools = asyncio.run(mcp.list_tools())

    # Verify we have all our tools
    tool_names = {tool.name for tool in tools}

    # All tools defined in main.py
    all_required_tools = {
        "get_db_schemas",
        "get_tables",
        "get_table_schema",
        "execute_sql_query",
        "send_management_api_request",
        "live_dangerously",
        "get_management_api_spec",
        "get_management_api_safety_rules",
    }

    assert all_required_tools.issubset(tool_names), (
        f"Missing required tools. Found: {tool_names}, Expected: {all_required_tools}"
    )

    # Verify tools have descriptions
    for tool in tools:
        assert tool.description, f"Tool {tool.name} missing description"
        assert tool.inputSchema is not None, f"Tool {tool.name} missing input schema"


# === INTEGRATION TESTS ===


@pytest.mark.integration
@pytest.mark.asyncio
async def test_db_tools_execution():
    """Integration test that verifies DB tools actually work

    Requires:
    - SUPABASE_PROJECT_REF
    - SUPABASE_DB_PASSWORD
    environment variables to be set
    """


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_db_schemas_tool(integration_client):
    """Test the get_db_schemas tool retrieves schema information properly.

    This test checks:
    1. The tool executes successfully
    2. Returns data in the expected format
    3. Contains at least the public schema
    """
    # Call the actual tool function from main.py
    from supabase_mcp.main import get_db_schemas

    # Execute the tool
    result = await get_db_schemas()

    # Verify result structure (should be a QueryResult)
    assert hasattr(result, "rows"), "Result should have rows attribute"
    assert hasattr(result, "count"), "Result should have count attribute"
    assert hasattr(result, "status"), "Result should have status attribute"

    # Verify we have some data
    assert result.count > 0, "Should return at least some schemas"

    # Get schema names for inspection
    schema_names = [schema["schema_name"] for schema in result.rows]

    # In Supabase, we at least expect the public schema to be available
    assert "public" in schema_names, "Expected 'public' schema not found"

    # Log available schemas for debugging
    logger.info(f"Available schemas: {schema_names}")

    # Verify schema structure
    first_schema = result.rows[0]
    expected_fields = ["schema_name", "total_size", "table_count"]
    for field in expected_fields:
        assert field in first_schema, f"Schema result missing '{field}' field"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_tables_tool(integration_client):
    """Test the get_tables tool retrieves table information from a schema.

    This test checks:
    1. The tool executes successfully
    2. Returns data in the expected format
    """
    # Call the actual tool function from main.py
    from supabase_mcp.main import get_tables

    # Execute the tool for the public schema
    result = await get_tables("public")

    # Verify result structure (should be a QueryResult)
    assert hasattr(result, "rows"), "Result should have rows attribute"
    assert hasattr(result, "count"), "Result should have count attribute"
    assert hasattr(result, "status"), "Result should have status attribute"

    # Log result for debugging
    logger.info(f"Found {result.count} tables in public schema")

    # If tables exist, verify their structure
    if result.count > 0:
        # Log table names
        table_names = [table.get("table_name") for table in result.rows]
        logger.info(f"Tables in public schema: {table_names}")

        # Verify table structure
        first_table = result.rows[0]
        expected_fields = ["table_name", "table_type"]
        for field in expected_fields:
            assert field in first_table, f"Table result missing '{field}' field"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_table_schema_tool(integration_client):
    """Test the get_table_schema tool retrieves column information for a table.

    This test checks:
    1. The tool executes successfully
    2. Returns data in the expected format
    3. Contains expected column information
    """
    # Call the actual tool functions from main.py
    from supabase_mcp.main import get_table_schema, get_tables

    # First get available tables in public schema
    tables_result = await get_tables("public")

    # Skip test if no tables available
    if tables_result.count == 0:
        pytest.skip("No tables available in public schema to test table schema")

    # Get the first table name to test with
    first_table = tables_result.rows[0]["table_name"]
    logger.info(f"Testing schema for table: {first_table}")

    # Execute the get_table_schema tool
    result = await get_table_schema("public", first_table)

    # Verify result structure
    assert hasattr(result, "rows"), "Result should have rows attribute"
    assert hasattr(result, "count"), "Result should have count attribute"
    assert hasattr(result, "status"), "Result should have status attribute"

    # Verify we have column data
    logger.info(f"Found {result.count} columns for table {first_table}")

    # If columns exist, verify their structure
    if result.count > 0:
        # Verify column structure
        first_column = result.rows[0]
        expected_fields = ["column_name", "data_type", "is_nullable"]
        for field in expected_fields:
            assert field in first_column, f"Column result missing '{field}' field"

        # Log column names for debugging
        column_names = [column.get("column_name") for column in result.rows]
        logger.info(f"Columns in {first_table}: {column_names}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_execute_sql_query_tool(integration_client):
    """Test the execute_sql_query tool runs arbitrary SQL queries.

    This test checks:
    1. The tool executes successfully
    2. Returns data in the expected format
    3. Can handle multiple query types
    """
    # Call the actual tool function from main.py
    from supabase_mcp.main import execute_sql_query

    # Test a simple SELECT query
    result = await execute_sql_query("SELECT 1 as number, 'test' as text")

    # Verify result structure
    assert hasattr(result, "rows"), "Result should have rows attribute"
    assert hasattr(result, "count"), "Result should have count attribute"
    assert hasattr(result, "status"), "Result should have status attribute"

    # Verify data matches what we expect
    assert result.count == 1, "Expected exactly one row"
    assert result.rows[0]["number"] == 1, "First column should be 1"
    assert result.rows[0]["text"] == "test", "Second column should be 'test'"

    # Test a query with no results
    result = await execute_sql_query(
        "SELECT * FROM information_schema.tables WHERE table_name = 'nonexistent_table_xyz123'"
    )
    assert result.count == 0, "Should return zero rows for non-matching query"

    # Test a more complex query that joins tables
    complex_result = await execute_sql_query("""
        SELECT
            table_schema,
            table_name,
            column_name
        FROM
            information_schema.columns
        WHERE
            table_schema = 'public'
        LIMIT 5
    """)

    # Log result for debugging
    logger.info(f"Complex query returned {complex_result.count} rows")

    # Verify structure of complex query result
    if complex_result.count > 0:
        expected_fields = ["table_schema", "table_name", "column_name"]
        for field in expected_fields:
            assert field in complex_result.rows[0], f"Result missing '{field}' field"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("CI"), reason="Management API test only runs in CI environment")
async def test_management_api_request_tool(integration_client):
    """Test the send_management_api_request tool for accessing Management API.

    This test:
    1. Only runs in CI environments where proper credentials are set up
    2. Makes a simple GET request to the API
    3. Verifies the tool handles requests correctly

    Requires:
    - SUPABASE_ACCESS_TOKEN environment variable to be set
    - Running in a CI environment
    """
    from supabase_mcp.api_manager.api_manager import SupabaseApiManager
    from supabase_mcp.main import send_management_api_request

    # Create a dedicated API manager for this test
    api_manager = await SupabaseApiManager.create()

    # Patch the get_manager method to return our dedicated instance
    with patch("supabase_mcp.api_manager.api_manager.SupabaseApiManager.get_manager", return_value=api_manager):
        try:
            # Make a simple GET request to list projects (a safe read-only operation)
            # This should work with any valid access token
            result = await send_management_api_request(
                method="GET", path="/v1/projects", request_params={}, request_body={}
            )

            # Verify we got a valid response - the API returns a list of projects
            assert isinstance(result, list), "Result should be a list of projects"

            # If we got project data, verify it has the expected structure
            if len(result) > 0:
                # Check the first project has expected fields
                project = result[0]
                assert isinstance(project, dict), "Project items should be dictionaries"
                assert "id" in project, "Project should have an ID"
                assert "name" in project, "Project should have a name"
                assert "database" in project, "Project should have database info"

                logger.info(f"Successfully retrieved {len(result)} projects")
            else:
                logger.warning("API returned an empty list of projects")
        finally:
            # Ensure we close the client even if the test fails
            await api_manager.close()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_live_dangerously_tool():
    """Test the live_dangerously tool for toggling safety modes.

    This test checks:
    1. The tool correctly toggles between safe and unsafe modes
    2. Works for both API and database services
    3. Returns the appropriate status information
    """
    from supabase_mcp.api_manager.api_safety_config import SafetyLevel
    from supabase_mcp.main import live_dangerously

    # Test database service mode switching
    # Start with safe mode
    result = await live_dangerously(service="database", enable=False)
    assert result["service"] == "database", "Response should identify database service"
    assert result["mode"] == "ro", "Database should be in read-only mode"

    # Switch to unsafe mode
    result = await live_dangerously(service="database", enable=True)
    assert result["service"] == "database", "Response should identify database service"
    assert result["mode"] == "rw", "Database should be in read-write mode"

    # Switch back to safe mode
    result = await live_dangerously(service="database", enable=False)
    assert result["service"] == "database", "Response should identify database service"
    assert result["mode"] == "ro", "Database should be in read-only mode"

    # Test API service mode switching
    # Start with safe mode
    result = await live_dangerously(service="api", enable=False)
    assert result["service"] == "api", "Response should identify API service"
    # Compare with the Enum value or check its string value
    assert result["mode"] == SafetyLevel.SAFE or result["mode"].value == "safe", "API should be in safe mode"

    # Switch to unsafe mode
    result = await live_dangerously(service="api", enable=True)
    assert result["service"] == "api", "Response should identify API service"
    assert result["mode"] == SafetyLevel.UNSAFE or result["mode"].value == "unsafe", "API should be in unsafe mode"

    # Switch back to safe mode
    result = await live_dangerously(service="api", enable=False)
    assert result["service"] == "api", "Response should identify API service"
    assert result["mode"] == SafetyLevel.SAFE or result["mode"].value == "safe", "API should be in safe mode"

    # Log final state
    logger.info("Successfully tested mode switching for both database and API services")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_management_api_spec_tool():
    """Test the get_management_api_spec tool returns the API specification.

    This test checks:
    1. The tool returns a valid OpenAPI specification
    2. The specification contains the expected structure
    """
    from supabase_mcp.main import get_management_api_spec

    # Get the API spec
    spec = await get_management_api_spec()

    # Verify result is a dictionary
    assert isinstance(spec, dict), "API spec should be a dictionary"

    # Verify spec has standard OpenAPI fields
    assert "openapi" in spec, "Spec should contain 'openapi' version field"
    assert "paths" in spec, "Spec should contain 'paths' section"
    assert "info" in spec, "Spec should contain 'info' section"

    # Verify paths contains API endpoints
    assert isinstance(spec["paths"], dict), "Paths should be a dictionary"
    assert len(spec["paths"]) > 0, "Spec should contain at least one path"

    # Log some basic spec info
    logger.info(f"API spec version: {spec.get('openapi')}")
    logger.info(f"API contains {len(spec['paths'])} endpoints")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_management_api_safety_rules_tool():
    """Test the get_management_api_safety_rules tool returns safety information.

    This test checks:
    1. The tool returns safety rule information
    2. The rules contain information about blocked and unsafe operations
    """
    from supabase_mcp.main import get_management_api_safety_rules

    # Get the safety rules
    rules = await get_management_api_safety_rules()

    # Verify result structure and content
    assert isinstance(rules, str), "Safety rules should be returned as a string"

    # Check for expected sections in the rules
    assert "BLOCKED Operations" in rules, "Rules should mention blocked operations"
    assert "UNSAFE Operations" in rules, "Rules should mention unsafe operations"
    assert "Current mode" in rules, "Rules should mention current mode"

    # Log the rules for debugging
    logger.info("Successfully retrieved Management API safety rules")
