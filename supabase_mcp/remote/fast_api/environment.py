from mcp.server.fastmcp import FastMCP


class FastApiEnvironment:
    MCP_SERVER: FastMCP | None = None
    """MCP Server will be use as default server in httpstream api"""