from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

"""
Data models for subscription services

This module provides Pydantic models for:
- Subscription data validation and serialization
- Default values and field constraints
"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, nullable=False)
    category = Column(String, nullable=True)    # ex. "Streaming", "Cloud", etc.
    monthly_cost = Column(Float, nullable=True)
    renewal_date = Column(Date, nullable=True)  # Optional: auto-renew marker
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="subscriptions")
"""
Subscription-related data models
"""

class Subscription(BaseModel):
    """
    Subscription service model
    
    Contains details about a subscription service including:
    - Name of the service
    - Monthly price
    - Category for grouping
    - Starting date
    """
    service_name: str = Field(..., description="Name of the subscription service")
    monthly_price: float = Field(..., description="Monthly cost of the subscription")
    category: str = Field(..., description="Category of the subscription (e.g., Entertainment, Productivity)")
    starting_date: Optional[date] = Field(default_factory=date.today, description="Date when the subscription started")
    
    @field_validator('monthly_price')
    @classmethod
    def validate_price(cls, v):
        """Validate that the price is non-negative"""
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        """Validate and normalize category"""
        if not v or not v.strip():
            raise ValueError("Category cannot be empty")
        
        # Basic normalization of category names
        return v.strip().capitalize()
    
    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, v):
        """Validate service name"""
        if not v or not v.strip():
            raise ValueError("Service name cannot be empty")
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "service_name": "Netflix",
                "monthly_price": 17.99,
                "category": "Entertainment",
                "starting_date": "2025-06-01"
            }
        }
    )

class SubscriptionSummary(BaseModel):
    """
    Summary statistics for a collection of user subscriptions
    
    total_monthly_cost: float
    number_of_subscriptions: int
    subscription_list: List[Subscription] 
    Attributes:
        total_monthly_cost: Sum of all monthly subscription costs
        number_of_subscriptions: Count of active subscriptions
        subscription_list: Full list of subscription objects
    """
    total_monthly_cost: float = Field(..., description="Total monthly spending on all subscriptions")
    number_of_subscriptions: int = Field(..., description="Number of active subscriptions")
    subscription_list: List[Subscription] = Field(..., description="Complete list of subscription details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_monthly_cost": 45.97,
                "number_of_subscriptions": 3,
                "subscription_list": [
                    {
                        "service_name": "Netflix",
                        "monthly_price": 17.99,
                        "category": "Entertainment",
                        "starting_date": "2025-01-15"
                    },
                    {
                        "service_name": "Spotify",
                        "monthly_price": 9.99,
                        "category": "Music",
                        "starting_date": "2025-02-01"
                    },
                    {
                        "service_name": "GitHub",
                        "monthly_price": 17.99,
                        "category": "Development",
                        "starting_date": "2024-11-10"
                    }
                ]
            }
        }
    )
