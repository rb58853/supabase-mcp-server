from mcp.server.fastmcp import FastMCP

from supabase_mcp.core.container import Container
from supabase_mcp.logger import logger
from supabase_mcp.settings import settings
from supabase_mcp.tools.registry import ToolRegistry

# Create mcp instance
mcp = FastMCP("supabase")

# Initialize services
services_container = Container(mcp_server=mcp).initialize(settings)

# Register tools
mcp = ToolRegistry(mcp=mcp, services_container=services_container).register_tools()


def run_server() -> None:
    logger.info("Starting Supabase MCP server")
    mcp.run()


def run_inspector() -> None:
    """Inspector mode - same as mcp dev"""
    logger.info("Starting Supabase MCP server inspector")

    from mcp.cli.cli import dev

    return dev(__file__)


if __name__ == "__main__":
    logger.info("Starting Supabase MCP server")
    run_server()
