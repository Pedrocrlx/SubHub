"""
SubHub API - Main Application Module

This module initializes and configures the SubHub FastAPI application with:
- API router registration for different feature areas
- CORS middleware configuration for cross-origin access
- Global exception handling for graceful error responses
- Application startup/shutdown lifecycle management
- Swagger UI and OpenAPI documentation setup
"""
from contextlib import asynccontextmanager
import traceback
from typing import List, Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler

# Application imports
from src.app.config import app_settings
from src.app.core.logging import application_logger
from src.app.db.storage import load_data_from_file
from src.app.api import auth, subscriptions, analytics, system

# ===== LIFECYCLE MANAGEMENT =====

@asynccontextmanager
async def application_lifespan(app_instance: FastAPI):
    """
    Manage application startup and shutdown lifecycle
    
    Handles initialization tasks like loading data on startup
    and cleanup operations on shutdown.
    """
    # Startup: Load persisted data when the application starts
    data_load_success = load_data_from_file()
    if data_load_success:
        application_logger.info("Application startup: Data loaded successfully")
    else:
        application_logger.warning("Application startup: No existing data found or load failed")
    
    yield  # Application runs during this yield
    
    # Shutdown: Any cleanup code goes here
    application_logger.info("Application shutdown: Performing cleanup operations")

# ===== API DOCUMENTATION CONFIG =====

api_documentation_tags = [
    {
        "name": "System", 
        "description": "General information about the API and health monitoring"
    },
    {
        "name": "Auth", 
        "description": "User registration, authentication, and session management"
    },
    {
        "name": "Subscriptions", 
        "description": "CRUD operations for user subscription services"
    },
    {
        "name": "Analytics", 
        "description": "Subscription analysis, spending insights, and search capabilities"
    }
]

# ===== APPLICATION INITIALIZATION =====

app = FastAPI(
    title=app_settings.APP_NAME, 
    version=app_settings.VERSION,
    description="API for managing and analyzing subscription services",
    openapi_tags=api_documentation_tags,
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=application_lifespan
)

# ===== MIDDLEWARE CONFIGURATION =====

# Configure CORS to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin - more secure than "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Type"]
)

# ===== EXCEPTION HANDLING =====

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exception: Exception):
    """
    Global exception handler for capturing all unhandled errors
    
    Provides unified error handling and prevents exposing sensitive
    error details to clients while ensuring proper logging.
    """
    # Get exception details for logging
    error_type = type(exception).__name__
    error_message = str(exception)
    
    # Log detailed error information including stack trace
    application_logger.error(
        f"Unhandled {error_type}: {error_message}"
    )
    application_logger.debug(traceback.format_exc())
    
    # Handle FastAPI HTTP exceptions specially to preserve status codes
    if isinstance(exception, HTTPException):
        return await http_exception_handler(request, exception)
    
    # For all other exceptions, return a generic 500 error
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# ===== ROUTER REGISTRATION =====

# Register API routes from different modules
app.include_router(system)
app.include_router(auth)
app.include_router(subscriptions, prefix="/subscriptions")
app.include_router(analytics, prefix="/analytics")