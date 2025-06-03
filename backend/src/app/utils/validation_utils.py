"""
Validation utility functions
"""
import re
from typing import Optional, List, Tuple

def is_valid_service_name(name: str) -> bool:
    """
    Validate a subscription service name
    
    Requirements:
    - Must not be empty
    - Must not be just whitespace
    """
    if not name or name.isspace():
        return False
    return True

def validate_password_strength(
    password: str, 
    min_length: int = 8,
    require_uppercase: bool = True,
    require_number: bool = True, 
    require_symbol: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate password strength and return validation status with error messages
    
    Returns:
        Tuple of (is_valid, list_of_missing_requirements)
    """
    missing_requirements = []
    
    if len(password) < min_length:
        missing_requirements.append(f"at least {min_length} characters")
        
    if require_uppercase and not any(char.isupper() for char in password):
        missing_requirements.append("at least one uppercase letter")
        
    if require_number and not any(char.isdigit() for char in password):
        missing_requirements.append("at least one number")
        
    if require_symbol and not any(not char.isalnum() for char in password):
        missing_requirements.append("at least one symbol")
    
    return (len(missing_requirements) == 0, missing_requirements)

def sanitize_input(text: str) -> str:
    """
    Basic sanitization of user input to prevent script injection
    
    This is a very basic implementation and should not be relied upon for security.
    FastAPI's built-in validation and Pydantic should be the primary mechanisms.
    """
    # Replace angle brackets to neutralize HTML/script tags
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return text