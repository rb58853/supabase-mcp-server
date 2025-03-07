from __future__ import annotations

import urllib.parse
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

import asyncpg
from pydantic import BaseModel, Field
from tenacity import RetryCallState, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from supabase_mcp.exceptions import ConnectionError, PermissionError, QueryError
from supabase_mcp.logger import logger
from supabase_mcp.services.database.sql.models import QueryValidationResults
from supabase_mcp.services.database.sql.validator import SQLValidator
from supabase_mcp.settings import Settings

# Define a type variable for generic return types
T = TypeVar("T")


class StatementResult(BaseModel):
    """Represents the result of a single SQL statement."""

    rows: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of rows returned by the statement. Is empty if the statement is a DDL statement.",
    )


class QueryResult(BaseModel):
    """Represents results of query execution, consisting of one or more statements."""

    results: list[StatementResult] = Field(
        description="List of results from the statements in the query.",
    )


# Helper function for retry decorator to safely log exceptions
def log_db_retry_attempt(retry_state: RetryCallState) -> None:
    """Log database retry attempts.

    Args:
        retry_state: Current retry state from tenacity
    """
    if retry_state.outcome is not None and retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        exception_str = str(exception)
        logger.warning(f"Database error, retrying ({retry_state.attempt_number}/3): {exception_str}")


# Add the new AsyncSupabaseClient class
class PostgresClient:
    """Asynchronous client for interacting with Supabase PostgreSQL database."""

    _instance: PostgresClient | None = None  # Singleton instance

    def __init__(
        self,
        settings: Settings,
        project_ref: str | None = None,
        db_password: str | None = None,
        db_region: str | None = None,
    ):
        """Initialize client configuration (but don't connect yet).

        Args:
            settings_instance: Settings instance to use for configuration.
            project_ref: Optional Supabase project reference. If not provided, will be taken from settings.
            db_password: Optional database password. If not provided, will be taken from settings.
            db_region: Optional database region. If not provided, will be taken from settings.
        """
        self._pool = None
        self._settings = settings
        self.project_ref = project_ref or self._settings.supabase_project_ref
        self.db_password = db_password or self._settings.supabase_db_password
        self.db_region = db_region or self._settings.supabase_region
        self.db_url = self._build_connection_string()
        self.sql_validator: SQLValidator = SQLValidator()

        logger.info(f"Initialized PostgresClient with project ref: {self.project_ref}")

    @classmethod
    def get_instance(
        cls,
        settings: Settings,
        project_ref: str | None = None,
        db_password: str | None = None,
    ) -> PostgresClient:
        """Create and return a configured AsyncSupabaseClient instance.

        This is the recommended way to create a client instance.

        Args:
            settings_instance: Settings instance to use for configuration
            project_ref: Optional Supabase project reference
            db_password: Optional database password

        Returns:
            Configured AsyncSupabaseClient instance
        """
        if cls._instance is None:
            cls._instance = cls(
                settings=settings,
                project_ref=project_ref,
                db_password=db_password,
            )
            # Doesn't connect yet - will connect lazily when needed
        return cls._instance

    def _build_connection_string(self) -> str:
        """Build the database connection string for asyncpg.

        Returns:
            PostgreSQL connection string compatible with asyncpg
        """
        encoded_password = urllib.parse.quote_plus(self.db_password)

        if self.project_ref.startswith("127.0.0.1"):
            # Local development
            connection_string = f"postgresql://postgres:{encoded_password}@{self.project_ref}/postgres"
            logger.debug("Using local development connection string")
            return connection_string

        # Production Supabase - via transaction pooler
        connection_string = (
            f"postgresql://postgres.{self.project_ref}:{encoded_password}"
            f"@aws-0-{self._settings.supabase_region}.pooler.supabase.com:6543/postgres"
        )
        logger.debug(f"Using production connection string for region: {self._settings.supabase_region}")
        return connection_string

    @retry(
        retry=retry_if_exception_type(
            (
                asyncpg.exceptions.ConnectionDoesNotExistError,  # Connection lost
                asyncpg.exceptions.InterfaceError,  # Connection disruption
                asyncpg.exceptions.TooManyConnectionsError,  # Temporary connection limit
                OSError,  # Network issues
            )
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=log_db_retry_attempt,
    )
    async def create_pool(self) -> asyncpg.Pool[asyncpg.Record]:
        """Create and configure a database connection pool.

        Returns:
            Configured asyncpg connection pool

        Raises:
            ConnectionError: If unable to establish a connection to the database
        """
        try:
            logger.debug(f"Creating asyncpg connection pool for: {self.db_url.split('@')[1]}")

            # Create the pool with optimal settings
            pool = await asyncpg.create_pool(
                self.db_url,
                min_size=2,  # Minimum connections to keep ready
                max_size=10,  # Maximum connections allowed (same as current)
                statement_cache_size=0,
                command_timeout=30.0,  # Command timeout in seconds
                max_inactive_connection_lifetime=300.0,  # 5 minutes
            )

            # Test the connection with a simple query
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")
                logger.debug("Connection test successful")

            logger.info("✓ Created PostgreSQL connection pool with asyncpg")
            return pool

        except (asyncpg.PostgresError, OSError) as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Could not connect to database: {e}") from e

    async def ensure_pool(self) -> None:
        """Ensure a valid connection pool exists.

        This method is called before executing queries to make sure
        we have an active connection pool.
        """
        if self._pool is None:
            logger.debug("No active connection pool, creating one")
            self._pool = await self.create_pool()
        else:
            logger.debug("Using existing connection pool")

    async def close(self) -> None:
        """Close the connection pool and release all resources.

        This should be called when shutting down the application.
        """
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Closed PostgreSQL connection pool")
        else:
            logger.debug("No connection pool to close")

    @classmethod
    async def reset(cls) -> None:
        """Reset the singleton instance cleanly.

        This closes any open connections and resets the singleton instance.
        """
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
            logger.info("AsyncSupabaseClient instance reset complete")

    async def with_connection(self, operation_func: Callable[[asyncpg.Connection[Any]], Awaitable[T]]) -> T:
        """Execute an operation with a database connection.

        Args:
            operation_func: Async function that takes a connection and returns a result

        Returns:
            The result of the operation function

        Raises:
            ConnectionError: If a database connection issue occurs
        """
        # Ensure we have an active connection pool
        await self.ensure_pool()

        # Acquire a connection from the pool and execute the operation
        async with self._pool.acquire() as conn:
            return await operation_func(conn)

    async def with_transaction(
        self, conn: asyncpg.Connection[Any], operation_func: Callable[[], Awaitable[T]], readonly: bool = False
    ) -> T:
        """Execute an operation within a transaction.

        Args:
            conn: Database connection
            operation_func: Async function that executes within the transaction
            readonly: Whether the transaction is read-only

        Returns:
            The result of the operation function

        Raises:
            QueryError: If the query execution fails
        """
        # Execute the operation within a transaction
        async with conn.transaction(readonly=readonly):
            return await operation_func()

    async def execute_statement(self, conn: asyncpg.Connection[Any], query: str) -> StatementResult:
        """Execute a single SQL statement.

        Args:
            conn: Database connection
            query: SQL query to execute

        Returns:
            StatementResult containing the rows returned by the statement

        Raises:
            QueryError: If the statement execution fails
        """
        try:
            # Execute the query
            result = await conn.fetch(query)

            # Convert records to dictionaries
            rows = [dict(record) for record in result]

            # Log success
            logger.debug(f"Statement executed successfully, rows: {len(rows)}")

            # Return the result
            return StatementResult(rows=rows)

        except asyncpg.PostgresError:
            # Let the transaction handler deal with this
            raise

    @retry(
        retry=retry_if_exception_type(
            (
                asyncpg.exceptions.ConnectionDoesNotExistError,  # Connection lost
                asyncpg.exceptions.InterfaceError,  # Connection disruption
                asyncpg.exceptions.TooManyConnectionsError,  # Temporary connection limit
                OSError,  # Network issues
            )
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=log_db_retry_attempt,
    )
    async def execute_query_async(
        self,
        validated_query: QueryValidationResults,
        readonly: bool = True,  # Default to read-only for safety
    ) -> QueryResult:
        """Execute a SQL query asynchronously with proper transaction management.

        Args:
            validated_query: Validated query containing statements to execute
            readonly: Whether to execute in read-only mode

        Returns:
            QueryResult containing the results of all statements

        Raises:
            ConnectionError: If a database connection issue occurs
            QueryError: If the query execution fails
            PermissionError: When user lacks required privileges
        """
        # Log query execution (truncate long queries for readability)
        truncated_query = (
            validated_query.original_query[:100] + "..."
            if len(validated_query.original_query) > 100
            else validated_query.original_query
        )
        logger.debug(f"Executing query (readonly={readonly}): {truncated_query}")

        # Define the operation to execute all statements within a transaction
        async def execute_all_statements(conn):
            async def transaction_operation():
                results = []
                for statement in validated_query.statements:
                    if statement.query:  # Skip statements with no query
                        result = await self.execute_statement(conn, statement.query)
                        results.append(result)
                    else:
                        logger.warning(f"Statement has no query, statement: {statement}")
                return results

            # Execute the operation within a transaction
            results = await self.with_transaction(conn, transaction_operation, readonly)
            return QueryResult(results=results)

        # Execute the operation with a connection
        return await self.with_connection(execute_all_statements)

    # Keep the original methods but mark them as deprecated

    # TODO: This method is now deprecated, use execute_query_async instead
    async def _execute_statements(
        self,
        validated_query: QueryValidationResults,
        readonly: bool = False,
    ) -> QueryResult:
        """Executes one or more statements in a transaction.

        DEPRECATED: Use execute_query_async instead.

        Args:
            validated_query: QueryValidationResults containing parsed statements
            readonly: Read-only mode override

        Returns:
            QueryResult containing combined rows from all statements
        """
        # This implementation is kept for backward compatibility
        # but will be removed in a future version
        async with self._pool.acquire() as conn:
            logger.debug(f"Wrapping query in transaction (readonly={readonly})")
            # Initialize results list
            results: list[StatementResult] = []

            async with conn.transaction(readonly=readonly):
                for statement in validated_query.statements:
                    if statement.query:
                        result = await self._execute_raw_query(conn, statement.query)
                        # Append each result inside the loop
                        results.append(result)

            # Return combined results
            return QueryResult(results=results)

    # TODO: This method is now deprecated, use execute_statement instead
    async def _execute_raw_query(
        self,
        conn: asyncpg.Connection[Any],
        query: str,
    ) -> StatementResult:
        """Execute the raw query and process results.

        DEPRECATED: Use execute_statement instead.

        Args:
            conn: Database connection
            query: SQL query to execute

        Returns:
            StatementResult containing rows and metadata
        """
        # This implementation is kept for backward compatibility
        # but will be removed in a future version
        try:
            result = await conn.fetch(query)
            logger.debug(f"Query executed successfully: {result}")

            # Convert records to dictionaries
            rows = [dict(record) for record in result]

            return StatementResult(rows=rows)

        except asyncpg.PostgresError as e:
            logger.error(f"PostgreSQL error during query execution: {e}")
            # Handle and convert exceptions - this will raise appropriate exceptions
            await self._handle_postgres_error(e)

            # This line will never be reached as _handle_postgres_error always raises an exception
            # But we need it to satisfy the type checker
            raise QueryError("Unexpected error occurred")

    async def _handle_postgres_error(self, error: asyncpg.PostgresError) -> None:
        """Handle PostgreSQL errors and convert to appropriate exceptions.

        Args:
            error: PostgreSQL error

        Raises:
            PermissionError: When user lacks required privileges
            QueryError: For schema errors or general query errors
        """
        if isinstance(error, asyncpg.exceptions.InsufficientPrivilegeError):
            logger.error(f"Permission denied: {error}")
            raise PermissionError(
                f"Access denied: {str(error)}. Use live_dangerously('database', True) for write operations."
            ) from error
        elif isinstance(
            error,
            (
                asyncpg.exceptions.UndefinedTableError,
                asyncpg.exceptions.UndefinedColumnError,
            ),
        ):
            logger.error(f"Schema error: {error}")
            raise QueryError(str(error)) from error
        else:
            logger.error(f"Database error: {error}")
            raise QueryError(f"Query failed: {str(error)}") from error
