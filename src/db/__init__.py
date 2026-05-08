"""Database connection wrapper and query helpers for Piramid-Tongue."""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Any


class DB:
    """SQLite connection wrapper with migration support."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else Path.home() / ".piramid-tongue" / "piramid-tongue.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Create or return existing connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    @contextmanager
    def session(self):
        """Context manager for transactional database operations."""
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a single query."""
        conn = self.connect()
        return conn.execute(query, params)

    def executemany(self, query: str, params: list[tuple]) -> sqlite3.Cursor:
        """Execute a query with multiple parameter sets."""
        conn = self.connect()
        return conn.executemany(query, params)

    def fetchone(self, query: str, params: tuple = ()) -> sqlite3.Row | None:
        """Fetch a single row."""
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Fetch all rows."""
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def init_schema(self, schema_path: str | Path | None = None) -> None:
        """Initialize database from schema.sql file."""
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.sql"
        schema_sql = Path(schema_path).read_text()
        with self.session() as conn:
            conn.executescript(schema_sql)

    # --- CRUD helpers ---

    def insert_vocab(self, word: str, definition: str, example: str | None = None,
                     ceFR_level: str | None = None) -> int:
        """Insert a new vocabulary word. Returns row ID."""
        with self.session() as conn:
            cursor = conn.execute(
                "INSERT INTO vocab (word, definition, example, ceFR_level) VALUES (?, ?, ?, ?)",
                (word, definition, example, ceFR_level),
            )
            return cursor.lastrowid

    def update_vocab_review(self, word_id: int, interval: int, ease_factor: float) -> None:
        """Update spaced repetition fields for a vocab entry."""
        self.execute(
            "UPDATE vocab SET interval = ?, ease_factor = ?, last_review = datetime('now') WHERE id = ?",
            (interval, ease_factor, word_id),
        )

    def get_vocab_due(self, limit: int = 20) -> list[sqlite3.Row]:
        """Get vocabulary words due for review based on SM-2 intervals."""
        return self.fetchall(
            """SELECT * FROM vocab
               WHERE status = 'learning'
                 AND (last_review IS NULL OR
                      datetime('now') >= datetime(last_review, '+' || interval || ' days'))
               ORDER BY last_review ASC
               LIMIT ?""",
            (limit,),
        )

    def update_skill_progress(self, skill_name: str, xp: int = 0, level: str | None = None) -> None:
        """Update skill progress. Creates entry if not exists."""
        with self.session() as conn:
            conn.execute(
                """INSERT INTO skills_progress (skill_name, xp, last_practiced, session_count)
                   VALUES (?, ?, datetime('now'), 1)
                   ON CONFLICT(skill_name) DO UPDATE SET
                       xp = xp + ?,
                       last_practiced = datetime('now'),
                       session_count = session_count + 1""",
                (skill_name, xp, xp),
            )
            if level:
                conn.execute(
                    "UPDATE skills_progress SET level = ? WHERE skill_name = ?",
                    (level, skill_name),
                )

    def log_session(self, skill_name: str, duration_seconds: int | None = None,
                    self_rating: int | None = None, notes: str | None = None) -> int:
        """Log a practice session. Returns session ID."""
        with self.session() as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (skill_name, duration_seconds, self_rating, notes) VALUES (?, ?, ?, ?)",
                (skill_name, duration_seconds, self_rating, notes),
            )
            return cursor.lastrowid

    def log_platform_progress(self, platform_name: str, level: str, unit_number: int,
                              unit_type: str, video_number: int,
                              self_rating: int | None = None, notes: str | None = None) -> int:
        """Log progress on a platform video. Returns row ID."""
        with self.session() as conn:
            cursor = conn.execute(
                """INSERT INTO platform_progress 
                   (platform_name, level, unit_number, unit_type, video_number, self_rating, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(platform_name, level, unit_number, unit_type, video_number) 
                   DO UPDATE SET self_rating = excluded.self_rating, notes = excluded.notes""",
                (platform_name, level, unit_number, unit_type, video_number, self_rating, notes),
            )
            return cursor.lastrowid

    def get_platform_progress(self, platform_name: str, level: str | None = None,
                              unit_number: int | None = None) -> list[sqlite3.Row]:
        """Get platform progress filtered by platform, optionally by level and/or unit."""
        query = "SELECT * FROM platform_progress WHERE platform_name = ?"
        params: list[Any] = [platform_name]
        
        if level is not None:
            query += " AND level = ?"
            params.append(level)
        if unit_number is not None:
            query += " AND unit_number = ?"
            params.append(unit_number)
        
        query += " ORDER BY unit_number, unit_type, video_number"
        return self.fetchall(query, tuple(params))

    def get_latest_platform_progress(self, platform_name: str) -> sqlite3.Row | None:
        """Get the most recent progress entry for a platform."""
        return self.fetchone(
            """SELECT * FROM platform_progress 
               WHERE platform_name = ? 
               ORDER BY completed_at DESC 
               LIMIT 1""",
            (platform_name,),
        )

    def is_video_completed(self, platform_name: str, level: str, unit_number: int,
                           unit_type: str, video_number: int) -> bool:
        """Check if a specific video has been completed on a platform."""
        row = self.fetchone(
            """SELECT 1 FROM platform_progress 
               WHERE platform_name = ? AND level = ? AND unit_number = ? 
               AND unit_type = ? AND video_number = ?""",
            (platform_name, level, unit_number, unit_type, video_number),
        )
        return row is not None

    # --- Weakness tracking for adaptive practice ---

    def add_weakness(self, category: str, description: str | None = None,
                     source: str = 'structural_analysis') -> int:
        """Add a new weakness or increment fail_count if category exists.
        Returns the weakness id.
        """
        # Check if weakness already exists for this category
        existing = self.fetchone(
            "SELECT id FROM weaknesses WHERE category = ? AND status = 'active'",
            (category,),
        )
        if existing:
            # Increment fail_count for existing weakness
            self.execute(
                "UPDATE weaknesses SET fail_count = fail_count + 1, last_practiced = datetime('now') WHERE id = ?",
                (existing['id'],),
            )
            return existing['id']
        
        # Create new weakness
        with self.session() as conn:
            cursor = conn.execute(
                """INSERT INTO weaknesses (category, description, source, fail_count)
                   VALUES (?, ?, ?, 1)""",
                (category, description, source),
            )
            return cursor.lastrowid

    def get_active_weaknesses(self, limit: int = 5) -> list[sqlite3.Row]:
        """Get active weaknesses sorted by fail_count DESC."""
        return self.fetchall(
            """SELECT * FROM weaknesses 
               WHERE status = 'active'
               ORDER BY fail_count DESC
               LIMIT ?""",
            (limit,),
        )

    def increment_fail(self, weakness_id: int) -> None:
        """Increment fail_count for a weakness."""
        self.execute(
            "UPDATE weaknesses SET fail_count = fail_count + 1, last_practiced = datetime('now') WHERE id = ?",
            (weakness_id,),
        )

    def increment_pass(self, weakness_id: int) -> None:
        """Increment pass_count for a weakness. Mark as mastered if pass_count >= 5."""
        self.execute(
            """UPDATE weaknesses 
               SET pass_count = pass_count + 1, 
                   last_practiced = datetime('now'),
                   status = CASE WHEN pass_count + 1 >= 5 THEN 'mastered' ELSE status END
               WHERE id = ?""",
            (weakness_id,),
        )

    def report_weakness(self, category: str, description: str | None = None) -> int:
        """Add a user-reported weakness."""
        return self.add_weakness(category, description, source='user_reported')
