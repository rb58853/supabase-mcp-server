import uuid

import pytest
from mcp.server.fastmcp import FastMCP

from supabase_mcp.core.container import Container
from supabase_mcp.exceptions import ConfirmationRequiredError, OperationNotAllowedError
from supabase_mcp.services.database.postgres_client import QueryResult
from supabase_mcp.services.safety.models import ClientType, OperationRiskLevel, SafetyMode


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.integration
class TestDatabaseTools:
    """Integration tests for database tools."""

    async def test_get_schemas_tool(
        self,
        initialized_container_integration: Container,
        mock_mcp_server_integration: FastMCP,
    ):
        """Test the get_schemas tool."""
        query_manager = initialized_container_integration.query_manager
        query = query_manager.get_schemas_query()
        result = await query_manager.handle_query(query)

        # 4. Assert expected results
        assert result is not None
        assert isinstance(result, QueryResult), "Result should be a QueryResult"
        assert hasattr(result, "results")
        assert len(result.results) > 0
        assert hasattr(result.results[0], "rows")
        assert len(result.results[0].rows) > 0

        # Check that we have the expected data in the result
        first_row = result.results[0].rows[0]
        assert "schema_name" in first_row
        assert "total_size" in first_row
        assert "table_count" in first_row

    async def test_get_tables_tool(self, initialized_container_integration: Container):
        """Test the get_tables tool retrieves table information from a schema."""
        query_manager = initialized_container_integration.query_manager

        # Get the tables query for the public schema
        query = query_manager.get_tables_query("public")
        result = await query_manager.handle_query(query)

        # Verify result structure
        assert isinstance(result, QueryResult), "Result should be a QueryResult"
        assert hasattr(result, "results"), "Result should have results attribute"

        # Verify we have table data
        assert len(result.results) > 0, "Should return at least one statement result"

        # If tables exist, verify their structure
        if len(result.results[0].rows) > 0:
            # Verify table structure
            first_table = result.results[0].rows[0]
            expected_fields = ["table_name", "table_type", "row_count", "size_bytes"]
            for field in expected_fields:
                assert field in first_table, f"Table result missing '{field}' field"

    async def test_get_table_schema_tool(self, initialized_container_integration: Container):
        """Test the get_table_schema tool retrieves column information for a table."""
        query_manager = initialized_container_integration.query_manager
        query = query_manager.get_tables_query("public")
        tables_result = await query_manager.handle_query(query)

        # Skip test if no tables available
        if len(tables_result.results[0].rows) == 0:
            pytest.skip("No tables available in public schema to test table schema")

        # Get the first table name to test with
        first_table = tables_result.results[0].rows[0]["table_name"]

        # Execute the get_table_schema tool
        query = query_manager.get_table_schema_query("public", first_table)
        result = await query_manager.handle_query(query)

        # Verify result structure
        assert isinstance(result, QueryResult), "Result should be a QueryResult"
        assert hasattr(result, "results"), "Result should have results attribute"

        # If columns exist, verify their structure
        if len(result.results[0].rows) > 0:
            # Verify column structure
            first_column = result.results[0].rows[0]
            expected_fields = ["column_name", "data_type", "is_nullable"]
            for field in expected_fields:
                assert field in first_column, f"Column result missing '{field}' field"

    async def test_execute_postgresql_safe_query(self, initialized_container_integration: Container):
        """Test the execute_postgresql tool runs safe SQL queries."""
        query_manager = initialized_container_integration.query_manager
        # Test a simple SELECT query
        result: QueryResult = await query_manager.handle_query("SELECT 1 as number, 'test' as text;")

        # Verify result structure
        assert isinstance(result, QueryResult), "Result should be a QueryResult"
        assert hasattr(result, "results"), "Result should have results attribute"

    async def test_execute_postgresql_unsafe_query(self, initialized_container_integration: Container):
        """Test the execute_postgresql tool handles unsafe queries properly."""
        query_manager = initialized_container_integration.query_manager
        safety_manager = initialized_container_integration.safety_manager
        # First, ensure we're in safe mode
        # await live_dangerously(service="database", enable_unsafe_mode=False)
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)

        # Try to execute an unsafe query (DROP TABLE)
        unsafe_query = """
        DROP TABLE IF EXISTS test_table;
        """

        # This should raise a safety error
        with pytest.raises(OperationNotAllowedError):
            await query_manager.handle_query(unsafe_query)

        # Now switch to unsafe mode
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.UNSAFE)

        # The query should now require confirmation
        with pytest.raises(ConfirmationRequiredError):
            await query_manager.handle_query(unsafe_query)

        # Switch back to safe mode for other tests
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)

    async def test_retrieve_migrations(self, initialized_container_integration: Container):
        """Test the retrieve_migrations tool retrieves migration information."""
        # Execute the retrieve_migrations tool
        query_manager = initialized_container_integration.query_manager
        query = query_manager.get_migrations_query()
        result: QueryResult = await query_manager.handle_query(query)

        # Verify result structure
        assert isinstance(result, QueryResult), "Result should be a QueryResult"
        assert hasattr(result, "results"), "Result should have results attribute"

        # Note: We don't assert on row count because there might not be any migrations
        # But we can verify the query executed successfully by checking that we got a result
        assert len(result.results) > 0, "Should have at least one statement result"

    async def test_execute_postgresql_medium_risk_safe_mode(self, initialized_container_integration: Container):
        """Test that MEDIUM risk operations (INSERT, UPDATE, DELETE) are not allowed in SAFE mode."""
        # Ensure we're in SAFE mode
        query_manager = initialized_container_integration.query_manager
        safety_manager = initialized_container_integration.safety_manager
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)

        # Try to execute a MEDIUM risk query (INSERT)
        medium_risk_query = """
        INSERT INTO public.test_values (value) VALUES ('test_value');
        """

        # This should raise an OperationNotAllowedError in SAFE mode
        with pytest.raises(OperationNotAllowedError):
            await query_manager.handle_query(medium_risk_query)

    async def test_execute_postgresql_medium_risk_unsafe_mode(self, initialized_container_integration: Container):
        """Test that MEDIUM risk operations (INSERT, UPDATE, DELETE) are allowed in UNSAFE mode without confirmation."""
        query_manager = initialized_container_integration.query_manager
        postgres_client = initialized_container_integration.postgres_client
        safety_manager = initialized_container_integration.safety_manager
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.UNSAFE)

        # Generate a unique table name for this test run to avoid migration conflicts
        unique_suffix = str(uuid.uuid4()).replace("-", "")[:8]
        test_table_name = f"test_values_{unique_suffix}"
        migration_name_pattern = f"create_public_{test_table_name}"

        # Store migration names created during this test for cleanup
        test_migration_names = []

        try:
            # First create a test table if it doesn't exist with a unique name
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS public.{test_table_name} (
                id SERIAL PRIMARY KEY,
                value TEXT
            );
            """

            await query_manager.handle_query(create_table_query)
            # Store migration name pattern for cleanup
            test_migration_names.append(migration_name_pattern)

            # Now test a MEDIUM risk operation (INSERT)
            medium_risk_query = f"""
            INSERT INTO public.{test_table_name} (value) VALUES ('test_value');
            """

            # This should NOT raise an error in UNSAFE mode
            result = await query_manager.handle_query(medium_risk_query)

            # Verify the operation was successful
            assert isinstance(result, QueryResult), "Result should be a QueryResult"

        finally:
            # Clean up any migrations created during this test
            safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.UNSAFE)

            # Use a direct SQL query to clean up migrations by name pattern
            for name_pattern in test_migration_names:
                try:
                    # Use a SQL query to find and delete migrations with matching names
                    cleanup_query = f"""
                    DELETE FROM supabase_migrations.schema_migrations
                    WHERE name LIKE '%{name_pattern}%';
                    """

                    # Execute the cleanup query directly
                    from supabase_mcp.services.database.sql.models import QueryValidationResults

                    # Create a simple validation result for the cleanup query
                    validation_result = QueryValidationResults(
                        statements=[],
                        highest_risk_level=OperationRiskLevel.MEDIUM,  # Medium risk
                        original_query=cleanup_query,
                    )

                    await postgres_client.execute_query_async(validation_result, readonly=False)
                    print(f"Cleaned up test migrations matching: {name_pattern}")
                except Exception as e:
                    print(f"Failed to clean up test migrations: {e}")

            # Drop the test table
            try:
                drop_table_query = f"DROP TABLE IF EXISTS public.{test_table_name};"
                await query_manager.handle_query(drop_table_query)
            except Exception as e:
                print(f"Failed to drop test table: {e}")

            # Reset safety mode
            safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)

    async def test_execute_postgresql_high_risk_safe_mode(self, initialized_container_integration: Container):
        """Test that HIGH risk operations (DROP, TRUNCATE) are not allowed in SAFE mode."""
        # Ensure we're in SAFE mode
        query_manager = initialized_container_integration.query_manager
        safety_manager = initialized_container_integration.safety_manager
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)

        # Try to execute a HIGH risk query (DROP TABLE)
        high_risk_query = """
        DROP TABLE IF EXISTS public.test_values;
        """

        # This should raise an OperationNotAllowedError in SAFE mode
        with pytest.raises(OperationNotAllowedError):
            await query_manager.handle_query(high_risk_query)

    async def test_execute_postgresql_high_risk_unsafe_mode(self, initialized_container_integration: Container):
        """Test that HIGH risk operations (DROP, TRUNCATE) require confirmation even in UNSAFE mode."""
        query_manager = initialized_container_integration.query_manager
        safety_manager = initialized_container_integration.safety_manager
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.UNSAFE)

        try:
            # Try to execute a HIGH risk query (DROP TABLE)
            high_risk_query = """
            DROP TABLE IF EXISTS public.test_values;
            """

            # This should raise a ConfirmationRequiredError even in UNSAFE mode
            with pytest.raises(ConfirmationRequiredError):
                await query_manager.handle_query(high_risk_query)

        finally:
            # Switch back to SAFE mode for other tests
            safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)

    async def test_execute_postgresql_safety_mode_switching(self, initialized_container_integration: Container):
        """Test that switching between SAFE and UNSAFE modes affects which operations are allowed."""
        # Start in SAFE mode
        query_manager = initialized_container_integration.query_manager
        safety_manager = initialized_container_integration.safety_manager
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)

        # Define queries with different risk levels
        low_risk_query = "SELECT 1 as number;"
        medium_risk_query = "INSERT INTO public.test_values (value) VALUES ('test_value');"
        high_risk_query = "DROP TABLE IF EXISTS public.test_values;"

        # LOW risk should work in SAFE mode
        low_result = await query_manager.handle_query(low_risk_query)
        assert isinstance(low_result, QueryResult), "LOW risk query should work in SAFE mode"

        # MEDIUM risk should fail in SAFE mode
        with pytest.raises(OperationNotAllowedError):
            await query_manager.handle_query(medium_risk_query)

        # HIGH risk should fail in SAFE mode
        with pytest.raises(OperationNotAllowedError):
            await query_manager.handle_query(high_risk_query)

        # Switch to UNSAFE mode
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.UNSAFE)

        # LOW risk should still work in UNSAFE mode
        low_result = await query_manager.handle_query(low_risk_query)
        assert isinstance(low_result, QueryResult), "LOW risk query should work in UNSAFE mode"

        # MEDIUM risk should work in UNSAFE mode (but we won't actually execute it to avoid side effects)
        # We'll just verify it doesn't raise OperationNotAllowedError
        try:
            await query_manager.handle_query(medium_risk_query)
        except Exception as e:
            assert not isinstance(e, OperationNotAllowedError), (
                "MEDIUM risk should not raise OperationNotAllowedError in UNSAFE mode"
            )

        # HIGH risk should require confirmation in UNSAFE mode
        with pytest.raises(ConfirmationRequiredError):
            await query_manager.handle_query(high_risk_query)

        # Switch back to SAFE mode
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.integration
class TestAPITools:
    """Integration tests for API tools."""

    # @pytest.mark.asyncio
    async def test_send_management_api_request_get(self, initialized_container_integration: Container):
        """Test the send_management_api_request tool with a GET request."""
        # Test a simple GET request to list services health
        api_manager = initialized_container_integration.api_manager
        result = await api_manager.execute_request(
            method="GET",
            path="/v1/projects/{ref}/health",
            path_params={},
            request_params={"services": ["auth", "db", "rest"]},
            request_body={},
        )

        # Verify result structure
        assert isinstance(result, list), "Result should be a list of dictionaries"
        assert len(result) > 0, "Result should contain at least one service"

        # Verify each service has the expected structure
        for service in result:
            assert isinstance(service, dict), "Each service should be a dictionary"
            assert "name" in service, "Service should have a name"
            assert "healthy" in service, "Service should have a health status"
            assert "status" in service, "Service should have a status"

    # @pytest.mark.asyncio
    async def test_send_management_api_request_medium_risk_safe_mode(
        self, initialized_container_integration: Container
    ):
        """Test that MEDIUM risk operations (POST, PATCH) are not allowed in SAFE mode."""
        # Ensure we're in SAFE mode
        api_manager = initialized_container_integration.api_manager
        safety_manager = initialized_container_integration.safety_manager
        safety_manager.set_safety_mode(ClientType.API, SafetyMode.SAFE)

        # Try to execute a MEDIUM risk operation (POST to create a function)
        with pytest.raises(OperationNotAllowedError):
            await api_manager.execute_request(
                method="POST",
                path="/v1/projects/{ref}/functions",
                path_params={},
                request_params={},
                request_body={"name": "test-function", "slug": "test-function", "verify_jwt": True},
            )

    async def test_send_management_api_request_medium_risk_unsafe_mode(
        self, initialized_container_integration: Container
    ):
        """Test that MEDIUM risk operations (POST, PATCH) are allowed in UNSAFE mode."""
        import uuid

        import pytest

        # Get API manager from container
        api_manager = initialized_container_integration.api_manager
        safety_manager = initialized_container_integration.safety_manager

        # Switch to UNSAFE mode for cleanup and test
        safety_manager.set_safety_mode(ClientType.API, SafetyMode.UNSAFE)

        # First, list all functions to find test functions to clean up
        try:
            functions_result = await api_manager.execute_request(
                method="GET",
                path="/v1/projects/{ref}/functions",
                path_params={},
                request_params={},
                request_body={},
            )

            # Clean up any existing test functions
            if isinstance(functions_result, list):
                for function in functions_result:
                    if (
                        isinstance(function, dict)
                        and "slug" in function
                        and function.get("slug", "").startswith("test_")
                    ):
                        try:
                            # Delete the test function
                            await api_manager.execute_request(
                                method="DELETE",
                                path="/v1/projects/{ref}/functions/{function_slug}",
                                path_params={"function_slug": function.get("slug")},
                                request_params={},
                                request_body={},
                            )
                            print(f"Cleaned up test function: {function.get('slug')}")
                        except Exception as e:
                            print(f"Failed to delete test function {function.get('slug')}: {e}")
        except Exception as e:
            print(f"Error listing functions: {e}")

        # Store function slug at class level for deletion in next test
        TestAPITools.function_slug = f"test_{uuid.uuid4().hex[:8]}"
        function_slug = TestAPITools.function_slug

        try:
            # Try to create a test function
            try:
                create_result = await api_manager.execute_request(
                    method="POST",
                    path="/v1/projects/{ref}/functions",
                    path_params={},
                    request_params={},
                    request_body={
                        "name": function_slug,
                        "slug": function_slug,
                        "verify_jwt": True,
                        "body": "export default async function(req, res) { return res.json({ message: 'Hello World' }) }",
                    },
                )
            except Exception as e:
                if "Max number of functions reached for project" in str(e):
                    pytest.skip("Max number of functions reached for project - skipping test")
                else:
                    raise e

            # Verify the function was created
            assert isinstance(create_result, dict), "Result should be a dictionary"
            assert "slug" in create_result, "Result should contain slug"
            assert create_result["slug"] == function_slug, "Function slug should match"

            # Update the function (PATCH operation)
            update_result = await api_manager.execute_request(
                method="PATCH",
                path="/v1/projects/{ref}/functions/{function_slug}",
                path_params={"function_slug": function_slug},
                request_params={},
                request_body={"verify_jwt": False},
            )

            # Verify the function was updated
            assert isinstance(update_result, dict), "Result should be a dictionary"
            assert "verify_jwt" in update_result, "Result should contain verify_jwt"
            assert update_result["verify_jwt"] is False, "Function verify_jwt should be updated to False"

            # Delete the function
            try:
                await api_manager.execute_request(
                    method="DELETE",
                    path="/v1/projects/{ref}/functions/{function_slug}",
                    path_params={"function_slug": function_slug},
                    request_params={},
                    request_body={},
                )
            except Exception as e:
                print(f"Failed to delete test function: {e}")

        finally:
            # Switch back to SAFE mode for other tests
            safety_manager.set_safety_mode(ClientType.API, SafetyMode.SAFE)

    # @pytest.mark.asyncio
    async def test_send_management_api_request_high_risk(self, initialized_container_integration: Container):
        """Test that HIGH risk operations (DELETE) require confirmation even in UNSAFE mode."""
        # Switch to UNSAFE mode
        api_manager = initialized_container_integration.api_manager
        safety_manager = initialized_container_integration.safety_manager
        safety_manager.set_safety_mode(ClientType.API, SafetyMode.UNSAFE)

        try:
            # Try to execute a HIGH risk operation (DELETE a function)
            with pytest.raises(ConfirmationRequiredError):
                await api_manager.execute_request(
                    method="DELETE",
                    path="/v1/projects/{ref}/functions/{function_slug}",
                    path_params={"function_slug": "test-function"},
                    request_params={},
                    request_body={},
                )
        finally:
            # Switch back to SAFE mode
            safety_manager.set_safety_mode(ClientType.API, SafetyMode.SAFE)

    # @pytest.mark.asyncio
    async def test_send_management_api_request_extreme_risk(self, initialized_container_integration: Container):
        """Test that EXTREME risk operations (DELETE project) are never allowed."""
        # Switch to UNSAFE mode
        api_manager = initialized_container_integration.api_manager
        safety_manager = initialized_container_integration.safety_manager
        safety_manager.set_safety_mode(ClientType.API, SafetyMode.UNSAFE)

        try:
            # Try to execute an EXTREME risk operation (DELETE a project)
            with pytest.raises(OperationNotAllowedError):
                await api_manager.execute_request(
                    method="DELETE", path="/v1/projects/{ref}", path_params={}, request_params={}, request_body={}
                )
        finally:
            # Switch back to SAFE mode
            safety_manager.set_safety_mode(ClientType.API, SafetyMode.SAFE)

    # @pytest.mark.asyncio
    async def test_get_management_api_spec(self, initialized_container_integration: Container):
        """Test the get_management_api_spec tool returns valid API specifications."""
        # Test getting API specifications
        api_manager = initialized_container_integration.api_manager
        result = await api_manager.handle_spec_request()

        # Verify result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "domains" in result, "Result should contain domains"

        # Verify domains are present
        assert len(result["domains"]) > 0, "Should have at least one domain"

        # Test getting all paths
        paths_result = await api_manager.handle_spec_request(all_paths=True)

        # Verify paths are present
        assert "paths" in paths_result, "Result should contain paths"
        assert len(paths_result["paths"]) > 0, "Should have at least one path"

        # Test getting a specific domain
        domain_result = await api_manager.handle_spec_request(domain="Edge Functions")

        # Verify domain data is present
        assert "domain" in domain_result, "Result should contain domain"
        assert domain_result["domain"] == "Edge Functions", "Domain should match"
        assert "paths" in domain_result, "Result should contain paths for the domain"

    # @pytest.mark.asyncio
    async def test_get_management_api_safety_rules(self, initialized_container_integration: Container):
        """Test the get_management_api_safety_rules tool returns safety rules."""
        # Test getting API safety rules
        api_manager = initialized_container_integration.api_manager
        result = api_manager.get_safety_rules()

        # Verify result is a string
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"

        # Verify it contains safety information
        assert "Safety Rules" in result, "Result should contain safety rules"
        assert "Current mode" in result, "Result should mention current mode"


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.integration
class TestSafetyTools:
    """Integration tests for safety tools."""

    async def test_live_dangerously_database(self, initialized_container_integration: Container):
        """Test the live_dangerously tool toggles database safety mode."""
        # Get the safety manager
        safety_manager = initialized_container_integration.safety_manager

        # Start with safe mode
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)
        assert safety_manager.get_safety_mode(ClientType.DATABASE) == SafetyMode.SAFE, "Database should be in safe mode"

        # Switch to unsafe mode
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.UNSAFE)
        assert safety_manager.get_safety_mode(ClientType.DATABASE) == SafetyMode.UNSAFE, (
            "Database should be in unsafe mode"
        )

        # Switch back to safe mode
        safety_manager.set_safety_mode(ClientType.DATABASE, SafetyMode.SAFE)
        assert safety_manager.get_safety_mode(ClientType.DATABASE) == SafetyMode.SAFE, "Database should be in safe mode"

    # @pytest.mark.asyncio
    async def test_live_dangerously_api(self, initialized_container_integration: Container):
        """Test the live_dangerously tool toggles API safety mode."""
        # Get the safety manager
        safety_manager = initialized_container_integration.safety_manager

        # Start with safe mode
        safety_manager.set_safety_mode(ClientType.API, SafetyMode.SAFE)
        assert safety_manager.get_safety_mode(ClientType.API) == SafetyMode.SAFE, "API should be in safe mode"

        # Switch to unsafe mode
        safety_manager.set_safety_mode(ClientType.API, SafetyMode.UNSAFE)
        assert safety_manager.get_safety_mode(ClientType.API) == SafetyMode.UNSAFE, "API should be in unsafe mode"

        # Switch back to safe mode
        safety_manager.set_safety_mode(ClientType.API, SafetyMode.SAFE)
        assert safety_manager.get_safety_mode(ClientType.API) == SafetyMode.SAFE, "API should be in safe mode"

    # @pytest.mark.asyncio
    async def test_confirm_destructive_operation(self, initialized_container_integration: Container):
        """Test the confirm_destructive_operation tool handles confirmations."""
        api_manager = initialized_container_integration.api_manager
        safety_manager = initialized_container_integration.safety_manager

        # Try to delete a function (HIGH risk) in SAFE mode - should be blocked
        with pytest.raises(OperationNotAllowedError):
            await api_manager.execute_request(
                method="DELETE",
                path="/v1/projects/{ref}/functions/{function_slug}",
                path_params={"function_slug": "test-function"},
                request_params={},
                request_body={},
            )

        # Switch to UNSAFE mode
        safety_manager.set_safety_mode(ClientType.API, SafetyMode.UNSAFE)

        # Try to delete a function (HIGH risk) in UNSAFE mode - should require confirmation
        with pytest.raises(ConfirmationRequiredError):
            await api_manager.execute_request(
                method="DELETE",
                path="/v1/projects/{ref}/functions/{function_slug}",
                path_params={"function_slug": "test-function"},
                request_params={},
                request_body={},
            )

        # Switch back to SAFE mode for other tests
        safety_manager.set_safety_mode(ClientType.API, SafetyMode.SAFE)


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.integration
class TestAuthTools:
    """Integration tests for Auth Admin tools."""

    async def test_get_auth_admin_methods_spec(self, initialized_container_integration: Container):
        """Test the get_auth_admin_methods_spec tool returns SDK method specifications."""
        # Test getting auth admin methods spec
        sdk_client = initialized_container_integration.sdk_client
        result = sdk_client.return_python_sdk_spec()

        # Verify result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert len(result) > 0, "Should have at least one method"

        # Check for common methods
        common_methods = ["get_user_by_id", "list_users", "create_user", "delete_user", "update_user_by_id"]
        for method in common_methods:
            assert method in result, f"Result should contain {method} method"
            assert "description" in result[method], f"{method} should have a description"
            assert "parameters" in result[method], f"{method} should have parameters"
            assert "returns" in result[method], f"{method} should have returns info"

    async def test_call_auth_admin_list_users(self, initialized_container_integration: Container):
        """Test the call_auth_admin_method tool with list_users method."""
        # Test listing users with pagination
        sdk_client = initialized_container_integration.sdk_client
        result = await sdk_client.call_auth_admin_method(method="list_users", params={"page": 1, "per_page": 5})

        # Verify result structure
        assert isinstance(result, list), "Result should be a list of User objects"

        # If there are users, verify their structure
        if len(result) > 0:
            user = result[0]
            assert hasattr(user, "id"), "User should have an ID"
            assert hasattr(user, "email"), "User should have an email"

    # @pytest.mark.asyncio
    async def test_call_auth_admin_create_user(self, initialized_container_integration: Container):
        """Test creating a user with the create_user method."""
        # Create a unique email for this test
        test_email = f"test-user-{uuid.uuid4()}@example.com"
        user_id = None

        try:
            # Create a user
            sdk_client = initialized_container_integration.sdk_client
            create_result = await sdk_client.call_auth_admin_method(
                method="create_user",
                params={
                    "email": test_email,
                    "password": "secure-password",
                    "email_confirm": True,
                    "user_metadata": {"name": "Test User", "is_test_user": True},
                },
            )

            # Verify user was created
            assert hasattr(create_result, "user"), "Create result should have a user attribute"
            assert create_result.user.email == test_email, "User email should match"

            # Store the user ID for cleanup
            user_id = create_result.user.id

        finally:
            # Clean up - delete the test user
            if user_id:
                try:
                    await sdk_client.call_auth_admin_method(method="delete_user", params={"id": user_id})
                except Exception as e:
                    print(f"Failed to delete test user: {e}")

    # @pytest.mark.asyncio
    async def test_call_auth_admin_get_user(self, initialized_container_integration: Container):
        """Test retrieving a user with the get_user_by_id method."""
        # Create a unique email for this test
        test_email = f"get-user-{uuid.uuid4()}@example.com"
        user_id = None

        try:
            # First create a user to get
            sdk_client = initialized_container_integration.sdk_client
            create_result = await sdk_client.call_auth_admin_method(
                method="create_user",
                params={
                    "email": test_email,
                    "password": "secure-password",
                    "email_confirm": True,
                },
            )
            user_id = create_result.user.id

            # Get the user by ID
            get_result = await sdk_client.call_auth_admin_method(method="get_user_by_id", params={"uid": user_id})

            # Verify get result
            assert hasattr(get_result, "user"), "Get result should have a user attribute"
            assert get_result.user.id == user_id, "User ID should match"
            assert get_result.user.email == test_email, "User email should match"

        finally:
            # Clean up
            if user_id:
                try:
                    await sdk_client.call_auth_admin_method(method="delete_user", params={"id": user_id})
                except Exception as e:
                    print(f"Failed to delete test user: {e}")

    # @pytest.mark.asyncio
    async def test_call_auth_admin_update_user(self, initialized_container_integration: Container):
        """Test updating a user with the update_user_by_id method."""
        # Create a unique email for this test
        test_email = f"update-user-{uuid.uuid4()}@example.com"
        user_id = None

        try:
            # First create a user to update
            sdk_client = initialized_container_integration.sdk_client
            create_result = await sdk_client.call_auth_admin_method(
                method="create_user",
                params={
                    "email": test_email,
                    "password": "secure-password",
                    "email_confirm": True,
                    "user_metadata": {"name": "Original Name"},
                },
            )
            user_id = create_result.user.id

            # Update the user
            sdk_client = initialized_container_integration.sdk_client
            update_result = await sdk_client.call_auth_admin_method(
                method="update_user_by_id",
                params={
                    "uid": user_id,
                    "attributes": {
                        "user_metadata": {"name": "Updated Name", "is_test_user": True},
                    },
                },
            )

            # Verify update result
            assert hasattr(update_result, "user"), "Update result should have a user attribute"
            assert update_result.user.id == user_id, "User ID should match"

            # The update might not be immediately reflected in the response
            # Just verify we got a valid response with the correct user ID

        finally:
            # Clean up
            if user_id:
                try:
                    await sdk_client.call_auth_admin_method(method="delete_user", params={"id": user_id})
                except Exception as e:
                    print(f"Failed to delete test user: {e}")

    # @pytest.mark.asyncio
    async def test_call_auth_admin_invite_user(self, initialized_container_integration: Container):
        """Test the invite_user_by_email method."""
        # Create a unique email for this test
        test_email = f"invite-{uuid.uuid4()}@example.com"
        user_id = None

        try:
            # Invite a user
            sdk_client = initialized_container_integration.sdk_client
            invite_result = await sdk_client.call_auth_admin_method(
                method="invite_user_by_email",
                params={"email": test_email, "options": {"data": {"name": "Invited Test User", "is_test_user": True}}},
            )

            # Verify invite result
            assert hasattr(invite_result, "user"), "Invite result should have a user attribute"
            assert invite_result.user.email == test_email, "User email should match"
            assert invite_result.user.invited_at is not None, "User should have an invited_at timestamp"

            # Store the user ID for cleanup
            user_id = invite_result.user.id

        finally:
            # Clean up
            if user_id:
                try:
                    await sdk_client.call_auth_admin_method(method="delete_user", params={"id": user_id})
                except Exception as e:
                    print(f"Failed to delete invited test user: {e}")

    # @pytest.mark.asyncio
    async def test_call_auth_admin_generate_signup_link(self, initialized_container_integration: Container):
        """Test generating a signup link with the generate_link method."""
        # Create a unique email for this test
        test_email = f"signup-{uuid.uuid4()}@example.com"

        # Generate a signup link
        sdk_client = initialized_container_integration.sdk_client
        signup_result = await sdk_client.call_auth_admin_method(
            method="generate_link",
            params={
                "type": "signup",
                "email": test_email,
                "password": "secure-password",
                "options": {
                    "data": {"name": "Link Test User", "is_test_user": True},
                    "redirect_to": "https://example.com/welcome",
                },
            },
        )

        # Verify signup link result based on actual structure
        assert hasattr(signup_result, "properties"), "Result should have properties"
        assert hasattr(signup_result.properties, "action_link"), "Properties should have an action_link"
        assert hasattr(signup_result.properties, "email_otp"), "Properties should have an email_otp"
        assert hasattr(signup_result.properties, "verification_type"), "Properties should have a verification type"
        assert "signup" in signup_result.properties.verification_type, "Verification type should be signup"

    # @pytest.mark.asyncio
    async def test_call_auth_admin_invalid_method(self, initialized_container_integration: Container):
        """Test that an invalid method raises an exception."""
        # Test with an invalid method name
        sdk_client = initialized_container_integration.sdk_client
        with pytest.raises(Exception):
            await sdk_client.call_auth_admin_method(method="invalid_method", params={})

        # Test with valid method but invalid parameters
        with pytest.raises(Exception):
            await sdk_client.call_auth_admin_method(method="get_user_by_id", params={"invalid_param": "value"})

            await sdk_client.call_auth_admin_method(method="invalid_method", params={})

        # Test with valid method but invalid parameters
        with pytest.raises(Exception):
            await sdk_client.call_auth_admin_method(method="get_user_by_id", params={"invalid_param": "value"})
