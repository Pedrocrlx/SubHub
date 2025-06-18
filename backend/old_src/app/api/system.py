from fastapi import APIRouter, Request
from app.config import app_settings
from app.core.logging import application_logger
from pydantic import BaseModel

router = APIRouter(tags=["System"])

class ApiInfo(BaseModel):
    """API information response model"""
    app: str
    status: str
    version: str

@router.get(
    "/", 
    response_model=ApiInfo,
    response_description="Basic API information and status"
)
def get_api_info(request: Request = None) -> ApiInfo:
    """
    Return basic API information
    
    This endpoint provides the application name, current status,
    and version information.
    """
    client_ip = request.client.host if request else "unknown"
    application_logger.info(f"API info requested from IP [{client_ip}]!")
    
    return ApiInfo(
        app=app_settings.APP_NAME,
        status="running",
        version=app_settings.VERSION
    )