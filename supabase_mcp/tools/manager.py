from __future__ import annotations

from enum import Enum
from pathlib import Path

import yaml

from supabase_mcp.logger import logger


class ToolName(str, Enum):
    """Enum of all available tools in the Supabase MCP server."""

    # Database tools
    GET_SCHEMAS = "get_schemas"
    GET_TABLES = "get_tables"
    GET_TABLE_SCHEMA = "get_table_schema"
    EXECUTE_POSTGRESQL = "execute_postgresql"
    RETRIEVE_MIGRATIONS = "retrieve_migrations"

    # Safety tools
    LIVE_DANGEROUSLY = "live_dangerously"
    CONFIRM_DESTRUCTIVE_OPERATION = "confirm_destructive_operation"

    # Management API tools
    SEND_MANAGEMENT_API_REQUEST = "send_management_api_request"
    GET_MANAGEMENT_API_SPEC = "get_management_api_spec"

    # Auth Admin tools
    GET_AUTH_ADMIN_METHODS_SPEC = "get_auth_admin_methods_spec"
    CALL_AUTH_ADMIN_METHOD = "call_auth_admin_method"

    # Logs & Analytics tools
    RETRIEVE_LOGS = "retrieve_logs"


class ToolManager:
    """Manager for tool descriptions and registration.

    This class is responsible for loading tool descriptions from YAML files
    and providing them to the main application.
    """

    _instance: ToolManager | None = None  # Singleton instance

    def __init__(self) -> None:
        """Initialize the tool manager."""
        self.descriptions: dict[str, str] = {}
        self._load_descriptions()

    @classmethod
    def get_instance(cls) -> ToolManager:
        """Get or create the singleton instance of ToolManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance of ToolManager."""
        if cls._instance is not None:
            cls._instance = None
            logger.info("ToolManager instance reset complete")

    def _load_descriptions(self) -> None:
        """Load tool descriptions from YAML files."""
        # Path to the descriptions directory
        descriptions_dir = Path(__file__).parent / "descriptions"

        # Check if the directory exists
        if not descriptions_dir.exists():
            raise FileNotFoundError(
                f"Tool descriptions directory not found: {descriptions_dir}"
            )

        # Load all YAML files in the directory
        for yaml_file in descriptions_dir.glob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    tool_descriptions = yaml.safe_load(f)
                    if tool_descriptions:
                        self.descriptions.update(tool_descriptions)
            except Exception as e:
                print(f"Error loading tool descriptions from {yaml_file}: {e}")

    def get_description(self, tool_name: str) -> str:
        """Get the description for a specific tool.

        Args:
            tool_name: The name of the tool to get the description for.

        Returns:
            The description of the tool, or an empty string if not found.
        """
        return self.descriptions.get(tool_name, "")
