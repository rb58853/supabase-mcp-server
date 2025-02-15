from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Initializes settings for Supabase MCP server."""

    supabase_project_ref: str = Field(..., env="SUPABASE_PROJECT_REF", description="Supabase project ref")
    supabase_db_password: str = Field(..., env="SUPABASE_DB_PASSWORD", description="Supabase db password")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
