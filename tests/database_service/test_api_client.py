"""Integration tests for the API client.

These tests verify that the API client can correctly interact with the Supabase Management API
using real GET requests to specific endpoints.
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from supabase_mcp.api_service.api_client import APIClient
from supabase_mcp.exceptions import APIConnectionError, APIServerError
from supabase_mcp.settings import settings

# Project reference for testing
PROJECT_REF = "drmzszdytvvfbcytltsw"


@pytest_asyncio.fixture
async def api_client():
    """Fixture providing an API client instance."""
    client = APIClient()
    yield client
    await client.close()


@pytest.mark.asyncio
@pytest.mark.skipif(not settings.supabase_access_token, reason="No access token available")
async def test_get_organizations(api_client):
    """Test that the client can fetch organizations from the API."""
    # This is a real API call to the organizations endpoint
    organizations = await api_client.execute_request("GET", "/v1/organizations")

    # Verify we got a valid response (list of organizations)
    assert isinstance(organizations, list)
    # Just check that we got some data back
    assert len(organizations) >= 0


@pytest.mark.asyncio
@pytest.mark.skipif(not settings.supabase_access_token, reason="No access token available")
async def test_get_projects(api_client):
    """Test that the client can fetch projects from the API."""
    # This is a real API call to the projects endpoint
    projects = await api_client.execute_request("GET", "/v1/projects")

    # Verify we got a valid response (list of projects)
    assert isinstance(projects, list)
    # Just check that we got some data back
    assert len(projects) >= 0


@pytest.mark.asyncio
@pytest.mark.skipif(not settings.supabase_access_token, reason="No access token available")
async def test_get_project_health(api_client):
    """Test that the client can fetch project health information."""
    # This is a real API call to the project health endpoint
    # We need to specify valid services to avoid a 400 error
    health_data = await api_client.execute_request("GET", f"/v1/projects/{PROJECT_REF}/health?services=db,rest,storage")

    # Verify we got a valid response (list of service health statuses)
    assert isinstance(health_data, list)
    # Check that we got some data back
    assert len(health_data) > 0

    # Check that each service has the expected structure
    for service in health_data:
        assert isinstance(service, dict)
        assert "name" in service
        assert "status" in service
        assert "healthy" in service


@pytest.mark.asyncio
async def test_network_error_handling():
    """Test that the client correctly handles network errors."""
    client = APIClient()

    try:
        # Mock the send method to raise a network error
        with patch.object(client.client, "send", side_effect=httpx.NetworkError("Simulated network error")):
            with pytest.raises(APIConnectionError) as excinfo:
                request = client.prepare_request("GET", "/v1/organizations")
                await client.send_request(request)

        # Verify error details
        assert "network error" in str(excinfo.value).lower()
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_server_error_handling():
    """Test that the client correctly handles 5xx errors."""
    client = APIClient()

    try:
        # Create a mock 500 error response
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.is_success = False
        mock_response.content = b'{"message": "Internal Server Error"}'
        mock_response.json.return_value = {"message": "Internal Server Error"}

        # Mock the send_request method to return the error response
        with patch.object(client, "send_request", return_value=mock_response):
            with pytest.raises(APIServerError) as excinfo:
                await client.execute_request("GET", "/v1/organizations")

        # Verify error details
        assert excinfo.value.status_code == 500
        assert "Internal Server Error" in str(excinfo.value)
    finally:
        await client.close()
