from pathlib import Path
from typing import Any

from supabase_mcp.db_client.db_client import QueryResult, SafetyMode, SupabaseClient
from supabase_mcp.db_client.migration_manager import MigrationManager
from supabase_mcp.exceptions import ConfirmationRequiredError, OperationNotAllowedError
from supabase_mcp.logger import logger
from supabase_mcp.sql_validator.models import SQLBatchValidationResult, SQLQuerySafetyLevel
from supabase_mcp.sql_validator.validator import SQLValidator


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
    SQL_DIR = Path(__file__).parent.parent / "sql"

    def __init__(self, db_client: SupabaseClient):
        """
        Initialize the QueryManager.

        Args:
            db_client: The database client to use for executing queries
        """
        self.db_client = db_client
        self.validator = SQLValidator()
        self.migration_manager = MigrationManager()
        logger.debug(f"QueryManager initialized with db_client mode: {db_client.mode}")

    def handle_query(self, query: str, params: tuple[Any, ...] | None = None) -> QueryResult:
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

        Returns:
            QueryResult: The result of the query execution

        Raises:
            OperationNotAllowedError: If the query is not allowed in the current safety mode
        """
        # Validate the query
        validation_result = self.validator.validate_query(query)

        # Check safety level
        self.validate_safety_level(validation_result)

        # Check if migration is needed
        if validation_result.needs_migration():
            logger.debug("Query requires migration, handling...")
            self.handle_migration(validation_result, query)
        else:
            logger.debug("No migration needed for this query")

        # Execute the query
        return self.db_client.execute_query(query, params)

    def validate_safety_level(self, validation_result: SQLBatchValidationResult) -> None:
        """
        Validate the safety level of a query.

        Args:
            validation_result: The validation result to check

        Raises:
            OperationNotAllowedError: If the query is not allowed in the current safety mode
            ConfirmationRequiredError: If the query requires user confirmation
        """
        # Get the current safety mode from the database client
        current_mode = self.db_client.mode
        logger.debug(f"Db_client safety level: {current_mode}")
        logger.debug(f"Query safety level: {validation_result.highest_safety_level}")

        # Read operations are always allowed regardless of mode
        if validation_result.highest_safety_level == SQLQuerySafetyLevel.SAFE:
            logger.debug("Query is SAFE, allowing execution in any mode")
            return

        # Write operations require READWRITE mode
        if validation_result.highest_safety_level == SQLQuerySafetyLevel.WRITE and current_mode == SafetyMode.READONLY:
            logger.debug(f"WRITE operation rejected in {current_mode.value} mode")
            raise OperationNotAllowedError(
                f"Write operation with safety level {validation_result.highest_safety_level} "
                f"is not allowed in {current_mode.value} mode"
            )

        # Destructive operations are rejected in non-READWRITE mode
        if (
            validation_result.highest_safety_level == SQLQuerySafetyLevel.DESTRUCTIVE
            and current_mode != SafetyMode.READWRITE
        ):
            logger.debug(f"DESTRUCTIVE operation rejected in {current_mode.value} mode")
            raise OperationNotAllowedError(
                f"Destructive operation with safety level {validation_result.highest_safety_level} "
                f"is not allowed in {current_mode.value} mode"
            )

        # Destructive operations require confirmation even in READWRITE mode
        if validation_result.highest_safety_level == SQLQuerySafetyLevel.DESTRUCTIVE:
            logger.debug("DESTRUCTIVE operation requires explicit confirmation")
            raise ConfirmationRequiredError(
                f"Destructive operation with safety level {validation_result.highest_safety_level} "
                f"requires explicit user confirmation"
            )

        logger.debug(f"Safety level {validation_result.highest_safety_level} allowed in {current_mode.value} mode")

    def handle_migration(self, validation_result: SQLBatchValidationResult, query: str) -> None:
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
            migration_query, migration_params = self.migration_manager.prepare_migration(migration_name, query)
            logger.debug(f"Migration query prepared with {len(migration_params[2])} statements")

            # Execute the migration query
            self.db_client.execute_query(migration_query, migration_params)
            logger.info(f"Created migration for query: {migration_name}")
        except Exception as e:
            logger.debug(f"Migration failure details: {str(e)}")
            raise e

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
