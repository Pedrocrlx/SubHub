from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Montar a pasta de ficheiros estáticos (por exemplo, a pasta 'frontend')
app.mount("/static", StaticFiles(directory="/workspaces/SubHub/frontend"), name="static")

# Rota principal: servir index.html
@app.get("/")
def read_index():
    return FileResponse("/workspaces/SubHub/frontend/index.html")
