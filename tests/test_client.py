import os

from supabase_mcp.client import SupabaseClient


def test_connection_string_local_default(integration_settings):
    """Test connection string generation with local development defaults"""
    # Skip in CI where we have real credentials
    if "CI" in os.environ:
        return

    client = SupabaseClient()
    assert client.db_url == "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


def test_connection_string_production(monkeypatch, integration_settings):
    """Test connection string generation with production settings"""
    # Patch the module-level settings
    monkeypatch.setattr("supabase_mcp.client.settings.supabase_project_ref", "abc123xyz")
    monkeypatch.setattr("supabase_mcp.client.settings.supabase_db_password", "secret-password")

    client = SupabaseClient()
    assert (
        client.db_url
        == "postgresql://postgres.abc123xyz:secret-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )
