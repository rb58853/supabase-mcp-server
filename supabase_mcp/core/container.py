from mcp.server.fastmcp import FastMCP

from supabase_mcp.logger import logger
from supabase_mcp.services.api.api_client import ManagementAPIClient
from supabase_mcp.services.api.api_manager import SupabaseApiManager
from supabase_mcp.services.database.postgres_client import PostgresClient
from supabase_mcp.services.database.query_manager import QueryManager
from supabase_mcp.services.safety.safety_manager import SafetyManager
from supabase_mcp.services.sdk.sdk_client import SupabaseSDKClient
from supabase_mcp.settings import Settings
from supabase_mcp.tools import ToolManager


class Container:
    def __init__(
        self,
        mcp_server: FastMCP,
        postgres_client: PostgresClient | None = None,
        api_client: ManagementAPIClient | None = None,
        sdk_client: SupabaseSDKClient | None = None,
        api_manager: SupabaseApiManager | None = None,
        safety_manager: SafetyManager | None = None,
        query_manager: QueryManager | None = None,
        tool_manager: ToolManager | None = None,
    ) -> None:
        """Create a new container container reference"""
        self.mcp_server = mcp_server
        self.postgres_client = postgres_client
        self.api_client = api_client
        self.api_manager = api_manager
        self.sdk_client = sdk_client
        self.safety_manager = safety_manager
        self.query_manager = query_manager
        self.tool_manager = tool_manager

    def initialize(self, settings: Settings) -> "Container":
        """Initializes all services in a synchronous manner to satisfy MCP runtime requirements"""
        # Create clients
        self.postgres_client = PostgresClient.get_instance(settings=settings)
        self.api_client = ManagementAPIClient(settings=settings)  # not a singleton, simple
        self.sdk_client = SupabaseSDKClient.get_instance(settings=settings)

        # Create managers
        self.safety_manager = SafetyManager.get_instance()
        self.api_manager = SupabaseApiManager.get_instance(
            api_client=self.api_client,
            safety_manager=self.safety_manager,
        )
        self.query_manager = QueryManager(
            postgres_client=self.postgres_client,
            safety_manager=self.safety_manager,
        )
        self.tool_manager = ToolManager.get_instance()

        # Register safety configs
        self.safety_manager.register_safety_configs()

        logger.info("✓ All services initialized successfully.")
        return self
