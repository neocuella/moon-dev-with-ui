"""
Database connection and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
# Default to SQLite for development (no external dependencies)
# For production, set DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./moon_dev_flows.db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create base class for models
Base = declarative_base()


def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database initialized")


def verify_connection():
    """Verify database connection"""
    try:
        with engine.connect() as conn:
            logger.info("✅ Database connection verified")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
