import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from supabase_mcp.logger import logger

# Startup scenarios
# .env file exists and env vars are set
# .env.mcp file exists and env vars are set
# .env file exists but env vars are not set
# .env.mcp file exists but env vars are not set
# Global config file exists
# No config files exist


def find_config_file() -> str | None:
    """Find the .env.mcp file in order of precedence:
    1. Current working directory (where command is run)
    2. Global config (~/.config/supabase-mcp/.env.mcp)
    """
    logger.info("Searching for configuration files...")

    # 1. Check current directory
    cwd_config = Path.cwd() / ".env.mcp"
    if cwd_config.exists():
        logger.info(f"Found local config file: {cwd_config}")
        return str(cwd_config)

    # 2. Check global config
    home = Path.home()
    global_config = home / ".config" / "supabase-mcp" / ".env.mcp"
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

    model_config = SettingsConfigDict(
        env_file=find_config_file(),
        env_file_encoding="utf-8",
        # Environment variables take precedence over .env.mcp file
        env_nested_delimiter="__",
        extra="ignore",
    )

    def __init__(self, **kwargs):
        config_file = find_config_file()
        super().__init__(**kwargs)

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
        logger.info(f"  Project ref: {self.supabase_project_ref}")
        logger.info(f"  Password: {'*' * len(self.supabase_db_password)}")


settings = Settings()
