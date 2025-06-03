from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date

app = FastAPI()

# Data models
class Subscription(BaseModel):
    service_name: str
    monthly_price: float
    category: str
    starting_date: date

class User(BaseModel):
    email: EmailStr
    name: str
    subscriptions: Optional[List[Subscription]] = []

# Montar a pasta de ficheiros estáticos (por exemplo, a pasta 'frontend')
app.mount("/static", StaticFiles(directory="/workspaces/SubHub/frontend"), name="static")

# Rota principal: servir index.html
@app.get("/")
def read_index():
    return FileResponse("/workspaces/SubHub/frontend/index.html")

