from ..core.container import ServicesContainer
from ..tools.registry import ToolRegistry, ToolName
from mcp.server.fastmcp import FastMCP
from ..logger import logger
from .fast_api.environment import FastApiEnvironment
from .doc.html_doc import server_info
from ..settings import settings


class ServerMCP:
    """
    Represents a server specialized in Supabase read and write operations. This class initializes and manages an MCP server, registers tools, and integrates the server into the FastAPI environment. It also provides methods for server configuration and documentation.

    Attributes:
        name (str): The name of the server.
        instructions (str): Instructions describing the server's purpose.
        exclude_tools (list[ToolName]): List of tools to exclude from the server.
        transfer_protocol (str): The transfer protocol used by the server.
        mcp_server (FastMCP): The MCP server instance.
        container (ServicesContainer): The container for managing services.
    """

    def __init__(
        self,
        name: str = "server",
        instructions: str = "This server specializes in supabase read and write operations.",
        exclude_tools: list[ToolName] = [],
        transfer_protocol="httpstream",
    ):
        """
        Initializes the ServerMCP instance.
        ## Aviable tranfer protocols
        - `httpstream`

        Args:
            name (str): The name of the server. Defaults to "server".
            instructions (str): Instructions describing the server's purpose. Defaults to "This server specializes in supabase read and write operations."
            exclude_tools (list[ToolName]): List of tools to exclude from the server. Defaults to an empty list.
            transfer_protocol (str): The transfer protocol used by the server. Defaults to "httpstream".

        Raises:
            Exception: If the specified transfer protocol is not implemented.

        """

        self.name: str = name
        self.instructions: str = instructions
        self.exclude_tools: list[ToolName] = exclude_tools
        self.trasfer_protocol: str = transfer_protocol
        # Set MCP server
        self.mcp_server = self.__create_fastmcp_server(
            name=self.name,
            instructions=self.instructions,
        )

        logger.info(f"CREATING MCP SERVER {name.upper()}")
        # Create an Services Container
        self.container: ServicesContainer = ServicesContainer(
            mcp_server=self.mcp_server,
        )
        self.container.initialize_services(settings=settings)

        # Initialize server, tools, resources and prompts
        self.__registry_tools(server=self)

        # Add to servers
        self.add_to_server()

        logger.info(f"✓ {self.name} MCP server created successfully.\n")

    def __create_fastmcp_server(self, name: str, instructions: str) -> FastMCP:
        # Create an MCP server
        mcp_server: FastMCP | None = None
        if self.trasfer_protocol == "httpstream":
            mcp_server = FastMCP(
                name=name,
                instructions=instructions,
                stateless_http=True,
            )
        else:
            Exception(f"{self.trasfer_protocol} is not implemented")

        return mcp_server

    def add_to_server(self) -> None:
        """Agrega este servidor a los servidores default que se van a exponer en fastapi. Al momento de crearse, se agrega automaticamente"""
        FastApiEnvironment.MCP_SERVERS.append(self)

    def remove_from_servers(self) -> None:
        """Elimina este servidor desde los servidores"""
        FastApiEnvironment.MCP_SERVERS.remove(self)

    def __registry_tools(self, server=None) -> None:
        """ """
        registry = ToolRegistry(self.mcp_server, self.container)
        registry.register_tools(server=server)
        logger.info("✓ Tools registered with MCP server successfully.")

    def __registry_resources(self) -> None:
        """ """
        Exception("Not Implemented Resources")

    def __registry_prompt(self) -> None:
        """ """
        Exception("Not Implemented Resources")

    def help_html_text(self) -> str:
        """
        Generates an HTML representation of the server's information.
        Returns:
            server_info (str): HTML text containing the server's name, description, and registered tools.
        """
        return server_info(
            name=self.name,
            description=self.instructions,
            tools=[tool.name for tool in self.mcp_server._tool_manager.list_tools()],
        )
