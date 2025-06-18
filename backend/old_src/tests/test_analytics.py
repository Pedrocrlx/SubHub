"""
Tests for analytics and reporting functionality.
"""
import pytest
from datetime import date
from .conftest import client, auth_header, TEST_SUBSCRIPTION, SECOND_SUBSCRIPTION

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

def test_performance_with_many_subscriptions(auth_header):
    """
    Test performance with a large number of subscriptions
    
    Verifies that:
    - API can handle a moderate number of subscriptions
    - Response times remain reasonable with more data
    """
    import time
    
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