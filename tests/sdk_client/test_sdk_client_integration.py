import os
import time
import uuid
from datetime import datetime

import pytest
import pytest_asyncio

from supabase_mcp.exceptions import PythonSDKError
from supabase_mcp.sdk_client.python_client import SupabaseSDKClient

# Unique identifier for test users to avoid conflicts
TEST_ID = f"test-{int(time.time())}-{uuid.uuid4().hex[:6]}"


# Create unique test emails
def get_test_email(prefix="user"):
    """Generate a unique test email"""
    return f"a.zuev+{prefix}-{TEST_ID}@outlook.com"


@pytest_asyncio.fixture
async def sdk_client():
    """
    Create a SupabaseSDKClient instance for integration testing.
    Uses environment variables directly.
    """
    # Reset the singleton to ensure we get a fresh instance
    SupabaseSDKClient._instance = None

    # Get Supabase credentials from environment variables
    project_ref = os.environ.get("SUPABASE_PROJECT_REF")
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not project_ref or not service_role_key:
        pytest.skip("SUPABASE_PROJECT_REF or SUPABASE_SERVICE_ROLE_KEY environment variables not set")

    client = await SupabaseSDKClient.create(project_ref, service_role_key)
    yield client

    # Cleanup after tests
    SupabaseSDKClient._instance = None


@pytest.mark.asyncio
class TestSDKClientIntegration:
    """
    Integration tests for the SupabaseSDKClient.
    These tests make actual API calls to the Supabase Auth service.
    """

    async def test_create_and_get_user(self, sdk_client):
        """Test creating a user and retrieving it by ID"""
        # Create a new test user
        test_email = get_test_email("create")
        create_params = {
            "attributes": {
                "email": test_email,
                "password": f"Password123!{TEST_ID}",
                "email_confirm": True,
                "user_metadata": {"name": "Test User", "test_id": TEST_ID},
            }
        }

        # Create the user
        create_result = await sdk_client.call_auth_admin_method("create_user", create_params)
        assert create_result is not None
        assert "id" in create_result
        user_id = create_result["id"]

        try:
            # Get the user by ID
            get_params = {"uid": user_id}
            get_result = await sdk_client.call_auth_admin_method("get_user_by_id", get_params)

            # Verify user data
            assert get_result is not None
            assert get_result["id"] == user_id
            assert get_result["email"] == test_email
            assert get_result["user_metadata"]["test_id"] == TEST_ID

        finally:
            # Clean up - delete the test user
            delete_params = {"id": user_id}
            await sdk_client.call_auth_admin_method("delete_user", delete_params)

    async def test_list_users(self, sdk_client):
        """Test listing users with pagination"""
        # Create test parameters
        list_params = {"page": 1, "per_page": 10}

        # List users
        result = await sdk_client.call_auth_admin_method("list_users", list_params)

        # Verify response format
        assert result is not None
        assert "users" in result
        assert "aud" in result
        assert isinstance(result["users"], list)

    async def test_update_user(self, sdk_client):
        """Test updating a user's attributes"""
        # Create a new test user
        test_email = get_test_email("update")
        create_params = {
            "attributes": {
                "email": test_email,
                "password": f"Password123!{TEST_ID}",
                "email_confirm": True,
                "user_metadata": {"name": "Before Update", "test_id": TEST_ID},
            }
        }

        # Create the user
        create_result = await sdk_client.call_auth_admin_method("create_user", create_params)
        user_id = create_result["id"]

        try:
            # Update the user
            update_params = {
                "uid": user_id,
                "attributes": {
                    "user_metadata": {
                        "name": "After Update",
                        "test_id": TEST_ID,
                        "updated_at": datetime.now().isoformat(),
                    }
                },
            }

            update_result = await sdk_client.call_auth_admin_method("update_user_by_id", update_params)

            # Verify user was updated
            assert update_result is not None
            assert update_result["id"] == user_id
            assert update_result["user_metadata"]["name"] == "After Update"
            assert "updated_at" in update_result["user_metadata"]

        finally:
            # Clean up - delete the test user
            delete_params = {"id": user_id}
            await sdk_client.call_auth_admin_method("delete_user", delete_params)

    async def test_invite_user_by_email(self, sdk_client):
        """Test inviting a user by email"""
        # Create invite parameters
        test_email = get_test_email("invite")
        invite_params = {
            "email": test_email,
            "options": {"data": {"test_id": TEST_ID, "invited_at": datetime.now().isoformat()}},
        }

        # Invite the user
        try:
            result = await sdk_client.call_auth_admin_method("invite_user_by_email", invite_params)

            # Verify response
            assert result is not None
            assert result["email"] == test_email

            # Clean up - delete the invited user
            if "id" in result:
                delete_params = {"id": result["id"]}
                await sdk_client.call_auth_admin_method("delete_user", delete_params)
        except PythonSDKError as e:
            # Some Supabase instances may have email sending disabled,
            # so we'll check if the error is related to that
            if "sending emails is not configured" in str(e).lower():
                pytest.skip("Email sending is not configured in this Supabase instance")
            else:
                raise

    async def test_generate_link(self, sdk_client):
        """Test generating a magic link"""
        # Create link parameters
        test_email = get_test_email("link")
        link_params = {"params": {"type": "magiclink", "email": test_email}}

        # Generate link
        try:
            result = await sdk_client.call_auth_admin_method("generate_link", link_params)

            # Verify response
            assert result is not None
            assert "action_link" in result
            assert result["email"] == test_email

        except PythonSDKError as e:
            # Some Supabase instances may have email sending disabled
            if "sending emails is not configured" in str(e).lower():
                pytest.skip("Email sending is not configured in this Supabase instance")
            else:
                raise

    async def test_signup_and_delete_user(self, sdk_client):
        """Test complete flow: signup with password and delete user"""
        # Generate signup link
        test_email = get_test_email("signup")
        signup_params = {"params": {"type": "signup", "email": test_email, "password": f"Password123!{TEST_ID}"}}

        # User IDs to clean up in case of failures
        created_user_id = None

        try:
            # Generate signup link
            signup_result = await sdk_client.call_auth_admin_method("generate_link", signup_params)

            # Sometimes signup directly creates a user, verify and store the ID if available
            if "id" in signup_result:
                created_user_id = signup_result["id"]

            # Verify response contains link
            assert signup_result is not None
            assert "action_link" in signup_result
            assert signup_result["email"] == test_email

            # Now let's manually create a user with same email to test deletion
            if not created_user_id:
                create_params = {
                    "attributes": {"email": test_email, "password": f"Password123!{TEST_ID}", "email_confirm": True}
                }
                create_result = await sdk_client.call_auth_admin_method("create_user", create_params)
                created_user_id = create_result["id"]

            # Delete the user
            if created_user_id:
                delete_params = {"id": created_user_id}
                delete_result = await sdk_client.call_auth_admin_method("delete_user", delete_params)

                # Verify deletion
                assert delete_result is not None

        finally:
            # Ensure cleanup if test fails
            if created_user_id:
                try:
                    delete_params = {"id": created_user_id}
                    await sdk_client.call_auth_admin_method("delete_user", delete_params)
                except Exception:
                    pass

    async def test_invalid_parameters(self, sdk_client):
        """Test validation errors with invalid parameters"""
        # Test with invalid parameters
        invalid_params = {"invalid_field": "value"}

        # Should raise PythonSDKError containing validation error details
        with pytest.raises(PythonSDKError) as excinfo:
            await sdk_client.call_auth_admin_method("get_user_by_id", invalid_params)

        # Verify error message contains validation info
        assert "Invalid parameters" in str(excinfo.value)

    async def test_empty_parameters(self, sdk_client):
        """Test validation errors with empty parameters"""
        # Test with empty parameters
        empty_params = {}

        # Should raise PythonSDKError containing validation error details
        with pytest.raises(PythonSDKError) as excinfo:
            await sdk_client.call_auth_admin_method("get_user_by_id", empty_params)

        # Verify error message contains validation info
        assert "Invalid parameters" in str(excinfo.value)
        assert "uid" in str(excinfo.value)
