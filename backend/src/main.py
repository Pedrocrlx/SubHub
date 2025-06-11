import os

from fastapi import FastAPI
#from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

<<<<<<< HEAD
from app.routers import auth, ping                  # Imports router modules (Giulio)
=======
>>>>>>> a859ae9 (feat:(User Model and CRUD): Start adding Files)
from app.db import Base, engine                     # For DB table creation (Giulio)
from app.routers import auth, user                  # Imports router module (Giulio)
from app.services.middleware import JWTMiddleware   # For Middleware protection (Giulio)

current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_dir, "..", "..", "frontend")
frontend_path = os.path.abspath(frontend_path)

app = FastAPI()
app.add_middleware(JWTMiddleware)

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
