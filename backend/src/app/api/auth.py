"""
Authentication routes for user registration, login, and logout
"""
from fastapi import APIRouter, Body, HTTPException, Request, Depends, status
from typing import Dict, Any, Optional

# Application imports
from src.app.models.user import User, RegisterRequest, LoginRequest
from src.app.core.security import (
    hash_password, verify_password, get_current_user, oauth2_scheme, 
    get_user_email_from_session
)
from src.app.db.storage import user_database, active_sessions, save_data_to_file
from src.app.core.logging import application_logger

# Map of email to active tokens for faster session invalidation
email_to_token_map: Dict[str, str] = {}

router = APIRouter(tags=["Auth"])

@router.post("/register", status_code=201)
def register_user(
    user_data: RegisterRequest = Body(..., description="User registration information"),
    request: Request = None
):
    """Register a new user account"""
    client_ip = request.client.host if request else "unknown"
    application_logger.info(f"Registration attempt: {user_data.email} from IP {client_ip}")
    
    # Check for existing email
    if user_data.email in user_database:
        application_logger.warning(f"Registration failed - email already exists: {user_data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user record
    user_database[user_data.email] = User(
        email=user_data.email, 
        name=user_data.name
    )
    
    # ✅ Store hashed password directly in the user object
    user_database[user_data.email].passhash = hash_password(user_data.password)
    
    # Save changes to file
    save_data_to_file()
    
    application_logger.info(f"User registered successfully: {user_data.email}, name: {user_data.name}")
    return {"message": "Registration successful"}

@router.post("/login")
def login_user(
    credentials: LoginRequest = Body(..., description="User login credentials"),
    request: Request = None
):
    """Authenticate user and provide access token"""
    client_ip = request.client.host if request else "unknown"
    application_logger.info(f"Login attempt: {credentials.email} from IP {client_ip}")
    
    # Verify user exists
    if credentials.email not in user_database:
        application_logger.warning(f"Login failed - user not found: {credentials.email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # ✅ Access stored password hash from user object
    stored_password_hash = user_database[credentials.email].passhash
    
    if not verify_password(credentials.password, stored_password_hash):
        application_logger.warning(f"Login failed - incorrect password: {credentials.email}")
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # Implement single-session policy: invalidate any existing sessions
    for existing_token, session_data in list(active_sessions.items()):
        user_email = get_user_email_from_session(session_data)
        if user_email == credentials.email:
            del active_sessions[existing_token]
            application_logger.info(f"Invalidated previous session for user: {credentials.email}")
    
    # Create new session token with expiration
    session_token = secrets.token_urlsafe(16)
    token_expiration = time.time() + 3600  # 1 hour from now
    
    active_sessions[session_token] = {
        "email": credentials.email,
        "expires": token_expiration
    }
    
    application_logger.info(f"Login successful: {credentials.email}, token valid for 1 hour")
    
    return {
        "access_token": session_token,
        "token_type": "bearer",
        "user_email": credentials.email,
        "user_name": user_database[credentials.email].name,
        "expires": token_expiration
    }

@router.post("/logout")
def logout_user(
    current_user: User = Depends(get_current_user), 
    auth_token: str = Depends(oauth2_scheme)
):
    """End a user session"""
    session_data = active_sessions.get(auth_token)
    
    if auth_token in active_sessions:
        user_email = get_user_email_from_session(session_data)
        del active_sessions[auth_token]
        application_logger.info(f"User logged out: {user_email}")
        return {"message": "Logout successful"}
    
    application_logger.warning(f"Logout attempted with invalid token")
    return {"message": "Already logged out"}
