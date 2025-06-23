from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler

# Application imports
from src.app.config import app_settings
from src.app.core.logging import application_logger
from src.app.db.storage import load_data_from_file
from src.app.api import auth, subscriptions, analytics, system

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_data_from_file()
    application_logger.info("Application startup: data loaded successfully")
    yield
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
    lifespan=lifespan,
    openapi_tags=api_tag_descriptions
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exception: Exception):
    error_message = f"Unhandled error: {str(exception)}"
    application_logger.error(error_message)

    if isinstance(exception, HTTPException):
        return await http_exception_handler(request, exception)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include routers AFTER middleware
app.include_router(system)
app.include_router(auth)
app.include_router(subscriptions, prefix="/subscriptions")
app.include_router(analytics)
