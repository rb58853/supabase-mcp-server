import os

import pytest

from supabase_mcp.client import SupabaseClient


def test_connection_string_local_default():
    """Test connection string generation with local development defaults"""
    client = SupabaseClient(project_ref="127.0.0.1:54322", db_password="postgres")
    assert client.db_url == "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


def test_connection_string_integration(integration_settings):
    """Test connection string generation with integration settings from .env.test"""
    client = SupabaseClient(settings_instance=integration_settings)
    expected_url = (
        f"postgresql://postgres.{integration_settings.supabase_project_ref}:"
        f"{integration_settings.supabase_db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )
    assert client.db_url == expected_url


def test_connection_string_explicit_params():
    """Test connection string generation with explicit parameters"""
    client = SupabaseClient(project_ref="my-project", db_password="my-password")
    expected_url = "postgresql://postgres.my-project:my-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    assert client.db_url == expected_url


@pytest.mark.skipif(not os.getenv("CI"), reason="Test only runs in CI environment")
def test_connection_string_ci(integration_settings):
    """Test connection string generation in CI environment"""
    client = SupabaseClient(settings_instance=integration_settings)
    expected_url = (
        f"postgresql://postgres.{integration_settings.supabase_project_ref}:"
        f"{integration_settings.supabase_db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )
    assert client.db_url == expected_url
