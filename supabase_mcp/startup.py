from supabase_mcp.logger import logger
from supabase_mcp.safety.configs.sql_safety_config import SQLSafetyConfig
from supabase_mcp.safety.core import ClientType
from supabase_mcp.safety.safety_manager import SafetyManager


def register_safety_configs():
    """Register all safety configurations with the SafetyManager."""
    safety_manager = SafetyManager.get_instance()

    # Register SQL safety config
    sql_config = SQLSafetyConfig()
    safety_manager.register_config(ClientType.DATABASE, sql_config)
    logger.info("Registered SQL safety configuration")

    # Register API safety config
    # TODO: Create a proper adapter for the API safety config
    # Note: We need to adapt the SafetyConfig to match the SafetyConfigBase interface
    # This is a temporary solution until we refactor the API safety config
    # api_config = SafetyConfig()
    # safety_manager.register_config(ClientType.API, api_config)
    logger.info("API safety configuration will be registered after refactoring")

    logger.info("✓ Safety configurations registered successfully")
