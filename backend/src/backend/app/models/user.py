"""
User-related data models
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import List
from app.config import app_settings
from app.models.subscription import Subscription

class User(BaseModel):
    """Represents a registered user in the system"""
    
    email: EmailStr
    name: str
    subscriptions: List[Subscription] = []
    
class LoginRequest(BaseModel):
    """Login form data"""
    
    email: EmailStr 
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "!Password123"
            }
        }
    }

class RegisterRequest(BaseModel):
    """Registration form data"""
    
    email: EmailStr
    name: str
    password: str

    @field_validator('password')
    def validate_password(cls, password):
        """Validate password strength against all security requirements"""
        
        missing_requirements = []
        
        # Check minimum length
        if len(password) < app_settings.MIN_PASSWORD_LENGTH:
            missing_requirements.append(f"at least {app_settings.MIN_PASSWORD_LENGTH} characters")
            
        # Check for uppercase letters
        if app_settings.PASSWORD_REQUIRES_UPPERCASE and not any(char.isupper() for char in password):
            missing_requirements.append("at least one uppercase letter")
            
        # Check for numbers
        if app_settings.PASSWORD_REQUIRES_NUMBER and not any(char.isdigit() for char in password):
            missing_requirements.append("at least one number")
            
        # Check for symbols
        if app_settings.PASSWORD_REQUIRES_SYMBOL and not any(not char.isalnum() for char in password):
            missing_requirements.append("at least one symbol")
        
        # Generate comprehensive error message if requirements aren't met
        if missing_requirements:
            requirements_text = missing_requirements[0] if len(missing_requirements) == 1 else \
                f"{', '.join(missing_requirements[:-1])}, and {missing_requirements[-1]}"
            raise ValueError(f"Your password must include {requirements_text}!")
            
        return password
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "new_user@example.com", 
                "name": "New User",
                "password": "!Password123"
            }
        }
    }