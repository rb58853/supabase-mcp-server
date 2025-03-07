from supabase_mcp.logger import logger


def create_mcp_server():
    try:
        return mcp
    except Exception as e:
        logger.error(f"Failed to create MCP server: {e}")
        raise e
