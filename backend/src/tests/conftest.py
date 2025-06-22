"""
Shared fixtures and configuration for all tests.

This module provides pytest fixtures for:
- API test client setup
- Test user creation and authentication
- Database isolation between tests
"""
import os
import pytest
from fastapi.testclient import TestClient
import tempfile

# Updated imports to use the new module structure
from app.main import app
from app.db.storage import user_database, active_sessions, save_data_to_file
from app.config import app_settings as settings
from app.core.security import verify_password, hash_password, create_access_token
from app.models.user import User

# Test data using "username" instead of "name"
TEST_USER = {
    "email": "test@example.com",
    "username": "Test User",
    "password": "!Testpass123"
}

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment with a temporary data file
    This runs once before all tests and cleans up afterward
    """
    # Use a temporary file for test data
    test_data_fd, test_data_path = tempfile.mkstemp()
    os.close(test_data_fd)
    
    # Store original settings
    original_data_path = settings.DATA_FILEPATH
    
    # Update settings to use test file
    settings.DATA_FILEPATH = test_data_path
    
    yield  # Run all tests
    
    # Clean up after tests complete
    if os.path.exists(test_data_path):
        os.unlink(test_data_path)
        
    # Restore original settings
    settings.DATA_FILEPATH = original_data_path

@pytest.fixture
def client():
    """
    Create a FastAPI TestClient with a clean database for each test
    """
    # Clear all databases before each test
    user_database.clear()
    active_sessions.clear()
    
    return TestClient(app)

@pytest.fixture
def authenticated_client():
    """
    Create a FastAPI TestClient with a pre-authenticated test user
    """
    # Clear all databases before each test
    user_database.clear()
    active_sessions.clear()
    
    # Create test user with password hash directly in the user object
    password_hash = hash_password(TEST_USER["password"])
    user_database[TEST_USER["email"]] = User(
        email=TEST_USER["email"],
        username=TEST_USER["username"],
        passhash=password_hash,
        subscriptions=[]
    )
    
    # Create authentication token
    token, _ = create_access_token(TEST_USER["email"])
    
    # Create test client with auth headers
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {token}"}
    
    return client

@pytest.fixture
def test_user():
    """
    Return test user data for use in tests
    """
    return TEST_USER