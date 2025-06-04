import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import auth                        # Imports router module (Giulio)
from app.db import Base, engine                     # For DB table creation (Giulio)
from app.services.middleware import JWTMiddleware   # For Middleware protection (Giulio)

current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_dir, "..", "..", "frontend")
frontend_path = os.path.abspath(frontend_path)

app = FastAPI()
app.add_middleware(JWTMiddleware)

# Creates tables
Base.metadata.create_all(bind=engine)

# Montar a pasta de ficheiros estáticos (por exemplo, a pasta 'frontend')
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Rota principal: servir index.html
@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

app.include_router(auth.router)
