# ==========================================
# SETUP INSTRUCTIONS
# ==========================================
# Run this command to install all required dependencies:
#
# $ pip install fastapi uvicorn pydantic email-validator passlib[bcrypt] python-multipart
#
# Then run the application with:
# $ uvicorn main:app --reload
#
# Access API documentation at: http://localhost:8000/docs
# ==========================================

# ==========================================
# IMPORTS AND DEPENDENCIES
# ==========================================
# Core FastAPI imports for building our API
from fastapi import FastAPI, HTTPException, Depends, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

# Pydantic for data validation and modeling
from pydantic import BaseModel, EmailStr, Field, validator

# Standard library imports
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
import json
import os

# Security libraries
from passlib.context import CryptContext  # For password hashing

# ==========================================
# APP INITIALIZATION
# ==========================================
# Create the main FastAPI application with metadata
app = FastAPI(
    title="SubHub API",
    description="A subscription management API to track and analyze subscription services",
    version="1.0.0"
)

# Enable CORS to allow web browsers to call this API from different domains
# This lets our frontend (which runs on a different port) talk to our backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any website (for development) - change this to specific sites in production (like 127.0.0.1 or 192.168.x.x))
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# DATA MODELS
# ==========================================
# Each class represents data structures used in the application

class Subscription(BaseModel):
    # A subscription service the user pays for
    service_name: str = Field(..., description="Name of the subscription service (e.g., Netflix)")
    monthly_price: float = Field(..., description="Monthly cost of the subscription")
    category: str = Field(..., description="Category the subscription belongs to")
    starting_date: date = Field(..., description="Date when the subscription started")
    
    @validator('monthly_price')
    def price_must_be_positive(cls, v):
        # Make sure price makes sense (greater than zero)
        if v <= 0:
            raise ValueError('Monthly price must be positive')
        return v
    
    @validator('category')
    def normalize_category(cls, v):
        # Make categories consistent by capitalizing first letter
        # This helps when grouping by category later
        return v.strip().title()

class User(BaseModel):
    # A user of the subscription management system
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    subscriptions: List[Subscription] = Field(default=[], description="User's subscriptions")

class UserLogin(BaseModel):
    # Data needed when a user logs in
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    # Data needed when registering a new user
    email: EmailStr
    name: str
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        # Make sure passwords are reasonably secure
        if len(v) < 6:
            raise ValueError('Password should be at least 6 characters')
        return v

class Summary(BaseModel):
    # Summary of a user's subscription data
    total_cost: float
    subscription_count: int
    subscriptions: List[Subscription]

# ==========================================
# SECURITY SETUP
# ==========================================
# Configure password hashing and basic authentication
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ==========================================
# IN-MEMORY DATABASE
# ==========================================
# Simple storage for our data (would use a real database in production)
users_db: Dict[str, User] = {}
user_passwords: Dict[str, str] = {}
active_tokens: Dict[str, str] = {}  # Maps token to email

# Data file path - store in the current directory
DATA_FILE = "subhub_data.json"

# ==========================================
# AUTHENTICATION FUNCTIONS
# ==========================================
# Functions for user authentication and security

def get_password_hash(password: str) -> str:
    # Create secure password hash - never store raw passwords!
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Check if a password matches its hash
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(email: str) -> User:
    # Get a user by email or raise exception if not found
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[email]

def get_user_by_token(token: str = Depends(oauth2_scheme)) -> User:
    # Get user from authentication token
    # This function will be called automatically by FastAPI
    email = active_tokens.get(token)
    if not email or email not in users_db:
        raise HTTPException(
            status_code=401, 
            detail="Invalid token or session expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return users_db[email]

def clear_old_tokens():
    # Simple token cleanup to prevent memory buildup
    # This is a basic version - a real app would use token expiration
    token_limit = 100
    if len(active_tokens) > token_limit:
        # Just keep the 50 most recent tokens if we have too many
        tokens_to_keep = list(active_tokens.keys())[-50:]
        new_tokens = {t: active_tokens[t] for t in tokens_to_keep}
        active_tokens.clear()
        active_tokens.update(new_tokens)

# ==========================================
# DATA PERSISTENCE
# ==========================================
# Save and load data for persistence between restarts

def save_data():
    # Save all user data to file
    # This function saves our data so it's not lost when the server restarts
    try:
        data = {
            "users": {email: user.dict() for email, user in users_db.items()},
            "passwords": user_passwords
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, default=str)
            print(f"Saved data for {len(users_db)} users")
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    # Load user data from file if available
    # This function loads our data when the server starts
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                
                # Process users
                for email, user_data in data["users"].items():
                    # Convert date strings back to date objects
                    for sub in user_data.get("subscriptions", []):
                        if "starting_date" in sub:
                            sub["starting_date"] = date.fromisoformat(sub["starting_date"])
                    
                    # Create user object
                    users_db[email] = User(**user_data)
                
                # Load passwords
                user_passwords.update(data.get("passwords", {}))
                
            print(f"Loaded data for {len(users_db)} users")
        except Exception as e:
            print(f"Error loading data: {e}")

# ==========================================
# APPLICATION LIFECYCLE
# ==========================================
# Startup and shutdown events

@app.on_event("startup")
def startup_event():
    # Load data when the app starts
    print("Starting SubHub API service...")
    load_data()

@app.on_event("shutdown")
def shutdown_event():
    # Save data when the app stops
    print("Shutting down SubHub API service...")
    save_data()

# ==========================================
# API ENDPOINTS
# ==========================================

# --- General endpoints ---
@app.get("/", tags=["General"])
def read_root():
    # Root endpoint - this is what you see when you visit the base URL
    return {
        "message": "Welcome to SubHub API", 
        "status": "online",
        "endpoints_available": {
            "Authentication": ["/register", "/login"],
            "Subscriptions": ["/subscriptions"],
            "Analysis": ["/summary", "/categories"]
        }
    }

# --- Authentication endpoints ---
@app.post("/register", tags=["Authentication"], status_code=201)
def register_user(user_data: UserRegister):
    # Register a new user
    # Check if this email is already used
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    new_user = User(email=user_data.email, name=user_data.name)
    users_db[user_data.email] = new_user
    
    # Hash and store password
    user_passwords[user_data.email] = get_password_hash(user_data.password)
    
    # Save the changes so we don't lose them if server crashes
    save_data()
    
    return {"message": "User registered successfully", "user_email": user_data.email}

@app.post("/login", tags=["Authentication"])
def login(user_data: UserLogin):
    # Log in and get token
    # Check if user exists
    if user_data.email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password
    stored_hash = user_passwords.get(user_data.email, "")
    if not verify_password(user_data.password, stored_hash):
        raise HTTPException(status_code=401, detail="Wrong password")
    
    # Clean up old tokens for this user (prevent buildup)
    for old_token, email in list(active_tokens.items()):
        if email == user_data.email:
            active_tokens.pop(old_token)
    
    # Create simple token
    token = f"token_{user_data.email}_{datetime.now().timestamp()}"
    active_tokens[token] = user_data.email
    
    # Clean up old tokens if we have too many
    clear_old_tokens()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": users_db[user_data.email]
    }

# --- Subscription management endpoints ---
@app.post("/subscriptions", tags=["Subscriptions"], status_code=201)
def add_subscription(subscription: Subscription, current_user: User = Depends(get_user_by_token)):
    # Add a subscription for the logged-in user
    # This will automatically get the user from their auth token
    current_user.subscriptions.append(subscription)
    
    # Save changes to prevent data loss
    save_data()
    
    return {
        "message": "Subscription added successfully",
        "service": subscription.service_name,
        "monthly_cost": subscription.monthly_price
    }

@app.get("/subscriptions", tags=["Subscriptions"], response_model=List[Subscription])
def get_subscriptions(current_user: User = Depends(get_user_by_token)):
    # Get all subscriptions for the logged-in user
    return current_user.subscriptions

@app.delete("/subscriptions/{service_name}", tags=["Subscriptions"])
def delete_subscription(
    service_name: str = Path(..., description="Name of subscription to delete"),
    current_user: User = Depends(get_user_by_token)
):
    # Delete a subscription from the logged-in user's account
    # First, remember how many subscriptions we have
    original_count = len(current_user.subscriptions)
    
    # Remove the subscription with matching name
    current_user.subscriptions = [s for s in current_user.subscriptions if s.service_name != service_name]
    
    # Check if we actually deleted anything
    if len(current_user.subscriptions) == original_count:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Save changes to prevent data loss
    save_data()
    
    return {"message": f"Subscription to {service_name} deleted successfully"}

# --- Analysis endpoints ---
@app.get("/summary", tags=["Analysis"], response_model=Summary)
def get_summary(current_user: User = Depends(get_user_by_token)):
    # Get a summary of all subscriptions for the logged-in user
    # Calculate the total monthly cost
    total_cost = sum(sub.monthly_price for sub in current_user.subscriptions)
    
    return Summary(
        total_cost=total_cost,
        subscription_count=len(current_user.subscriptions),
        subscriptions=current_user.subscriptions
    )

@app.get("/categories", tags=["Analysis"])
def get_categories(current_user: User = Depends(get_user_by_token)):
    # Get spending breakdown by category
    # This shows how much you spend in each category (like Entertainment, Utilities, etc.)
    categories = {}
    
    for sub in current_user.subscriptions:
        # If we haven't seen this category before, create an entry for it
        if sub.category not in categories:
            categories[sub.category] = {"total": 0.0, "count": 0}
        
        # Add this subscription's cost to the category total
        categories[sub.category]["total"] += sub.monthly_price
        categories[sub.category]["count"] += 1
    
    # Add percentage of total spending for each category
    total_spending = sum(cat["total"] for cat in categories.values())
    if total_spending > 0:
        for cat in categories:
            categories[cat]["percentage"] = round(
                (categories[cat]["total"] / total_spending) * 100, 1
            )
    
    return categories

# --- Added feature: Search subscriptions ---
@app.get("/search", tags=["Subscriptions"])
def search_subscriptions(
    query: str = Query(..., description="Search term for finding subscriptions"),
    current_user: User = Depends(get_user_by_token)
):
    # Search for subscriptions by name or category
    # This lets users find subscriptions by typing part of the name or category
    query = query.lower()
    results = []
    
    for sub in current_user.subscriptions:
        if query in sub.service_name.lower() or query in sub.category.lower():
            results.append(sub)
    
    return results

# ==========================================
# APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    # This code runs when you start the app directly
    import uvicorn
    print("Starting SubHub API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # The reload=True option makes development easier by auto-reloading when code changes