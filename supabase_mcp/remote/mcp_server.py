from ..core.container import ServicesContainer
from ..tools.registry import ToolRegistry, ToolName
from mcp.server.fastmcp import FastMCP
from ..logger import logger
from .fast_api.environment import FastApiEnvironment
from .doc.httpstream_doc import admin
from ..settings import settings


class ServerMCP:
    """ """

    def __init__(
        self,
        name: str = "server",
        instructions: str = "This server specializes in supabase read and write operations.",
        exclude_tools: list[ToolName] = [],
        help_html_text: str | None = None,
        transfer_protocol="httpstream",
    ):
        """
        ### Aviable tranfer protocols
        - `httpstream`
        """

        def create_fastmcp_server() -> FastMCP:
            # Create an MCP server
            mcp_server: FastMCP | None = None
            if self.trasfer_protocol == "httpstream":
                mcp_server = FastMCP(
                    name=name,
                    instructions=instructions,
                    stateless_http=True,
                )
            else:
                Exception(f"{self.transfer_protocl} is not implemented")

            return mcp_server

        def add_to_server() -> None:
            """Establece este servidor como servidor default que se va a exponer en fastapi"""
            FastApiEnvironment.MCP_SERVERS.append(self)
            FastApiEnvironment.HTML_DOC = self.help_html_text

        def registry_tools() -> None:
            """ """
            registry = ToolRegistry(self.mcp_server, self.container)
            registry.register_tools()
            logger.info("✓ Tools registered with MCP server successfully.")

        def registry_resources() -> None:
            """ """
            Exception("Not Implemented Resources")

        def registry_prompt() -> None:
            """ """
            Exception("Not Implemented Resources")


        self.help_html_text: str = help_html_text
        self.name: str = name
        self.instructions: str = instructions
        self.exclude_tools: list[ToolName] = exclude_tools
        self.trasfer_protocol: str = transfer_protocol
        # Set MCP server
        self.mcp_server = create_fastmcp_server()
        
        logger.info(f"CREATING MCP SERVER {name.upper()}")
        # Create an Services Container
        self.container: ServicesContainer = ServicesContainer(
            mcp_server=self.mcp_server,
        )
        self.container.initialize_services(settings=settings)

        # Initialize server, tools, resources and prompts
        registry_tools()

        # Add to servers
        add_to_server()

        logger.info(f"✓ {self.name} MCP server created successfully.\n")
