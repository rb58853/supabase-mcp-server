import logging
from dataclasses import dataclass
from typing import Any, List

from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from tenacity import retry, stop_after_attempt, wait_exponential

from src.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Represents a query result with metadata."""

    rows: List[dict[str, Any]]
    count: int
    status: str


class SupabaseClient:
    """Connects to Supabase PostgreSQL database directly."""

    def __init__(self):
        """Initialize the PostgreSQL connection pool."""
        self._pool = None
        self.db_url = self._get_db_url_from_supabase()

    def _get_db_url_from_supabase(self) -> str:
        """Create PostgreSQL connection string from settings."""
        if settings.supabase_project_ref.startswith("127.0.0.1"):
            # Local development
            return f"postgresql://postgres:{settings.supabase_db_password}@{settings.supabase_project_ref}/postgres"

        # Production Supabase
        return (
            f"postgresql://postgres:{settings.supabase_db_password}"
            f"@db.{settings.supabase_project_ref}.supabase.co:5432/postgres"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=15),
    )
    def _get_pool(self):
        """Get or create PostgreSQL connection pool with read-only enforcement."""
        if self._pool is None:
            try:
                logger.debug(f"Creating connection pool for: {self.db_url.split('@')[1]}")
                self._pool = SimpleConnectionPool(minconn=1, maxconn=10, cursor_factory=RealDictCursor, dsn=self.db_url)
                # Test the connection
                with self._pool.getconn() as conn:
                    conn.set_session(readonly=True)
                    self._pool.putconn(conn)
                logger.info("✓ Created PostgreSQL connection pool in READ ONLY mode")
            except Exception:
                logger.exception("Failed to create PostgreSQL connection pool")
                raise
        return self._pool

    def query(self, query: str, params: tuple = None) -> QueryResult:
        """Execute a SQL query and return structured results.

        Args:
            query: SQL query to execute
            params: Optional query parameters to prevent SQL injection

        Returns:
            QueryResult containing rows and metadata

        Example:
            >>> result = client.query("SELECT * FROM chat.messages")
            >>> print(f"Found {result.count} messages")
            >>> for row in result.rows:
            >>>     print(row['content'])
        """
        pool = self._get_pool()
        conn = pool.getconn()
        try:
            conn.set_session(readonly=True)
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall() or []
                status = cur.statusmessage
                return QueryResult(rows=rows, count=len(rows), status=status)
        finally:
            pool.putconn(conn)

    @classmethod
    def create(cls) -> "SupabaseClient":
        """Create and return a configured SupabaseClient instance."""
        return cls()

    def __del__(self):
        """Close all connections in the pool when object is destroyed."""
        if self._pool is not None:
            self._pool.closeall()
