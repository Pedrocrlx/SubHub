"""
System-wide API endpoints for SubHub

This module provides:
- Root endpoint with API information
- Health check endpoint for monitoring
- System status information
"""
from fastapi import APIRouter, status, Response
from typing import Dict, Any
from functools import lru_cache

from app.config import app_settings
from app.core.logging import application_logger

# Create router with appropriate tag
router = APIRouter(tags=["System"])

# Cache the root info to avoid recreating it on every request
@lru_cache(maxsize=1)
def get_api_info() -> Dict[str, Any]:
    """
    Create API information dictionary
    
    Returns cached API information to improve performance
    for frequently accessed root endpoint.
    """
    return {
        "name": app_settings.APP_NAME,
        "version": app_settings.VERSION,
        "status": "healthy"
    }

@router.get("/", status_code=status.HTTP_200_OK)
def get_root_info(response: Response) -> Dict[str, Any]:
    """
    Root endpoint providing basic API information
    
    This is the landing page for the API that provides general information
    about the system including version and status.
    
    Returns:
        Dictionary with API information
    """
    # Add cache headers to allow browsers to cache this response
    response.headers["Cache-Control"] = "public, max-age=60"
    
    application_logger.debug("Root endpoint accessed")
    return get_api_info()

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring
    
    This endpoint allows monitoring tools to verify the API is operational.
    Returns a simple status message indicating the service is healthy.
    
    Returns:
        Dictionary with status information
    """
    application_logger.debug("Health check performed")
    return {"status": "healthy"}