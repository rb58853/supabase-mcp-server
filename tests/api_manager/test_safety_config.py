import asyncio

import pytest

from supabase_mcp.api_manager.api_manager import SupabaseApiManager
from supabase_mcp.api_manager.api_safety_config import SafetyConfig, SafetyLevel


@pytest.fixture
def safety_config():
    return SafetyConfig()


@pytest.fixture
async def api_manager():
    """Fixture that provides an API manager instance"""
    manager = SupabaseApiManager.create()  # Properly await the async function
    try:
        yield manager
    finally:
        asyncio.run(manager.close())  # Cleanup after tests


class TestPathMatching:
    """Tests for path matching functionality"""

    def test_basic_path_matching(self, safety_config):
        """Test basic path matching with and without parameters"""
        # Direct matches
        assert safety_config._path_matches("/v1/projects", "/v1/projects")

        # Parameter matches
        assert safety_config._path_matches("/v1/projects/{ref}", "/v1/projects/123")
        assert safety_config._path_matches("/v1/projects/{ref}/functions/{slug}", "/v1/projects/123/functions/my-func")

        # Non-matches
        assert not safety_config._path_matches("/v1/projects", "/v1/other")
        assert not safety_config._path_matches("/v1/projects/{ref}", "/v1/projects/123/extra")
        assert not safety_config._path_matches("/v1/projects", "/v1/projects/123")


class TestSafetyLevels:
    """Tests for operation safety level determination"""

    def test_blocked_operations(self, safety_config):
        """Test blocked operations are correctly identified"""
        test_cases = [
            ("DELETE", "/v1/projects/123"),  # Delete project
            ("DELETE", "/v1/organizations/myorg"),  # Delete org
            ("DELETE", "/v1/projects/123/database"),  # Delete database
        ]

        for method, path in test_cases:
            allowed, reason, level = safety_config.is_operation_allowed(method, path)
            assert not allowed, f"Operation {method} {path} should be blocked"
            assert level == SafetyLevel.BLOCKED
            assert "blocked" in reason.lower()

    def test_unsafe_operations(self, safety_config):
        """Test unsafe operations are correctly identified"""
        test_cases = [
            ("POST", "/v1/projects"),  # Create project
            ("POST", "/v1/organizations"),  # Create org
            ("PATCH", "/v1/projects/123/config/auth"),  # Auth config
            ("PUT", "/v1/projects/123/config/secrets"),  # Secrets
            ("PATCH", "/v1/projects/123/config/pooler"),  # Pooler config
            ("PUT", "/v1/projects/123/config/database/postgres"),  # Postgres config
        ]

        for method, path in test_cases:
            allowed, reason, level = safety_config.is_operation_allowed(method, path)
            assert allowed, f"Operation {method} {path} should be allowed but unsafe"
            assert level == SafetyLevel.UNSAFE
            assert "yolo" in reason.lower()

    def test_safe_operations(self, safety_config):
        """Test safe operations are correctly identified"""
        test_cases = [
            ("GET", "/v1/projects"),  # List projects
            ("GET", "/v1/projects/123/config"),  # Get config
            ("GET", "/v1/organizations"),  # List orgs
        ]

        for method, path in test_cases:
            allowed, reason, level = safety_config.is_operation_allowed(method, path)
            assert allowed, f"Operation {method} {path} should be allowed"
            assert level == SafetyLevel.SAFE
            assert "allowed" in reason.lower()


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_unknown_method(self, safety_config):
        """Test handling of unknown HTTP methods"""
        allowed, reason, level = safety_config.is_operation_allowed("INVALID", "/v1/projects")
        assert level == SafetyLevel.SAFE  # Unknown methods default to safe
        assert allowed

    def test_empty_path(self, safety_config):
        """Test handling of empty paths"""
        allowed, reason, level = safety_config.is_operation_allowed("GET", "")
        assert level == SafetyLevel.SAFE
        assert allowed

    def test_rule_listing(self, safety_config):
        """Test rule listing functionality"""
        rules = safety_config.list_all_rules()
        assert "Blocked operations" in rules
        assert "Unsafe operations" in rules
        # Verify key operations are listed
        assert "/v1/projects/{ref}" in rules  # Blocked operation
        assert "/v1/projects/{ref}/config/auth" in rules  # Unsafe operation
