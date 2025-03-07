import json
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import httpx
import pytest

from supabase_mcp.services.api.spec_manager import ApiSpecManager

# Test data
SAMPLE_SPEC = {"openapi": "3.0.0", "paths": {"/v1/test": {"get": {"operationId": "test"}}}}


class TestApiSpecManager:
    """Integration tests for api spec manager tools."""

    # Local Spec Tests
    def test_load_local_spec_success(self, spec_manager_integration: ApiSpecManager):
        """Test successful loading of local spec file"""
        mock_file = mock_open(read_data=json.dumps(SAMPLE_SPEC))

        with patch("builtins.open", mock_file):
            result = spec_manager_integration._load_local_spec()

        assert result == SAMPLE_SPEC
        mock_file.assert_called_once()

    def test_load_local_spec_file_not_found(self, spec_manager_integration: ApiSpecManager):
        """Test handling of missing local spec file"""
        with patch("builtins.open", side_effect=FileNotFoundError), pytest.raises(FileNotFoundError):
            spec_manager_integration._load_local_spec()

    def test_load_local_spec_invalid_json(self, spec_manager_integration: ApiSpecManager):
        """Test handling of invalid JSON in local spec"""
        mock_file = mock_open(read_data="invalid json")

        with patch("builtins.open", mock_file), pytest.raises(json.JSONDecodeError):
            spec_manager_integration._load_local_spec()

    # Remote Spec Tests
    @pytest.mark.asyncio
    async def test_fetch_remote_spec_success(self, spec_manager_integration: ApiSpecManager):
        """Test successful remote spec fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_SPEC

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client  # Mock async context manager

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await spec_manager_integration._fetch_remote_spec()

        assert result == SAMPLE_SPEC
        mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_remote_spec_api_error(self, spec_manager_integration: ApiSpecManager):
        """Test handling of API error during remote fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client  # Mock async context manager

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await spec_manager_integration._fetch_remote_spec()

        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_remote_spec_network_error(self, spec_manager_integration: ApiSpecManager):
        """Test handling of network error during remote fetch"""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.NetworkError("Network error")

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await spec_manager_integration._fetch_remote_spec()

        assert result is None

    # Startup Flow Tests
    @pytest.mark.asyncio
    async def test_startup_remote_success(self, spec_manager_integration: ApiSpecManager):
        """Test successful startup with remote fetch"""
        # Reset spec to None to ensure we're testing the fetch
        spec_manager_integration.spec = None

        # Mock the fetch method to return sample spec
        mock_fetch = AsyncMock(return_value=SAMPLE_SPEC)

        with patch.object(spec_manager_integration, "_fetch_remote_spec", mock_fetch):
            result = await spec_manager_integration.get_spec()

        assert result == SAMPLE_SPEC
        mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_spec_remote_fail_local_fallback(self, spec_manager_integration: ApiSpecManager):
        """Test get_spec with remote failure and local fallback"""
        # Reset spec to None to ensure we're testing the fetch and fallback
        spec_manager_integration.spec = None

        # Mock fetch to fail and local to succeed
        mock_fetch = AsyncMock(return_value=None)
        mock_local = MagicMock(return_value=SAMPLE_SPEC)

        with (
            patch.object(spec_manager_integration, "_fetch_remote_spec", mock_fetch),
            patch.object(spec_manager_integration, "_load_local_spec", mock_local),
        ):
            result = await spec_manager_integration.get_spec()

        assert result == SAMPLE_SPEC
        mock_fetch.assert_called_once()
        mock_local.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_spec_both_fail(self, spec_manager_integration: ApiSpecManager):
        """Test get_spec with both remote and local failure"""
        # Reset spec to None to ensure we're testing the fetch and fallback
        spec_manager_integration.spec = None

        # Mock both fetch and local to fail
        mock_fetch = AsyncMock(return_value=None)
        mock_local = MagicMock(side_effect=FileNotFoundError("Test file not found"))

        with (
            patch.object(spec_manager_integration, "_fetch_remote_spec", mock_fetch),
            patch.object(spec_manager_integration, "_load_local_spec", mock_local),
            pytest.raises(FileNotFoundError),
        ):
            await spec_manager_integration.get_spec()

        mock_fetch.assert_called_once()
        mock_local.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_spec_cached(self, spec_manager_integration: ApiSpecManager):
        """Test that get_spec returns cached spec if available"""
        # Set the spec directly
        spec_manager_integration.spec = SAMPLE_SPEC

        # Mock the fetch method to verify it's not called
        mock_fetch = AsyncMock()

        with patch.object(spec_manager_integration, "_fetch_remote_spec", mock_fetch):
            result = await spec_manager_integration.get_spec()

        assert result == SAMPLE_SPEC
        mock_fetch.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_spec_not_loaded(self, spec_manager_integration: ApiSpecManager):
        """Test behavior when spec is not loaded but can be loaded"""
        # Reset spec to None
        spec_manager_integration.spec = None

        # Mock fetch to succeed
        mock_fetch = AsyncMock(return_value=SAMPLE_SPEC)

        with patch.object(spec_manager_integration, "_fetch_remote_spec", mock_fetch):
            result = await spec_manager_integration.get_spec()

        assert result == SAMPLE_SPEC
        mock_fetch.assert_called_once()
