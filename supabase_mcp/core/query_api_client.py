import httpx

from supabase_mcp.core.http_client import AsyncHTTPClient
from supabase_mcp.logger import logger
from supabase_mcp.settings import settings


class QueryApiClient(AsyncHTTPClient):
    """Query API client connecting to thequery.dev for premium features and subscription validation.

    To preserve backwards compatibility and ensure a smooth UX for existing users,
    API key is not required as of now.
    """

    def __init__(
        self,
        query_api_key: str | None = None,
        query_api_url: str | None = None,
    ):
        """Initialize the Query API client"""
        self.query_api_key = query_api_key or settings.query_api_key
        self.query_api_url = query_api_url or settings.query_api_url
        self._check_api_key_set()
        self.client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure client exists and is ready for use.

        Creates the client if it doesn't exist yet.
        Returns the client instance.
        """
        if self.client is None:
            logger.info("Creating new Query API client")
            self.client = httpx.AsyncClient()
        logger.info("Returning existing Query API client")
        return self.client

    async def close(self) -> None:
        """Close the client and release resources."""
        if self.client:
            await self.client.aclose()
            logger.info("Query API client closed")

    def _check_api_key_set(self) -> None:
        """Check if the API key is set"""
        if not self.query_api_key:
            logger.warning("Query API key is not set. Only free features will be available.")
            return
