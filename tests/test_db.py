"""Tests for src/db module."""

import sqlite3
from pathlib import Path

import pytest

from src.db import DB


class TestDB:
    """Test database connection and basic operations."""

    def test_init_creates_db_file(self, temp_db):
        """Database file is created on initialization."""
        assert temp_db.db_path.exists()

    def test_connect_returns_connection(self, temp_db):
        """connect() returns a sqlite3 Connection."""
        conn = temp_db.connect()
        assert isinstance(conn, sqlite3.Connection)

    def test_connect_returns_same_connection(self, temp_db):
        """Multiple calls to connect() return the same connection."""
        conn1 = temp_db.connect()
        conn2 = temp_db.connect()
        assert conn1 is conn2

    def test_close_closes_connection(self, temp_db):
        """close() properly closes the connection."""
        temp_db.connect()
        temp_db.close()
        assert temp_db._conn is None

    def test_close_allows_reconnect(self, temp_db):
        """After close(), connect() creates a new connection."""
        temp_db.connect()
        temp_db.close()
        conn = temp_db.connect()
        assert conn is not None

    def test_execute_returns_cursor(self, temp_db):
        """execute() returns a cursor."""
        cursor = temp_db.execute("SELECT 1 as test")
        assert isinstance(cursor, sqlite3.Cursor)

    def test_fetchone_returns_row(self, temp_db):
        """fetchone() returns a single row."""
        temp_db.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        temp_db.execute("INSERT INTO test VALUES (1, 'Alice')")
        row = temp_db.fetchone("SELECT * FROM test")
        assert row["id"] == 1
        assert row["name"] == "Alice"

    def test_fetchall_returns_list(self, temp_db):
        """fetchall() returns a list of rows."""
        temp_db.execute("CREATE TABLE test (id INTEGER)")
        temp_db.executemany("INSERT INTO test VALUES (?)", [(1,), (2,), (3,)])
        rows = temp_db.fetchall("SELECT * FROM test")
        assert len(rows) == 3

    def test_session_commits_on_success(self, temp_db):
        """Session context manager commits on success."""
        with temp_db.session() as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test VALUES (1)")
        # Verify data persists
        row = temp_db.fetchone("SELECT * FROM test")
        assert row is not None

    def test_session_rollbacks_on_error(self, temp_db):
        """Session context manager rolls back on error."""
        temp_db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        with pytest.raises(Exception):
            with temp_db.session() as conn:
                conn.execute("INSERT INTO test VALUES (1)")
                raise Exception("Test error")
        # Verify data was rolled back
        rows = temp_db.fetchall("SELECT * FROM test")
        assert len(rows) == 0


class TestDBMigrations:
    """Test database schema initialization."""

    def test_init_schema_creates_tables(self, temp_db):
        """init_schema() creates all required tables."""
        temp_db.init_schema()
        
        # Check vocab table
        assert temp_db.fetchone("SELECT name FROM sqlite_master WHERE type='table' AND name='vocab'")
        # Check skills_progress table
        assert temp_db.fetchone("SELECT name FROM sqlite_master WHERE type='table' AND name='skills_progress'")
        # Check sessions table
        assert temp_db.fetchone("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        # Check streaks table
        assert temp_db.fetchone("SELECT name FROM sqlite_master WHERE type='table' AND name='streaks'")

    def test_init_schema_is_idempotent(self, temp_db):
        """Calling init_schema() multiple times doesn't error."""
        temp_db.init_schema()
        temp_db.init_schema()  # Should not raise
        temp_db.init_schema()


class TestDBCRUD:
    """Test CRUD helper methods."""

    def test_insert_vocab_returns_id(self, db):
        """insert_vocab() returns the row ID."""
        row_id = db.insert_vocab("test", "definition", "example", "B1")
        assert isinstance(row_id, int)
        assert row_id > 0

    def test_insert_vocab_stores_data(self, db):
        """insert_vocab() correctly stores vocabulary."""
        db.insert_vocab("hello", "greeting", "Hello world!", "A1")
        row = db.fetchone("SELECT * FROM vocab WHERE word = 'hello'")
        assert row is not None
        assert row["word"] == "hello"
        assert row["definition"] == "greeting"
        assert row["example"] == "Hello world!"
        assert row["ceFR_level"] == "A1"

    def test_update_vocab_review(self, db):
        """update_vocab_review() updates SRS fields."""
        row_id = db.insert_vocab("test", "def")
        db.update_vocab_review(row_id, interval=5, ease_factor=2.3)
        row = db.fetchone("SELECT * FROM vocab WHERE id = ?", (row_id,))
        assert row["interval"] == 5
        assert row["ease_factor"] == 2.3
        assert row["last_review"] is not None

    def test_get_vocab_due(self, db):
        """get_vocab_due() returns words due for review."""
        # Insert words with different statuses
        db.insert_vocab("new_word", "new", None, None)  # status='new' - not due
        db.insert_vocab("learning", "learning", None, None)  # status='learning' - due
        
        # Manually set one to learning status and set last_review to past
        db.execute("UPDATE vocab SET status='learning', last_review=datetime('now', '-10 days') WHERE word='learning'")
        
        due = db.get_vocab_due()
        assert len(due) >= 1
        words_due = [row["word"] for row in due]
        assert "learning" in words_due

    def test_update_skill_progress_creates_entry(self, db):
        """update_skill_progress() creates skill entry if not exists."""
        db.update_skill_progress("vocab", xp=100, level="A2")
        row = db.fetchone("SELECT * FROM skills_progress WHERE skill_name = 'vocab'")
        assert row is not None
        assert row["xp"] == 100
        assert row["level"] == "A2"

    def test_update_skill_progress_accumulates_xp(self, db):
        """update_skill_progress() accumulates XP."""
        db.update_skill_progress("vocab", xp=100)
        db.update_skill_progress("vocab", xp=50)
        row = db.fetchone("SELECT * FROM skills_progress WHERE skill_name = 'vocab'")
        assert row["xp"] == 150

    def test_update_skill_progress_increments_session_count(self, db):
        """update_skill_progress() increments session count."""
        db.update_skill_progress("vocab", xp=100)
        db.update_skill_progress("vocab", xp=50)
        row = db.fetchone("SELECT * FROM skills_progress WHERE skill_name = 'vocab'")
        assert row["session_count"] == 2

    def test_log_session_returns_id(self, db):
        """log_session() returns the session ID."""
        session_id = db.log_session("vocab", duration_seconds=600, self_rating=4)
        assert isinstance(session_id, int)
        assert session_id > 0

    def test_log_session_stores_data(self, db):
        """log_session() correctly stores session data."""
        db.log_session("vocab", duration_seconds=600, self_rating=4, notes="Great session")
        row = db.fetchone("SELECT * FROM sessions WHERE skill_name = 'vocab'")
        assert row is not None
        assert row["duration_seconds"] == 600
        assert row["self_rating"] == 4
        assert row["notes"] == "Great session"
