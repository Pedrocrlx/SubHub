"""
System information and general API endpoints
"""
from fastapi import APIRouter
from app.config import app_settings

router = APIRouter(tags=["System"])

@router.get("/")
def get_api_info():
    """Return basic API information"""
    return {
        "app": app_settings.APP_NAME,
        "status": "running",
        "version": app_settings.VERSION
    }