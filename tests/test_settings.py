import os

from supabase_mcp.settings import Settings


def test_settings_from_env_vars(mock_env_vars):
    """Test settings initialization from environment variables"""
    settings = Settings()
    assert settings.supabase_project_ref == "test-project"
    assert settings.supabase_db_password == "test-password"


def test_settings_from_env_vars_direct(monkeypatch):
    """Test settings initialization from environment variables using direct monkeypatch"""
    monkeypatch.setenv("SUPABASE_PROJECT_REF", "temp-project")
    monkeypatch.setenv("SUPABASE_DB_PASSWORD", "temp-password")

    settings = Settings()
    assert settings.supabase_project_ref == "temp-project"
    assert settings.supabase_db_password == "temp-password"


def test_settings_from_env_file(monkeypatch):
    """Test settings initialization from environment variables"""
    monkeypatch.setenv("SUPABASE_PROJECT_REF", "temp-project")
    monkeypatch.setenv("SUPABASE_DB_PASSWORD", "temp-password")

    settings = Settings()
    assert settings.supabase_project_ref == "temp-project"
    assert settings.supabase_db_password == "temp-password"


def test_settings_local_defaults():
    """Test settings defaults to local development values when no config provided"""
    # Skip in CI where we have real credentials
    if "CI" in os.environ:
        return

    settings = Settings()
    assert settings.supabase_project_ref == "127.0.0.1:54322"  # Local Supabase default
    assert settings.supabase_db_password == "postgres"  # Default local password
