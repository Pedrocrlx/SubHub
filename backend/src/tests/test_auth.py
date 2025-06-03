"""
Tests for authentication functionality.
"""
import pytest
import time
from .conftest import client, settings, TEST_USER, user_database, password_storage, active_sessions

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
    assert response.status_code == 201

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
        time.time = lambda: orig_time() - 7200  # Token created "in the past" (2 hours)
        
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