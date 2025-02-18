import logging


def setup_logger():
    """Configure logging for the MCP server."""
    logger = logging.getLogger("supabase-mcp")

    # Set level
    logger.setLevel(logging.INFO)

    return logger


logger = setup_logger()
