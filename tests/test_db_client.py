import os

import pytest

from supabase_mcp.db_client.db_client import QueryResult, SupabaseClient
from supabase_mcp.db_client.db_safety_config import DbSafetyLevel
from supabase_mcp.exceptions import QueryError


# Connection string tests
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


# Safety mode tests
def test_client_default_mode():
    """Test client initializes in read-only mode by default"""
    client = SupabaseClient(project_ref="127.0.0.1:54322", db_password="postgres")
    assert client.mode == DbSafetyLevel.RO


def test_client_explicit_mode():
    """Test client respects explicit mode setting"""
    client = SupabaseClient(project_ref="127.0.0.1:54322", db_password="postgres", _mode=DbSafetyLevel.RW)
    assert client.mode == DbSafetyLevel.RW


def test_mode_switching():
    """Test mode switching works correctly"""
    client = SupabaseClient(project_ref="127.0.0.1:54322", db_password="postgres")
    assert client.mode == DbSafetyLevel.RO

    client.switch_mode(DbSafetyLevel.RW)
    assert client.mode == DbSafetyLevel.RW

    client.switch_mode(DbSafetyLevel.RO)
    assert client.mode == DbSafetyLevel.RO


# Query execution tests
@pytest.mark.integration
def test_readonly_query_execution(integration_client):
    """Test read-only query executes successfully in both modes"""
    # Test in read-only mode
    result = integration_client.execute_query("SELECT 1 as num")
    assert isinstance(result, QueryResult)
    assert result.rows == [{"num": 1}]

    # Should also work in read-write mode
    integration_client.switch_mode(DbSafetyLevel.RW)
    result = integration_client.execute_query("SELECT 1 as num")
    assert result.rows == [{"num": 1}]


@pytest.mark.integration
def test_write_query_fails_in_readonly(integration_client):
    """Test write query fails in read-only mode"""
    with pytest.raises(QueryError) as exc_info:
        integration_client.execute_query("CREATE TEMPORARY TABLE IF NOT EXISTS test_table (id int)")
    assert "read-only transaction" in str(exc_info.value)


@pytest.mark.integration
def test_query_error_handling(integration_client):
    """Test various query error scenarios"""
    # Test schema error
    with pytest.raises(QueryError) as exc_info:
        integration_client.execute_query("SELECT * FROM nonexistent_table")
    assert "relation" in str(exc_info.value)

    # Test syntax error
    with pytest.raises(QueryError) as exc_info:
        integration_client.execute_query("INVALID SQL")
    assert "syntax error" in str(exc_info.value).lower()
