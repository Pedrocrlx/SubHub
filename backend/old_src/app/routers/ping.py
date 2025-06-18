from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import SessionLocal

router = APIRouter()

# Dependency Injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/ping-db") # Test Ping
def ping_db(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {"ok": result == 1}
    except Exception as e:
        return {"ok": False, "error": str(e)} 