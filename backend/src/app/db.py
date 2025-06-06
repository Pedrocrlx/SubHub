from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Read from .env or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# For SQLite -- NEEDED: Special connect args
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Creates a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#  Base class for model classes
Base = declarative_base()
