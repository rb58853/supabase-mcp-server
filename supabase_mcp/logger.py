import logging
import sys


def setup_logger():
    """Configure logging for the MCP server."""
    logger = logging.getLogger("supabase-mcp")

    # Only add handler if none exist (prevent duplicate handlers)
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)

        # Create formatter
        formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%y/%m/%d %H:%M:%S")

        # Add formatter to handler
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    # Set level
    logger.setLevel(logging.INFO)

    return logger


logger = setup_logger()
