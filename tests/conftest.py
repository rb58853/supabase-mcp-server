import os
from collections.abc import Generator
from pathlib import Path

import pytest
from dotenv import load_dotenv

from supabase_mcp.db_client.db_client import SupabaseClient
from supabase_mcp.logger import logger
from supabase_mcp.settings import Settings


def load_test_env() -> dict:
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
def clean_environment() -> Generator[None, None, None]:
    """Fixture to provide a clean environment without Supabase-related variables"""
    # Store original environment
    original_env = dict(os.environ)

    # Remove Supabase-related environment variables
    for key in ["SUPABASE_PROJECT_REF", "SUPABASE_DB_PASSWORD"]:
        os.environ.pop(key, None)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def clean_settings(clean_environment) -> Generator[Settings, None, None]:
    """Fixture to provide a clean Settings instance without any environment variables"""

    # Clear SupabaseClient singleton
    if hasattr(SupabaseClient, "_instance"):
        delattr(SupabaseClient, "_instance")

    settings = Settings()
    logger.info(f"Clean settings initialized: {settings}")
    yield settings


@pytest.fixture
def custom_connection_settings() -> Generator[Settings, None, None]:
    """Fixture that provides Settings instance for integration tests using .env.test"""

    # Clear SupabaseClient singleton
    SupabaseClient.reset()

    # Load test environment
    test_env = load_test_env()
    original_env = dict(os.environ)

    # Set up test environment
    os.environ.update(test_env)

    # Create fresh settings instance
    settings = Settings()
    logger.info(f"Custom connection settings initialized: {settings}")

    yield settings

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def custom_connection_client(custom_connection_settings):
    """Fixture providing a client connected to test database"""
    client = SupabaseClient(settings_instance=custom_connection_settings)
    yield client
    client.close()  # Ensure connection is closed after test


@pytest.fixture
def integration_client() -> Generator[SupabaseClient, None, None]:
    """Fixture providing a client connected to a database for integration tests.

    This fixture uses the default settings for connecting to the database,
    which makes it work automatically with local Supabase or CI environments.
    """
    # Reset the SupabaseClient singleton to ensure we get a fresh instance
    SupabaseClient.reset()

    # Create client using default settings
    client = SupabaseClient.create()

    # Log connection details (without credentials)
    db_url_parts = client.db_url.split("@")
    if len(db_url_parts) > 1:
        safe_conn_info = db_url_parts[1]
    else:
        safe_conn_info = "unknown"
    logger.info(f"Integration client connecting to: {safe_conn_info}")

    yield client

    # Clean up
    client.close()
