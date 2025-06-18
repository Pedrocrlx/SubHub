"""
Authentication routes for user registration, login, and logout
"""
from fastapi import APIRouter, Body, HTTPException, Request, Depends, Form, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import User, RegisterRequest, LoginRequest
from app.core.security import (
    hash_password, verify_password, get_current_user, oauth2_scheme, 
    get_user_email_from_session
)
from app.db.storage import user_database, password_storage, active_sessions, save_data_to_file
from app.core.logging import application_logger
import secrets
import time

router = APIRouter(tags=["Auth"])

@router.post("/register", status_code=201)
def register_user(
    user_data: RegisterRequest = Body(..., description="User registration information"),
    request: Request = None
):
    """Register a new user account"""
    client_ip = request.client.host if request else "unknown"
    application_logger.info(f"Registration attempt: [{user_data.email}] from IP [{client_ip}]!")
    
    # Check for existing email
    if user_data.email in user_database:
        application_logger.warning(f"Registration failed - email already exists: [{user_data.email}]!")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user record
    user_database[user_data.email] = User(
        email=user_data.email, 
        name=user_data.name
    )
    user_database[user_data.email].subscriptions = []  # Ensure subscriptions is initialized
    
    # Store hashed password
    password_storage[user_data.email] = hash_password(user_data.password)
    
    # Save changes to file
    save_data_to_file()
    
    application_logger.info(f"User registered successfully: [{user_data.email}], name: [{user_data.name}]!")
    return {"message": "Registration successful"}

@router.post("/login")
def login_user(
    credentials: LoginRequest = Body(None),
    form_data: OAuth2PasswordRequestForm = Depends(None),
    request: Request = None
):
    """Authenticate user and provide access token"""
    # Support both JSON and form data for login
    email = None
    password = None
    
    if credentials:
        email = credentials.email
        password = credentials.password
    elif form_data:
        email = form_data.username
        password = form_data.password
    else:
        # Instead of using await, use Body parameter above
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing credentials - provide either form data or JSON body"
        )
        
    client_ip = request.client.host if request else "unknown"
    application_logger.info(f"Login attempt: [{email}] from IP [{client_ip}]!")
    
    # Verify user exists
    if email not in user_database:
        application_logger.warning(f"Login failed - user not found: [{email}]!")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password
    stored_password_hash = password_storage[email]
    if not verify_password(password, stored_password_hash):
        application_logger.warning(f"Login failed - incorrect password: [{email}]!")
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # Implement single-session policy: invalidate any existing sessions
    for existing_token, session_data in list(active_sessions.items()):
        user_email = get_user_email_from_session(session_data)
        if user_email == email:
            del active_sessions[existing_token]
            application_logger.info(f"Invalidated previous session for user: [{email}]!")
    
    # Create new session token with expiration
    session_token = secrets.token_urlsafe(16)
    token_expiration = time.time() + 3600  # 1 hour from now
    
    active_sessions[session_token] = {
        "email": email,
        "expires": token_expiration
    }
    
    application_logger.info(f"Login successful: [{email}], token valid for [1 hour]!")
    
    return {
        "access_token": session_token,
        "token_type": "bearer",
        "user_email": email,
        "user_name": user_database[email].name,
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
        application_logger.info(f"User logged out: [{user_email}]!")
        return {"message": "Logout successful"}
    
    application_logger.warning(f"Logout attempted with invalid token!")
    return {"message": "Already logged out"}
