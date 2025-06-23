"""
Entry point for the SubHub API with exports for test compatibility
"""

import os
frontend_path = os.getenv("FRONTEND_PATH", "frontend")
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from app.routers import auth, ping, subscription    # Imports router modules (Giulio)
from app.db import Base, engine                     # For DB table creation (Giulio)
from app.routers import auth, user                  # Imports router module (Giulio)

from app.core.security import hash_password, verify_password, create_access_token

# Re-export settings
from app.config import app_settings  # Changed: don't rename this variable

app = FastAPI()

# Creates DB tables
Base.metadata.create_all(bind=engine)

# Montar a pasta de ficheiros estáticos (por exemplo, a pasta 'frontend') -- (Giulio) Momentarily commented out due to container mounting conflicts. REMEMBER TO PUT IT BACK IN LATER
# app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Rota principal: servir index.html
@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Login/Register route: serves login.html (Giulio)
@app.get("/login", response_class=HTMLResponse)
def read_login():
    return FileResponse(os.path.join(frontend_path, "login.html"))
