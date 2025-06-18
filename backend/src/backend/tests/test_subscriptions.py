"""
Tests for subscription management functionality.
"""
import pytest
from datetime import date
from .conftest import (
    client, auth_header, TEST_SUBSCRIPTION, SECOND_SUBSCRIPTION,
    user_database, active_sessions
)

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
    client.post("/register", json={
        "email": "sub_validation@example.com",
        "name": "Validation User",
        "password": "!Password123"
    })
    login_response = client.post("/login", json={
        "email": "sub_validation@example.com",
        "password": "!Password123"
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
        "password": "!Password456"
    })
    login_b = client.post("/login", json={
        "email": "user_b@example.com",
        "password": "!Password456"
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