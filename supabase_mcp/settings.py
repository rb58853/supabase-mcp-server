import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from supabase_mcp.logger import logger


def find_config_file() -> str | None:
    """Find the .env file in order of precedence:
    1. Current working directory (where command is run)
    2. Global config:
       - Windows: %APPDATA%/supabase-mcp/.env
       - macOS/Linux: ~/.config/supabase-mcp/.env
    """
    logger.info("Searching for configuration files...")

    # 1. Check current directory
    cwd_config = Path.cwd() / ".env"
    if cwd_config.exists():
        logger.info(f"Found local config file: {cwd_config}")
        return str(cwd_config)

    # 2. Check global config
    home = Path.home()
    if os.name == "nt":  # Windows
        global_config = Path(os.environ.get("APPDATA", "")) / "supabase-mcp" / ".env"
    else:  # macOS/Linux
        global_config = home / ".config" / "supabase-mcp" / ".env"

    if global_config.exists():
        logger.info(f"Found global config file: {global_config}")
        return str(global_config)

    logger.warning("No config files found, using default settings")
    return None


class Settings(BaseSettings):
    """Initializes settings for Supabase MCP server."""

    supabase_project_ref: str = Field(
        default="127.0.0.1:54322",  # Local Supabase default
        env="SUPABASE_PROJECT_REF",
        description="Supabase project ref",
    )
    supabase_db_password: str = Field(
        default="postgres",  # Local Supabase default
        env="SUPABASE_DB_PASSWORD",
        description="Supabase db password",
    )

    @classmethod
    def with_config(cls, config_file: str | None = None) -> "Settings":
        """Create Settings with specific config file.

        Args:
            config_file: Path to .env file to use, or None for no config file
        """

        # Create a new Settings class with the specific config
        class SettingsWithConfig(cls):
            model_config = SettingsConfigDict(env_file=config_file, env_file_encoding="utf-8")

        instance = SettingsWithConfig()

        # Log configuration source and precedence
        env_vars_present = any(var in os.environ for var in ["SUPABASE_PROJECT_REF", "SUPABASE_DB_PASSWORD"])

        if env_vars_present:
            logger.warning("Using environment variables (highest precedence)")
            if config_file:
                logger.warning(f"Note: Config file {config_file} exists but environment variables take precedence")
            for var in ["SUPABASE_PROJECT_REF", "SUPABASE_DB_PASSWORD"]:
                if var in os.environ:
                    logger.info(f"Using {var} from environment")
        elif config_file:
            logger.info(f"Using settings from config file: {config_file}")
        else:
            logger.info("Using default settings (local development)")

        # Log final configuration
        logger.info("Final configuration:")
        logger.info(f"  Project ref: {instance.supabase_project_ref}")
        logger.info(f"  Password: {'*' * len(instance.supabase_db_password)}")

        return instance


# Module-level singleton - maintains existing interface
settings = Settings.with_config(find_config_file())
