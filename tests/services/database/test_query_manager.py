from unittest.mock import MagicMock

import pytest

from supabase_mcp.exceptions import SafetyError
from supabase_mcp.services.database.query_manager import QueryManager
from supabase_mcp.services.database.sql.validator import (
    QueryValidationResults,
    SQLQueryCategory,
    SQLQueryCommand,
    ValidatedStatement,
)
from supabase_mcp.services.safety.models import OperationRiskLevel


class TestQueryManager:
    """Tests for the Query Manager."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_query_execution(self, mock_query_manager: QueryManager):
        """Test query execution through the Query Manager."""

        query_manager = mock_query_manager

        # Create a mock validation result for a SELECT query
        validated_statement = ValidatedStatement(
            category=SQLQueryCategory.DQL,
            command=SQLQueryCommand.SELECT,
            risk_level=OperationRiskLevel.LOW,
            query="SELECT * FROM users",
            needs_migration=False,
            object_type="TABLE",
            schema_name="public",
        )

        validation_result = QueryValidationResults(
            statements=[validated_statement],
            highest_risk_level=OperationRiskLevel.LOW,
            has_transaction_control=False,
            original_query="SELECT * FROM users",
        )

        # Make the validator return our mock validation result
        query_manager.validator.validate_query.return_value = validation_result

        # Make the db_client return a mock query result
        mock_query_result = MagicMock()
        query_manager.db_client.execute_query_async.return_value = mock_query_result

        # Execute a query
        query = "SELECT * FROM users"
        result = await query_manager.handle_query(query)

        # Verify the query was processed correctly
        query_manager.validator.validate_query.assert_called_once_with(query)
        query_manager.safety_manager.validate_operation.assert_called_once()
        query_manager.db_client.execute_query_async.assert_called_once()

        # Verify that the result is what we expected
        assert result == mock_query_result

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_safety_validation_blocks_dangerous_query(self, mock_query_manager: QueryManager):
        """Test that the safety validation blocks dangerous queries."""

        # Create a query manager with the mock dependencies
        query_manager = mock_query_manager

        # Create a mock validation result for a DROP TABLE query
        validated_statement = ValidatedStatement(
            category=SQLQueryCategory.DDL,
            command=SQLQueryCommand.DROP,
            risk_level=OperationRiskLevel.HIGH,
            query="DROP TABLE users",
            needs_migration=False,
            object_type="TABLE",
            schema_name="public",
        )

        validation_result = QueryValidationResults(
            statements=[validated_statement],
            highest_risk_level=OperationRiskLevel.HIGH,
            has_transaction_control=False,
            original_query="DROP TABLE users",
        )

        # Make the validator return our mock validation result
        query_manager.validator.validate_query.return_value = validation_result

        # Make the safety manager raise a SafetyError
        query_manager.safety_manager.validate_operation.side_effect = SafetyError("Operation not allowed")

        # The handle_query method should raise the SafetyError
        with pytest.raises(SafetyError) as excinfo:
            await query_manager.handle_query("DROP TABLE users")

        # Verify the error message
        assert "Operation not allowed" in str(excinfo.value)

        # Verify the query was validated but not executed
        query_manager.validator.validate_query.assert_called_once()
        query_manager.safety_manager.validate_operation.assert_called_once()
        query_manager.db_client.execute_query_async.assert_not_called()
