import json
from dataclasses import dataclass
from pathlib import Path

import httpx

from supabase_mcp.api_manager.api_safety_config import SafetyConfig
from supabase_mcp.logger import logger

# Constants
SPEC_URL = "https://api.supabase.com/api/v1-json"
LOCAL_SPEC_PATH = Path(__file__).parent / "specs" / "api_spec.json"


@dataclass
class ValidationResult:
    """Result of request validation against OpenAPI spec"""

    is_valid: bool
    error: str | None = None
    operation_id: str | None = None
    operation_info: dict | None = None


class SpecManager:
    """
    Manages the OpenAPI specification for the Supabase Management API.
    Handles spec loading, caching, and validation.
    """

    def __init__(self):
        self.safety_config = SafetyConfig()
        self.spec: dict | None = None

    @classmethod
    async def create(cls) -> "SpecManager":
        """Async factory method to create and initialize a SpecManager"""
        manager = cls()
        await manager.on_startup()
        return manager

    async def on_startup(self) -> None:
        """Load and enrich spec on startup"""
        # Try to fetch latest spec
        raw_spec = await self._fetch_remote_spec()

        if not raw_spec:
            # If remote fetch fails, use our fallback spec
            logger.info("Using fallback API spec")
            raw_spec = self._load_local_spec()

        self.spec = raw_spec

    async def _fetch_remote_spec(self) -> dict | None:
        """
        Fetch latest OpenAPI spec from Supabase API.
        Returns None if fetch fails.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(SPEC_URL)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Failed to fetch API spec: {response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"Error fetching API spec: {e}")
            return None

    def _load_local_spec(self) -> dict:
        """
        Load OpenAPI spec from local file.
        This is our fallback spec shipped with the server.
        """
        try:
            with open(LOCAL_SPEC_PATH) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Local spec not found at {LOCAL_SPEC_PATH}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in local spec: {e}")
            raise

    def get_spec(self) -> dict:
        """Retrieve the enriched spec."""
        if self.spec is None:
            logger.error("OpenAPI spec not loaded by spec manager")
            raise ValueError("OpenAPI spec not loaded")
        return self.spec
