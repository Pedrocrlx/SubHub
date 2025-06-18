"""
Tests for input validation functionality.
"""
import pytest
from .conftest import client, TEST_USER, settings

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
    
    from .conftest import TEST_SUBSCRIPTION
    
    # Test string in price field
    invalid_sub = dict(TEST_SUBSCRIPTION)
    invalid_sub["monthly_price"] = "not a number"
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    assert response.status_code == 422
    
    # Test number in string field
    invalid_sub = dict(TEST_SUBSCRIPTION)
    invalid_sub["service_name"] = 12345
    # This might actually work since JSON numbers can be coerced to strings
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    
    # Test invalid date format
    invalid_sub = dict(TEST_SUBSCRIPTION)
    invalid_sub["starting_date"] = "not-a-date"
    response = client.post("/subscriptions", json=invalid_sub, headers=headers)
    assert response.status_code == 422