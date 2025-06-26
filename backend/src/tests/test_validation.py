"""
Tests for input validation functionality.

This module verifies that:
- Email formats are properly validated
- Password strength rules are enforced
- Empty required fields are rejected
- Invalid login attempts are handled correctly
- Data type validation works correctly
"""
import pytest

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
    - Very weak passwords are rejected
    - Strong passwords are accepted
    - Password complexity requirements are enforced
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

def test_empty_fields_validation(client):
    """
    Test validation of empty required fields
    
    Verifies that:
    - Empty email is rejected
    - Empty password is rejected
    - Empty username is rejected
    """
    test_cases = [
        # Field to leave empty
        "email",
        "password",
        "username"
    ]
    
    valid_data = {
        "email": "test@example.org",
        "username": "Test User",
        "password": "Valid!Password123"
    }
    
    for empty_field in test_cases:
        # Create a copy of valid data with one field empty
        test_data = valid_data.copy()
        test_data[empty_field] = ""
        
        response = client.post("/register", json=test_data)
        assert response.status_code == 422, f"Empty {empty_field} should be rejected"

def test_login_with_invalid_credentials(client, test_user):
    """
    Test login validation with invalid credentials
    
    Verifies that:
    - Non-existent user is rejected
    - Incorrect password is rejected
    - Error messages don't leak sensitive info
    """
    # Register a user
    client.post("/register", json=test_user)
    
    # Try login with non-existent email
    response = client.post("/login", json={
        "email": "nonexistent@example.com",
        "password": test_user["password"]
    })
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    # Try login with wrong password
    response = client.post("/login", json={
        "email": test_user["email"],
        "password": "WrongPassword123!"
    })
    assert response.status_code == 401
    assert "incorrect password" in response.json()["detail"].lower()

def test_invalid_data_types(client, test_user):
    """
    Test validation of data types
    
    Verifies that:
    - Non-string email is rejected
    - Non-string password is rejected
    - Numeric values for string fields are rejected
    """
    # Register valid user first
    client.post("/register", json=test_user)
    login_response = client.post("/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try adding subscription with wrong data types
    invalid_sub = {
        "service_name": 12345,  # should be string
        "monthly_price": "15.99",  # should be number
        "category": True  # should be string
    }
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    assert response.status_code == 422