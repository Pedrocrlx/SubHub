"""
User models for authentication and data storage

This module provides Pydantic models for:
- User data validation and serialization
- Request and response schemas for authentication endpoints
- Field constraints and validations
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict

from app.models.subscription import Subscription
from app.utils.validation_utils import validate_password_strength
from app.config import app_settings  # Add this import

class User(BaseModel):
    """
    Core user model
    
    Contains essential user account information including:
    - Username for display purposes
    - Password hash stored directly with user data
    - Email address (used as primary identifier)
    - List of subscriptions
    """
    username: str = Field(..., description="User's display name")
    passhash: str = Field(..., description="SHA-256 hash of the user's password")
    email: EmailStr = Field(..., description="User's email address (used for login)")
    subscriptions: List[Subscription] = Field(default_factory=list, description="User's subscription services")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username is not empty"""
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "passhash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
                "email": "john@example.com",
                "subscriptions": [
                    {
                        "service_name": "Netflix",
                        "monthly_price": 17.99,
                        "category": "Entertainment",
                        "starting_date": "2025-01-15"
                    }
                ]
            }
        }
    )

class RegisterRequest(BaseModel):
    """
    User registration request model
    
    Validates registration data including:
    - Email format
    - Password strength requirements
    """
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's display name")
    password: str = Field(..., min_length=app_settings.MIN_PASSWORD_LENGTH, description="User's password")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username is not empty"""
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password meets strength requirements"""
        return validate_password_strength(v)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "username": "john_doe",
                "password": "SecurePassword123!"
            }
        }
    )

class LoginRequest(BaseModel):
    """
    User login request model
    
    Validates login credentials format
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "password": "SecurePassword123!"
            }
        }
    )
