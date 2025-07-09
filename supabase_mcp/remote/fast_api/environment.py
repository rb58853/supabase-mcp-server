# from mcp.server.fastmcp import FastMCP

# from ..mcp_server import ServerMCP
# from fastapi import FastAPI


class FastApiEnvironment:
    # MCP_SERVERS: list[ServerMCP] = []
    MCP_SERVERS: list = []
    """Lis of MCP Servers will be use as default server in httpstream api"""

    # This var is used only for documentation
    EXPOSE_IP: str | None = "http://127.0.0.1:8080"
    """Public hosted root IP """

    # DNS Anula el uso de EXPOSE_IP
    # This var is used only for documentation
    DNS: str | None = None
    """Public hosted DNS"""

    def clear_servers():
        FastApiEnvironment.MCP_SERVERS = []
