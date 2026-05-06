"""Pytest configuration and fixtures for Piramid-Tongue tests."""

import os
import tempfile
from pathlib import Path

import pytest

from src.db import DB
from src.core.config import Config
from src.core.pyramid_engine import PyramidState


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = DB(db_path)
        db.init_schema()
        yield db
        db.close()


@pytest.fixture
def db(temp_db):
    """Provide an initialized test database."""
    return temp_db


@pytest.fixture
def pyramid():
    """Provide a fresh PyramidState for testing."""
    return PyramidState()


@pytest.fixture
def sample_config():
    """Provide a Config with test settings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config = Config(config_dir=config_dir)
        config.update("level", "B1")
        config.update("objectives", ["fluency"])
        yield config


@pytest.fixture
def populated_db(db):
    """Provide a database with sample data."""
    # Add vocabulary
    db.insert_vocab("hello", "greeting", "Hello, world!", "A1")
    db.insert_vocab("computer", "electronic device", "I use a computer", "B1")
    
    # Add skill progress
    db.update_skill_progress("vocab", xp=150, level="A2")
    db.update_skill_progress("read", xp=50, level="A1")
    db.update_skill_progress("listen", xp=30, level="A1")
    db.update_skill_progress("write", xp=0, level="A1")
    db.update_skill_progress("speak", xp=0, level="A1")
    
    # Add sessions
    db.log_session("vocab", duration_seconds=600, self_rating=4)
    db.log_session("vocab", duration_seconds=900, self_rating=5)
    db.log_session("read", duration_seconds=1200, self_rating=3)
    db.log_session("listen", duration_seconds=1800, self_rating=3)
    
    return db
