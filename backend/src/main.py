"""
Entry point for the SubHub API with exports for test compatibility
"""
# Import the app
from app.main import app

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from app.routers import auth, ping, subscription    # Imports router modules (Giulio)
from app.db import Base, engine                     # For DB table creation (Giulio)
from app.routers import auth, user                  # Imports router module (Giulio)

# Re-export variables needed by tests
from app.db.storage import (
    user_database, 
    password_storage, 
    active_sessions,
    save_data_to_file,
    load_data_from_file
)
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

# Re-export security functions needed by tests
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

# Re-export settings
from app.config import app_settings  # Changed: don't rename this variable

app = FastAPI()

# Creates tables
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

app.include_router(auth.router)
app.include_router(ping.router)
app.include_router(user.router)
>>>>>>> 43432ec (fix:(User Model and CRUD): Implement user registration, login with JWT, and protected route access -- All functional)
