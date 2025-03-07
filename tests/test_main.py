import asyncio
import subprocess
from unittest.mock import ANY, patch

import pytest

from supabase_mcp.logger import logger
from supabase_mcp.main import create_server, mcp, run_inspector

# === UNIT TESTS ===


class TestMain:
    """Unit tests for main MCP server modules."""

    @pytest.mark.unit
    def test_mcp_server_initializes(self):
        """Test that MCP server initializes with default configuration and tools"""
        # Verify server name
        assert mcp.name == "supabase"

        # Verify tools are properly registered using the actual MCP protocol
        tools = asyncio.run(mcp.list_tools())

        # We should have at least 8 tools (the core functionality)
        assert len(tools) >= 8, f"Expected at least 8 tools, but got {len(tools)}"

        # Log the actual number of tools for reference
        logger.info(f"Found {len(tools)} MCP tools registered")

        # Verify each tool has proper MCP protocol structure
        for tool in tools:
            assert tool.name, "Tool must have a name"
            assert tool.description, "Tool must have a description"
            assert tool.inputSchema, "Tool must have an input schema"

        # Verify we have tools for core functionality categories
        # Instead of checking specific names, check for categories of functionality
        tool_names = {tool.name for tool in tools}

        # Check that we have database tools
        assert any("schema" in name.lower() for name in tool_names), "Missing schema-related tools"
        assert any("table" in name.lower() for name in tool_names), "Missing table-related tools"

        # Check that we have SQL execution capability
        assert any(
            "sql" in name.lower() or "postgresql" in name.lower() or "query" in name.lower() for name in tool_names
        ), "Missing SQL execution tools"

        # Log all available tools for debugging
        tool_list = ", ".join(sorted(tool_names))
        logger.info(f"Available MCP tools: {tool_list}")

    @pytest.mark.unit
    def test_run_server_starts(self):
        """Test that server run function executes without errors"""
        with patch("supabase_mcp.main.mcp.run") as mock_run:
            create_server()
            mock_run.assert_called_once()

    @pytest.mark.unit
    def test_inspector_mode(self):
        """Test that inspector mode initializes correctly"""
        with patch("mcp.cli.cli.dev") as mock_dev:
            run_inspector()
            mock_dev.assert_called_once_with(file_spec=ANY)

    @pytest.mark.unit
    def test_server_command_starts(self):
        """Test that the server command executes without errors"""
        result = subprocess.run(
            ["supabase-mcp-server"],
            capture_output=True,
            text=True,
            timeout=2,  # Kill after 2 seconds since it's a server
        )
        assert result.returncode == 0, f"Server command failed: {result.stderr}"
