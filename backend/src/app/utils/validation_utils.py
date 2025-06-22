"""
Validation utility functions for data validation across the application
"""
import re
from typing import Optional

from app.config import app_settings

def validate_password_strength(password: str) -> str:
    """
    Validate password meets strength requirements
    
    Requirements:
    - Minimum length (from app settings)
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    
    Args:
        password: Password to validate
        
    Returns:
        The original password if valid
        
    Raises:
        ValueError: If password doesn't meet requirements
    """
    if len(password) < app_settings.MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {app_settings.MIN_PASSWORD_LENGTH} characters")
        
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
        
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
        
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit")
        
    # Return the original password, not a boolean
    return password

def is_valid_service_name(service_name: str) -> bool:
    """
    Validate if a service name is acceptable
    
    Requirements:
    - Non-empty string
    - Maximum 100 characters
    - Contains only alphanumeric chars, spaces, and common punctuation
    
    Args:
        service_name: Service name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not service_name or not isinstance(service_name, str):
        return False
        
    # Check length
    if len(service_name) > 100:
        return False
        
    # Check for valid characters (allowing alphanumeric, spaces, and basic punctuation)
    valid_pattern = r'^[\w\s\-\+\&\.\,\!\?\(\)\'\"]+$'
    return bool(re.match(valid_pattern, service_name))