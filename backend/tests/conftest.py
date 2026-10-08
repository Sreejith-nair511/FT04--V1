"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import Settings


@pytest.fixture
def temp_db():
    """Create temporary SQLite database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    engine = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    engine.dispose()  # Close all connections
    try:
        Path(path).unlink()
    except (PermissionError, FileNotFoundError):
        pass  # Ignore cleanup errors on Windows


@pytest.fixture
def temp_storage(tmp_path):
    """Create temporary storage directory"""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    (storage_dir / "uploads").mkdir()
    (storage_dir / "frames").mkdir()
    (storage_dir / "reports").mkdir()
    return storage_dir


@pytest.fixture
def sample_image_bytes():
    """Create minimal valid PNG bytes for testing"""
    # Minimal 1x1 PNG
    return bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
        0x42, 0x60, 0x82
    ])


@pytest.fixture
def sample_finding():
    """Sample dark pattern finding"""
    return {
        "category": "subscription_trap",
        "title": "Subscription Trap",
        "severity": "high",
        "confidence": 94,
        "evidence_text": "Free trial — ₹499/month after 7 days",
        "why_problematic": "Hidden recurring billing",
        "user_impact": "Users charged unexpectedly",
        "recommended_fix": "Make terms clear",
        "evidence": {
            "x": 0.18,
            "y": 0.57,
            "width": 0.64,
            "height": 0.14
        }
    }
