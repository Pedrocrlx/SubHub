from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db import get_db
from app.models.user import User
from app.services import user_service
from app.services.auth import SECRET_KEY, ALGORITHM
import argon2
from fastapi.security import OAuth2PasswordBearer
import secrets
import time
from fastapi import Depends, HTTPException
from app.db.storage import user_database, active_sessions

# OAuth2 scheme declaration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token: no subject")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
"""
Security functions for authentication and password management
"""

# Initialize password hasher
password_hasher = argon2.PasswordHasher()

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    """Create secure hash of a password using Argon2"""
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if a plaintext password matches its hashed version"""
    try:
        password_hasher.verify(hashed_password, plain_password)
        return True
    except:
        return False

def get_user_email_from_session(session_data):
    """Extract user email from session data regardless of format"""
    return session_data["email"] if isinstance(session_data, dict) else session_data

def get_current_user(auth_token: str = Depends(oauth2_scheme)):
    """Authenticate and return the current user based on their token"""
    
    # Check if token exists
    if auth_token not in active_sessions:
        raise HTTPException(
            status_code=401, 
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
            raise HTTPException(
                status_code=401, 
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        user_email = session_data["email"]
    else:
        # Old format token without expiration
        user_email = session_data
        
    # Verify user exists
    if user_email not in user_database:
        raise HTTPException(
            status_code=401, 
            detail="Account not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    return user_database[user_email]

def create_access_token(email: str, expiration_seconds: int = 3600):
    """Create a new access token with specified expiration time"""
    session_token = secrets.token_urlsafe(16)
    token_expiration = time.time() + expiration_seconds
    
    active_sessions[session_token] = {
        "email": email,
        "expires": token_expiration
    }
    
    return session_token, token_expiration
