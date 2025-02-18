# Potentially integration tests
# Can you test that server runs?
# Can you test that inspector runs?
# Can you test that the server replies to connect or list tools?

import asyncio
import subprocess
import sys
from unittest.mock import patch

from supabase_mcp.main import inspector, mcp, run


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
    required_tools = {"get_db_schemas", "get_tables", "get_table_schema", "query_db"}
    assert required_tools.issubset(tool_names), f"Missing required tools. Found: {tool_names}"


def test_run_server_starts():
    """Test that server run function executes without errors"""
    with patch("supabase_mcp.main.mcp.run") as mock_run:
        run()
        mock_run.assert_called_once()


def test_inspector_mode():
    """Test that inspector mode initializes correctly"""
    with patch("mcp.cli.cli.dev") as mock_dev:
        inspector()
        mock_dev.assert_called_once_with(file_spec="supabase_mcp/main.py")


def test_package_script_runs():
    """Test that the package can be run as a module"""
    result = subprocess.run(
        [sys.executable, "-m", "supabase_mcp.main"],
        capture_output=True,
        text=True,
        timeout=2,  # Kill after 2 seconds since it's a server
    )
    assert "Starting Supabase MCP server" in result.stdout


def test_mcp_server_tools():
    """Test that all expected tools are registered and accessible"""
    tools = asyncio.run(mcp.list_tools())

    # Verify we have all our tools
    tool_names = {tool.name for tool in tools}
    assert "get_db_schemas" in tool_names
    assert "get_tables" in tool_names
    assert "get_table_schema" in tool_names
    assert "query_db" in tool_names

    # Verify tools have descriptions
    for tool in tools:
        assert tool.description, f"Tool {tool.name} missing description"
        assert tool.inputSchema is not None, f"Tool {tool.name} missing input schema"


@pytest.mark.integration
async def test_db_tools_execution():
    """Integration test that verifies DB tools actually work

    Requires:
    - SUPABASE_PROJECT_REF
    - SUPABASE_DB_PASSWORD
    environment variables to be set
    """
    # Get schemas
    schemas = await mcp.call_tool("get_db_schemas", {})
    assert len(schemas) > 0, "Expected at least one schema"
    assert any(schema for schema in schemas if "public" in str(schema)), "Expected public schema"

    # Get tables from public schema
    tables = await mcp.call_tool("get_tables", {"schema": "public"})
    assert isinstance(tables, list), "Expected list of tables"

    # Try a simple query
    query_result = await mcp.call_tool("query_db", {"query": "SELECT current_database();"})
    assert "postgres" in str(query_result), "Expected postgres database"
