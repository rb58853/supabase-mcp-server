from mcp.server.fastmcp import FastMCP

# from ..mcp_server import ServerMCP
from fastapi import FastAPI


class FastApiEnvironment:
    # MCP_SERVERS: list[ServerMCP] = []
    MCP_SERVERS: list = []
    """Lis of MCP Servers will be use as default server in httpstream api"""

    def clear_servers():
        FastApiEnvironment.MCP_SERVERS = []
