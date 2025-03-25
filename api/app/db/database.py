import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine with PostgreSQL configuration
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Test connections before using them
    pool_size=10,        # Maximum number of connections to keep in the pool
    max_overflow=20,     # Maximum number of connections to create beyond pool_size
    pool_recycle=3600,   # Recycle connections after one hour
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Dependency to get a database session
def get_db():
    """
    Yield a database session for dependency injection in FastAPI routes.
    Ensures proper cleanup of session after request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 