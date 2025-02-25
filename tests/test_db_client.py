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


def test_connection_string_integration(custom_connection_settings):
    """Test connection string generation with integration settings from .env.test"""
    client = SupabaseClient(settings_instance=custom_connection_settings)
    expected_url = (
        f"postgresql://postgres.{custom_connection_settings.supabase_project_ref}:"
        f"{custom_connection_settings.supabase_db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )
    assert client.db_url == expected_url


def test_connection_string_explicit_params():
    """Test connection string generation with explicit parameters"""
    client = SupabaseClient(project_ref="my-project", db_password="my-password")
    expected_url = "postgresql://postgres.my-project:my-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    assert client.db_url == expected_url


@pytest.mark.skipif(not os.getenv("CI"), reason="Test only runs in CI environment")
def test_connection_string_ci():
    """Test connection string generation in CI environment"""
    # Just create the client using singleton method
    client = SupabaseClient.create()

    # Verify we're using a remote connection, not localhost
    assert "127.0.0.1" not in client.db_url, "CI should use remote DB, not localhost"

    # Verify we have the expected format without exposing credentials
    assert "postgresql://postgres." in client.db_url, "Connection string should use Supabase format"
    assert "pooler.supabase.com" in client.db_url, "Connection string should use Supabase pooler"

    # Verify the client can actually connect (this is a better test than checking the URL)
    try:
        result = client.execute_query("SELECT 1 as connection_test")
        assert result.rows[0]["connection_test"] == 1, "Connection test query failed"
    except Exception as e:
        pytest.fail(f"Connection failed: {e}")


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


@pytest.mark.integration
def test_transaction_commit_in_write_mode(integration_client):
    """Test that transactions are properly committed in write mode"""
    # Switch to write mode
    integration_client.switch_mode(DbSafetyLevel.RW)

    try:
        # Use explicit transaction control with a regular table (not temporary)
        integration_client.execute_query("""
            BEGIN;
            CREATE TABLE IF NOT EXISTS public.test_commit (id SERIAL PRIMARY KEY, value TEXT);
            INSERT INTO public.test_commit (value) VALUES ('test_value');
            COMMIT;
        """)

        # Verify data was committed by querying it back
        result = integration_client.execute_query("SELECT value FROM public.test_commit")

        # Check that we got the expected result
        assert len(result.rows) == 1
        assert result.rows[0]["value"] == "test_value"

    finally:
        # Clean up - drop the table
        try:
            integration_client.execute_query("DROP TABLE IF EXISTS public.test_commit")
        except Exception as e:
            print(f"Cleanup error: {e}")

        # Switch back to read-only mode
        integration_client.switch_mode(DbSafetyLevel.RO)


@pytest.mark.integration
def test_explicit_transaction_control(integration_client):
    """Test explicit transaction control with BEGIN/COMMIT"""
    # Switch to write mode
    integration_client.switch_mode(DbSafetyLevel.RW)

    try:
        # Create a test table
        integration_client.execute_query("""
            BEGIN;
            CREATE TABLE IF NOT EXISTS public.transaction_test (id SERIAL PRIMARY KEY, data TEXT);
            COMMIT;
        """)

        # Test transaction that should be committed
        integration_client.execute_query("""
            BEGIN;
            INSERT INTO public.transaction_test (data) VALUES ('committed_data');
            COMMIT;
        """)

        # Verify data was committed
        result = integration_client.execute_query("SELECT data FROM public.transaction_test")
        assert len(result.rows) == 1
        assert result.rows[0]["data"] == "committed_data"

    finally:
        # Clean up
        try:
            integration_client.execute_query("DROP TABLE IF EXISTS public.transaction_test")
        except Exception as e:
            print(f"Cleanup error: {e}")

        # Switch back to read-only mode
        integration_client.switch_mode(DbSafetyLevel.RO)


@pytest.mark.integration
def test_savepoint_and_rollback(integration_client):
    """Test savepoint and rollback functionality within transactions"""
    # Switch to write mode
    integration_client.switch_mode(DbSafetyLevel.RW)

    try:
        # Create a test table
        integration_client.execute_query("""
            BEGIN;
            CREATE TABLE IF NOT EXISTS public.savepoint_test (id SERIAL PRIMARY KEY, data TEXT);
            COMMIT;
        """)

        # Test transaction with savepoint and rollback
        integration_client.execute_query("""
            BEGIN;
            INSERT INTO public.savepoint_test (data) VALUES ('data1');
            SAVEPOINT sp1;
            INSERT INTO public.savepoint_test (data) VALUES ('data2');
            ROLLBACK TO sp1;
            INSERT INTO public.savepoint_test (data) VALUES ('data3');
            COMMIT;
        """)

        # Verify only data1 and data3 were committed (data2 was rolled back)
        result = integration_client.execute_query("""
            SELECT data FROM public.savepoint_test ORDER BY id
        """)

        assert len(result.rows) == 2
        assert result.rows[0]["data"] == "data1"
        assert result.rows[1]["data"] == "data3"

    finally:
        # Clean up
        try:
            integration_client.execute_query("DROP TABLE IF EXISTS public.savepoint_test")
        except Exception as e:
            print(f"Cleanup error: {e}")

        # Switch back to read-only mode
        integration_client.switch_mode(DbSafetyLevel.RO)
        assert integration_client.mode == DbSafetyLevel.RO
