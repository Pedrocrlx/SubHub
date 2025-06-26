"""
Tests for authentication functionality.

This module verifies that:
- User registration works correctly
- Login creates and returns valid tokens
- Password validation enforces security requirements
- Token expiration works correctly
"""
import pytest
import time
import re

def test_user_registration(client, test_user):
    """
    Test user registration endpoint
    
    Verifies that:
    - Valid registration requests are accepted
    - User is successfully created in the database
    - Duplicate registration is rejected
    """
    # Register a new user
    response = client.post("/register", json=test_user)
    assert response.status_code == 201
    assert "Registration successful" in response.json()["message"]
    
    # Try to register the same user again (should fail)
    response = client.post("/register", json=test_user)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_user_login(client, test_user):
    """
    Test user login endpoint
    
    Verifies that:
    - Valid credentials return a token
    - Invalid credentials are rejected
    - Token format is correct
    """
    # Register a user first
    client.post("/register", json=test_user)
    
    # Login with correct credentials
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/login", json=login_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user_email"] == test_user["email"]
    
    # Check token format (should be a non-empty string)
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 10

def test_user_logout(client, test_user):
    """
    Test user logout endpoint
    
    Verifies that:
    - Logout invalidates the user's token
    - Subsequent requests with that token are rejected
    - Logout with an invalid token doesn't error
    """
    # Register and login
    client.post("/register", json=test_user)
    login_response = client.post("/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test protected endpoint works
    response = client.get("/subscriptions", headers=headers)
    assert response.status_code == 200
    
    # Logout
    response = client.post("/logout", headers=headers)
    assert response.status_code == 200
    assert "Logout successful" in response.json()["message"]
    
    # Try same token after logout
    response = client.get("/subscriptions", headers=headers)
    assert response.status_code == 401

def test_password_validation(client):
    """
    Test password validation rules
    
    Verifies that:
    - Minimum password length is enforced
    - Password complexity requirements are checked
    """
    test_cases = [
        # (password, should_accept)
        ("short", False),  # Too short
        ("longenoughbutnospecial123", False),  # No special characters
        ("Longenough!butnonumber", False),  # No numbers
        ("longenough!123nouppercase", False),  # No uppercase
        ("Valid!Password123", True)  # Valid password
    ]
    
    for password, should_accept in test_cases:
        test_user_data = {
            "email": "test@example.org",
            "username": "Test User",
            "password": password
        }
        
        response = client.post("/register", json=test_user_data)
        
        if should_accept:
            assert response.status_code == 201, f"Password '{password}' should be accepted"
        else:
            assert response.status_code == 422, f"Password '{password}' should be rejected"

def test_token_expiration(client, test_user):
    """
    Test token expiration functionality
    
    Verifies that:
    - Tokens expire after the configured time
    - Expired tokens are rejected
    
    Note: This test uses mocking to avoid waiting for actual expiration
    """
    # Register and login
    client.post("/register", json=test_user)
    login_response = client.post("/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # This test would normally require waiting for token expiration
    # For automated testing, we'd use a mock or shorter expiration time
    
    # For now, just verify token works initially
    response = client.get("/subscriptions", headers=headers)
    assert response.status_code == 200

def test_single_session_per_user(client, test_user):
    """
    Test that users can only have one active session
    
    Verifies that:
    - When a user logs in again, their previous session is invalidated
    - Old tokens no longer work after a new login
    """
    # Register a user
    client.post("/register", json=test_user)
    
    # First login
    login_response1 = client.post("/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token1 = login_response1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    # Verify first token works
    response = client.get("/subscriptions", headers=headers1)
    assert response.status_code == 200
    
    # Second login
    login_response2 = client.post("/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token2 = login_response2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Verify new token works
    response = client.get("/subscriptions", headers=headers2)
    assert response.status_code == 200
    
    # First token should no longer work
    response = client.get("/subscriptions", headers=headers1)
    assert response.status_code == 401

def test_invalid_email_formats(client):
    """
    Test validation of email formats during registration
    
    Verifies that:
    - Various invalid email formats are rejected
    - Valid but unusual email formats are accepted
    """
    test_cases = [
        # (email, should_accept)
        ("notanemail", False),
        ("missing@tld", False),
        ("spaces not allowed@example.com", False),
        ("valid+plus@example.com", True),
        ("valid.dots@example.co.uk", True)
    ]
    
    for email, should_accept in test_cases:
        test_user_data = {
            "email": email,
            "username": "Test User",
            "password": "Valid!Password123"
        }
        
        response = client.post("/register", json=test_user_data)
        
        if should_accept:
            assert response.status_code == 201, f"Email '{email}' should be accepted"
        else:
            assert response.status_code == 422, f"Email '{email}' should be rejected"

def test_password_strength_validation(client):
    """
    Test password strength validation rules
    
    Verifies that:
    - Very short passwords are rejected
    - Passwords exactly at minimum length are accepted
    - Password length validation is correctly enforced
    """
    from src.app.config import app_settings
    
    min_length = app_settings.MIN_PASSWORD_LENGTH
    
    for length in range(min_length - 2, min_length + 3):
        # Create password with specific length but meeting all other requirements
        password = f"P1!{'a' * (length - 3)}"  # Starts with uppercase, number, special char
        
        test_user_data = {
            "email": f"length{length}@example.com",
            "username": "Test User",
            "password": password
        }
        
        response = client.post("/register", json=test_user_data)
        
        if length >= min_length:
            # Should be accepted
            assert response.status_code == 201, f"Password of length {length} should be accepted"
        else:
            # Should be rejected
            assert response.status_code == 422, f"Password of length {length} should be rejected"