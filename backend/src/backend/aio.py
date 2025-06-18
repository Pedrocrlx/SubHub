# Dependencies: pip install fastapi uvicorn pydantic argon2-cffi
# Start Server: uvicorn main:app --reload

from fastapi import FastAPI, HTTPException, Depends, Query, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Dict, Optional, Any, Callable
import time
from datetime import date
import json
import os
import secrets
import argon2
import traceback
import logging

# ===== LOGGING SETUP =====

class TimestampSplitFormatter(logging.Formatter):
    """Custom formatter that splits timestamps into separate date and time columns for CSV logs"""
    
    def format(self, record):
        # Format timestamp according to specified date format
        record.asctime = self.formatTime(record, self.datefmt)
        
        # Split timestamp into date and time components
        timestamp_parts = record.asctime.split()
        if len(timestamp_parts) == 2:
            record.date_part = timestamp_parts[0]  # YYYY-MM-DD
            record.time_part = timestamp_parts[1]  # HH:MM:SS
        else:
            # Handle unexpected format with clear error markers
            record.date_part = "ERROR_DATE"
            record.time_part = "ERROR_TIME"
            print(f"ERROR: Timestamp format error: '{record.asctime}'")
            
        # Return CSV-formatted log entry
        return f'{record.date_part},{record.time_part},{record.levelname},{record.name},"{record.getMessage()}"'

def setup_logging():
    """Configure application logging with both file and console output"""
    
    # Define logs directory relative to application location
    logs_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(logs_directory):
        os.makedirs(logs_directory)
    
    # Create uniquely named log file with timestamp
    log_file_path = os.path.join(logs_directory, f"log_{int(time.time())}.log")
    
    # Write CSV header as first line of log file
    with open(log_file_path, 'w') as log_file:
        log_file.write('date,time,level,name,message\n')
    
    # Configure root logger with file and console output
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler(log_file_path, mode='a'),  # Append to log file
            logging.StreamHandler()  # Output to console
        ]
    )
    
    # Apply custom formatter to all handlers
    csv_formatter = TimestampSplitFormatter(datefmt='%Y-%m-%d %H:%M:%S')
    for log_handler in logging.getLogger().handlers:
        log_handler.setFormatter(csv_formatter)
    
    # Create application logger
    application_logger = logging.getLogger("log")
    application_logger.info(f"SubHub initiated (log file: [{log_file_path}])")
    
    return application_logger, log_file_path

application_logger, log_file_path = setup_logging()

# ===== CONFIG =====

class ApplicationSettings:
    """Central configuration settings for the SubHub application"""
    
    APP_NAME = "SubHub API"  
    VERSION = "1.0"
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_REQUIRES_UPPERCASE = True
    PASSWORD_REQUIRES_NUMBER = True
    PASSWORD_REQUIRES_SYMBOL = True
    SECRET_KEY = secrets.token_bytes(32) 
    DATA_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subhub_data.json")

app_settings = ApplicationSettings()

# ===== DATA MODELS =====

class Subscription(BaseModel):
    """Represents a user's subscription service"""
    
    service_name: str
    monthly_price: float
    category: str
    starting_date: date

    @field_validator("monthly_price")
    def validate_price(cls, price):
        """Ensure price is positive"""
        if price <= 0:
            raise ValueError("You're expected to pay for your subscriptions, not the other way around!")
        return price

    @field_validator("category")
    def format_category(cls, category):
        """Normalize category format (strip whitespace, title case)"""
        return category.strip().title()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "service_name": "Netflix",
                "monthly_price": 17.99,
                "category": "Entertainment",
                "starting_date": "2025-06-01"
            }
        }
    }

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

class SubscriptionSummary(BaseModel):
    """Summary statistics for user subscriptions"""
    
    total_monthly_cost: float
    number_of_subscriptions: int
    subscription_list: List[Subscription] 
    
# ===== DATA STORAGE =====

user_database: Dict[str, User] = {}
password_storage: Dict[str, str] = {}
active_sessions: Dict[str, Any] = {}

# ===== SECURITY =====

password_hasher = argon2.PasswordHasher()

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

# ===== FILE OPERATIONS =====

def safe_operation(operation: Callable, error_message: str, *args, **kwargs):
    """Execute an operation safely with error handling"""
    try:
        return operation(*args, **kwargs)
    except Exception as error:
        application_logger.error(f"{error_message}: {str(error)}")
        application_logger.debug(traceback.format_exc())
        return None

def save_data_to_file():
    """Save all application data to disk as JSON"""
    def perform_save():
        data_to_save = {
            "users": {email: user.model_dump() for email, user in user_database.items()},
            "passwords": password_storage
        }
        with open(app_settings.DATA_FILEPATH, "w") as data_file:
            json.dump(data_to_save, data_file, default=str, indent=2)
    
    safe_operation(perform_save, "Could not save data to file")

def load_data_from_file():
    """Load application data from disk if available"""
    if not os.path.exists(app_settings.DATA_FILEPATH):
        return
    
    def perform_load():
        with open(app_settings.DATA_FILEPATH, "r") as data_file:
            loaded_data = json.load(data_file)
            
            # Clear existing data
            user_database.clear()
            password_storage.clear()
            active_sessions.clear()
            
            # Restore user data
            for email, user_data in loaded_data.get("users", {}).items():
                # Convert date strings back to date objects
                for subscription in user_data.get("subscriptions", []):
                    if "starting_date" in subscription:
                        subscription["starting_date"] = date.fromisoformat(subscription["starting_date"])
                # Recreate user object
                user_database[email] = User(**user_data)
                
            # Restore password hashes
            password_storage.update(loaded_data.get("passwords", {}))
            
    safe_operation(perform_load, "Could not load data from file")

# ===== API SETUP =====

api_tag_descriptions = [
    {"name": "System", "description": "General information about the API"},
    {"name": "Auth", "description": "User registration and authentication"},
    {"name": "Subscriptions", "description": "Manage user subscription services"},
    {"name": "Analytics", "description": "Subscription analysis, reporting, and search"}
]

app = FastAPI(
    title=app_settings.APP_NAME, 
    version=app_settings.VERSION,
    openapi_tags=api_tag_descriptions,
    swagger_ui_parameters={
        "deepLinking": True,
        "persistAuthorization": True,
        "defaultModelsExpandDepth": 1,
        "displayRequestDuration": True
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== ERROR HANDLING =====

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exception: Exception):
    """Global exception handler to catch all unhandled errors"""
    
    error_message = f"Unhandled error: {str(exception)}"
    application_logger.error(error_message)
    
    if isinstance(exception, HTTPException):
        return await http_exception_handler(request, exception)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# ===== AUTHENTICATION =====

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(auth_token: str = Depends(oauth2_scheme)) -> User:
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

def get_user_email_from_session(session_data):
    """Extract user email from session data regardless of format"""
    return session_data["email"] if isinstance(session_data, dict) else session_data

# Load saved data when application starts
load_data_from_file()

# ===== API ENDPOINTS =====

@app.get("/", tags=["System"])
def get_api_info():
    """Return basic API information"""
    return {
        "app": app_settings.APP_NAME,
        "status": "running",
        "version": app_settings.VERSION
    }

@app.post("/register", tags=["Auth"], status_code=201)
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
    
    # Store hashed password
    password_storage[user_data.email] = hash_password(user_data.password)
    
    # Save changes to file
    save_data_to_file()
    
    application_logger.info(f"User registered successfully: {user_data.email}, name: {user_data.name}")
    return {"message": "Registration successful"}

@app.post("/login", tags=["Auth"])
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
    
    # Verify password
    stored_password_hash = password_storage[credentials.email]
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

@app.post("/logout", tags=["Auth"])
def logout_user(
    current_user: User = Depends(get_current_user), 
    auth_token: str = Depends(oauth2_scheme)
):
    """End a user session"""
    session_data = active_sessions.get(auth_token)
    
    if auth_token in active_sessions:
        if isinstance(session_data, dict) and "email" in session_data:
            user_email = session_data["email"]
        else:
            user_email = session_data
            
        del active_sessions[auth_token]
        application_logger.info(f"User logged out: {user_email}")
        return {"message": "Logout successful"}
    
    application_logger.warning(f"Logout attempted with invalid token")
    return {"message": "Already logged out"}

@app.post("/subscriptions", tags=["Subscriptions"], status_code=201)
def add_subscription(
    new_subscription: Subscription = Body(..., description="Subscription details to add"),
    current_user: User = Depends(get_current_user)
):
    """Add a new subscription for the current user"""
    application_logger.info(
        f"User {current_user.email} adding subscription: {new_subscription.service_name} "
        f"(${new_subscription.monthly_price:.2f}/month, category: {new_subscription.category})"
    )
    
    # Check for duplicate subscriptions (case-insensitive)
    if any(existing_sub.service_name.lower() == new_subscription.service_name.lower() 
           for existing_sub in current_user.subscriptions):
        application_logger.warning(
            f"User {current_user.email} attempted to add duplicate subscription: {new_subscription.service_name}"
        )
        raise HTTPException(status_code=409, detail="Subscription already exists")
    
    # Add subscription to user's list
    current_user.subscriptions.append(new_subscription)
    save_data_to_file()
    
    application_logger.info(f"User {current_user.email} successfully added subscription: {new_subscription.service_name}")
    return {"message": "Subscription added", "service": new_subscription.service_name}

@app.get("/subscriptions", tags=["Subscriptions"],
         summary="List all subscriptions",
         description="Returns all subscriptions for the current user")
def list_subscriptions(
    current_user: User = Depends(get_current_user)
):
    """Get all subscriptions for the current user"""
    application_logger.info(f"User {current_user.email} viewed their {len(current_user.subscriptions)} subscriptions")
    return current_user.subscriptions

@app.delete("/subscriptions/{service_name}", tags=["Subscriptions"])
def delete_subscription(
    service_name: str, 
    current_user: User = Depends(get_current_user)
):
    """Delete a subscription by service name"""
    # Find and remove the subscription with matching name
    for index, subscription in enumerate(current_user.subscriptions):
        if subscription.service_name == service_name:
            current_user.subscriptions.pop(index)
            application_logger.info(f"User {current_user.email} deleted subscription: {service_name}")
            save_data_to_file()
            return {"message": f"Subscription {service_name} deleted successfully"}
    
    # If we get here, no matching subscription was found
    application_logger.warning(f"User {current_user.email} attempted to delete non-existent subscription: {service_name}")
    raise HTTPException(status_code=404, detail=f"Subscription {service_name} not found for current user")

@app.get("/search", tags=["Analytics"],
         summary="Search subscriptions",
         description="Finds subscriptions matching the search term in name or category")
def search_subscriptions(
    # Change parameter name from 'search_term' to 'term' to match tests
    term: str = Query(..., description="Search term for finding subscriptions"), 
    current_user: User = Depends(get_current_user)
):
    # Convert search term to lowercase for case-insensitive matching
    normalized_search_term = term.lower()
    
    # Find subscriptions with matching name or category
    matching_subscriptions = [
        subscription for subscription in current_user.subscriptions
        if normalized_search_term in subscription.service_name.lower() or 
           normalized_search_term in subscription.category.lower()
    ]
    
    application_logger.info(
        f"User {current_user.email} searched for '{term}', found {len(matching_subscriptions)} matches"
    )
    return matching_subscriptions

@app.get("/summary", tags=["Analytics"])
def get_subscription_summary(
    current_user: User = Depends(get_current_user)
):
    """Get summary statistics for user's subscriptions"""
    # Calculate total monthly cost
    total_monthly_cost = sum(subscription.monthly_price for subscription in current_user.subscriptions)
    
    application_logger.info(
        f"User {current_user.email} viewed subscription summary: "
        f"{len(current_user.subscriptions)} subscriptions totaling ${total_monthly_cost:.2f}/month"
    )
    
    return SubscriptionSummary(
        total_monthly_cost=total_monthly_cost,
        number_of_subscriptions=len(current_user.subscriptions),
        subscription_list=current_user.subscriptions
    )

@app.get("/categories", tags=["Analytics"],
         summary="Analyze spending by category",
         description="Groups subscriptions by category with cost breakdown and percentages")
def analyze_spending_by_category(
    current_user: User = Depends(get_current_user)
):
    """Analyze user's subscription spending by category"""
    # Group subscriptions by category
    category_statistics = {}
    
    # Collect data for each category
    for subscription in current_user.subscriptions:
        category_name = subscription.category
        
        # Initialize category if first time seeing it
        if category_name not in category_statistics:
            category_statistics[category_name] = {
                "total_cost": 0, 
                "count": 0
            }
        
        # Update category statistics
        category_statistics[category_name]["total_cost"] += subscription.monthly_price
        category_statistics[category_name]["count"] += 1
    
    # Calculate overall total cost
    total_monthly_cost = sum(data["total_cost"] for data in category_statistics.values())
    
    # Add percentage breakdowns if there are any subscriptions
    if total_monthly_cost > 0:
        for category_name in category_statistics:
            category_percentage = (category_statistics[category_name]["total_cost"] / total_monthly_cost) * 100
            category_statistics[category_name]["percentage"] = round(category_percentage, 1)
    
    application_logger.info(f"User {current_user.email} viewed category analysis")
    return category_statistics


if __name__ == "__main__":
    import uvicorn
    print(f"Starting {app_settings.APP_NAME}...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)