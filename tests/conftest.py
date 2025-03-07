import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from supabase_mcp.api_service.api_client import APIClient
from supabase_mcp.database.postgres_client import AsyncSupabaseClient
from supabase_mcp.database.query_manager import QueryManager
from supabase_mcp.logger import logger
from supabase_mcp.sdk.sdk_client import SupabaseSDKClient
from supabase_mcp.settings import Settings, find_config_file
from supabase_mcp.tools import ToolManager


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


@pytest.fixture(scope="class")
def settings_integration() -> Settings:
    """Fixture providing settings for integration tests.

    This fixture loads settings from environment variables or .env.test file.
    """
    return Settings.with_config(find_config_file(".env.test"))


@pytest.fixture
def tool_manager_integration() -> ToolManager:
    """Fixture providing a tool manager for integration tests."""
    return ToolManager()


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


@pytest_asyncio.fixture(autouse=True, scope="class")
async def postgres_client_integration(settings_integration: Settings) -> AsyncGenerator[AsyncSupabaseClient, None]:
    """Fixture providing a database client connected to a database for integration tests.

    This fixture creates an AsyncSupabaseClient connected to the test database
    for integration tests. The client is automatically used for all tests.
    It is scoped to the class level to avoid teardown issues with event loops.
    """
    # BEFORE TEST: Reset all global singletons to ensure fresh clients

    # Reset the Postgres client singleton
    await AsyncSupabaseClient.reset()

    # Create a new client
    client = AsyncSupabaseClient(settings_instance=settings_integration)

    # Log connection details (without credentials)
    db_url_parts = client.db_url.split("@")
    if len(db_url_parts) > 1:
        safe_conn_info = db_url_parts[1]
    else:
        safe_conn_info = "unknown"
    logger.info(f"Integration client connecting to: {safe_conn_info}")

    try:
        # Yield the client for the tests to use
        yield client
    finally:
        await client.close()


@pytest_asyncio.fixture(autouse=True)
async def query_manager_integration(
    postgres_client_integration: AsyncSupabaseClient,
) -> AsyncGenerator[QueryManager, None]:
    """Fixture providing a query manager for integration tests."""
    query_manager = QueryManager(postgres_client_integration)
    yield query_manager


@pytest_asyncio.fixture(autouse=True)
async def api_client_integration() -> AsyncGenerator[APIClient, None]:
    """Fixture providing an API client for integration tests.

    This client is configured to make real API requests to the Supabase Management API.
    """
    # Create a new API client
    client = APIClient()

    try:
        # Yield the client for the test to use
        yield client
    finally:
        # Clean up by closing the client
        await client.close()


@pytest_asyncio.fixture(autouse=True, scope="class")
async def sdk_client_integration(settings_integration: Settings) -> SupabaseSDKClient:
    """Fixture providing a function-scoped SDK client for integration tests.

    This ensures the SDK client is created once per test function and properly closed at the end.
    """

    # Reset the SDK client singleton
    SupabaseSDKClient._instance = None

    # Create a new SDK client
    client = await SupabaseSDKClient.create(
        project_ref=settings_integration.supabase_project_ref,
        service_role_key=settings_integration.supabase_service_role_key,
    )
    return client
