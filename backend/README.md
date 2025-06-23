SubHub API Documentation

LIBRARIES AND DEPENDENCIES
=========================

1. FastAPI
   Description: Modern, high-performance Python web framework for building APIs
   Project Example: The API endpoints in app/api/auth.py use FastAPI's router system:
   
   from fastapi import APIRouter, Body, Depends, HTTPException
   
   router = APIRouter(tags=["Auth"])
   
   @router.post("/register", status_code=201)
   def register_user(new_user: RegisterRequest = Body(...)):
       if new_user.email in user_database:
           raise HTTPException(status_code=400, detail="User already registered")
       # rest of the implementation...

2. Pydantic
   Description: Data validation and settings management
   Project Example: The User model in app/models/user.py uses Pydantic validation:
   
   class User(BaseModel):
       email: EmailStr
       name: str
       subscriptions: List[Subscription] = []
   
       @field_validator("password")
       def validate_password(cls, password):
           # Password validation logic...

3. Argon2-cffi
   Description: Secure password hashing library
   Project Example: In app/core/security.py:
   
   from argon2 import PasswordHasher
   
   password_hasher = PasswordHasher()
   
   def hash_password(password: str) -> str:
       return password_hasher.hash(password)
   
   def verify_password(plain_password: str, hashed_password: str) -> bool:
       try:
           password_hasher.verify(hashed_password, plain_password)
           return True
       except:
           return False

4. Uvicorn
   Description: ASGI server for running FastAPI applications
   Project Example: In main.py:
   
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

5. Pytest
   Description: Testing framework for Python
   Project Example: In tests/test_auth.py:
   
   def test_user_registration():
       response = client.post("/register", json=TEST_USER)
       assert response.status_code == 201
       assert "message" in response.json()


PROJECT STRUCTURE
================
/workspaces/SubHub/
├── backend/
│   ├── src/
│   │   ├── backend/
│   │   │   ├── app/                   # Application modules
│   │   │   │   ├── api/               # API endpoints
│   │   │   │   │   ├── auth.py        # Authentication routes
│   │   │   │   │   ├── subscriptions.py # Subscription management
│   │   │   │   │   ├── analytics.py   # Analytics and search
│   │   │   │   │   └── system.py      # System information
│   │   │   │   ├── core/              # Core functionality
│   │   │   │   │   ├── security.py    # Authentication and security
│   │   │   │   │   └── logging.py     # Logging configuration
│   │   │   │   ├── db/                # Database operations
│   │   │   │   │   └── storage.py     # File-based storage
│   │   │   │   ├── models/            # Data models
│   │   │   │   │   ├── user.py        # User models
│   │   │   │   │   └── subscription.py # Subscription models
│   │   │   │   └── utils/             # Helper utilities
│   │   │   ├── main.py                # Main entry point
│   │   │   └── tests/                 # Test suite


COMMANDS TO RUN THE SERVER
=========================

1. Set Up Environment:
   cd /workspaces/SubHub/backend
   pip install fastapi uvicorn pydantic argon2-cffi pytest

2. Run Development Server:
   cd /workspaces/SubHub/backend/src/backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

3. Access API Documentation:
   "$BROWSER" http://localhost:8000/docs


COMMANDS TO RUN TESTS
====================

1. Run Complete Test Suite:
   cd /workspaces/SubHub/backend/src/backend
   python -m pytest tests/

2. Run Specific Test Files:
   cd /workspaces/SubHub/backend/src/backend
   python -m pytest tests/test_auth.py -v
   python -m pytest tests/test_subscriptions.py -v
   python -m pytest tests/test_analytics.py -v

3. Run Tests With Coverage:
   cd /workspaces/SubHub/backend/src/backend
   python -m pytest tests/ --cov=app

4. Run Original Test File:
   cd /workspaces/SubHub/backend/src/backend
   python -m pytest test_main.py -v


COMPONENT DESCRIPTIONS
====================

1. API Module (app/api/)
   - auth.py: Handles user registration, login, and logout
   - subscriptions.py: Manages user subscription CRUD operations
   - analytics.py: Provides analytics and reports about subscriptions
   - system.py: Returns system information and status

2. Core Module (app/core/)
   - security.py: Contains security functions like password hashing and token management
   - logging.py: Sets up application logging with proper file handling

3. Database Module (app/db/)
   - storage.py: Manages file-based storage of users and subscriptions

4. Models Module (app/models/)
   - user.py: Defines User and authentication-related data models
   - subscription.py: Defines Subscription data model and validation

5. Utils Module (app/utils/)
   - validation_utils.py: Contains input validation functions
   - format_utils.py: Contains data formatting utilities


API ENDPOINTS
============

1. Authentication Endpoints
   - POST /register - Register new user account
     Example: curl -X POST http://localhost:8000/register -d '{"email":"user@example.com","name":"User Name","password":"!Password123"}'
   
   - POST /login - Authenticate and get access token
     Example: curl -X POST http://localhost:8000/login -d '{"email":"user@example.com","password":"!Password123"}'
   
   - POST /logout - End current session (requires auth)
     Example: curl -X POST http://localhost:8000/logout -H "Authorization: Bearer {token}"

2. Subscription Endpoints
   - POST /subscriptions - Add new subscription
     Example: curl -X POST http://localhost:8000/subscriptions -H "Authorization: Bearer {token}" -d '{"service_name":"Netflix","monthly_price":15.99,"category":"Entertainment","starting_date":"2023-01-01"}'
   
   - GET /subscriptions - Get all subscriptions
     Example: curl -X GET http://localhost:8000/subscriptions -H "Authorization: Bearer {token}"
   
   - DELETE /subscriptions/{service_name} - Delete a subscription
     Example: curl -X DELETE http://localhost:8000/subscriptions/Netflix -H "Authorization: Bearer {token}"

3. Analytics Endpoints
   - GET /summary - Get subscription summary
     Example: curl -X GET http://localhost:8000/summary -H "Authorization: Bearer {token}"
   
   - GET /categories - Get category analysis
     Example: curl -X GET http://localhost:8000/categories -H "Authorization: Bearer {token}"
   
   - GET /search?term={query} - Search subscriptions
     Example: curl -X GET "http://localhost:8000/search?term=netflix" -H "Authorization: Bearer {token}"

4. System Endpoint
   - GET / - API information
     Example: curl -X GET http://localhost:8000/


DATA STORAGE
===========
- User data is stored in JSON format at: /workspaces/SubHub/backend/src/backend/subhub_data.json
- Test data is stored separately at: /workspaces/SubHub/backend/src/backend/test_subhub_data.json
- Logs are stored in: /workspaces/SubHub/backend/src/backend/logs/


TROUBLESHOOTING
=============

1. Import Issues
   Problem: "ImportError: cannot import name X from Y"
   Solution: Set PYTHONPATH environment variable:
   export PYTHONPATH=$PYTHONPATH:/workspaces/SubHub/backend/src

2. Authentication Errors
   Problem: 401 Unauthorized errors
   Solutions:
   - Check token format (must be "Bearer {token}")
   - Verify token hasn't expired (tokens expire after 1 hour)
   - Ensure user exists in database

3. Database Issues
   Problem: Changes not persisting between restarts
   Solution: Check file permissions on data directory
   chmod 755 /workspaces/SubHub/backend/src/backend/

4. Test Failures
   Problem: Tests failing with import errors
   Solution: Ensure main.py re-exports all needed components:
   - from app.db.storage import user_database, password_storage, active_sessions 
   - from app.core.security import verify_password, hash_password


SECURITY FEATURES
===============
1. Password Storage
   - Uses Argon2 (winner of Password Hashing Competition)
   - Example from security.py: password_hasher = PasswordHasher()

2. Password Requirements
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one number
   - At least one special character

3. Token-based Authentication
   - OAuth2 Bearer token scheme
   - 1-hour expiration
   - Single active session per user

4. Input Validation
   - All user inputs validated with Pydantic models
   - Email format verification
   - Numeric field range checking