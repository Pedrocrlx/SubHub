# SubHub - Subscription Management Backend

SubHub is a subscription management application with a FastAPI backend allowing users to register, login, and track their subscription services.

## Project Overview

SubHub helps users:
- Track all their subscription services in one place.
- Analyze monthly spending by subscription and category.
- Search and filter their subscription data.

## Libraries and Dependencies

### Web Framework
- **FastAPI**: Modern web framework for building APIs with Python based on standard type hints

### Authentication & Security
- **SHA-256**: Used for password hashing in the MVP (see code comments for production recommendations)
- **FastAPI Security**: OAuth2 with Bearer tokens for endpoint protection and user authentication

### Data Management
- **Pydantic v2**: Data validation and settings management
- **JSON**: Lightweight data storage for persistent storage of user and subscription data

### Development & Testing
- **Pytest**: Testing framework for unit and integration tests
- **TestClient**: FastAPI test client for API endpoint testing

## Installation

Install dependencies with poetry:

```
poetry install
```

## Running the Application

### Start FastAPI Server

From the src directory:

```
uvicorn src.app.main:app --reload
```

For production:

```
uvicorn src.app.main:app
```

### Run Tests

Run all tests:

```
cd /workspaces/SubHub/backend/
```
```bash
poetry run pytest
```

Run specific test files:

```
python -m pytest tests/test_auth.py
python -m pytest tests/test_subscriptions.py
python -m pytest tests/test_analytics.py
python -m pytest tests/test_security.py
python -m pytest tests/test_system.py
python -m pytest tests/test_validation.py
```

Run tests with verbose output:

```
python -m pytest -v
```

Run tests with coverage report:

```
python -m pytest --cov=app tests/
```

### Generate Demo Data

The project includes a script to generate demo users and random subscriptions for testing and demonstration purposes.

First, ensure the scripts directory exists:

```
mkdir -p /workspaces/SubHub/backend/src/scripts
```

The demo data generator script creates:
- 6 demo users with different profiles
- 3-8 random subscriptions per user
- Various subscription categories (Entertainment, Music, Gaming, etc.)
- Random starting dates and prices within realistic ranges

To run the script:

```
cd /workspaces/SubHub/backend/src
poetry run python scripts/generate_demo_data.py
```

To clear existing data before generating new demo users:

```
poetry run python scripts/generate_demo_data.py --clear
```

After running the script, login credentials for all demo users will be displayed, making it easy to test the application with pre-populated data.

## API Endpoints

### Authentication
- **POST /register**: Register a new user.
- **POST /login**: Login and get access token.
- **POST /logout**: Invalidate current session.

### Subscriptions
- **GET /subscriptions**: List all user subscriptions.
- **POST /subscriptions**: Add a new subscription.
- **PUT /subscriptions/{service_name}**: Update a subscription.
- **DELETE /subscriptions/{service_name}**: Delete a subscription.

### Analytics
- **GET /analytics/summary**: Get subscription spending summary.
- **GET /analytics/categories**: Get spending breakdown by category.

### System
- **GET /**: Root endpoint with API information.
- **GET /health**: Health check endpoint for monitoring.

## Configuration

The application uses settings defined in `app/config.py`:

- **APP_NAME**: SubHub
- **VERSION**: 1.0
- **MIN_PASSWORD_LENGTH**: Minimum password length requirement (8 characters).
- **PASSWORD_REQUIRES_UPPERCASE**: At least one capitalised letter.
- **PASSWORD_REQUIRES_NUMBER**: At least one number.
- **PASSWORD_REQUIRES_SYMBOL**: At least one symbol.
- **DATA_FILEPATH**: TBD.

## Project Structure

```
/workspaces/SubHub/backend/src/
├── app/                       # Main application package
│   ├── api/                   # API endpoints
│   │   ├── analytics.py       # Subscription analysis endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── subscriptions.py   # Subscription CRUD operations
│   │   └── system.py          # System/health endpoints
│   ├── config.py              # Application configuration
│   ├── core/                  # Core functionality
│   │   ├── logging.py         # Logging configuration
│   │   └── security.py        # Authentication and security
│   ├── db/                    # Database functionality
│   │   └── storage.py         # Data persistence
│   ├── main.py                # FastAPI application setup
│   ├── models/                # Data models
│   │   ├── subscription.py    # Subscription models
│   │   └── user.py            # User models
│   └── utils/                 # Utility functions
│       ├── format_utils.py    # Formatting helpers
│       └── validation_utils.py# Input validation
├── scripts/                   # Utility scripts
│   └── generate_demo_data.py  # Demo data generator
└── tests/                     # Test suite
    ├── conftest.py            # Test fixtures
    ├── test_analytics.py      # Analytics tests
    ├── test_auth.py           # Authentication tests
    ├── test_security.py       # Security tests
    ├── test_subscriptions.py  # Subscription tests
    ├── test_system.py         # System tests
    └── test_validation.py     # Validation tests
```

## Notes

- For MVP, password hashing uses SHA-256 for simplicity. For production, upgrade to Argon2 or bcrypt.
- Data is stored in a JSON file for easy development and testing. For production, consider using a database.
- The codebase is modular and ready for extension or migration to more robust infrastructure as needed.