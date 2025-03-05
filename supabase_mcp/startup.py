from supabase_mcp.logger import logger
from supabase_mcp.safety.configs.api_safety_config import APISafetyConfig
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
    api_config = APISafetyConfig()
    safety_manager.register_config(ClientType.API, api_config)
    logger.info("Registered API safety configuration")

    logger.info("✓ Safety configurations registered successfully")
