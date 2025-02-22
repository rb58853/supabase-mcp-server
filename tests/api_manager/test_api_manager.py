import asyncio

import pytest
import pytest_asyncio

from supabase_mcp.api_manager.api_manager import SupabaseApiManager
from supabase_mcp.api_manager.api_safety_config import SafetyLevel
from supabase_mcp.exceptions import SafetyError


@pytest_asyncio.fixture
async def api_manager():
    """Fixture that provides an API manager instance"""
    manager = await SupabaseApiManager.get_manager()
    try:
        yield manager
    finally:
        await manager.close()  # Cleanup after tests


class TestApiManager:
    """Tests for the Supabase Management API manager"""

    @pytest.mark.asyncio
    async def test_safety_modes(self, api_manager):
        """Test API manager safety modes"""
        # Start in safe mode
        assert api_manager.mode == SafetyLevel.SAFE

        # Switch to unsafe mode
        api_manager.switch_mode(SafetyLevel.UNSAFE)
        assert api_manager.mode == SafetyLevel.UNSAFE

        # Switch back to safe mode
        api_manager.switch_mode(SafetyLevel.SAFE)
        assert api_manager.mode == SafetyLevel.SAFE

    def test_mode_safety(self, api_manager):
        """Test that unsafe operations are blocked in safe mode"""
        api_manager.switch_mode(SafetyLevel.SAFE)

        unsafe_operations = [
            ("PATCH", "/v1/projects/123/config/auth"),  # Auth config
            ("PUT", "/v1/projects/123/config/database/postgres"),  # DB config
        ]

        for method, path in unsafe_operations:
            with pytest.raises(SafetyError) as exc:
                asyncio.run(api_manager.execute_request(method, path))  # Keep asyncio.run() in a sync test
            assert "requires YOLO mode" in str(exc.value)

        # Should work in unsafe mode
        api_manager.switch_mode(SafetyLevel.UNSAFE)
        for method, path in unsafe_operations:
            try:
                asyncio.run(api_manager.execute_request(method, path))
            except Exception as e:
                assert not isinstance(e, SafetyError), f"Should not raise SafetyError in unsafe mode: {e}"

    @pytest.mark.asyncio
    async def test_spec_loading(self, api_manager):
        """Test that API spec is properly loaded"""
        spec = api_manager.get_spec()
        assert isinstance(spec, dict)
        assert "paths" in spec  # OpenAPI spec should have paths
        assert "components" in spec  # OpenAPI spec should have components
