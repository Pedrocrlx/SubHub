"""
Analytics and reporting endpoints
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

@router.get("/search")
def search_subscriptions(
    # IMPORTANT: Using 'term' as parameter name to make tests pass
    term: str = Query(..., description="Search term for finding subscriptions"), 
    current_user: User = Depends(get_current_user)
):
    """Search for subscriptions by name or category"""
    # Convert search term to lowercase for case-insensitive matching
    normalized_search_term = term.lower()
    
    # Find subscriptions with matching name or category
    matching_subscriptions = [
        subscription for subscription in current_user.subscriptions
        if normalized_search_term in subscription.service_name.lower() or 
           normalized_search_term in subscription.category.lower()
    ]
    
    application_logger.info(
        f"User {current_user.email} searched for '{term}', found {len(matching_subscriptions)} matches"
    )
    return matching_subscriptions

@router.get("/summary")
def get_subscription_summary(
    current_user: User = Depends(get_current_user)
):
    """Get summary statistics for user's subscriptions"""
    # Calculate total monthly cost
    total_monthly_cost = sum(subscription.monthly_price for subscription in current_user.subscriptions)
    
    application_logger.info(
        f"User {current_user.email} viewed subscription summary: "
        f"{len(current_user.subscriptions)} subscriptions totaling ${total_monthly_cost:.2f}/month"
    )
    
    return SubscriptionSummary(
        total_monthly_cost=total_monthly_cost,
        number_of_subscriptions=len(current_user.subscriptions),
        subscription_list=current_user.subscriptions
    )

@router.get("/categories")
def analyze_spending_by_category(
    current_user: User = Depends(get_current_user)
):
    """Analyze user's subscription spending by category"""
    # Group subscriptions by category
    category_statistics = {}
    
    # Collect data for each category
    for subscription in current_user.subscriptions:
        category_name = subscription.category
        
        # Initialize category if first time seeing it
        if category_name not in category_statistics:
            category_statistics[category_name] = {
                "total_cost": 0, 
                "count": 0
            }
        
        # Update category statistics
        category_statistics[category_name]["total_cost"] += subscription.monthly_price
        category_statistics[category_name]["count"] += 1
    
    # Calculate overall total cost
    total_monthly_cost = sum(data["total_cost"] for data in category_statistics.values())
    
    # Add percentage breakdowns if there are any subscriptions
    if total_monthly_cost > 0:
        for category_name in category_statistics:
            category_percentage = (category_statistics[category_name]["total_cost"] / total_monthly_cost) * 100
            category_statistics[category_name]["percentage"] = round(category_percentage, 1)
    
    application_logger.info(f"User {current_user.email} viewed category analysis")
    return category_statistics
