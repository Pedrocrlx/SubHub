"""
Tests for security and authentication features.

This module verifies that:
- Password hashing and verification work correctly
- Endpoint authentication requirements are enforced
- The application handles potentially malicious input safely
- Data persistence mechanisms function properly
"""
import pytest
import time
from datetime import date

from src.app.db.storage import user_database, active_sessions, save_data_to_file, load_data_from_file
from src.app.core.security import verify_password

# Test subscription data
TEST_SUBSCRIPTION = {
    "service_name": "Netflix",
    "monthly_price": 15.99,
    "category": "Entertainment",
    "starting_date": str(date.today())
}

def test_password_hashing(client, test_user):
    """
    Test password security features
    
    Verifies that:
    - Passwords are properly hashed, not stored in plaintext
    - Password hashes can be verified with correct password
    - Password hashes reject incorrect passwords
    """
    # Register user
    client.post("/register", json=test_user)
    
    # Get stored password hash directly from user object
    user = user_database.get(test_user["email"])
    assert user is not None, "User not found in database"
    hashed_password = user.passhash
    
    # Verify hash format (now using SHA-256 instead of Argon2)
    assert hashed_password is not None, "Password hash is missing"
    assert len(hashed_password) == 64, "SHA-256 hash should be 64 characters"
    assert hashed_password != test_user["password"], "Password should not be stored in plaintext"
    
    # Verify correct password matches hash
    assert verify_password(test_user["password"], hashed_password)
    
    # Verify incorrect password fails
    assert not verify_password("wrong_password", hashed_password)

def test_authentication_required(client):
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

def test_xss_injection_attempt(authenticated_client):
    """
    Test handling of potentially malicious input
    
    Verifies that:
    - Script tags in fields don't break the application
    - Malicious input is handled safely
    """
    # Use the authenticated_client fixture which already has a valid token
    # Register and login handled by the fixture
    
    # Test HTML/script injection
    xss_sub = {
        "service_name": "<script>alert('XSS')</script>",
        "monthly_price": 9.99,
        "category": "<b>Malicious</b>",
        "starting_date": str(date.today())
    }
    response = authenticated_client.post("/subscriptions", json=xss_sub)
    # Should accept but sanitize or escape the input
    assert response.status_code == 201
    
    # Verify it was stored and retrievable
    response = authenticated_client.get("/subscriptions")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_data_persistence(client, test_user):
    """
    Test data persistence mechanism
    
    Verifies that:
    - Data is properly saved to disk
    - Data can be reloaded from disk
    - User and subscription information is preserved accurately
    """
    # Register a user and add subscriptions using the client fixture
    client.post("/register", json=test_user)
    login_response = client.post("/login", json={
        "email": test_user["email"], 
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add a subscription
    client.post("/subscriptions", json=TEST_SUBSCRIPTION, headers=headers)
    
    # Force a save operation
    save_data_to_file()
    
    # Clear in-memory data
    user_database.clear()
    active_sessions.clear()
    
    # Load data back
    load_data_from_file()
    
    # Verify data was restored
    assert test_user["email"] in user_database
    assert len(user_database[test_user["email"]].subscriptions) == 1

def test_malformed_data_handling(client, test_user):
    """
    Test handling of malformed input data
    
    Verifies that:
    - Non-JSON request bodies are rejected properly
    - Malformed JSON is handled gracefully
    - Empty request bodies don't crash the server
    """
    # Register a user for authentication
    client.post("/register", json=test_user)
    login_response = client.post("/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
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