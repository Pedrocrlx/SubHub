"""
Subscription-related data models
"""
from datetime import date
from pydantic import BaseModel, field_validator
from typing import List

class Subscription(BaseModel):
    """Represents a user's subscription service"""
    
    service_name: str
    monthly_price: float
    category: str
    starting_date: date

    @field_validator("monthly_price")
    def validate_price(cls, price):
        """Ensure price is positive"""
        if price <= 0:
            raise ValueError("You're expected to pay for your subscriptions, not the other way around!")
        return price

    @field_validator("category")
    def format_category(cls, category):
        """Normalize category format (strip whitespace, title case)"""
        return category.strip().title()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "service_name": "Netflix",
                "monthly_price": 17.99,
                "category": "Entertainment",
                "starting_date": "2025-06-01"
            }
        }
    }

class SubscriptionSummary(BaseModel):
    """Summary statistics for user subscriptions"""
    
    total_monthly_cost: float
    number_of_subscriptions: int
    subscription_list: List[Subscription] 