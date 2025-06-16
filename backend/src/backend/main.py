# ==========================================
# SUBHUB API - THE BACKSTREETS
# ==========================================
# REST API for tracking subscription services with user authentication.
# Allows users to register, manage their subscription services, and analyze their subscription spending.
# ==========================================
# Dependencies (install): $ pip install fastapi uvicorn pydantic email-validator argon2-cffi
# Start Server:     $ cd /workspaces/SubHub/backend/src/backend && uvicorn main:app --reload
# API Docs:    $ "$BROWSER" http://localhost:8000/docs
# ==========================================

# ===== Imports & dependencies =====

# FastAPI core are tools used to build the web app and handle requests
# > FastAPI is the main tool used to create the API (web service)
# > HTTPException is used to send custom error messages (errors like 404 or 403) to the user
# > Depends helps manage things the app needs, such as checking if a user is logged in
# > Query works with parameters in the URL (for example, '?sort=price')
# > Path defines and checks values in the URL path (values such as '/user/123')
# > Body gets and checks data sent directly in the request, like form fields or JSON
# > Request gives access to the incoming request details, such as headers or method used
from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, Request

# fastapi.middleware.cors will help web browsers talk to your API from different websites
# > CORSMiddleware will enable the backend to receive requests from the frontend
from fastapi.middleware.cors import CORSMiddleware

# fastapi.security will handle login tokens for secure API access
# > OAuth2PasswordBearer extracts the access token sent by the frontend to check who’s logged in
from fastapi.security import OAuth2PasswordBearer

# fastapi.responses controls what gets sent back to users
# > JSONResponse sends back data and status codes, like an error when something goes wrong such as codes 4xx
from fastapi.responses import JSONResponse


# fastapi.encoders helps prepare complex Python objects for JSON responses
# > jsonable_encoder converts Python objects to JSON-friendly format (like turning datetime objects into strings before sending)
from fastapi.encoders import jsonable_encoder

# fastapi.exception_handler helps manage errors in a clean way
# > http_exception_handler ensures HTTP errors like "404 Not Found" are shown clearly and consistently
from fastapi.exception_handlers import http_exception_handler

# pydantic ensures data is the right format and type
# > BaseModel creates templates for data (like a "user") and makes sure the data is correct
# > EmailStr is a special field type that checks email addresses are valid (makes sure "user@example" fails but "user@example.com" passes)
# > field_validator adds custom rules to check field values (like ensuring prices are positive or categories follow naming rules)
from pydantic import BaseModel, EmailStr, field_validator

# typing makes code easier to understand and debug
# > List, Dict, Optional, Any and Callable helps Python know what kind of data you’re working with (like List[Subscription] means a list of Subscription items)
from typing import List, Dict, Optional, Any, Callable

#  time provides time-related functions (generates unique timestamps for log files)
import time

# datetime manages calendar dates for subscriptions
# > date stores dates without time information (such as tracking when a subscription started, like "2023-06-15")
from datetime import date

# json converts python objects to text and back for storage (like saving a user subscriptions as a text file)
import json

# os manages file paths and system tasks, helping your program find the right folder to save files on any computer
import os

# secrets creates cryptographically strong random values, generating secure session tokens that can't be guessed
import secrets

# argon2 is an industry-leading password hashing algorithm turning plain text passwords into an unreadable secure hash
import argon2

# traceback will show detailed error information for debugging, printing the exact line where an error happened
import traceback

# logging records events and errors in a structured way (such as logging when users log in or when errors happen)
import logging

# ===== LOGGING SETUP =====

# Function to set up logging for the application
def setup_logging():
    # Define the logs directory path relative to where the application is installed
    logs_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

    # Creates the directory to store the logs if it doesn't exist
    if not os.path.exists(logs_directory):
        os.makedirs(logs_directory)
    
    # Create log file with UNIX timestamp in the filename 
    log_filename = os.path.join(logs_directory, f"log_{int(time.time())}.log")

    # Writes title row to the first line of the log file
    with open(log_filename, 'w') as f:
        f.write('timestamp,level,name,message\n')

    # Configures root logger
    logging.basicConfig(
        # Set the logging level to INFO to capture all INFO, WARNING, ERROR, and CRITICAL messages (ignores DEBUG)
        level=logging.INFO,
        # Formats logs with timestamp, log level, logger name, and message (separated by commas)
        format='%(created).0f,%(levelname)s,%(name)s,"%(message)s"',
        # Configures output of the logs to both a file and the console
        handlers=[
        # Mode 'a' stands for 'append', which means new logs will be added to the end of the file, without overwriting existing logs
        logging.FileHandler(log_filename, mode='a'),
        # Prints logs to the console as well to be visible live during execution
        logging.StreamHandler()
        ]
    )
    # Initialize a logger instance for the "subhub" application
    logger = logging.getLogger("subhub")
    # Logs the start of the application at INFO level
    logger.info(f"Starting SubHub API, logging to {log_filename}")
    
    # Return the logger instance and the log filename for reference
    return logger, log_filename

# Initialize logging and get the logger instance
logger, log_filename = setup_logging()

# ===== CONFIG =====
# Central configuration class to store application settings
# Having all settings in one place makes them easier to update

class Settings:
    # Simple configuration class for application settings
    APP_NAME = "SubHub API"  # Application name for documentation
    VERSION = "1.0"  # API version for documentation
    MIN_PASSWORD_LENGTH = 8  # Security requirement for user passwords
    SECRET_KEY = secrets.token_bytes(32)  # Cryptographic key used for security features
    # Store data in the same directory as the script for reliability
    DATA_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subhub_data.json")

# Create a single instance of settings to be used throughout the application
app_config = Settings()

# ===== DATA MODELS =====
# Pydantic models for data validation, serialization, and documentation
# These models define the shape of the data used in the application

class Subscription(BaseModel):
    # Represents a recurring subscription service a user pays for
    service_name: str  # Name of the service (e.g., "Netflix", "Spotify")
    monthly_price: float  # Monthly cost in currency units
    category: str  # Type of service (e.g., "Entertainment", "Productivity")
    starting_date: date  # When the subscription began

    # Validation methods remain the same
    @field_validator('monthly_price')
    def validate_price(cls, price):
        if price <= 0:
            raise ValueError('Monthly price must be positive')
        return price

    @field_validator('category')
    def format_category(cls, category):
        return category.strip().title()
    
    # Add examples for the Swagger UI
    model_config = {
        "json_schema_extra": {
            "example": {
                "service_name": "Netflix",
                "monthly_price": 15.99,
                "category": "Entertainment",
                "starting_date": "2023-06-01"
            }
        }
    }

class User(BaseModel):
    # Represents a registered user of the system
    email: EmailStr  # Email address (validated format by Pydantic)
    name: str  # User's display name
    subscriptions: List[Subscription] = []  # List of user's subscriptions, empty by default

class LoginRequest(BaseModel):
    # Data model for login request validation
    email: EmailStr  # User's email address
    password: str  # User's password (will be securely checked against stored hash)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }
    }

class RegisterRequest(BaseModel):
    # Data model for user registration validation
    email: EmailStr  # User's email address
    name: str  # User's display name
    password: str  # User's chosen password

    @field_validator('password')
    def validate_password(cls, password):
        # Basic password strength check for security
        # Prevents users from using very short, weak passwords
        if len(password) < app_config.MIN_PASSWORD_LENGTH:
            raise ValueError(f'Password must be at least {app_config.MIN_PASSWORD_LENGTH} characters')
        return password
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "new@example.com", 
                "name": "New User",
                "password": "password123"
            }
        }
    }

class SubscriptionSummary(BaseModel):
    # Data model for subscription summary statistics
    total_monthly_cost: float  # Sum of all monthly subscription costs
    number_of_subscriptions: int  # Count of active subscriptions
    subscription_list: List[Subscription]  # Full details of all subscriptions

# ===== DATA STORAGE =====
# Simple in-memory database using dictionaries
# For an MVP, this is simpler than setting up a full database
# Data is persisted to disk using JSON serialization

# Maps email -> User object
user_database: Dict[str, User] = {}

# Maps email -> hashed password
# Stored separately from user objects for better security
password_storage: Dict[str, str] = {}

# Maps token -> email (our session store)
# Tracks which authentication tokens are valid and which user they belong to
active_sessions: Dict[str, str] = {}

# ===== SECURITY =====
# Security-related functionality for user authentication

# Initialize Argon2 password hasher with default security parameters
# Argon2 is a modern password hashing algorithm, winner of the Password Hashing Competition
password_tool = argon2.PasswordHasher()

def hash_password(password: str) -> str:
    # Creates a secure one-way hash of a user password
    # Makes it impossible to recover the original password from the hash
    # The hash includes salt automatically to prevent rainbow table attacks
    return password_tool.hash(password)

def check_password(password: str, hashed: str) -> bool:
    # Securely verifies a password against a stored hash
    # Returns True if matching, False otherwise
    # Uses constant-time comparison to prevent timing attacks
    try:
        password_tool.verify(hashed, password)
        return True
    except:
        # Any exception means verification failed
        return False

# ===== FILE OPERATIONS =====
# Functions for saving and loading data to/from disk
# This provides persistence between application restarts

def safe_operation(operation: Callable, error_message: str, *args, **kwargs):
    """
    Execute an operation safely with error handling
    
    This is a higher-order function that wraps any operation with
    try-except logic to prevent crashes and provide consistent error handling.
    
    Args:
        operation: The function to execute safely
        error_message: Message to log if operation fails
        *args, **kwargs: Arguments to pass to the operation
    
    Returns:
        The result of the operation or None if it failed
    """
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        # Log the error with a descriptive message
        logger.error(f"{error_message}: {str(e)}")
        # Include full stack trace at debug level for developers
        logger.debug(traceback.format_exc())
        return None

def save_to_file():
    """
    Save all application data to disk as JSON
    
    This function preserves user data and passwords between server restarts.
    It's called whenever data is modified to ensure persistence.
    """
    def _save():
        # Prepare data structure for serialization
        data = {
            # Convert User objects to dictionaries using Pydantic's model_dump()
            "users": {email: user.model_dump() for email, user in user_database.items()},
            # Store password hashes separately for security
            "passwords": password_storage
        }
        
        # Write to file with pretty formatting (indent=2)
        # default=str handler converts dates to ISO format strings
        with open(app_config.DATA_FILEPATH, "w") as file:
            json.dump(data, file, default=str, indent=2)
    
    # Execute the save operation safely
    safe_operation(_save, "Could not save data to file")

def load_from_file():
    """
    Load application data from disk
    
    This function restores user data and passwords when the server starts.
    It's called during application initialization to restore state.
    """
    # Skip if no data file exists yet (first run)
    if not os.path.exists(app_config.DATA_FILEPATH):
        return
    
    def _load():
        # Open and parse the JSON file
        with open(app_config.DATA_FILEPATH, "r") as file:
            data = json.load(file)
            
            # Clear existing data to avoid conflicts
            user_database.clear()
            password_storage.clear()
            active_sessions.clear()
            
            # Process user data
            for email, user_data in data.get("users", {}).items():
                # Handle date conversion for subscriptions
                # JSON stores dates as strings, so convert back to date objects
                for sub in user_data.get("subscriptions", []):
                    if "starting_date" in sub:
                        sub["starting_date"] = date.fromisoformat(sub["starting_date"])
                
                # Create User object and store in our database
                user_database[email] = User(**user_data)
            
            # Restore password hashes
            password_storage.update(data.get("passwords", {}))
    
    # Execute the load operation safely
    safe_operation(_load, "Could not load data from file")

# ===== API SETUP =====
# FastAPI application configuration and setup

# Define tags for documentation organization
# These tags are used to group endpoints in the Swagger UI documentation
tags_metadata = [
    {
        "name": "System",
        "description": "Basic API information and status endpoints",
    },
    {
        "name": "Auth",
        "description": "User registration and authentication",
    },
    {
        "name": "Subscriptions",
        "description": "Manage user subscription services",
    },
    {
        "name": "Analytics",
        "description": "Subscription analysis, reporting, and search",
    }
]

# Create FastAPI application instance with metadata for documentation
app = FastAPI(
    title=app_config.APP_NAME, 
    version=app_config.VERSION,
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        "deepLinking": True,
        "persistAuthorization": True,
        "defaultModelsExpandDepth": 1,
        "displayRequestDuration": True
    }
)

# Enable web browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== ERROR HANDLING =====

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for catching all unhandled errors"""
    error_msg = f"Unhandled error: {str(exc)}"
    logger.error(error_msg)
    logger.debug(traceback.format_exc())
    
    if isinstance(exc, HTTPException):
        return await http_exception_handler(request, exc)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# ===== AUTHENTICATION =====

# Authentication token scheme
token_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Authentication dependency
def get_current_user(token: str = Depends(token_scheme)) -> User:
    """
    Authenticate and return the current user based on their token.
    
    This function serves as a dependency for protected endpoints,
    ensuring that only authenticated users can access them.
    
    Automatically extracts the token from the Authorization header.
    Also checks if the token has expired.
    """
    # Check if token exists in active sessions
    if token not in active_sessions:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user session data
    session_data = active_sessions[token]
    
    # Check for token expiration if using the new format
    if isinstance(session_data, dict) and "expires" in session_data:
        if time.time() > session_data["expires"]:
            # Token has expired, remove it
            del active_sessions[token]
            raise HTTPException(
                status_code=401, 
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        user_email = session_data["email"]
    else:
        # Handle old format for backward compatibility
        user_email = session_data
    
    # Check if user still exists
    if user_email not in user_database:
        raise HTTPException(
            status_code=401, 
            detail="User account not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Return authenticated user
    return user_database[user_email]

# Load data at startup
load_from_file()

# ===== API ENDPOINTS =====

# --- System Endpoints ---
@app.get("/", tags=["System"])
def home():
    # Welcome page - no authentication required
    return {
        "app": app_config.APP_NAME,
        "status": "running",
        "version": app_config.VERSION
    }

# --- User Authentication Endpoints ---
@app.post("/register", tags=["Auth"], status_code=201)
def register_user(
    user_data: RegisterRequest = Body(..., description="User registration information"),
    request: Request = None
):
    # Create a new user account - no authentication required
    
    # Log registration attempt with IP address
    client_ip = request.client.host if request else "unknown"
    logger.info(f"Registration attempt: {user_data.email} from IP {client_ip}")
    
    # Check if email already exists
    if user_data.email in user_database:
        logger.warning(f"Registration failed - email already exists: {user_data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user without storing password in user object
    user_database[user_data.email] = User(
        email=user_data.email, 
        name=user_data.name
    )
    
    # Store password hash separately
    password_storage[user_data.email] = hash_password(user_data.password)
    
    # Save to file
    save_to_file()
    
    # Log successful registration
    logger.info(f"User registered successfully: {user_data.email}, name: {user_data.name}")
    
    return {"message": "Registration successful"}

@app.post("/login", tags=["Auth"])
def login_user(
    credentials: LoginRequest = Body(..., description="User login credentials"),
    request: Request = None
):
    # Log in and get access token - no authentication required
    client_ip = request.client.host if request else "unknown"
    logger.info(f"Login attempt: {credentials.email} from IP {client_ip}")
    
    # Check if user exists
    if credentials.email not in user_database:
        logger.warning(f"Login failed - user not found: {credentials.email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check password
    stored_password = password_storage[credentials.email]
    if not check_password(credentials.password, stored_password):
        logger.warning(f"Login failed - incorrect password: {credentials.email}")
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # Invalidate any existing sessions for this user
    for existing_token, session_data in list(active_sessions.items()):
        user_email = session_data["email"] if isinstance(session_data, dict) else session_data
        if user_email == credentials.email:
            del active_sessions[existing_token]
            logger.info(f"Invalidated previous session for user: {credentials.email}")
    
    # Create session token with expiration
    session_token = secrets.token_urlsafe(16)
    expiration_time = time.time() + 3600  # 1 hour from now
    active_sessions[session_token] = {
        "email": credentials.email,
        "expires": expiration_time
    }
    
    logger.info(f"Login successful: {credentials.email}, token valid for 1 hour")
    
    return {
        "access_token": session_token,  # Standard OAuth2 response format
        "token_type": "bearer",
        "user_email": credentials.email,
        "user_name": user_database[credentials.email].name,
        "expires": expiration_time
    }

@app.post("/logout", tags=["Auth"])
def logout_user(
    current_user: User = Depends(get_current_user), 
    token: str = Depends(token_scheme)
):
    # Log out (requires authentication)
    session_data = active_sessions.get(token)
    
    if token in active_sessions:
        # Get email from either format of session data
        if isinstance(session_data, dict) and "email" in session_data:
            user_email = session_data["email"]
        else:
            user_email = session_data
            
        del active_sessions[token]
        logger.info(f"User logged out: {user_email}")
        return {"message": "Logout successful"}
    
    logger.warning(f"Logout attempted with invalid token")
    return {"message": "Already logged out"}

# --- Subscription Management Endpoints ---
@app.post("/subscriptions", tags=["Subscriptions"], status_code=201)
def add_subscription(
    new_subscription: Subscription = Body(..., description="Subscription details to add"),
    current_user: User = Depends(get_current_user)
):
    # Add a new subscription for the user (requires authentication)
    logger.info(f"User {current_user.email} adding subscription: {new_subscription.service_name} " +
                f"(${new_subscription.monthly_price:.2f}/month, category: {new_subscription.category})")
    
    # Check for duplicates - optimized version
    if any(sub.service_name.lower() == new_subscription.service_name.lower() for sub in current_user.subscriptions):
        logger.warning(f"User {current_user.email} attempted to add duplicate subscription: {new_subscription.service_name}")
        raise HTTPException(status_code=409, detail="Subscription already exists")
    
    # Add subscription
    current_user.subscriptions.append(new_subscription)
    save_to_file()
    
    logger.info(f"User {current_user.email} successfully added subscription: {new_subscription.service_name}")
    return {"message": "Subscription added", "service": new_subscription.service_name}

@app.get("/subscriptions", tags=["Subscriptions"],
         summary="List all subscriptions",
         description="Returns all subscriptions for the current user")
def list_subscriptions(
    current_user: User = Depends(get_current_user)
):
    # Get all user's subscriptions (requires authentication)
    logger.info(f"User {current_user.email} viewed their {len(current_user.subscriptions)} subscriptions")
    return current_user.subscriptions

@app.delete("/subscriptions/{service_name}", tags=["Subscriptions"])
def remove_subscription(
    service_name: str = Path(..., description="Name of subscription to delete"), 
    current_user: User = Depends(get_current_user)
):
    # Delete a subscription (requires authentication)
    logger.info(f"User {current_user.email} attempting to delete subscription: {service_name}")
    
    initial_count = len(current_user.subscriptions)
    
    # Remove matching subscription
    current_user.subscriptions = [
        sub for sub in current_user.subscriptions 
        if sub.service_name != service_name
    ]
    
    # Check if anything was removed
    if len(current_user.subscriptions) == initial_count:
        logger.warning(f"User {current_user.email} tried to delete non-existent subscription: {service_name}")
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    save_to_file()
    logger.info(f"User {current_user.email} successfully deleted subscription: {service_name}")
    return {"message": f"Removed subscription: {service_name}"}

# --- Analytics and Reporting Endpoints ---
@app.get("/search", tags=["Analytics"],
         summary="Search subscriptions",
         description="Finds subscriptions matching the search term in name or category")
def search(
    term: str = Query(..., description="Search term for finding subscriptions"), 
    current_user: User = Depends(get_current_user)
):
    # Search subscriptions by name or category (requires authentication)
    search_term = term.lower()
    
    matching_subscriptions = [
        sub for sub in current_user.subscriptions
        if search_term in sub.service_name.lower() or search_term in sub.category.lower()
    ]
    
    return matching_subscriptions

@app.get("/summary", tags=["Analytics"])
def get_summary(
    current_user: User = Depends(get_current_user)
):
    # Get subscription overview (requires authentication)
    total_cost = sum(sub.monthly_price for sub in current_user.subscriptions)
    
    logger.info(f"User {current_user.email} viewed subscription summary: " +
                f"{len(current_user.subscriptions)} subscriptions totaling ${total_cost:.2f}/month")
    
    return SubscriptionSummary(
        total_monthly_cost=total_cost,
        number_of_subscriptions=len(current_user.subscriptions),
        subscription_list=current_user.subscriptions
    )

@app.get("/categories", tags=["Analytics"],
         summary="Analyze spending by category",
         description="Groups subscriptions by category with cost breakdown and percentages")
def analyze_categories(
    current_user: User = Depends(get_current_user)
):
    # Group subscriptions by category (requires authentication)
    category_data = {}
    
    # Calculate totals for each category
    for sub in current_user.subscriptions:
        category = sub.category
        if category not in category_data:
            category_data[category] = {"total_cost": 0, "count": 0}
        
        category_data[category]["total_cost"] += sub.monthly_price
        category_data[category]["count"] += 1
    
    # Calculate percentage for each category
    total_cost = sum(data["total_cost"] for data in category_data.values())
    if total_cost > 0:
        for category in category_data:
            percentage = (category_data[category]["total_cost"] / total_cost) * 100
            category_data[category]["percentage"] = round(percentage, 1)
    
    return category_data

# Start server if run directly
if __name__ == "__main__":
    import uvicorn
    print(f"Starting {app_config.APP_NAME}...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)