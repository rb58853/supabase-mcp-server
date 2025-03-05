from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from typing import Any

# Add asyncpg import
import asyncpg
from tenacity import RetryCallState, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from supabase_mcp.exceptions import ConnectionError, PermissionError, QueryError
from supabase_mcp.logger import logger
from supabase_mcp.settings import Settings
from supabase_mcp.sql_validator.validator import SQLValidator


@dataclass
class QueryResult:
    """Represents a query result with metadata."""

    rows: list[dict[str, Any]]
    count: int
    status: str


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
class AsyncSupabaseClient:
    """Connects to Supabase PostgreSQL database using asyncpg for async operations."""

    _instance: AsyncSupabaseClient | None = None  # Singleton instance

    def __init__(
        self,
        settings_instance: Settings,
        project_ref: str | None = None,
        db_password: str | None = None,
    ):
        """Initialize client configuration (but don't connect yet).

        Args:
            settings_instance: Settings instance to use for configuration.
            project_ref: Optional Supabase project reference. If not provided, will be taken from settings.
            db_password: Optional database password. If not provided, will be taken from settings.
        """
        self._pool = None
        self._settings = settings_instance
        self.project_ref = project_ref or self._settings.supabase_project_ref
        self.db_password = db_password or self._settings.supabase_db_password
        self.db_url = self._build_connection_string()
        self.sql_validator = SQLValidator()

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
    async def create_pool(self) -> asyncpg.Pool:
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
    def get_instance(
        cls,
        settings_instance: Settings,
        project_ref: str | None = None,
        db_password: str | None = None,
    ) -> AsyncSupabaseClient:
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
                settings_instance=settings_instance,
                project_ref=project_ref,
                db_password=db_password,
            )
            # Don't connect yet - will connect lazily when needed
        return cls._instance

    @classmethod
    async def reset(cls) -> None:
        """Reset the singleton instance cleanly.

        This closes any open connections and resets the singleton instance.
        """
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
            logger.info("AsyncSupabaseClient instance reset complete")

    async def execute_query_async(
        self,
        query: str,
        params: list[Any] | tuple[Any, ...] | None = None,
        readonly: bool = True,  # Default to read-only for safety
    ) -> QueryResult:
        """Execute a SQL query asynchronously with proper transaction management.

        Args:
            query: SQL query to execute
            params: Optional query parameters (list or tuple)
            readonly: Whether the query is read-only (defaults to True for safety)

        Returns:
            QueryResult containing rows and metadata

        Raises:
            ConnectionError: When database connection fails
            QueryError: When query execution fails (schema or general errors)
            PermissionError: When user lacks required privileges
        """
        # Ensure pool exists
        await self.ensure_pool()

        # Check if query contains transaction control statements
        has_transaction_control = self.sql_validator.validate_transaction_control(query)

        # Log query execution (truncate long queries for readability)
        truncated_query = query[:100] + "..." if len(query) > 100 else query
        logger.debug(
            f"Executing query (readonly={readonly}, has_transaction_control={has_transaction_control}): {truncated_query}"
        )

        # Execute with appropriate transaction handling
        return await self._execute_with_transaction_control(query, params, readonly, has_transaction_control)

    async def _execute_with_transaction_control(
        self,
        query: str,
        params: list[Any] | tuple[Any, ...] | None = None,
        readonly: bool = False,
        has_transaction_control: bool = False,
    ) -> QueryResult:
        """Execute query with appropriate transaction control.

        Args:
            query: SQL query to execute
            params: Optional query parameters (list or tuple)
            readonly: Whether the query is read-only
            has_transaction_control: Whether the query contains transaction control statements

        Returns:
            QueryResult containing rows and metadata
        """
        async with self._pool.acquire() as conn:
            try:
                # Case 1: Query has its own transaction control statements
                if has_transaction_control:
                    logger.debug("Executing query with its own transaction control")
                    # Execute directly without transaction wrapper
                    return await self._execute_raw_query(conn, query, params)

                # Case 2: Query needs to be wrapped in a transaction
                else:
                    logger.debug(f"Wrapping query in transaction (readonly={readonly})")
                    # Use transaction context manager
                    async with conn.transaction(readonly=readonly):
                        return await self._execute_raw_query(conn, query, params)

            except asyncpg.PostgresError as e:
                logger.error(f"PostgreSQL error during query execution: {e}")
                # Handle and convert exceptions - this will raise appropriate exceptions
                await self._handle_postgres_error(e)

                # This line will never be reached as _handle_postgres_error always raises an exception
                # But we need it to satisfy the type checker
                raise QueryError("Unexpected error occurred")

    async def _execute_raw_query(
        self,
        conn: asyncpg.Connection[Any],
        query: str,
        params: list[Any] | tuple[Any, ...] | None = None,
    ) -> QueryResult:
        """Execute the raw query and process results.

        Args:
            conn: Database connection
            query: SQL query to execute
            params: Optional query parameters (list or tuple)

        Returns:
            QueryResult containing rows and metadata
        """
        # Execute with parameters if provided
        if params:
            logger.debug(f"Executing query with {len(params)} parameters")
            # Handle both list and tuple types for parameters
            if isinstance(params, tuple):
                # Unpack tuple parameters
                result = await conn.fetch(query, *params)
            else:
                # Use list parameters directly
                result = await conn.fetch(query, *params)
        else:
            logger.debug("Executing query without parameters")
            result = await conn.fetch(query)

        # Convert records to dictionaries
        rows = [dict(record) for record in result]

        # Determine status message
        status = self._get_query_status(query)

        logger.debug(f"Query executed successfully: {status}, rows: {len(rows)}")
        return QueryResult(rows=rows, count=len(rows), status=status)

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

    def _get_query_status(self, query: str) -> str:
        """Determine a status message based on the query type.

        Args:
            query: SQL query

        Returns:
            Status message string
        """
        query_upper = query.strip().upper()

        if query_upper.startswith("SELECT"):
            return "SELECT"
        elif query_upper.startswith("INSERT"):
            return "INSERT"
        elif query_upper.startswith("UPDATE"):
            return "UPDATE"
        elif query_upper.startswith("DELETE"):
            return "DELETE"
        elif query_upper.startswith("CREATE"):
            return "CREATE"
        elif query_upper.startswith("ALTER"):
            return "ALTER"
        elif query_upper.startswith("DROP"):
            return "DROP"
        else:
            return "OK"
