import argon2
from fastapi.security import OAuth2PasswordBearer
import secrets
import time
from fastapi import Depends, HTTPException, status
from app.db.storage import user_database, active_sessions
from app.models.user import User
from app.core.logging import application_logger
from typing import Tuple, Dict, Any, Optional, Union, cast

# Initialize password hasher
password_hasher = argon2.PasswordHasher()

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    """
    Create secure hash of a password using Argon2
    
    Args:
        password: The plaintext password to hash
        
    Returns:
        A secure password hash
    """
    try:
        return password_hasher.hash(password)
    except Exception as e:
        application_logger.error(f"Password hashing error: [{str(e)}]!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password"
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plaintext password matches its hashed version
    
    Args:
        plain_password: The plaintext password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        password_hasher.verify(hashed_password, plain_password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False
    except Exception as e:
        application_logger.error(f"Password verification error: [{str(e)}]!")
        return False

def get_user_email_from_session(session_data: Union[Dict[str, Any], str]) -> str:
    """
    Extract user email from session data regardless of format
    
    Args:
        session_data: Either a dict with email key or a string email
        
    Returns:
        The user's email address
    """
    return session_data["email"] if isinstance(session_data, dict) else cast(str, session_data)

def get_current_user(auth_token: str = Depends(oauth2_scheme)) -> User:
    """
    Authenticate and return the current user based on their token
    
    Args:
        auth_token: The authentication token from request header
        
    Returns:
        The authenticated User object
        
    Raises:
        HTTPException: If authentication fails for any reason
    """
    # Check if token exists
    if auth_token not in active_sessions:
        application_logger.warning(f"Authentication failed - invalid token: [{auth_token[:5]}...]!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get session data
    session_data = active_sessions[auth_token]
    
    # Handle expiration if token is using the newer dict format
    if isinstance(session_data, dict) and "expires" in session_data:
        if time.time() > session_data["expires"]:
            # Token has expired, remove it
            del active_sessions[auth_token]
            application_logger.warning(f"Authentication failed - token expired: [{auth_token[:5]}...]!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        user_email = session_data["email"]
    else:
        # Old format token without expiration
        user_email = cast(str, session_data)
        
    # Verify user exists
    if user_email not in user_database:
        application_logger.warning(f"Authentication failed - account not found: [{user_email}]!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Account not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    application_logger.debug(f"User [{user_email}] authenticated successfully!")
    return user_database[user_email]

def create_access_token(email: str, expiration_seconds: int = 3600) -> Tuple[str, float]:
    """
    Create a new access token with specified expiration time
    
    Args:
        email: The user's email address
        expiration_seconds: Token validity period in seconds (default: 1 hour)
        
    Returns:
        Tuple containing (token_string, expiration_timestamp)
    """
    session_token = secrets.token_urlsafe(16)
    token_expiration = time.time() + expiration_seconds
    
    active_sessions[session_token] = {
        "email": email,
        "expires": token_expiration
    }
    
    application_logger.info(f"Created access token for user [{email}] valid for [{expiration_seconds//60} minutes]!")
    return session_token, token_expiration