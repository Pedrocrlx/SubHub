"""
Compatibility module that re-exports SQLAlchemy components from app.db
"""
from app.db import Base, SessionLocal, engine

__all__ = ["Base", "SessionLocal", "engine"]
