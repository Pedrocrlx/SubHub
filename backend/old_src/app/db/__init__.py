"""
Database initialization and configuration.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Read from .env or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# For SQLite -- NEEDED: Special connect args
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Creates a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for model classes
Base = declarative_base()

# Define database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Re-export storage functions to maintain backward compatibility
from app.db.storage import load_data_from_file, save_data_to_file

__all__ = ["Base", "engine", "SessionLocal", "get_db", "load_data_from_file", "save_data_to_file"]
