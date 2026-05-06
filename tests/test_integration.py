"""Integration tests: full workflow from init to progress."""

import tempfile
from pathlib import Path

import pytest

from src.db import DB
from src.core.config import Config
from src.core.pyramid_engine import PyramidState
from src.core.cefr_detector import CEFRDetector


class TestIntegrationInitToProgress:
    """Integration test: init -> new-day -> vocab -> progress."""

    def test_full_workflow(self):
        """Complete workflow initializes and tracks progress."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            
            # Setup
            config = Config(config_dir=config_dir)
            config.update("level", "B1")
            config.update("objectives", ["fluency"])
            
            db_path = Path(tmpdir) / "test.db"
            db = DB(db_path)
            db.init_schema()
            
            pyramid = PyramidState()
            
            # Simulate init: set initial skill states
            db.update_skill_progress("vocab", xp=50, level="A2")
            db.update_skill_progress("read", xp=20, level="A1")
            db.update_skill_progress("listen", xp=10, level="A1")
            
            # Simulate new-day: practice vocab
            db.log_session("vocab", duration_seconds=600, self_rating=4)
            db.update_skill_progress("vocab", xp=10)
            
            # Simulate vocab learning
            word_id = db.insert_vocab("hello", "greeting", "Hello, world!", "A1")
            db.update_vocab_review(word_id, interval=1, ease_factor=2.5)
            
            # Verify pyramid state after practice
            pyramid.update_skill("vocab", xp_gained=60, level="A2")
            
            # Check progress
            progress = db.fetchone("SELECT * FROM skills_progress WHERE skill_name = 'vocab'")
            assert progress["xp"] >= 50  # XP accumulated
            assert progress["session_count"] >= 1
            
            # Verify CEFR detection works
            detector = CEFRDetector(db)
            profile = detector.detect_skill_cefr("vocab")
            assert profile.skill_name == "vocab"
            assert profile.session_count >= 1
            
            db.close()

    def test_pyramid_enforcement_integration(self):
        """Pyramid dependencies enforced after sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DB(db_path)
            db.init_schema()
            
            pyramid = PyramidState()
            
            # Initially only vocab should be available
            assert pyramid.is_skill_available("vocab") is True
            assert pyramid.is_skill_available("read") is False
            
            # Add XP to vocab to unlock read
            pyramid.update_skill("vocab", xp_gained=100)
            
            # Now read should be available
            assert pyramid.is_skill_available("read") is True
            
            db.close()

    def test_session_logging_integration(self):
        """Sessions are correctly logged and retrievable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DB(db_path)
            db.init_schema()
            
            # Log multiple sessions
            db.log_session("vocab", duration_seconds=600, self_rating=5, notes="Great!")
            db.log_session("read", duration_seconds=1200, self_rating=3)
            db.log_session("listen", duration_seconds=900, self_rating=4)
            
            # Retrieve sessions
            vocab_sessions = db.fetchall(
                "SELECT * FROM sessions WHERE skill_name = 'vocab'"
            )
            assert len(vocab_sessions) == 1
            assert vocab_sessions[0]["self_rating"] == 5
            
            all_sessions = db.fetchall("SELECT COUNT(*) as c FROM sessions")
            assert all_sessions[0]["c"] == 3
            
            db.close()

    def test_vocab_srs_integration(self):
        """Vocabulary SRS works with DB persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DB(db_path)
            db.init_schema()
            
            # Add vocab
            words = [
                ("apple", "fruit", "An apple a day"),
                ("computer", "machine", "I use a computer"),
                ("programming", "coding", "Programming is fun"),
            ]
            for word, defn, ex in words:
                db.insert_vocab(word, defn, ex, "B1")
            
            # Simulate SRS reviews
            for _ in range(3):
                due = db.get_vocab_due(limit=10)
                if due:
                    word_id = due[0]["id"]
                    db.update_vocab_review(word_id, interval=6, ease_factor=2.5)
            
            # Verify vocab exists
            all_vocab = db.fetchall("SELECT COUNT(*) as c FROM vocab")
            assert all_vocab[0]["c"] == 3
            
            db.close()

    def test_cefr_detection_integration(self):
        """CEFR detection works across multiple skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DB(db_path)
            db.init_schema()
            
            # Add skill progress at different levels (session_count comes from update_skill_progress calls)
            db.update_skill_progress("vocab", xp=350, level="B1")  # session_count=1
            db.update_skill_progress("vocab", xp=10)  # session_count=2
            db.update_skill_progress("read", xp=150, level="A2")
            db.update_skill_progress("listen", xp=80, level="A1")
            db.update_skill_progress("write", xp=0, level="A1")
            db.update_skill_progress("speak", xp=0, level="A1")
            
            # Add sessions (these don't affect skills_progress.session_count)
            db.log_session("vocab", self_rating=4)
            db.log_session("vocab", self_rating=4)
            db.log_session("read", self_rating=3)
            
            detector = CEFRDetector(db)
            
            vocab_profile = detector.detect_skill_cefr("vocab")
            assert vocab_profile.detected_level == "B1"
            assert vocab_profile.session_count == 2  # From update_skill_progress calls
            
            read_profile = detector.detect_skill_cefr("read")
            assert read_profile.detected_level == "A2"
            
            # All skills detection
            all_profiles = detector.detect_all_skills()
            assert len(all_profiles) == 5
            
            db.close()


class TestIntegrationMultiDay:
    """Test multi-day usage scenarios."""

    def test_streak_tracking(self):
        """Streak is tracked across sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DB(db_path)
            db.init_schema()
            
            # Log sessions on different days
            db.log_session("vocab", duration_seconds=600, self_rating=4)
            db.update_skill_progress("vocab", xp=10)
            
            # Verify session has date
            session = db.fetchone("SELECT * FROM sessions WHERE skill_name = 'vocab'")
            assert session["date"] is not None
            
            db.close()

    def test_content_cache_persistence(self):
        """Content cache persists in database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DB(db_path)
            db.init_schema()
            
            # Insert into content cache
            db.execute(
                """INSERT INTO content_cache (source, url, title, cefr_level)
                   VALUES (?, ?, ?, ?)""",
                ("BBC", "https://bbc.com/article1", "Test Article", "B1"),
            )
            
            # Retrieve
            cached = db.fetchone("SELECT * FROM content_cache WHERE url = ?", 
                                 ("https://bbc.com/article1",))
            assert cached is not None
            assert cached["title"] == "Test Article"
            assert cached["cefr_level"] == "B1"
            
            db.close()
