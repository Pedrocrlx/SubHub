from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi import HTTPException
from app.config import app_settings
from app.core.logging import application_logger
from app.db.storage import load_data_from_file
from app.api import auth, subscriptions, analytics, system

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load data when the app starts
    load_data_from_file()
    application_logger.info("Application startup: data loaded successfully")
    
    yield  # This is where the app runs
    
    # Shutdown: Any cleanup code would go here
    application_logger.info("Application shutdown")

# API documentation
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
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=lifespan  # Include the lifespan manager here
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handler
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

# Include routers
app.include_router(system)
app.include_router(auth)
app.include_router(subscriptions, prefix="/subscriptions")
app.include_router(analytics)