from mcp.server.fastmcp import FastMCP

from supabase_mcp.logger import logger


def create_mcp_server():
    try:
        mcp = FastMCP("supabase")
        return mcp
    except Exception as e:
        logger.error(f"Failed to create MCP server: {e}")
        raise e
