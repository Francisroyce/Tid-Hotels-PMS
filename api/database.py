# -*- coding: utf-8 -*-
"""
Database Configuration for Tide Hotels PMS
Provides SQLAlchemy setup with SQLite database
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# Database file path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'tide_hotels.db')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Create a configured session class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create a scoped session for thread safety
db_session = scoped_session(SessionLocal)

# Create a base class for declarative models
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Initialize the database, creating all tables"""
    import models
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DATABASE_PATH}")


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """Drop all tables and recreate them (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset completed")