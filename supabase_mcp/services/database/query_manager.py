from pathlib import Path

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

    async def handle_query(self, query: str, has_confirmation: bool = False, migration_name: str = "") -> QueryResult:
        """
        Handle a SQL query with validation and potential migration. Uses migration name, if provided.

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
        # 1. Run through the validator
        validated_query = self.validator.validate_query(query)

        # 2. Ensure execution is allowed
        self.safety_manager.validate_operation(ClientType.DATABASE, validated_query, has_confirmation)
        logger.debug(f"Operation with risk level {validated_query.highest_risk_level} validated successfully")

        # 3. Handle migration if needed
        await self.handle_migration(validated_query, query, migration_name)

        # 4. Execute the query
        return await self.handle_query_execution(validated_query)

    async def handle_query_execution(self, validated_query: QueryValidationResults) -> QueryResult:
        """
        Handle query execution with validation and potential migration.

        This method:
        1. Checks the readonly mode
        2. Executes the query
        3. Returns the result

        Args:
            validated_query: The validation result
            query: The original query

        Returns:
            QueryResult: The result of the query execution
        """
        readonly = self.check_readonly()
        result = await self.db_client.execute_query_async(validated_query, readonly)
        logger.debug(f"Query result: {result}")
        return result

    async def handle_migration(
        self, validation_result: QueryValidationResults, original_query: str, migration_name: str = ""
    ) -> None:
        """
        Handle migration for a query that requires it.

        Args:
            validation_result: The validation result
            query: The original query
            migration_name: Migration name to use, if provided
        """
        # 1. Check if migration is needed
        if not validation_result.needs_migration():
            logger.info("No migration needed for this query")
            return

        # 2. Create migration
        try:
            # Prepare the migration with the original query
            migration_query, migration_name = self.migration_manager.prepare_migration_query(
                validation_result, original_query, migration_name
            )

            # Validate migration query, since it's a raw query
            validated_query = self.validator.validate_query(migration_query)

            await self.handle_query_execution(validated_query)
            logger.info(f"Successfully created migration: {migration_name}")
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

    def get_migrations_query(
        self, limit: int = 50, offset: int = 0, name_pattern: str = "", include_full_queries: bool = False
    ) -> str:
        """
        Get a query to retrieve migrations from Supabase with filtering and pagination.

        Args:
            limit: Maximum number of migrations to return (default: 50)
            offset: Number of migrations to skip (for pagination)
            name_pattern: Optional pattern to filter migrations by name
            include_full_queries: Whether to include the full SQL statements in the result

        Returns:
            str: SQL query to get migrations with the specified filters
        """
        logger.debug(f"Getting migrations query with limit={limit}, offset={offset}, name_pattern='{name_pattern}'")
        sql = self.load_sql("get_migrations")

        # Sanitize inputs to prevent SQL injection
        sanitized_limit = max(1, min(100, limit))  # Limit between 1 and 100
        sanitized_offset = max(0, offset)
        sanitized_name_pattern = name_pattern.replace("'", "''")  # Escape single quotes

        # Format the SQL query with the parameters
        return sql.format(
            limit=sanitized_limit,
            offset=sanitized_offset,
            name_pattern=sanitized_name_pattern,
            include_full_queries="true" if include_full_queries else "false",
        )
