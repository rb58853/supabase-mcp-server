"""Supabase MCP Server package."""

from supabase_mcp._version import __version__, version, version_tuple
from supabase_mcp.remote.default_servers import ServerMCP, ToolName, httpstream_api
from supabase_mcp.remote.fast_api.environment import FastApiEnvironment

__all__ = [
    "__version__",
    "version",
    "version_tuple",
    "httpstream_api",
    "ServerMCP",
    "FastApiEnvironment",
    "ToolName",
]
