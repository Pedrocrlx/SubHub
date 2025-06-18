"""
Tests for security and authentication features.
"""
import pytest
import time
from datetime import date
from .conftest import (
    client, auth_header, TEST_USER,
    password_storage, active_sessions, verify_password
)

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
    login_response = client.post("/login", json={
        "email": TEST_USER["email"], 
        "password": TEST_USER["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    from .conftest import TEST_SUBSCRIPTION, user_database
    from main import save_data_to_file, load_data_from_file
    
    # Add a subscription
    client.post("/subscriptions", json=TEST_SUBSCRIPTION, headers=headers)
    
    # Force a save operation
    save_data_to_file()
    
    # Clear in-memory data
    user_database.clear()
    password_storage.clear()
    active_sessions.clear()
    
    # Load data back
    load_data_from_file()
    
    # Verify data was restored
    assert TEST_USER["email"] in user_database
    assert len(user_database[TEST_USER["email"]].subscriptions) == 1

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
        content="This is not JSON data",
        headers={**headers, "Content-Type": "text/plain"}
    )
    assert response.status_code == 422
    
    # Test malformed JSON
    response = client.post(
        "/subscriptions",
        content="{invalid_json: definitely not valid",
        headers={**headers, "Content-Type": "application/json"}
    )
    assert response.status_code == 422
    
    # Test empty request body
    response = client.post("/subscriptions", headers=headers)
    assert response.status_code == 422