"""
Main FastAPI application entry point for SubHub API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi import HTTPException

from app.config import app_settings
from app.core.logging import application_logger
from app.db.storage import load_data_from_file, save_data_to_file
from app.api import auth, subscriptions, analytics, system

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager handling startup and shutdown tasks
    """
    # Startup: Load data when the app starts
    load_data_from_file()
    application_logger.info("Application startup: data loaded successfully!")
    
    yield  # This is where the app runs
    
    # Shutdown: Any cleanup code would go here
    application_logger.info("Application shutdown!")

app = FastAPI(
    title=app_settings.APP_NAME, 
    version=app_settings.VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Export functions needed by tests
# This fixes test_security.py::test_data_persistence and test_auth.py::test_token_expiration
save_data_to_file = save_data_to_file
load_data_from_file = load_data_from_file

# Include routers without the .router attribute
app.include_router(system)
app.include_router(auth) 
app.include_router(subscriptions, prefix="/subscriptions")
app.include_router(analytics)
