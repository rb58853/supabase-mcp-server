from mcp.server.fastmcp import FastMCP

# from ..mcp_server import ServerMCP
from fastapi import FastAPI


class FastApiEnvironment:
    # MCP_SERVERS: list[ServerMCP] = []
    MCP_SERVERS: list = []
    """Lis of MCP Servers will be use as default server in httpstream api"""

    BASE_IP:str|None = "http://0.0.0.0:8080"
    """Public hosted root IP """
    
    #DNS Anula el uso de BASE_IP
    DNS:str|None = None
    """Public hosted DNS"""
    
    def clear_servers():
        FastApiEnvironment.MCP_SERVERS = []