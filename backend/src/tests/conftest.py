"""
Shared fixtures and configuration for all tests.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from datetime import date

# Add the current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the app and related components
from main import app
from main import user_database, password_storage, active_sessions
from main import app_settings as settings
from main import verify_password, hash_password  # Add these imports

# Create test client
client = TestClient(app)

# Use a separate test data file to avoid interfering with production data
TEST_DATA_FILE = "test_subhub_data.json"

# ===== TEST DATA =====
# Sample data used across multiple tests

# Test user for authentication tests
TEST_USER = {
    "email": "test@example.com",
    "name": "Test User",
    "password": "!Testpass123"
}

# Sample subscription for testing subscription management
TEST_SUBSCRIPTION = {
    "service_name": "Netflix",
    "monthly_price": 15.99,
    "category": "Entertainment",
    "starting_date": str(date.today())
}

# Second subscription for testing multiple items
SECOND_SUBSCRIPTION = {
    "service_name": "Spotify",
    "monthly_price": 9.99,
    "category": "Music",
    "starting_date": str(date.today())
}

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Setup and teardown for each test
    
    This fixture runs automatically before and after each test to:
    1. Redirect data storage to a test file
    2. Clear in-memory data stores for clean state
    3. Clean up test files after the test
    """
    # Store original data file path
    original_data_file = settings.DATA_FILEPATH
    
    # Redirect to test file
    import main
    main.app_settings.DATA_FILEPATH = TEST_DATA_FILE
    
    # Clear any existing data
    user_database.clear()
    password_storage.clear()
    active_sessions.clear()
    
    yield  # Test runs here
    
    # Reset to original data file
    main.app_settings.DATA_FILEPATH = original_data_file
    
    # Clean up test files
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)

def get_auth_token():
    """Helper function to register a user and get authentication token"""
    # Register test user
    client.post("/register", json=TEST_USER)
    
    # Login to get token
    response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    return response.json()["access_token"]

@pytest.fixture
def auth_header():
    """Fixture that provides a valid authentication header"""
    token = get_auth_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="session", autouse=True)
def disable_pytest_log_capture():
    """Disable pytest's log capturing to allow logs to be written to file"""
    import logging
    logging.getLogger().handlers = []  # Clear any handlers pytest might have added
    
    # Re-initialize our logging setup
    from main import setup_logging
    logger, log_file_path = setup_logging()
    
    yield
    
    # Make sure logs are written to disk after test session
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            handler.flush()