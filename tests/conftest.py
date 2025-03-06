import asyncio
import os
from collections.abc import Generator
from pathlib import Path

import pytest
from dotenv import load_dotenv

from supabase_mcp.database_service.postgres_client import AsyncSupabaseClient
from supabase_mcp.database_service.query_manager import QueryManager
from supabase_mcp.logger import logger
from supabase_mcp.settings import Settings, find_config_file
from supabase_mcp.tool_manager import ToolManager


def load_test_env() -> dict[str, str | None]:
    """Load test environment variables from .env.test file"""
    env_test_path = Path(__file__).parent.parent / ".env.test"
    if not env_test_path.exists():
        raise FileNotFoundError(f"Test environment file not found at {env_test_path}")

    load_dotenv(env_test_path)
    return {
        "SUPABASE_PROJECT_REF": os.getenv("SUPABASE_PROJECT_REF"),
        "SUPABASE_DB_PASSWORD": os.getenv("SUPABASE_DB_PASSWORD"),
    }


@pytest.fixture
def settings_integration() -> Generator[Settings, None, None]:
    """Fixture to provide a clean Settings instance without any environment variables"""

    yield Settings.with_config(find_config_file(".env.test"))


@pytest.fixture
def settings_integration_custom_env() -> Generator[Settings, None, None]:
    """Fixture that provides Settings instance for integration tests using .env.test"""

    # Load custom environment variables
    test_env = load_test_env()
    original_env = dict(os.environ)

    # Set up test environment
    for key, value in test_env.items():
        if value is not None:
            os.environ[key] = value

    # Create fresh settings instance
    settings = Settings()
    logger.info(f"Custom connection settings initialized: {settings}")

    yield settings

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def postgres_client_custom_connection(settings_integration_custom_env: Settings):
    """Fixture providing a client connected to test database"""
    client = AsyncSupabaseClient(settings_instance=settings_integration_custom_env)
    yield client
    asyncio.run(client.close())  # Ensure connection is closed after test


@pytest.fixture
def postgres_client_integration(settings_integration: Settings) -> Generator[AsyncSupabaseClient, None, None]:
    """Fixture providing a database client connected to a database for integration tests.

    This fixture uses the default settings for connecting to the database,
    which makes it work automatically with local Supabase or CI environments.
    """
    # Reset the SupabaseClient singleton to ensure we get a fresh instance
    asyncio.run(AsyncSupabaseClient.reset())

    client = AsyncSupabaseClient(settings_instance=settings_integration)

    # Log connection details (without credentials)
    db_url_parts = client.db_url.split("@")
    if len(db_url_parts) > 1:
        safe_conn_info = db_url_parts[1]
    else:
        safe_conn_info = "unknown"
    logger.info(f"Integration client connecting to: {safe_conn_info}")

    yield client

    # Clean up
    asyncio.run(client.close())


@pytest.fixture()
def query_manager_integration(postgres_client_integration: AsyncSupabaseClient) -> QueryManager:
    """Fixture providing a query manager connected to a database for integration tests."""
    return QueryManager(postgres_client_integration)


@pytest.fixture()
def tool_manager_integration() -> ToolManager:
    """Fixture providing a tool manager for integration tests."""
    return ToolManager()


# For backward compatibility
integration_client = postgres_client_integration
