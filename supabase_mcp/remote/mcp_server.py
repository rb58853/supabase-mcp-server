from ..core.container import ServicesContainer
from ..tools.registry import ToolRegistry
from mcp.server.fastmcp import FastMCP
from ..logger import logger
from .fast_api.environment import FastApiEnvironment


class ServerMCP:
    """
    ### Use Case
    Create a instance of `ServerMCP`. For example:
    ```python
    #This server will be the api mcp server

    ```
    """

    def __init__(
        self,
        name: str = "supabase-mcp-server",
        instructions: str = "This server specializes in supabase operations.",
        use_as_server: bool = True,
        help_html_text: str | None = None,
    ):
        # Create an MCP server
        self.mcp_server: FastMCP = FastMCP(
            name=name,
            instructions=instructions,
            stateless_http=True,
        )

        # Create an Services Container
        self.container: ServicesContainer = ServicesContainer(
            mcp_server=self.mcp_server
        )

        self.help_html_text = help_html_text
        if use_as_server:
            self.use_as_server()

    def registry_tools(self) -> None:
        """ """
        registry = ToolRegistry(self.mcp_server, self.container)
        registry.register_tools()
        logger.info("✓ Tools registered with MCP server successfully.")

    def registry_resources(self) -> None:
        """ """
        Exception("Not Implemented Resources")

    def use_as_server(self):
        """Establece este servidor como servidor default que se va a exponer en fastapi"""
        FastApiEnvironment.MCP_SERVER = self.mcp_server
