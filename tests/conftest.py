import os
from collections.abc import Generator
from pathlib import Path

import pytest
from dotenv import load_dotenv

from supabase_mcp.client import SupabaseClient
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
    # Clear Settings singleton
    if hasattr(Settings, "_instance"):
        delattr(Settings, "_instance")

    # Clear SupabaseClient singleton
    if hasattr(SupabaseClient, "_instance"):
        delattr(SupabaseClient, "_instance")

    settings = Settings()
    logger.info(f"Clean settings initialized: {settings}")
    yield settings


@pytest.fixture
def integration_settings() -> Generator[Settings, None, None]:
    """Fixture that provides Settings instance for integration tests using .env.test"""
    # Clear Settings singleton
    if hasattr(Settings, "_instance"):
        delattr(Settings, "_instance")

    # Clear SupabaseClient singleton
    if hasattr(SupabaseClient, "_instance"):
        delattr(SupabaseClient, "_instance")

    # Load test environment
    test_env = load_test_env()
    original_env = dict(os.environ)

    # Set up test environment
    os.environ.update(test_env)

    settings = Settings()
    logger.info(f"Integration settings initialized: {settings}")

    yield settings

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
