from unittest.mock import patch

import pytest
from pydantic import ValidationError

from supabase_mcp.settings import SUPPORTED_REGIONS, Settings


@pytest.fixture(autouse=True)
def reset_settings_singleton():
    """Reset the Settings singleton before each test"""
    # Clear singleton instance if it exists
    if hasattr(Settings, "_instance"):
        delattr(Settings, "_instance")
    yield
    # Clean up after test
    if hasattr(Settings, "_instance"):
        delattr(Settings, "_instance")


def test_settings_default_values(clean_environment):
    """Test default values (no config file, no env vars)"""
    settings = Settings.with_config()  # No config file
    assert settings.supabase_project_ref == "127.0.0.1:54322"
    assert settings.supabase_db_password == "postgres"


def test_settings_from_env_test(clean_environment):
    """Test loading from .env.test"""
    settings = Settings.with_config(".env.test")
    assert settings.supabase_project_ref == "test-project-ref"
    assert settings.supabase_db_password == "test-db-password"


def test_settings_from_env_vars(clean_environment):
    """Test env vars take precedence over config file"""
    env_values = {"SUPABASE_PROJECT_REF": "from-env", "SUPABASE_DB_PASSWORD": "env-password"}
    with patch.dict("os.environ", env_values, clear=True):
        settings = Settings.with_config(".env.test")  # Even with config file
        assert settings.supabase_project_ref == "from-env"
        assert settings.supabase_db_password == "env-password"


def test_settings_region_validation():
    """Test region validation."""
    # Test default region
    settings = Settings()
    assert settings.supabase_region == "us-east-1"

    # Test valid region from environment
    env_values = {"SUPABASE_REGION": "ap-southeast-1"}
    with patch.dict("os.environ", env_values, clear=True):
        settings = Settings()
        assert settings.supabase_region == "ap-southeast-1"

    # Test invalid region
    with pytest.raises(ValidationError) as exc_info:
        env_values = {"SUPABASE_REGION": "invalid-region"}
        with patch.dict("os.environ", env_values, clear=True):
            Settings()
    assert "Region 'invalid-region' is not supported" in str(exc_info.value)


def test_supported_regions():
    """Test that all supported regions are valid."""
    for region in SUPPORTED_REGIONS.__args__:
        env_values = {"SUPABASE_REGION": region}
        with patch.dict("os.environ", env_values, clear=True):
            settings = Settings()
            assert settings.supabase_region == region
