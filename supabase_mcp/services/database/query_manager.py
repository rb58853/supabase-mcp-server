from pathlib import Path
from typing import Any

from supabase_mcp.exceptions import OperationNotAllowedError
from supabase_mcp.logger import logger
from supabase_mcp.services.database.migration_manager import MigrationManager
from supabase_mcp.services.database.postgres_client import PostgresClient, QueryResult
from supabase_mcp.services.database.sql.models import QueryValidationResults
from supabase_mcp.services.database.sql.validator import SQLValidator
from supabase_mcp.services.safety.models import ClientType, SafetyMode
from supabase_mcp.services.safety.safety_manager import SafetyManager


class QueryManager:
    """
    Manages SQL query execution with validation and migration handling.

    This class is responsible for:
    1. Validating SQL queries for safety
    2. Executing queries through the database client
    3. Managing migrations for queries that require them
    4. Loading SQL queries from files

    It acts as a central point for all SQL operations, ensuring consistent
    validation and execution patterns.
    """

    # Path to SQL files directory
    SQL_DIR = Path(__file__).parent / "sql" / "queries"

    def __init__(
        self,
        postgres_client: PostgresClient,
        safety_manager: SafetyManager,
        sql_validator: SQLValidator | None = None,
        migration_manager: MigrationManager | None = None,
    ):
        """
        Initialize the QueryManager.

        Args:
            db_client: The database client to use for executing queries
        """
        self.db_client = postgres_client
        self.safety_manager = safety_manager
        self.validator = sql_validator or SQLValidator()
        self.migration_manager = migration_manager or MigrationManager()

    def check_readonly(self) -> bool:
        """Returns true if current safety mode is SAFE."""
        result = self.safety_manager.get_safety_mode(ClientType.DATABASE) == SafetyMode.SAFE
        logger.debug(f"Check readonly result: {result}")
        return result

    async def handle_query(
        self, query: str, params: tuple[Any, ...] | None = None, has_confirmation: bool = False
    ) -> QueryResult:
        """
        Handle a SQL query with validation and potential migration.

        This method:
        1. Validates the query for safety
        2. Checks if the query requires migration
        3. Handles migration if needed
        4. Executes the query

        Args:
            query: SQL query to execute
            params: Query parameters
            has_confirmation: Whether the operation has been confirmed by the user

        Returns:
            QueryResult: The result of the query execution

        Raises:
            OperationNotAllowedError: If the query is not allowed in the current safety mode
            ConfirmationRequiredError: If the query requires confirmation and has_confirmation is False
        """
        # Validate the query
        validated_query = self.validator.validate_query(query)

        # Use the safety manager to validate the operation
        self.safety_manager.validate_operation(ClientType.DATABASE, validated_query, has_confirmation)
        logger.debug(f"Operation with risk level {validated_query.highest_risk_level} validated successfully")

        # Check if migration is needed
        if validated_query.needs_migration():
            logger.debug("Query requires migration, handling...")
            await self.handle_migration(validated_query, query)
        else:
            logger.debug("No migration needed for this query")

        # Check readonly
        readonly = self.check_readonly()

        # Execute the query
        result = await self.db_client.execute_query_async(validated_query, readonly)
        logger.debug(f"Query result: {result}")
        return result

    async def handle_migration(self, validation_result: QueryValidationResults, query: str) -> None:
        """
        Handle migration for a query that requires it.

        Args:
            validation_result: The validation result
            query: The original query
        """
        # Generate a descriptive name using the MigrationManager
        migration_name = self.migration_manager.generate_descriptive_name(validation_result)

        try:
            # Prepare the migration with the original query
            migration_query = self.migration_manager.prepare_migration(migration_name, query)
            logger.debug("Migration query prepared")

            # Validate migration query
            validated_query = self.validator.validate_query(migration_query)

            # Check readonly
            readonly = self.check_readonly()

            # Execute the migration query
            await self.db_client.execute_query_async(validated_query, readonly)
            logger.info(f"Created migration for query: {migration_name}")
        except Exception as e:
            logger.debug(f"Migration failure details: {str(e)}")
            raise e

    async def handle_confirmation(self, confirmation_id: str) -> QueryResult:
        """
        Handle a confirmed operation using its confirmation ID.

        This method retrieves the stored operation and passes it to handle_query.

        Args:
            confirmation_id: The unique ID of the confirmation to process

        Returns:
            QueryResult: The result of the query execution
        """
        # Get the stored operation
        operation = self.safety_manager.get_stored_operation(confirmation_id)
        if not operation:
            raise OperationNotAllowedError(f"Invalid or expired confirmation ID: {confirmation_id}")

        # Get the query from the operation
        query = operation.original_query
        logger.debug(f"Processing confirmed operation with ID {confirmation_id}")

        # Call handle_query with the query and has_confirmation=True
        return await self.handle_query(query, has_confirmation=True)

    @classmethod
    def load_sql(cls, filename: str) -> str:
        """
        Load SQL from a file in the sql directory.

        Args:
            filename: Name of the SQL file (with or without .sql extension)

        Returns:
            str: The SQL query from the file

        Raises:
            FileNotFoundError: If the SQL file doesn't exist
        """
        # Ensure the filename has .sql extension
        if not filename.endswith(".sql"):
            filename = f"{filename}.sql"

        file_path = cls.SQL_DIR / filename

        if not file_path.exists():
            logger.error(f"SQL file not found: {file_path}")
            raise FileNotFoundError(f"SQL file not found: {file_path}")

        with open(file_path) as f:
            sql = f.read().strip()
            logger.debug(f"Loaded SQL file: {filename} ({len(sql)} chars)")
            return sql

    def get_schemas_query(self) -> str:
        """
        Get SQL query to list all schemas with their sizes and table counts.

        Returns:
            str: SQL query for listing schemas
        """
        logger.debug("Getting schemas query")
        return self.load_sql("get_schemas")

    def get_tables_query(self, schema_name: str) -> str:
        """
        Get SQL query to list all tables in a schema.

        Args:
            schema_name: Name of the schema

        Returns:
            str: SQL query for listing tables
        """
        logger.debug(f"Getting tables query for schema: {schema_name}")
        sql = self.load_sql("get_tables")
        return sql.format(schema_name=schema_name)

    def get_table_schema_query(self, schema_name: str, table: str) -> str:
        """
        Get SQL query to get detailed table schema.

        Args:
            schema_name: Name of the schema
            table: Name of the table

        Returns:
            str: SQL query for getting table schema
        """
        logger.debug(f"Getting table schema query for {schema_name}.{table}")
        sql = self.load_sql("get_table_schema")
        return sql.format(schema_name=schema_name, table=table)

    def get_migrations_query(self) -> str:
        """
        Get a query to retrieve all migrations from Supabase.

        Returns:
            str: SQL query to get all migrations
        """
        logger.debug("Getting migrations query")
        return self.load_sql("get_migrations")
