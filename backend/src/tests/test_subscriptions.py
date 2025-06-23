"""
Tests for subscription management functionality.

This module verifies that:
- Users can add, update, and delete subscriptions
- Subscription data is validated correctly
- Edge cases like price limits are handled properly
- User data is properly isolated between different users
"""
import pytest
from datetime import date, timedelta

# Test subscription data
TEST_SUBSCRIPTION = {
    "service_name": "Netflix",
    "monthly_price": 15.99,
    "category": "Entertainment",
    "starting_date": str(date.today())
}

def test_subscription_validation(authenticated_client):
    """
    Test validation of subscription data
    
    Verifies that:
    - Required fields are enforced
    - Field types are validated
    - Duplicate subscriptions are rejected
    """
    # Add valid subscription - should succeed
    response = authenticated_client.post("/subscriptions", json=TEST_SUBSCRIPTION)
    assert response.status_code == 201
    
    # Try adding with same name - should fail (duplicate)
    response = authenticated_client.post("/subscriptions", json=TEST_SUBSCRIPTION)
    assert response.status_code == 409
    
    # Try adding with missing required field
    invalid_sub = {
        "service_name": "Missing Price Service",
        # monthly_price is missing
        "category": "Test"
    }
    response = authenticated_client.post("/subscriptions", json=invalid_sub)
    assert response.status_code == 422
    
    # Try adding with wrong type
    invalid_sub = {
        "service_name": "Wrong Type Service",
        "monthly_price": "not a number",  # should be a number
        "category": "Test"
    }
    response = authenticated_client.post("/subscriptions", json=invalid_sub)
    assert response.status_code == 422

def test_price_edge_cases(authenticated_client):
    """
    Test edge cases for subscription prices
    
    Verifies that:
    - Zero price is accepted
    - Very high prices are accepted
    - Negative prices are rejected
    """
    # Test zero price
    zero_price_sub = {
        "service_name": "Free Service",
        "monthly_price": 0,
        "category": "Free"
    }
    response = authenticated_client.post("/subscriptions", json=zero_price_sub)
    assert response.status_code == 201
    
    # Test very high price
    high_price_sub = {
        "service_name": "Expensive Service",
        "monthly_price": 9999.99,
        "category": "Luxury"
    }
    response = authenticated_client.post("/subscriptions", json=high_price_sub)
    assert response.status_code == 201
    
    # Test negative price (should fail)
    negative_price_sub = {
        "service_name": "Invalid Service",
        "monthly_price": -10.0,
        "category": "Invalid"
    }
    response = authenticated_client.post("/subscriptions", json=negative_price_sub)
    assert response.status_code == 422

def test_user_data_isolation(client):
    """
    Test that users can only access their own subscriptions
    
    Verifies that:
    - Data is properly isolated between users
    - Users cannot see or modify other users' subscriptions
    """
    # Create two users
    user1 = {
        "email": "user1@example.com",
        "username": "User One",
        "password": "Password123!"
    }
    
    user2 = {
        "email": "user2@example.com",
        "username": "User Two",
        "password": "Password123!"
    }
    
    # Register both users
    client.post("/register", json=user1)
    client.post("/register", json=user2)
    
    # Log in as user1
    login_response = client.post("/login", json={
        "email": user1["email"],
        "password": user1["password"]
    })
    user1_token = login_response.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    
    # Add subscription for user1
    user1_sub = {
        "service_name": "User1's Service",
        "monthly_price": 10.99,
        "category": "User1"
    }
    response = client.post("/subscriptions", json=user1_sub, headers=user1_headers)
    assert response.status_code == 201
    
    # Log in as user2
    login_response = client.post("/login", json={
        "email": user2["email"],
        "password": user2["password"]
    })
    user2_token = login_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    
    # Add subscription for user2
    user2_sub = {
        "service_name": "User2's Service",
        "monthly_price": 20.99,
        "category": "User2"
    }
    response = client.post("/subscriptions", json=user2_sub, headers=user2_headers)
    assert response.status_code == 201
    
    # Verify user1 can see only their subscription
    response = client.get("/subscriptions", headers=user1_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["service_name"] == "User1's Service"
    
    # Verify user2 can see only their subscription
    response = client.get("/subscriptions", headers=user2_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["service_name"] == "User2's Service"
    
    # Try to delete user1's subscription as user2 (should fail or not find it)
    response = client.delete("/subscriptions/User1's Service", headers=user2_headers)
    assert response.status_code == 404

def test_subscription_editing(authenticated_client):
    """
    Test updating subscription details
    
    Verifies that:
    - Users can edit their own subscriptions
    - Validation rules are enforced during edits
    - Changes are properly saved
    """
    # First create a subscription
    initial_sub = {
        "service_name": "Netflix",
        "monthly_price": 15.99,
        "category": "Entertainment",
        "starting_date": str(date.today())
    }
    
    # Add the subscription
    response = authenticated_client.post("/subscriptions", json=initial_sub)
    assert response.status_code == 201
    
    # Update the subscription
    updated_sub = {
        "service_name": "Netflix",  # Same name to identify the subscription
        "monthly_price": 19.99,     # Changed price
        "category": "Streaming",    # Changed category
        "starting_date": str(date.today())
    }
    
    # Send PUT request to update
    response = authenticated_client.put("/subscriptions/Netflix", json=updated_sub)
    assert response.status_code == 200
    
    # Verify the update was successful
    response = authenticated_client.get("/subscriptions")
    assert response.status_code == 200
    
    subscriptions = response.json()
    assert len(subscriptions) == 1
    assert subscriptions[0]["monthly_price"] == 19.99
    assert subscriptions[0]["category"] == "Streaming"
    
    # Test editing non-existent subscription
    response = authenticated_client.put("/subscriptions/NonExistent", json=updated_sub)
    assert response.status_code == 404
    
    # Test invalid data in update
    invalid_update = {
        "service_name": "Netflix",
        "monthly_price": -5.99,  # Invalid negative price
        "category": "Streaming"
    }
    
    response = authenticated_client.put("/subscriptions/Netflix", json=invalid_update)
    assert response.status_code == 422

def test_subscription_edit_validation(authenticated_client):
    """
    Test validation during subscription editing
    
    Verifies that:
    - Cannot rename subscription to conflict with existing one
    - Invalid field types are rejected during edits
    - Invalid dates are rejected
    - Partial updates work correctly
    """
    # Create two subscriptions first
    subscriptions = [
        {
            "service_name": "Netflix",
            "monthly_price": 15.99,
            "category": "Entertainment"
        },
        {
            "service_name": "Disney+",
            "monthly_price": 7.99,
            "category": "Entertainment"
        }
    ]
    
    for sub in subscriptions:
        response = authenticated_client.post("/subscriptions", json=sub)
        assert response.status_code == 201
    
    # Test 1: Try to rename Netflix to Disney+ (should fail due to conflict)
    rename_update = {
        "service_name": "Disney+",  # Trying to rename to existing name
        "monthly_price": 15.99,
        "category": "Entertainment"
    }
    response = authenticated_client.put("/subscriptions/Netflix", json=rename_update)
    assert response.status_code == 409
    assert "already exists" in response.json().get("detail", "").lower()
    
    # Test 2: Try updating with invalid data types
    invalid_types = {
        "service_name": "Netflix",
        "monthly_price": "not-a-number",  # String instead of number
        "category": 123  # Number instead of string
    }
    response = authenticated_client.put("/subscriptions/Netflix", json=invalid_types)
    assert response.status_code == 422
    
    # Test 3: Try with invalid date format
    invalid_date = {
        "service_name": "Netflix",
        "monthly_price": 15.99,
        "category": "Entertainment",
        "starting_date": "not-a-date"
    }
    response = authenticated_client.put("/subscriptions/Netflix", json=invalid_date)
    assert response.status_code == 422
    
    # Test 4: Partial update (only price)
    partial_update = {
        "monthly_price": 19.99,
    }
    response = authenticated_client.put("/subscriptions/Netflix", json=partial_update)
    assert response.status_code == 200
    
    # Verify partial update worked
    response = authenticated_client.get("/subscriptions")
    assert response.status_code == 200
    
    subscriptions = response.json()
    netflix = next(sub for sub in subscriptions if sub["service_name"] == "Netflix")
    assert netflix["monthly_price"] == 19.99
    assert netflix["category"] == "Entertainment"  # Original value preserved
    
    # Test 5: Empty values
    empty_values = {
        "service_name": "Netflix",
        "monthly_price": 15.99,
        "category": ""  # Empty category
    }
    response = authenticated_client.put("/subscriptions/Netflix", json=empty_values)
    assert response.status_code == 422

def test_bulk_subscription_operations(authenticated_client):
    """
    Test practical user flows with multiple subscription operations
    
    Verifies that:
    - User can add multiple subscriptions
    - User can update one subscription while keeping others intact
    - User can delete one subscription while keeping others intact
    - Analytics correctly reflect changes after each operation
    """
    # Add multiple subscriptions
    subscriptions = [
        {
            "service_name": "Netflix",
            "monthly_price": 15.99,
            "category": "Entertainment"
        },
        {
            "service_name": "Spotify",
            "monthly_price": 9.99,
            "category": "Music"
        },
        {
            "service_name": "GitHub",
            "monthly_price": 7.99,
            "category": "Development"
        }
    ]
    
    for sub in subscriptions:
        response = authenticated_client.post("/subscriptions", json=sub)
        assert response.status_code == 201
    
    # Verify all were added
    response = authenticated_client.get("/subscriptions")
    assert response.status_code == 200
    assert len(response.json()) == 3
    
    # Update one subscription
    updated_sub = {
        "service_name": "Netflix",
        "monthly_price": 19.99,  # Price increase
        "category": "Entertainment"
    }
    
    response = authenticated_client.put("/subscriptions/Netflix", json=updated_sub)
    assert response.status_code == 200
    
    # Verify only one was updated
    response = authenticated_client.get("/subscriptions")
    subs = {s["service_name"]: s for s in response.json()}
    assert len(subs) == 3
    assert subs["Netflix"]["monthly_price"] == 19.99
    assert subs["Spotify"]["monthly_price"] == 9.99
    
    # Delete one subscription
    response = authenticated_client.delete("/subscriptions/GitHub")
    assert response.status_code == 200
    
    # Verify deletion and remaining subscriptions
    response = authenticated_client.get("/subscriptions")
    subs = response.json()
    assert len(subs) == 2
    assert all(s["service_name"] != "GitHub" for s in subs)
    
    # Check analytics reflect changes
    response = authenticated_client.get("/analytics/summary")
    summary = response.json()
    assert summary["subscription_count"] == 2
    assert round(summary["total_monthly_cost"], 2) == round(19.99 + 9.99, 2)
