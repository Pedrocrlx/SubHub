from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.routers import auth        # Imports router module (Giulio)
from backend.app.db import Base, engine     # For DB table creation (Giulio)

app = FastAPI()

# Creates tables
Base.metadata.create_all(bind=engine)

# Montar a pasta de ficheiros estáticos (por exemplo, a pasta 'frontend')
app.mount("/static", StaticFiles(directory="/workspaces/SubHub/frontend"), name="static")

# Rota principal: servir index.html
@app.get("/")
def read_index():
    return FileResponse("/workspaces/SubHub/frontend/index.html")

app.include_router(auth.router)
