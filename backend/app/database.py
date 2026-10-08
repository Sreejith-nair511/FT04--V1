"""
Database connection and session management
"""

import logging
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Parse database URL
if settings.database_url.startswith("sqlite:"):
    # Extract the file path
    db_path = settings.database_url.replace("sqlite:///", "").replace("sqlite://", "")
    
    # Create data directory if it doesn't exist
    data_dir = Path(db_path).parent
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create SQLite engine with check_same_thread disabled for async support
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        echo=settings.log_level == "DEBUG"
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Enable foreign keys for SQLite"""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    engine = create_engine(settings.database_url, echo=settings.log_level == "DEBUG")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


def check_db_connection() -> bool:
    """Check if database is accessible"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
