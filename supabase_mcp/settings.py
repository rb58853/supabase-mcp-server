from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
