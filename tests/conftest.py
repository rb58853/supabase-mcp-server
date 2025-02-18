import os

import pytest

from supabase_mcp.client import SupabaseClient
from supabase_mcp.settings import Settings


@pytest.fixture(autouse=True)
def clear_settings():
    """Fixture to clear settings singleton between tests"""
    # Clear the singleton instance if it exists
    if hasattr(Settings, "_instance"):
        delattr(Settings, "_instance")
    yield


@pytest.fixture
def mock_env_vars(clear_settings):
    """Fixture to provide mock Supabase environment variables for production"""
    original_env = dict(os.environ)

    # Clear any existing env vars first
    for key in ["SUPABASE_PROJECT_REF", "SUPABASE_DB_PASSWORD"]:
        os.environ.pop(key, None)

    # Set up production environment
    test_vars = {"SUPABASE_PROJECT_REF": "test-project", "SUPABASE_DB_PASSWORD": "test-password"}
    os.environ.update(test_vars)

    yield test_vars

    # Cleanup
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_local_env_vars(clear_settings):
    """Fixture to test local development defaults"""
    original_env = dict(os.environ)

    # Clear any existing env vars to let defaults take effect
    for key in ["SUPABASE_PROJECT_REF", "SUPABASE_DB_PASSWORD"]:
        os.environ.pop(key, None)

    yield {
        "SUPABASE_PROJECT_REF": "127.0.0.1:54322",  # Should match settings default
        "SUPABASE_DB_PASSWORD": "postgres",  # Should match settings default
    }

    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def integration_settings(monkeypatch, request):
    """Fixture that provides a fresh Settings instance for integration tests"""
    # Clear Settings singleton
    if hasattr(Settings, "_instance"):
        delattr(Settings, "_instance")

    # Clear SupabaseClient singleton
    if hasattr(SupabaseClient, "_instance"):
        delattr(SupabaseClient, "_instance")

    # Prevent loading from any .env file
    monkeypatch.setattr("supabase_mcp.settings.find_config_file", lambda: None)

    settings = Settings()
    return settings
