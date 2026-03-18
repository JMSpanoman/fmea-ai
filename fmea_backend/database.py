from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from `.env` only in non-production environments.
if os.getenv("ENVIRONMENT", "").lower() not in ("production", "prod"):
    load_dotenv()

# Get database URL from environment variable; default to local file in this package when not set
_db_dir = os.path.dirname(os.path.abspath(__file__))
_default_sqlite = f"sqlite:///{os.path.join(_db_dir, 'fmea.db')}"
DATABASE_URL = os.getenv("DATABASE_URL", _default_sqlite)

# Determine if we're using SQLite or PostgreSQL
is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
