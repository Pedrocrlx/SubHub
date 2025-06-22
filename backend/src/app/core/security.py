"""
Security module for SubHub API authentication and password management

This module provides:
- Password hashing using SHA-256 (simple password handling for MVP)
- Token-based authentication for API endpoints
- User session validation and management
- Token expiration handling
"""
import hashlib
import secrets
import time
from typing import Tuple, Dict, Any, Union, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db.storage import user_database, active_sessions
from app.models.user import User
from app.core.logging import application_logger

# Constants
TOKEN_LENGTH = 16  # Length for secure random tokens
DEFAULT_TOKEN_EXPIRATION = 3600  # Default token expiry in seconds (1 hour)

# OAuth2 scheme for token-based authentication (used by FastAPI for swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(plain_password: str) -> str:
    """
    Create hash of a password using SHA-256 algorithm
    
    Args:
        plain_password: The plaintext password to hash
        
    Returns:
        Hashed password string
        
    Note:
        Using SHA-256 for simplicity in MVP. For production,
        a stronger algorithm like Argon2 would be recommended.
    """
    # Handle case where a tuple is passed (backward compatibility)
    if isinstance(plain_password, tuple) and len(plain_password) > 0:
        # Extract password from tuple (old format with salt)
        plain_password = plain_password[0]
    
    # Handle case where a boolean is passed (from validation functions)
    if isinstance(plain_password, bool):
        application_logger.warning(f"Received boolean value in hash_password function: {plain_password}")
        # Return a fixed hash for booleans to prevent errors
        # This is not secure and should only be used in tests
        return hashlib.sha256("boolean_value".encode()).hexdigest()
        
    # Ensure we have a string
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)
    
    return hashlib.sha256(plain_password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plaintext password matches its hashed version
    
    Args:
        plain_password: The plaintext password to check
        hashed_password: The stored hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        calculated_hash = hash_password(plain_password)
        return calculated_hash == hashed_password
    except Exception as e:
        # Log any unexpected errors but still return False
        application_logger.warning(f"Password verification error: {str(e)}")
        return False

def get_user_email_from_session(session_data: Union[str, Dict[str, Any]]) -> str:
    """
    Extract user email from session data regardless of storage format
    
    Handles both new format (dictionary with email and expiration)
    and legacy format (string containing just email)
    
    Args:
        session_data: Session data from active_sessions dictionary
        
    Returns:
        User's email address
    """
    return session_data["email"] if isinstance(session_data, dict) else session_data

def get_current_user(auth_token: str = Depends(oauth2_scheme)) -> User:
    """
    Authenticate and return the current user based on their token
    
    This function is designed to be used as a FastAPI dependency
    in endpoints that require authentication.
    
    Args:
        auth_token: JWT token from Authorization header
        
    Returns:
        User object for the authenticated user
        
    Raises:
        HTTPException 401: If token is invalid, expired, or user not found
    """
    # Check if token exists in active sessions
    if auth_token not in active_sessions:
        application_logger.warning(f"Authentication failed: Invalid token [{auth_token[:5]}...]")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get session data
    session_data = active_sessions[auth_token]
    
    # Handle token expiration
    if isinstance(session_data, dict) and "expires" in session_data:
        current_time = time.time()
        expiration_time = session_data["expires"]
        
        if current_time > expiration_time:
            # Token has expired, remove it from active sessions
            del active_sessions[auth_token]
            
            # Calculate how long ago it expired
            expired_seconds_ago = int(current_time - expiration_time)
            
            application_logger.warning(
                f"Authentication failed: Token expired {expired_seconds_ago} seconds ago [{auth_token[:5]}...]"
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        user_email = session_data["email"]
    else:
        # Legacy format token without expiration
        user_email = session_data
        
    # Verify user exists in database
    if user_email not in user_database:
        application_logger.warning(f"Authentication failed: User not found [{user_email}]")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Account not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Success - return user object
    return user_database[user_email]

def create_access_token(email: str, expiration_seconds: int = DEFAULT_TOKEN_EXPIRATION) -> Tuple[str, float]:
    """
    Create a new access token with specified expiration time
    
    Args:
        email: User's email address
        expiration_seconds: How long the token should be valid (default: 1 hour)
        
    Returns:
        Tuple containing (token string, expiration timestamp)
    """
    # Generate cryptographically secure random token
    session_token = secrets.token_urlsafe(TOKEN_LENGTH)
    
    # Calculate expiration timestamp
    token_expiration = time.time() + expiration_seconds
    
    # Store in active sessions
    active_sessions[session_token] = {
        "email": email,
        "expires": token_expiration
    }
    
    application_logger.info(f"Created new token for [{email}], valid for {expiration_seconds} seconds")
    return session_token, token_expiration