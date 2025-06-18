"""
User-related data models and validation
"""
from pydantic import BaseModel, EmailStr, field_validator, Field
from app.database import Base
from sqlalchemy import Column, String, Integer
from typing import List, Optional, ClassVar, Set
import re
from app.config import app_settings
from app.models.subscription import Subscription  # Add this import

# SQLAlchemy model
class User(Base):
    """
    SQLAlchemy model for users in the database
    
    Attributes:
        id: Unique identifier for the user
        email: User's email address (unique)
        name: User's display name
        hashed_password: Securely hashed password (never stored in plain text)
        subscriptions: List of user's subscriptions
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    
    # Add subscriptions attribute - initialized as empty list
    subscriptions: List[Subscription] = []

# Pydantic Models for API
class UserBase(BaseModel):
    """
    Base model for user data shared across requests and responses
    """
    email: EmailStr = Field(..., description="User's email address (must be valid format)")
    name: str = Field(..., description="User's display name")

class UserCreate(UserBase):
    """
    Model for user creation with password validation
    """
    password: str = Field(
        ..., 
        description=f"Password (min {app_settings.MIN_PASSWORD_LENGTH} chars with uppercase, number, and special char)"
    )
    
    # Class constants
    SPECIAL_CHARS: ClassVar[Set[str]] = set("!@#$%^&*()_+-=[]{}|;:,.<>?/")
    
    @field_validator("password")
    def validate_password_strength(cls, password: str) -> str:
        """
        Validate that password meets minimum security requirements
        
        Args:
            password: The password to validate
            
        Returns:
            The validated password
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        missing_requirements = []
        
        if len(password) < app_settings.MIN_PASSWORD_LENGTH:
            missing_requirements.append(f"at least {app_settings.MIN_PASSWORD_LENGTH} characters")
        
        if not any(c.isupper() for c in password):
            missing_requirements.append("at least one uppercase letter")
            
        if not any(c.isdigit() for c in password):
            missing_requirements.append("at least one number")
            
        if not any(c in cls.SPECIAL_CHARS for c in password):
            missing_requirements.append("at least one symbol")  # Use "symbol" not "special character"
            
        if missing_requirements:
            raise ValueError(f"Password must contain {', '.join(missing_requirements)}")
            
        return password

class LoginRequest(BaseModel):
    """
    Data model for login requests
    """
    email: EmailStr
    password: str

class RegisterRequest(UserCreate):
    """
    Data model for user registration
    
    Extends UserCreate with all its validation
    """
    pass

class UserInDB(UserBase):
    """
    User model as stored in the database (with ID)
    """
    id: int

    model_config = {
        "from_attributes": True
    }

class UserResponse(UserBase):
    """
    User model returned in API responses
    """
    id: int

    model_config = {
        "from_attributes": True
    }