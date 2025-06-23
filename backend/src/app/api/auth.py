"""
Authentication routes for user registration, login, and logout

This module provides endpoints for:
- User registration with secure password hashing
- User authentication with token generation
- Session management with automatic expiration
- User logout functionality
"""
from fastapi import APIRouter, Body, HTTPException, Request, Depends, status
from typing import Dict, Any, Optional

# Application imports
from src.app.models.user import User, RegisterRequest, LoginRequest
from src.app.core.security import (
    hash_password, verify_password, get_current_user, oauth2_scheme, 
    get_user_email_from_session, create_access_token
)
from src.app.db.storage import user_database, active_sessions, save_data_to_file
from src.app.core.logging import application_logger

# Map of email to active tokens for faster session invalidation
email_to_token_map: Dict[str, str] = {}

router = APIRouter(tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Dict[str, str])
def register_user(
    user_data: RegisterRequest = Body(..., description="User registration information"),
    request: Request = None
) -> Dict[str, str]:
    """
    Register a new user account
    
    Creates a new user with the provided email, name, and securely hashed password.
    Validates that the email is not already registered.
    
    Returns a success message on successful registration.
    """
    # Get client IP for security logging
    client_ip = request.client.host if request else "unknown"
    application_logger.info(f"Registration attempt: [{user_data.email}] from IP [{client_ip}]")
    
    # Check for existing email - early return pattern
    if user_data.email in user_database:
        application_logger.warning(f"Registration failed - email already exists: [{user_data.email}]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    # Hash the password
    password_hash = hash_password(user_data.password)
    
    # Create user record with password hash included directly
    user_database[user_data.email] = User(
        email=user_data.email, 
        username=user_data.username,
        passhash=password_hash,
        subscriptions=[]
    )
    
    # Persist user data to disk
    save_data_to_file()
    
    application_logger.info(f"User registered successfully: [{user_data.email}], username: [{user_data.username}]")
    return {"message": "Registration successful"}

@router.post("/login", response_model=Dict[str, Any])
def login_user(
    credentials: LoginRequest = Body(..., description="User login credentials"),
    request: Request = None
) -> Dict[str, Any]:
    """
    Authenticate user and provide access token
    
    Verifies the user's credentials and generates a session token with a 1-hour expiration.
    Implements single-session policy by invalidating any existing user sessions.
    
    Returns an access token and user information on successful authentication.
    """
    # Get client IP for security logging
    client_ip = request.client.host if request else "unknown"
    application_logger.info(f"Login attempt: [{credentials.email}] from IP [{client_ip}]")
    
    # Verify user exists - early return pattern
    if credentials.email not in user_database:
        application_logger.warning(f"Login failed - user not found: [{credentials.email}]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Get user
    user = user_database[credentials.email]
    
    # Validate password in a single check with proper error reporting
    if not hasattr(user, "passhash") or not user.passhash:
        application_logger.warning(f"Login failed - no password hash: [{credentials.email}]")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Password not set for account"
        )
    
    if not verify_password(credentials.password, user.passhash):
        application_logger.warning(f"Login failed - incorrect password: [{credentials.email}]")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect password"
        )
    
    # Single-session policy: Invalidate existing sessions for this user
    # Optimized to use direct lookup instead of iterating through all sessions
    if credentials.email in email_to_token_map:
        existing_token = email_to_token_map[credentials.email]
        if existing_token in active_sessions:
            del active_sessions[existing_token]
            application_logger.info(f"Invalidated previous session for user: [{credentials.email}]")
    
    # Create new session token with expiration
    session_token, token_expiration_time = create_access_token(credentials.email)
    
    # Update email-to-token mapping for faster lookups
    email_to_token_map[credentials.email] = session_token
    
    application_logger.info(f"Login successful: [{credentials.email}], token valid for [1 hour]")
    
    # Return authentication details
    return {
        "access_token": session_token,
        "token_type": "bearer",
        "user_email": credentials.email,
        "username": user.username,
        "expires": token_expiration_time
    }

@router.post("/logout", response_model=Dict[str, str])
def logout_user(
    current_user: User = Depends(get_current_user), 
    auth_token: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """
    End a user session
    
    Invalidates the current authentication token, effectively logging out the user.
    If the token is already invalid, returns a message indicating the user was already logged out.
    
    Returns a success message on successful logout.
    """
    # Get session data for the token
    session_data = active_sessions.get(auth_token)
    
    if auth_token in active_sessions:
        # Get user email for logging
        user_email = get_user_email_from_session(session_data)
        
        # Remove the session
        del active_sessions[auth_token]
        
        # Update our lookup map
        if user_email in email_to_token_map and email_to_token_map[user_email] == auth_token:
            del email_to_token_map[user_email]
        
        application_logger.info(f"User logged out: [{user_email}]")
        return {"message": "Logout successful"}
    
    application_logger.warning(f"Logout attempted with invalid token")
    return {"message": "Already logged out"}