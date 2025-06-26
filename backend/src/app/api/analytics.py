"""
Analytics endpoints for user subscription data

This module provides API endpoints for:
- Calculation of total monthly spending
- Category-based spending breakdown
- Subscription search capabilities
"""
from fastapi import APIRouter, Query, Depends, status
from typing import List, Dict, Any, Optional
from collections import defaultdict

from src.app.models.subscription import Subscription
from src.app.models.user import User
from src.app.core.security import get_current_user
from src.app.utils.format_utils import format_currency
from src.app.core.logging import application_logger

router = APIRouter(tags=["Analytics"])

@router.get("/search", response_model=List[Subscription])
def search_subscriptions(
    term: str = Query(
        None,
        description="Search term to filter subscriptions by name or category",
        examples={"partial_match": {"value": "netflix"}, "category": {"value": "entertainment"}}
    ),
    current_user: User = Depends(get_current_user)
) -> List[Subscription]:
    """
    Search for specific subscriptions
    
    Allows filtering subscriptions by a search term that matches against
    service names and categories (case-insensitive partial matching).
    Returns all subscriptions if no search term is provided.
    
    Args:
        term: Optional search term for filtering
        current_user: Authenticated user from the security dependency
    
    Returns:
        List of matching subscription objects
    """
    # If no search term, return all subscriptions
    if not term:
        return current_user.subscriptions
    
    # Convert to lowercase for case-insensitive matching
    term_lower = term.lower()
    
    # Filter subscriptions by name or category (case-insensitive)
    matching_subscriptions = [
        subscription for subscription in current_user.subscriptions
        if term_lower in subscription.service_name.lower() or 
           term_lower in subscription.category.lower()
    ]
    
    subscription_count = len(matching_subscriptions)
    application_logger.info(
        f"User [{current_user.email}] searched for [{term}], found [{subscription_count}] matches"
    )
    
    return matching_subscriptions

@router.get("/summary", response_model=Dict[str, Any])
def get_spending_summary(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get summary of monthly subscription spending
    
    Calculates total monthly spending across all subscriptions,
    average cost per subscription, and total number of subscriptions.
    
    Args:
        current_user: Authenticated user from the security dependency
    
    Returns:
        Dictionary with spending metrics and subscription counts
    """
    subscription_count = len(current_user.subscriptions)
    
    if subscription_count == 0:
        application_logger.info(f"User [{current_user.email}] has no subscriptions for summary")
        return {
            "total_monthly_cost": 0,
            "average_subscription_price": 0,
            "subscription_count": 0,
            "formatted_total": "$0.00",
            "subscription_list": []
        }
    
    # Calculate total in a single pass
    total_spend = sum(sub.monthly_price for sub in current_user.subscriptions)
    average_price = total_spend / subscription_count
    
    application_logger.info(
        f"User [{current_user.email}] viewed spending summary: "
        f"${total_spend:.2f}/month across [{subscription_count}] subscriptions"
    )
    
    return {
        "total_monthly_cost": total_spend,
        "average_subscription_price": average_price,
        "subscription_count": subscription_count,
        "formatted_total": format_currency(total_spend),
        "subscription_list": current_user.subscriptions
    }

@router.get("/categories", response_model=Dict[str, Any])
def get_spending_by_category(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get breakdown of spending by category
    
    Groups subscriptions by their category and calculates total spending
    for each category, sorted by highest spending first.
    
    Args:
        current_user: Authenticated user from the security dependency
        
    Returns:
        Dictionary of categories with spending data
    """
    # Use defaultdict to simplify category creation
    categorized_subscriptions = defaultdict(lambda: {
        "subscriptions": [],
        "count": 0,
        "total_cost": 0
    })
    
    # Process all subscriptions in a single pass
    total_cost = 0
    for subscription in current_user.subscriptions:
        category = subscription.category
        category_data = categorized_subscriptions[category]
        
        # Update category data
        category_data["subscriptions"].append(subscription)
        category_data["count"] += 1
        category_data["total_cost"] += subscription.monthly_price
        total_cost += subscription.monthly_price
    
    # Calculate percentages and format costs
    if total_cost > 0:
        for category_data in categorized_subscriptions.values():
            category_data["percentage"] = (category_data["total_cost"] / total_cost) * 100
            category_data["formatted_cost"] = format_currency(category_data["total_cost"])
    else:
        # Handle zero total cost case
        for category_data in categorized_subscriptions.values():
            category_data["percentage"] = 0
            category_data["formatted_cost"] = format_currency(0)
    
    category_count = len(categorized_subscriptions)
    application_logger.info(
        f"User [{current_user.email}] viewed spending breakdown across [{category_count}] categories"
    )
    
    # Convert defaultdict to regular dict for serialization
    return dict(categorized_subscriptions)