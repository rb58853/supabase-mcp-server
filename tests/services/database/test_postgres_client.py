import asyncpg
import pytest
from asyncpg.exceptions import PostgresError

from supabase_mcp.exceptions import ConnectionError
from supabase_mcp.services.database.postgres_client import PostgresClient, QueryResult, StatementResult
from supabase_mcp.services.database.sql.validator import (
    QueryValidationResults,
    SQLQueryCategory,
    SQLQueryCommand,
    ValidatedStatement,
)
from supabase_mcp.services.safety.models import OperationRiskLevel


@pytest.mark.asyncio(loop_scope="class")
@pytest.mark.integration
class TestPostgresClient:
    """Integration tests for the Postgres client."""

    async def test_execute_simple_select(self, postgres_client_integration: PostgresClient):
        """Test executing a simple SELECT query."""
        # Create a simple validation result with a SELECT query
        query = "SELECT 1 as number;"
        statement = ValidatedStatement(
            query=query,
            command=SQLQueryCommand.SELECT,
            category=SQLQueryCategory.DQL,
            risk_level=OperationRiskLevel.LOW,
            needs_migration=False,
            object_type=None,
            schema_name=None,
        )
        validation_result = QueryValidationResults(
            statements=[statement],
            original_query=query,
            highest_risk_level=OperationRiskLevel.LOW,
        )

        # Execute the query
        result = await postgres_client_integration.execute_query_async(validation_result)

        # Verify the result
        assert isinstance(result, QueryResult)
        assert len(result.results) == 1
        assert isinstance(result.results[0], StatementResult)
        assert len(result.results[0].rows) == 1
        assert result.results[0].rows[0]["number"] == 1

    async def test_execute_multiple_statements(self, postgres_client_integration: PostgresClient):
        """Test executing multiple SQL statements in a single query."""
        # Create validation result with multiple statements
        query = "SELECT 1 as first; SELECT 2 as second;"
        statements = [
            ValidatedStatement(
                query="SELECT 1 as first;",
                command=SQLQueryCommand.SELECT,
                category=SQLQueryCategory.DQL,
                risk_level=OperationRiskLevel.LOW,
                needs_migration=False,
                object_type=None,
                schema_name=None,
            ),
            ValidatedStatement(
                query="SELECT 2 as second;",
                command=SQLQueryCommand.SELECT,
                category=SQLQueryCategory.DQL,
                risk_level=OperationRiskLevel.LOW,
                needs_migration=False,
                object_type=None,
                schema_name=None,
            ),
        ]
        validation_result = QueryValidationResults(
            statements=statements,
            original_query=query,
            highest_risk_level=OperationRiskLevel.LOW,
        )

        # Execute the query
        result = await postgres_client_integration.execute_query_async(validation_result)

        # Verify the result
        assert isinstance(result, QueryResult)
        assert len(result.results) == 2
        assert result.results[0].rows[0]["first"] == 1
        assert result.results[1].rows[0]["second"] == 2

    async def test_execute_query_with_parameters(self, postgres_client_integration: PostgresClient):
        """Test executing a query with parameters."""
        # This test would normally use parameterized queries, but since we're using the validation results
        # we'll just use a query that includes the parameter values directly
        query = "SELECT 'test' as name, 42 as value;"
        statement = ValidatedStatement(
            query=query,
            command=SQLQueryCommand.SELECT,
            category=SQLQueryCategory.DQL,
            risk_level=OperationRiskLevel.LOW,
            needs_migration=False,
            object_type=None,
            schema_name=None,
        )
        validation_result = QueryValidationResults(
            statements=[statement],
            original_query=query,
            highest_risk_level=OperationRiskLevel.LOW,
        )

        # Execute the query
        result = await postgres_client_integration.execute_query_async(validation_result)

        # Verify the result
        assert isinstance(result, QueryResult)
        assert len(result.results) == 1
        assert result.results[0].rows[0]["name"] == "test"
        assert result.results[0].rows[0]["value"] == 42

    async def test_execute_query_with_error(self, postgres_client_integration: PostgresClient):
        """Test executing a query that results in an error."""
        # Create a validation result with an invalid query
        query = "SELECT * FROM nonexistent_table;"
        statement = ValidatedStatement(
            query=query,
            command=SQLQueryCommand.SELECT,
            category=SQLQueryCategory.DQL,
            risk_level=OperationRiskLevel.LOW,
            needs_migration=False,
            object_type="nonexistent_table",
            schema_name="public",
        )
        validation_result = QueryValidationResults(
            statements=[statement],
            original_query=query,
            highest_risk_level=OperationRiskLevel.LOW,
        )

        # Execute the query and expect an error
        with pytest.raises(PostgresError):
            await postgres_client_integration.execute_query_async(validation_result)

    async def test_execute_metadata_query(self, postgres_client_integration: PostgresClient):
        """Test executing a metadata query."""
        # Create a simple validation result with a SELECT query
        query = "SELECT schema_name FROM information_schema.schemata LIMIT 5;"
        statement = ValidatedStatement(
            query=query,
            command=SQLQueryCommand.SELECT,
            category=SQLQueryCategory.DQL,
            risk_level=OperationRiskLevel.LOW,
            needs_migration=False,
            object_type="schemata",
            schema_name="information_schema",
        )
        validation_result = QueryValidationResults(
            statements=[statement],
            original_query=query,
            highest_risk_level=OperationRiskLevel.LOW,
        )

        # Execute the query
        result = await postgres_client_integration.execute_query_async(validation_result)

        # Verify the result
        assert isinstance(result, QueryResult)
        assert len(result.results) == 1
        assert len(result.results[0].rows) == 5
        assert "schema_name" in result.results[0].rows[0]

    async def test_connection_retry_mechanism(self, monkeypatch, postgres_client_integration: PostgresClient):
        """Test that the tenacity retry mechanism works correctly for database connections."""

        # Create a simple mock that always raises a connection error
        async def mock_create_pool(*args, **kwargs):
            raise asyncpg.exceptions.ConnectionDoesNotExistError("Simulated connection failure")

        # Replace asyncpg's create_pool with our mock
        monkeypatch.setattr(asyncpg, "create_pool", mock_create_pool)

        # Close the existing pool to force a new connection
        await postgres_client_integration.close()

        # This should trigger the retry mechanism and eventually fail
        with pytest.raises(ConnectionError) as exc_info:
            await postgres_client_integration.ensure_pool()

        # Verify the error message indicates a connection failure after retries
        assert "Could not connect to database" in str(exc_info.value)
