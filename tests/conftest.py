import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from supabase_mcp.database_service.postgres_client import AsyncSupabaseClient
from supabase_mcp.database_service.query_manager import QueryManager
from supabase_mcp.logger import logger
from supabase_mcp.settings import Settings, find_config_file
from supabase_mcp.tool_manager import ToolManager


@pytest.fixture
def clean_environment() -> Generator[None, None, None]:
    """Fixture to provide a clean environment without any Supabase-related env vars."""
    # Save original environment
    original_env = dict(os.environ)

    # Remove all Supabase-related environment variables
    for key in list(os.environ.keys()):
        if key.startswith("SUPABASE_"):
            del os.environ[key]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


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
def settings_integration() -> Settings:
    """Fixture providing settings for integration tests.

    This fixture loads settings from environment variables or .env.test file.
    """
    return Settings.with_config(find_config_file(".env.test"))


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


@pytest_asyncio.fixture
async def postgres_client_custom_connection(settings_integration_custom_env: Settings):
    """Fixture providing a client connected to test database"""
    client = AsyncSupabaseClient(settings_instance=settings_integration_custom_env)
    yield client
    await client.close()  # Use await instead of asyncio.run()


@pytest_asyncio.fixture
async def postgres_client_integration(settings_integration: Settings) -> AsyncGenerator[AsyncSupabaseClient, None]:
    """Fixture providing a database client connected to a database for integration tests.

    This fixture uses the default settings for connecting to the database,
    which makes it work automatically with local Supabase or CI environments.
    """
    # Reset the SupabaseClient singleton to ensure we get a fresh instance
    await AsyncSupabaseClient.reset()

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
    await client.close()


@pytest_asyncio.fixture
async def query_manager_integration(
    postgres_client_integration: AsyncSupabaseClient,
) -> AsyncGenerator[QueryManager, None]:
    """Fixture providing a query manager for integration tests."""
    query_manager = QueryManager(postgres_client_integration)
    yield query_manager


@pytest.fixture()
def tool_manager_integration() -> ToolManager:
    """Fixture providing a tool manager for integration tests."""
    return ToolManager()


# For backward compatibility
integration_client = postgres_client_integration
