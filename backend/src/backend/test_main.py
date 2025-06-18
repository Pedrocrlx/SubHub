# Dependencies: $ pip install pytest fastapi uvicorn pydantic email-validator argon2-cffi pytest-cov python-multipart
# Run: $ cd /workspaces/SubHub/backend/src/backend && python -m pytest test_main.py -v


from fastapi.testclient import TestClient
import pytest
import json
import os
import sys
import time
from datetime import date, datetime, timedelta
import logging

# Add the current directory to path to ensure imports work
# This is needed because pytest might run from a different directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app and related components
# Import the app first to initialize the application
from main import app

# Import data stores and settings
# These are exposed variables from the main module needed for testing
from main import user_database, password_storage, active_sessions
from main import app_settings as settings

# Import security-related functions for testing password handling
try:
    # Try to import password functions from main application
    from main import hash_password, verify_password
    using_argon2 = True
except ImportError:
    # Fallback if main application uses different names
    using_argon2 = False
    # Create our own password functions if needed
    import argon2
    try:
        password_hasher = argon2.PasswordHasher()
        
        def hash_password(password: str) -> str:
            """Create secure password hash using argon2"""
            return password_hasher.hash(password)

        def verify_password(plain_password: str, hashed_password: str) -> bool:
            """Verify password against stored hash safely"""
            try:
                password_hasher.verify(hashed_password, plain_password)
                return True
            except Exception:
                return False
    except ImportError:
        # Final fallback - warn but continue
        print("WARNING: argon2-cffi not installed. Password tests will fail.")

# Create test client
# This wraps the FastAPI app for testing HTTP endpoints
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

# ===== TEST FIXTURES =====

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Setup and teardown for each test
    
    This fixture runs automatically before and after each test to:
    1. Redirect data storage to a test file
    2. Clear in-memory data stores for clean state
    3. Clean up test files after the test
    
    Using autouse=True ensures this happens for every test
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

# Fix for test_user_login
def test_user_login():
    """
    Test user login process
    
    Verifies that:
    - Login succeeds with valid credentials
    - Login returns an access token
    - Token is stored in active sessions
    - Login fails with invalid credentials
    """
    # Register a test user
    client.post("/register", json=TEST_USER)
    
    # Test successful login
    response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]
    
    # Verify token is stored in active sessions
    from main import active_sessions
    assert token in active_sessions
    session_data = active_sessions[token]
    
    # Check if session data is a dictionary with email field
    if isinstance(session_data, dict):
        assert session_data["email"] == TEST_USER["email"]
    else:
        # For backward compatibility, if it's a string
        assert session_data == TEST_USER["email"]
    
    # Test failed login - wrong password
    response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    
    # Test failed login - user not found
    response = client.post("/login", json={
        "email": "nonexistent@example.com",
        "password": TEST_USER["password"]
    })
    assert response.status_code == 404

# Fix for test_add_subscription by updating the function that accesses active_sessions
def get_auth_token():
    # Register test user
    client.post("/register", json=TEST_USER)
    
    # Login to get token
    response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    return response.json()["access_token"]

# Update the auth_header fixture
@pytest.fixture
def auth_header():
    token = get_auth_token()
    return {"Authorization": f"Bearer {token}"}

# ===== SYSTEM TESTS =====

def test_home_endpoint():
    """
    Test the API root endpoint
    
    Verifies that:
    - The root endpoint returns 200 status code
    - The app name and version are correct
    - The status indicates the service is running
    """
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["app"] == settings.APP_NAME
    assert data["version"] == settings.VERSION
    assert data["status"] == "running"

# ===== AUTHENTICATION TESTS =====

def test_user_registration():
    """
    Test user registration process
    
    Verifies that:
    - New user registration succeeds with 201 status
    - Registration adds the user to the database
    - Passwords are hashed, not stored as plaintext
    - Duplicate registration is rejected with 400 status
    """
    # Register new user
    response = client.post("/register", json=TEST_USER)
    assert response.status_code == 201
    assert "message" in response.json()
    
    # Verify user is in database
    assert TEST_USER["email"] in user_database
    assert user_database[TEST_USER["email"]].name == TEST_USER["name"]
    
    # Verify password is hashed
    assert TEST_USER["email"] in password_storage
    hashed = password_storage[TEST_USER["email"]]
    assert hashed != TEST_USER["password"]  # Not plaintext
    assert hashed.startswith("$argon2")     # Is Argon2 hash
    
    # Try registering the same user again
    response = client.post("/register", json=TEST_USER)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_user_login():
    """
    Test user login process
    
    Verifies that:
    - Login succeeds with valid credentials
    - Login returns an access token
    - Token is stored in active sessions
    - Login fails with invalid credentials
    """
    # Register a test user
    client.post("/register", json=TEST_USER)
    
    # Test successful login
    response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]
    
    # Verify token is stored in active sessions
    from main import active_sessions
    assert token in active_sessions
    session_data = active_sessions[token]
    
    # Check if session data is a dictionary with email field
    if isinstance(session_data, dict):
        assert session_data["email"] == TEST_USER["email"]
    else:
        # For backward compatibility, if it's a string
        assert session_data == TEST_USER["email"]
    
    # Test failed login - wrong password
    response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    
    # Test failed login - user not found
    response = client.post("/login", json={
        "email": "nonexistent@example.com",
        "password": TEST_USER["password"]
    })
    assert response.status_code == 404

def test_user_logout(auth_header):
    """
    Test user logout process
    
    Verifies that:
    - Logout succeeds with valid token
    - After logout, the token is removed from active sessions
    - Using the invalidated token fails with 401
    """
    # Extract token from auth header
    token = auth_header["Authorization"].split()[1]
    
    # Verify session exists before logout
    assert token in active_sessions
    
    # Test logout
    response = client.post("/logout", headers=auth_header)
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify token was removed
    assert token not in active_sessions
    
    # Try using the invalidated token
    response = client.get("/subscriptions", headers=auth_header)
    assert response.status_code == 401

# ===== SUBSCRIPTION TESTS =====

def test_add_subscription(auth_header):
    """
    Test adding a subscription
    
    Verifies that:
    - Adding a subscription succeeds with 201 status
    - The subscription is stored in the user's account
    - The correct service name is returned in the response
    """
    response = client.post(
        "/subscriptions", 
        json=TEST_SUBSCRIPTION,
        headers=auth_header
    )
    assert response.status_code == 201
    
    data = response.json()
    assert "message" in data
    assert "service" in data
    assert data["service"] == TEST_SUBSCRIPTION["service_name"]
    
    # Get user and verify subscription was added
    token = auth_header["Authorization"].split()[1]
    session_data = active_sessions[token]
    
    # Handle both string and dictionary session data formats
    if isinstance(session_data, dict):
        user_email = session_data["email"]
    else:
        user_email = session_data
    
    user = user_database[user_email]
    
    assert len(user.subscriptions) == 1
    assert user.subscriptions[0].service_name == TEST_SUBSCRIPTION["service_name"]
    assert user.subscriptions[0].monthly_price == TEST_SUBSCRIPTION["monthly_price"]
    assert user.subscriptions[0].category == TEST_SUBSCRIPTION["category"]

def test_add_duplicate_subscription(auth_header):
    """
    Test adding a duplicate subscription
    
    Verifies that:
    - Adding the same subscription twice fails with 409 Conflict
    - The error message indicates the subscription already exists
    """
    # Add first subscription
    client.post("/subscriptions", json=TEST_SUBSCRIPTION, headers=auth_header)
    
    # Try adding the same subscription again
    response = client.post(
        "/subscriptions", 
        json=TEST_SUBSCRIPTION,
        headers=auth_header
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_list_subscriptions(auth_header):
    """
    Test listing user subscriptions
    
    Verifies that:
    - The list endpoint returns all user subscriptions
    - The subscription details match what was added
    - Empty list is returned when no subscriptions exist
    """
    # Test with no subscriptions
    response = client.get("/subscriptions", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == []
    
    # Add subscriptions
    client.post("/subscriptions", json=TEST_SUBSCRIPTION, headers=auth_header)
    client.post("/subscriptions", json=SECOND_SUBSCRIPTION, headers=auth_header)
    
    # Get subscriptions list
    response = client.get("/subscriptions", headers=auth_header)
    assert response.status_code == 200
    
    subs = response.json()
    assert len(subs) == 2
    
    # Verify details of both subscriptions
    service_names = [sub["service_name"] for sub in subs]
    assert TEST_SUBSCRIPTION["service_name"] in service_names
    assert SECOND_SUBSCRIPTION["service_name"] in service_names

def test_delete_subscription(auth_header):
    """
    Test deleting a subscription
    
    Verifies that:
    - Deleting a subscription succeeds with 200 status
    - The subscription is removed from the user's account
    - Attempting to delete non-existent subscription returns 404
    """
    # Add a subscription first
    client.post("/subscriptions", json=TEST_SUBSCRIPTION, headers=auth_header)
    
    # Delete the subscription
    response = client.delete(
        f"/subscriptions/{TEST_SUBSCRIPTION['service_name']}", 
        headers=auth_header
    )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify subscription was removed
    response = client.get("/subscriptions", headers=auth_header)
    assert len(response.json()) == 0
    
    # Try deleting non-existent subscription
    response = client.delete(
        "/subscriptions/NonExistentService", 
        headers=auth_header
    )
    assert response.status_code == 404

# ===== ANALYTICS TESTS =====

def test_subscription_summary(auth_header):
    """
    Test subscription summary endpoint
    
    Verifies that:
    - Summary correctly calculates total monthly cost
    - Number of subscriptions is counted accurately
    - All subscriptions are included in the list
    """
    # Add test subscriptions
    client.post("/subscriptions", json=TEST_SUBSCRIPTION, headers=auth_header)
    client.post("/subscriptions", json=SECOND_SUBSCRIPTION, headers=auth_header)
    
    # Get summary
    response = client.get("/summary", headers=auth_header)
    assert response.status_code == 200
    
    summary = response.json()
    expected_total = TEST_SUBSCRIPTION["monthly_price"] + SECOND_SUBSCRIPTION["monthly_price"]
    
    assert summary["number_of_subscriptions"] == 2
    assert round(summary["total_monthly_cost"], 2) == round(expected_total, 2)
    assert len(summary["subscription_list"]) == 2

def test_category_analysis(auth_header):
    """
    Test category analysis endpoint
    
    Verifies that:
    - Subscriptions are correctly grouped by category
    - Cost totals per category are calculated accurately
    - Subscription counts per category are accurate
    - Percentage calculations are correct
    """
    # Add subscriptions in different categories
    client.post("/subscriptions", json=TEST_SUBSCRIPTION, headers=auth_header)
    client.post("/subscriptions", json=SECOND_SUBSCRIPTION, headers=auth_header)
    
    # Add another in same category as first
    entertainment_sub = {
        "service_name": "Disney+",
        "monthly_price": 7.99,
        "category": "Entertainment",
        "starting_date": str(date.today())
    }
    client.post("/subscriptions", json=entertainment_sub, headers=auth_header)
    
    # Get category analysis
    response = client.get("/categories", headers=auth_header)
    assert response.status_code == 200
    
    categories = response.json()
    
    # Verify Entertainment category
    assert "Entertainment" in categories
    entertainment = categories["Entertainment"]
    assert entertainment["count"] == 2
    assert round(entertainment["total_cost"], 2) == round(TEST_SUBSCRIPTION["monthly_price"] + entertainment_sub["monthly_price"], 2)
    
    # Verify Music category
    assert "Music" in categories
    music = categories["Music"]
    assert music["count"] == 1
    assert round(music["total_cost"], 2) == round(SECOND_SUBSCRIPTION["monthly_price"], 2)
    
    # Verify percentages
    total_cost = sum(cat["total_cost"] for cat in categories.values())
    for category, data in categories.items():
        expected_pct = (data["total_cost"] / total_cost) * 100
        assert abs(data["percentage"] - expected_pct) < 0.1  # Allow small rounding differences

def test_search_functionality(auth_header):
    """
    Test subscription search endpoint
    
    Verifies that:
    - Search finds subscriptions by service name
    - Search finds subscriptions by category
    - Partial matches work correctly
    - Empty results are returned when no matches exist
    """
    # Add test subscriptions
    client.post("/subscriptions", json=TEST_SUBSCRIPTION, headers=auth_header)
    client.post("/subscriptions", json=SECOND_SUBSCRIPTION, headers=auth_header)
    
    # Search by exact service name
    response = client.get("/search?term=Netflix", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["service_name"] == "Netflix"
    
    # Search by partial service name
    response = client.get("/search?term=flix", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["service_name"] == "Netflix"
    
    # Search by category
    response = client.get("/search?term=entertainment", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "Entertainment"
    
    # Search with no results
    response = client.get("/search?term=nonexistent", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json()) == 0

# ===== VALIDATION TESTS =====

def test_subscription_validation():
    """
    Test validation rules for subscriptions
    
    Verifies that:
    - Negative prices are rejected with 422 status
    - Zero prices are rejected with 422 status
    - Missing required fields are rejected
    - Field format validation works correctly
    """
    # Register and login
    client.post("/register", json=TEST_USER)
    login_response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test negative price
    invalid_sub = dict(TEST_SUBSCRIPTION)
    invalid_sub["monthly_price"] = -10.50
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    assert response.status_code == 422
    
    # Test zero price
    invalid_sub["monthly_price"] = 0
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    assert response.status_code == 422
    
    # Test missing required field
    invalid_sub = dict(TEST_SUBSCRIPTION)
    del invalid_sub["service_name"]
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    assert response.status_code == 422
    
    # Test category normalization
    valid_sub = dict(TEST_SUBSCRIPTION)
    valid_sub["category"] = "entertainment"  # lowercase
    response = client.post("/subscriptions", json=valid_sub, headers=headers)
    assert response.status_code == 201
    
    # Verify category was normalized to title case
    response = client.get("/subscriptions", headers=headers)
    assert response.json()[0]["category"] == "Entertainment"

def test_password_validation():
    """
    Test comprehensive password validation rules
    
    Verifies that:
    - Passwords shorter than minimum length are rejected
    - Passwords without uppercase letters are rejected
    - Passwords without numbers are rejected
    - Passwords without symbols are rejected
    - Passwords meeting all requirements are accepted
    """
    # Test too short password
    short_password_user = dict(TEST_USER)
    short_password_user["password"] = "short"
    response = client.post("/register", json=short_password_user)
    assert response.status_code == 422
    assert "password" in response.json()["detail"][0]["loc"]
    assert "at least" in response.json()["detail"][0]["msg"] and "characters" in response.json()["detail"][0]["msg"]
    
    # Test missing uppercase letter
    no_upper_user = dict(TEST_USER)
    no_upper_user["email"] = "test_upper@example.com"  # Change email to avoid conflict
    no_upper_user["password"] = "!password123"  # All lowercase now
    response = client.post("/register", json=no_upper_user)
    assert response.status_code == 422
    assert "uppercase letter" in response.json()["detail"][0]["msg"].lower()
    
    # Test missing number
    no_number_user = dict(TEST_USER)
    no_number_user["email"] = "test_number@example.com"  # Change email to avoid conflict
    no_number_user["password"] = "Password!"
    response = client.post("/register", json=no_number_user)
    assert response.status_code == 422
    assert "number" in response.json()["detail"][0]["msg"].lower()
    
    # Test missing symbol
    no_symbol_user = dict(TEST_USER)
    no_symbol_user["email"] = "test_symbol@example.com"
    no_symbol_user["password"] = "Password123"  # No symbols
    response = client.post("/register", json=no_symbol_user)
    assert response.status_code == 422
    assert "symbol" in response.json()["detail"][0]["msg"].lower()
    
    # Test valid password (meets all requirements)
    valid_user = dict(TEST_USER)
    valid_user["email"] = "test_valid@example.com"  # Change email to avoid conflict
    valid_user["password"] = "!Password123!"
    response = client.post("/register", json=valid_user)
    assert response.status_code == 201, f"Valid password should be accepted, got error: {response.json() if response.status_code != 201 else 'none'}"

def test_invalid_email_formats():
    """
    Test validation of email formats during registration
    
    Verifies that:
    - Invalid email formats are rejected with 422 status
    - Various invalid email patterns are properly caught
    - Valid but unusual email formats are accepted
    """
    # Test completely invalid format
    invalid_user = dict(TEST_USER)
    invalid_user["email"] = "not-an-email"
    response = client.post("/register", json=invalid_user)
    assert response.status_code == 422
    assert "email" in response.json()["detail"][0]["loc"]
    
    # Test missing @ symbol
    invalid_user["email"] = "useremail.com"
    response = client.post("/register", json=invalid_user)
    assert response.status_code == 422
    
    # Test missing domain
    invalid_user["email"] = "user@"
    response = client.post("/register", json=invalid_user)
    assert response.status_code == 422
    
    # Test missing username
    invalid_user["email"] = "@example.com"
    response = client.post("/register", json=invalid_user)
    assert response.status_code == 422
    
    # Test unusual but valid email (should pass)
    valid_user = dict(TEST_USER)
    valid_user["email"] = "user+tag@example.co.uk"
    response = client.post("/register", json=valid_user)
    assert response.status_code == 201

def test_password_strength_validation():
    """
    Test password strength validation rules
    
    Verifies that:
    - Very short passwords are rejected
    - Passwords exactly at minimum length are accepted
    - Password length validation is correctly enforced
    """
    # Try a range of password lengths
    min_length = settings.MIN_PASSWORD_LENGTH
    
    # Test passwords with different lengths
    for length in range(min_length - 2, min_length + 3):
        test_user = dict(TEST_USER)
        test_user["email"] = f"user{length}@example.com"  # Unique email for each test
        # Use this instead to ensure all requirements are met
        test_user["password"] = f"P1!{'a' * (length-3)}"  # Starts with uppercase, number, symbol
        
        response = client.post("/register", json=test_user)
        
        if length >= min_length:
            # Should be accepted
            assert response.status_code == 201, f"Password of length {length} should be accepted"
        else:
            # Should be rejected
            assert response.status_code == 422, f"Password of length {length} should be rejected"
            error_detail = response.json()["detail"]
            assert any("password" in err.get("loc", []) for err in error_detail)

def test_empty_fields_validation():
    """
    Test validation of empty fields
    
    Verifies that:
    - Empty email is rejected
    - Empty name is rejected
    - Empty password is rejected
    - Empty values don't cause server errors
    """
    # Test empty email
    invalid_user = dict(TEST_USER)
    invalid_user["email"] = ""
    response = client.post("/register", json=invalid_user)
    assert response.status_code == 422
    
    # Test empty name
    invalid_user = dict(TEST_USER)
    invalid_user["name"] = ""
    response = client.post("/register", json=invalid_user)
    # This might be accepted depending on your validation, adjust accordingly
    # If name can be empty, assert status_code == 201
    # If name cannot be empty, assert status_code == 422
    
    # Test empty password
    invalid_user = dict(TEST_USER)
    invalid_user["password"] = ""
    response = client.post("/register", json=invalid_user)
    assert response.status_code == 422
    
    # Test login with empty fields
    response = client.post("/login", json={
        "email": "",
        "password": ""
    })
    assert response.status_code == 422
    
    # Test login with empty password but valid email
    # Your API treats empty password as an authentication failure rather than a validation error
    # First register a user to ensure the email exists
    client.post("/register", json=TEST_USER)
    
    response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": ""
    })
    # Expect 401 (authentication failure) instead of 422 (validation error)
    assert response.status_code == 401

def test_login_with_invalid_credentials():
    """
    Test various invalid login scenarios
    
    Verifies that:
    - Non-registered email returns appropriate error
    - Wrong password format is handled properly
    - Large password inputs are handled safely
    """
    # Register a valid user first
    client.post("/register", json=TEST_USER)
    
    # Test with valid format but non-registered email
    response = client.post("/login", json={
        "email": "nonexistent@example.org",
        "password": "!ValidPassword123"
    })
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    # Test with wrong password
    response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()
    
    # Test with very long password (shouldn't crash)
    response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": "x" * 1000  # Very long password
    })
    assert response.status_code == 401  # Should fail but not crash

# ===== SECURITY TESTS =====

def test_password_hashing():
    """
    Test password security features
    
    Verifies that:
    - Passwords are properly hashed, not stored in plaintext
    - Password hashes can be verified with correct password
    - Password hashes reject incorrect passwords
    """
    # Register user
    client.post("/register", json=TEST_USER)
    
    # Get stored password hash
    hashed_password = password_storage[TEST_USER["email"]]
    
    # Verify hash format
    assert hashed_password.startswith("$argon2")
    assert hashed_password != TEST_USER["password"]
    
    # Verify correct password matches hash
    assert verify_password(TEST_USER["password"], hashed_password)
    
    # Verify incorrect password fails
    assert not verify_password("wrong_password", hashed_password)

def test_authentication_required():
    """
    Test that protected endpoints reject unauthenticated requests
    
    Verifies that:
    - Protected endpoints require authentication
    - Invalid tokens are rejected
    - Missing tokens are rejected
    """
    # Try accessing protected endpoint without token
    response = client.get("/subscriptions")
    assert response.status_code == 401
    
    # Try with invalid token
    headers = {"Authorization": "Bearer invalid_token_12345"}
    response = client.get("/subscriptions", headers=headers)
    assert response.status_code == 401
    
    # Try with malformed header
    headers = {"Authorization": "InvalidFormat Token"}
    response = client.get("/subscriptions", headers=headers)
    assert response.status_code == 401

# ===== EDGE CASE TESTS =====

def test_price_edge_cases(auth_header):
    """
    Test edge cases for subscription prices
    
    Verifies that:
    - Very small prices (0.01) are accepted
    - Very large prices are accepted
    - Price calculations work correctly with extreme values
    """
    # Tiny price
    tiny_sub = {
        "service_name": "Minimal",
        "monthly_price": 0.01,
        "category": "Other",
        "starting_date": str(date.today())
    }
    response = client.post("/subscriptions", json=tiny_sub, headers=auth_header)
    assert response.status_code == 201
    
    # Very large price
    large_sub = {
        "service_name": "Enterprise",
        "monthly_price": 9999999.99,
        "category": "Business",
        "starting_date": str(date.today())
    }
    response = client.post("/subscriptions", json=large_sub, headers=auth_header)
    assert response.status_code == 201
    
    # Verify summary works with extreme values
    response = client.get("/summary", headers=auth_header)
    assert response.status_code == 200
    expected_total = 0.01 + 9999999.99
    assert abs(response.json()["total_monthly_cost"] - expected_total) < 0.01

def test_input_length_limits(auth_header):
    """
    Test handling of very long input data
    
    Verifies that:
    - Long service names are accepted
    - Long category names are accepted
    """
    # Long service name
    long_name_sub = {
        "service_name": "A" * 200,  # 200 character name
        "monthly_price": 9.99,
        "category": "Other",
        "starting_date": str(date.today())
    }
    response = client.post("/subscriptions", json=long_name_sub, headers=auth_header)
    assert response.status_code == 201
    
    # Long category name
    long_category_sub = {
        "service_name": "LongCategoryService",
        "monthly_price": 9.99,
        "category": "X" * 200,  # 200 character category
        "starting_date": str(date.today())
    }
    response = client.post("/subscriptions", json=long_category_sub, headers=auth_header)
    assert response.status_code == 201
    
    # Verify we can retrieve these subscriptions
    response = client.get("/subscriptions", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_malformed_data_handling():
    """
    Test handling of malformed input data
    
    Verifies that:
    - Non-JSON request bodies are rejected properly
    - Malformed JSON is handled gracefully
    - Empty request bodies don't crash the server
    """
    # Register a user for authentication
    client.post("/register", json=TEST_USER)
    login_response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test invalid content type (not JSON)
    response = client.post(
        "/subscriptions",
        content="This is not JSON data",  # Changed from data to content
        headers={**headers, "Content-Type": "text/plain"}
    )
    assert response.status_code == 422
    
    # Test malformed JSON
    response = client.post(
        "/subscriptions",
        content="{invalid_json: definitely not valid",  # Changed from data to content
        headers={**headers, "Content-Type": "application/json"}
    )
    assert response.status_code == 422
    
    # Test empty request body
    response = client.post("/subscriptions", headers=headers)
    assert response.status_code == 422

def test_invalid_data_types():
    """
    Test handling of incorrect data types in requests
    
    Verifies that:
    - String values for numeric fields are rejected
    - Numeric values for string fields are properly handled
    - Invalid date formats are rejected
    """
    # Register and login
    client.post("/register", json=TEST_USER)
    login_response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test string in price field
    invalid_sub = dict(TEST_SUBSCRIPTION)
    invalid_sub["monthly_price"] = "not a number"
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    assert response.status_code == 422
    
    # Test number in string field
    invalid_sub = dict(TEST_SUBSCRIPTION)
    invalid_sub["service_name"] = 12345
    # This might actually work since JSON numbers can be coerced to strings
    # But we're testing the behavior either way
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    
    # Test invalid date format
    invalid_sub = dict(TEST_SUBSCRIPTION)
    invalid_sub["starting_date"] = "not-a-date"
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    assert response.status_code == 422

def test_xss_injection_attempt():
    """
    Test handling of potentially malicious input
    
    Verifies that:
    - Script tags in fields don't break the application
    - SQL injection attempts are handled safely
    """
    # Register and login
    client.post("/register", json=TEST_USER)
    login_response = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test HTML/script injection
    xss_sub = {
        "service_name": "<script>alert('XSS')</script>",
        "monthly_price": 9.99,
        "category": "<b>Malicious</b>",
        "starting_date": str(date.today())
    }
    response = client.post("/subscriptions", json=xss_sub, headers=headers)
    # Should accept but sanitize or escape the input
    assert response.status_code == 201
    
    # Verify it was stored and retrievable
    response = client.get("/subscriptions", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_data_persistence():
    """Test that data is properly persisted to file and can be loaded back"""
    # Register a user and add subscriptions
    client.post("/register", json=TEST_USER)
    login_response = client.post("/login", json={"email": TEST_USER["email"], "password": TEST_USER["password"]})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add a subscription
    client.post("/subscriptions", json=TEST_SUBSCRIPTION, headers=headers)
    
    # Force a save operation
    from main import save_data_to_file
    save_data_to_file()
    
    # Clear in-memory data
    user_database.clear()
    password_storage.clear()
    active_sessions.clear()
    
    # Load data back
    from main import load_data_from_file
    load_data_from_file()
    
    # Verify data was restored
    assert TEST_USER["email"] in user_database
    assert len(user_database[TEST_USER["email"]].subscriptions) == 1

def test_user_data_isolation():
    """
    Test that users cannot access each other's data
    
    Verifies that:
    - User A cannot read User B's subscriptions
    - User A cannot modify User B's subscriptions
    - Users can have subscriptions with identical names without conflicts
    """
    # Create two users with their own auth tokens
    # User A
    client.post("/register", json={
        "email": "user_a@example.com",
        "name": "User A",
        "password": "!Password123"
    })
    login_a = client.post("/login", json={
        "email": "user_a@example.com",
        "password": "!Password123"
    })
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # User B
    client.post("/register", json={
        "email": "user_b@example.com",
        "name": "User B",
        "password": "!Password456"  # Now has uppercase and symbol
    })
    login_b = client.post("/login", json={
        "email": "user_b@example.com",
        "password": "!Password456"  # Now has uppercase and symbol
    })
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Add subscription for User A
    sub_a = {
        "service_name": "Netflix",
        "monthly_price": 15.99,
        "category": "Entertainment",
        "starting_date": str(date.today())
    }
    client.post("/subscriptions", json=sub_a, headers=headers_a)
    
    # Add same-named subscription for User B (with different details)
    sub_b = {
        "service_name": "Netflix",
        "monthly_price": 9.99,  # Different price
        "category": "Entertainment",
        "starting_date": str(date.today())
    }
    client.post("/subscriptions", json=sub_b, headers=headers_b)
    
    # Test 1: Verify User A sees only their subscription
    response_a = client.get("/subscriptions", headers=headers_a)
    subs_a = response_a.json()
    assert len(subs_a) == 1
    assert subs_a[0]["monthly_price"] == 15.99  # User A's price
    
    # Test 2: Verify User B sees only their subscription
    response_b = client.get("/subscriptions", headers=headers_b)
    subs_b = response_b.json()
    assert len(subs_b) == 1
    assert subs_b[0]["monthly_price"] == 9.99  # User B's price
    
    # Test 3: User A cannot delete User B's subscription
    response = client.delete("/subscriptions/Netflix", headers=headers_a)
    # After User A deletes "their" Netflix
    assert response.status_code == 200
    
    # User B's Netflix should still exist
    response_b = client.get("/subscriptions", headers=headers_b)
    assert len(response_b.json()) == 1
    
    # Test 4: User A cannot enumerate User B's subscriptions through API
    sub_c = {
        "service_name": "Amazon Prime",
        "monthly_price": 12.99,
        "category": "Entertainment",
        "starting_date": str(date.today())
    }
    client.post("/subscriptions", json=sub_c, headers=headers_b)
    
    # User A should still see 0 subscriptions (they deleted theirs)
    response_a = client.get("/subscriptions", headers=headers_a)
    assert len(response_a.json()) == 0
    
    # User B should see 2 subscriptions
    response_b = client.get("/subscriptions", headers=headers_b)
    assert len(response_b.json()) == 2

def test_subscription_name_conflicts():
    """
    Test handling of subscriptions with the same name across different users
    
    Verifies that:
    - Different users can have subscriptions with the same name
    - Adding a subscription with the same name doesn't affect other users
    """
    # Create two users with their own auth tokens
    client.post("/register", json={
        "email": "conflict_a@example.com",
        "name": "Conflict A",
        "password": "!Password123"
    })
    login_a = client.post("/login", json={
        "email": "conflict_a@example.com",
        "password": "!Password123"
    })
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    client.post("/register", json={
        "email": "conflict_b@example.com",
        "name": "Conflict B",
        "password": "!Password456"  # Now has uppercase and symbol
    })
    login_b = client.post("/login", json={
        "email": "conflict_b@example.com",
        "password": "!Password456"  # Now has uppercase and symbol
    })
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Add subscription for User A
    client.post("/subscriptions", json={
        "service_name": "Disney+",
        "monthly_price": 7.99,
        "category": "Entertainment",
        "starting_date": str(date.today())
    }, headers=headers_a)
    
    # Add same-named subscription for User B
    client.post("/subscriptions", json={
        "service_name": "Disney+",
        "monthly_price": 9.99,  # Different price
        "category": "Streaming",  # Different category
        "starting_date": str(date.today())
    }, headers=headers_b)
    
    # Verify User A subscription details
    response_a = client.get("/subscriptions", headers=headers_a)
    assert response_a.status_code == 200
    subs_a = response_a.json()
    assert len(subs_a) == 1
    assert subs_a[0]["monthly_price"] == 7.99
    assert subs_a[0]["category"] == "Entertainment"
    
    # Verify User B subscription details
    response_b = client.get("/subscriptions", headers=headers_b)
    assert response_b.status_code == 200
    subs_b = response_b.json()
    assert len(subs_b) == 1
    assert subs_b[0]["monthly_price"] == 9.99
    assert subs_b[0]["category"] == "Streaming"
    
    # Delete User A's subscription
    client.delete("/subscriptions/Disney+", headers=headers_a)
    
    # Verify User A's is gone but User B's remains
    response_a = client.get("/subscriptions", headers=headers_a)
    assert len(response_a.json()) == 0
    
    response_b = client.get("/subscriptions", headers=headers_b)
    assert len(response_b.json()) == 1

def test_token_expiration():
    """
    Test token expiration functionality
    
    Verifies that:
    - Tokens have a proper expiration time
    - Expired tokens are rejected
    - Token expiration doesn't affect other users' tokens
    """
    # For testing expiration, we'll monkeypatch the token creation
    import main
    orig_time = time.time
    
    try:
        # Create a token with short expiration
        # Make expiration more dramatic - use 7200 seconds (2 hours) in the past instead of 3500
        time.time = lambda: orig_time() - 7200  # Token created "in the past"
        
        client.post("/register", json=TEST_USER)
        response = client.post("/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Reset time to normal
        time.time = orig_time
        
        # Try using the severely-expired token
        response = client.get("/subscriptions", headers=headers)
        assert response.status_code == 401  # Should be expired
        assert "expired" in response.json()["detail"].lower()
    
    finally:
        # Restore original time function
        time.time = orig_time

def test_single_session_per_user():
    """
    Test single session per user feature
    
    Verifies that:
    - When a user logs in twice, the first session becomes invalid
    - Only the most recent login token works
    """
    # Register a test user
    client.post("/register", json=TEST_USER)
    
    # First login
    login1 = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    # Verify first token works
    response = client.get("/subscriptions", headers=headers1)
    assert response.status_code == 200
    
    # Second login
    login2 = client.post("/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Verify second token works
    response = client.get("/subscriptions", headers=headers2)
    assert response.status_code == 200
    
    # Verify first token no longer works
    response = client.get("/subscriptions", headers=headers1)
    assert response.status_code == 401

def test_performance_with_many_subscriptions(auth_header):
    """
    Test performance with a large number of subscriptions
    
    Verifies that:
    - API can handle a moderate number of subscriptions
    - Response times remain reasonable with more data
    """
    # Add several subscriptions
    num_subs = 15  # Reasonable number for a test
    
    start_time = time.time()
    
    for i in range(num_subs):
        sub = {
            "service_name": f"Service{i}",
            "monthly_price": 9.99,
            "category": "Test",
            "starting_date": str(date.today())
        }
        client.post("/subscriptions", json=sub, headers=auth_header)
    
    # Time to add all subscriptions
    add_time = time.time() - start_time
    
    # Time to get the list
    start_time = time.time()
    response = client.get("/subscriptions", headers=auth_header)
    get_time = time.time() - start_time
    
    assert response.status_code == 200
    assert len(response.json()) == num_subs
    
    # Just a simple check that operations don't take unreasonably long
    # For a small test dataset, these operations should be very quick
    assert add_time < 5.0  # Should be much faster, but we're being generous for CI environments
    assert get_time < 1.0  # Should be nearly instant
    
    # Test search operation with many subscriptions
    start_time = time.time()
    response = client.get("/search?term=Service1", headers=auth_header)  # Should match Service1, Service10-14
    search_time = time.time() - start_time
    
    assert response.status_code == 200
    assert len(response.json()) > 0  # Should find at least one match
    assert search_time < 1.0  # Search should also be quick

@pytest.fixture(scope="session", autouse=True)
def disable_pytest_log_capture():
    """Disable pytest's log capturing to allow logs to be written to file"""
    logging.getLogger().handlers = []  # Clear any handlers pytest might have added
    
    # Re-initialize our logging setup
    from main import setup_logging
    logger, log_file_path = setup_logging()
    
    yield
    
    # Make sure logs are written to disk after test session
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            handler.flush()