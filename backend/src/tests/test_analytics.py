"""
Tests for analytics and reporting functionality.

This module verifies that the analytics endpoints correctly:
- Calculate subscription cost summaries
- Group and analyze spending by category
- Search across subscriptions
- Handle performance with multiple subscriptions
"""
import pytest
from datetime import date
import time

# Import test fixtures
from .conftest import client, authenticated_client, test_user

# Test subscription data
TEST_SUBSCRIPTION = {
    "service_name": "Netflix",
    "monthly_price": 15.99,
    "category": "Entertainment",
    "starting_date": str(date.today())
}

SECOND_SUBSCRIPTION = {
    "service_name": "Spotify",
    "monthly_price": 9.99,
    "category": "Music",
    "starting_date": str(date.today())
}

def test_subscription_summary(authenticated_client):
    """
    Test subscription summary endpoint
    
    Verifies that:
    - Summary correctly calculates total monthly cost
    - Number of subscriptions is counted accurately
    - All subscriptions are included in the list
    """
    # Add test subscriptions
    authenticated_client.post("/subscriptions", json=TEST_SUBSCRIPTION)
    authenticated_client.post("/subscriptions", json=SECOND_SUBSCRIPTION)
    
    # Get summary - updated path to match optimized API structure
    response = authenticated_client.get("/analytics/summary")
    assert response.status_code == 200
    
    summary = response.json()
    expected_total = TEST_SUBSCRIPTION["monthly_price"] + SECOND_SUBSCRIPTION["monthly_price"]
    
    assert summary["subscription_count"] == 2  # Changed from number_of_subscriptions to subscription_count
    assert round(summary["total_monthly_cost"], 2) == round(expected_total, 2)
    assert len(summary["subscription_list"]) == 2

def test_category_analysis(authenticated_client):
    """
    Test category analysis endpoint
    
    Verifies that:
    - Subscriptions are correctly grouped by category
    - Cost totals per category are calculated accurately
    - Subscription counts per category are accurate
    - Percentage calculations are correct
    """
    # Add subscriptions in different categories
    authenticated_client.post("/subscriptions", json=TEST_SUBSCRIPTION)
    authenticated_client.post("/subscriptions", json=SECOND_SUBSCRIPTION)
    
    # Add another in same category as first
    entertainment_sub = {
        "service_name": "Disney+",
        "monthly_price": 7.99,
        "category": "Entertainment",
        "starting_date": str(date.today())
    }
    authenticated_client.post("/subscriptions", json=entertainment_sub)
    
    # Get category analysis - updated path to match optimized API structure
    response = authenticated_client.get("/analytics/categories")
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

def test_search_functionality(authenticated_client):
    """
    Test subscription search endpoint
    
    Verifies that:
    - Search finds subscriptions by service name
    - Search finds subscriptions by category
    - Partial matches work correctly
    - Empty results are returned when no matches exist
    """
    # Add test subscriptions
    authenticated_client.post("/subscriptions", json=TEST_SUBSCRIPTION)
    authenticated_client.post("/subscriptions", json=SECOND_SUBSCRIPTION)
    
    # Search by exact service name - updated path to match optimized API structure
    response = authenticated_client.get("/analytics/search?term=Netflix")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["service_name"] == "Netflix"
    
    # Search by partial service name
    response = authenticated_client.get("/analytics/search?term=flix")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["service_name"] == "Netflix"
    
    # Search by category
    response = authenticated_client.get("/analytics/search?term=entertainment")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "Entertainment"
    
    # Search with no results
    response = authenticated_client.get("/analytics/search?term=nonexistent")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_performance_with_many_subscriptions(authenticated_client):
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
        authenticated_client.post("/subscriptions", json=sub)
    
    # Time to add all subscriptions
    add_time = time.time() - start_time
    
    # Time to get the list
    start_time = time.time()
    response = authenticated_client.get("/subscriptions")
    get_time = time.time() - start_time
    
    assert response.status_code == 200
    assert len(response.json()) == num_subs
    
    # Test search operation with many subscriptions
    start_time = time.time()
    response = authenticated_client.get("/analytics/search?term=Service1")  # Should match Service1, Service10-14
    search_time = time.time() - start_time
    
    assert response.status_code == 200
    assert len(response.json()) > 0  # Should find at least one match
    assert search_time < 1.0  # Search should be quick
    
    # Performance assertions - be generous for CI environments
    assert add_time < 5.0
    assert get_time < 1.0

def test_analytics_with_empty_data(authenticated_client):
    """
    Test analytics endpoints when user has no subscriptions
    
    Verifies that:
    - Summary endpoint handles empty subscription list
    - Categories endpoint handles empty subscription list
    - Search endpoint handles empty subscription list
    """
    # Ensure no subscriptions exist
    response = authenticated_client.get("/subscriptions")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    # Test summary with no subscriptions
    response = authenticated_client.get("/analytics/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_monthly_cost"] == 0
    assert summary["subscription_count"] == 0  # Changed from number_of_subscriptions to subscription_count
    
    # Test categories with no subscriptions
    response = authenticated_client.get("/analytics/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 0 or all(categories[cat]["count"] == 0 for cat in categories)
    
    # Test search with no subscriptions
    response = authenticated_client.get("/analytics/search?term=test")
    assert response.status_code == 200
    assert len(response.json()) == 0
