import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from app.api import auth, subscriptions, analytics, system  # Updated import paths
from app.db import Base, engine, load_data_from_file, save_data_to_file
from app.core.logging import application_logger

# Define file paths
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_dir, "..", "..", "frontend")
frontend_path = os.path.abspath(frontend_path)

# Lifespan context for application startup/shutdown tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load data on startup
    application_logger.info(f"Application starting up - loading data...")
    load_data_from_file()
    
    yield
    
    # Save data on shutdown
    application_logger.info(f"Application shutting down - saving data...")
    save_data_to_file(force=True)

# Create FastAPI application
app = FastAPI(
    title="SubHub API",
    description="Subscription management and analytics API",
    version="1.0.0",
    lifespan=lifespan
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Mount static files directory
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Main route: serve index.html
@app.get("/")
def read_index():
    application_logger.info(f"Serving index page!")
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Login/Register route: serves login.html
@app.get("/login", response_class=HTMLResponse)
def read_login():
    application_logger.info(f"Serving login page!")
    return FileResponse(os.path.join(frontend_path, "login.html"))

# Include all API routers
app.include_router(auth.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api/subscriptions")
app.include_router(analytics.router, prefix="/api/analytics")
app.include_router(system.router, prefix="/api")

# If you still need the ping router
# from app.routers import ping
# app.include_router(ping.router)
