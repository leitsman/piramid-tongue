-- Piramid-Tongue SQLite Schema
-- Version: 1

-- Vocabulary with spaced repetition fields
CREATE TABLE IF NOT EXISTS vocab (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    definition TEXT NOT NULL,
    example TEXT,
    added_date TEXT NOT NULL DEFAULT (datetime('now')),
    last_review TEXT,
    interval INTEGER DEFAULT 0,
    ease_factor REAL DEFAULT 2.5,
    status TEXT DEFAULT 'new' CHECK(status IN ('new', 'learning', 'acquired')),
    ceFR_level TEXT
);

-- Skill progress tracking (vocab, listen, read, write, speak)
CREATE TABLE IF NOT EXISTS skills_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE CHECK(skill_name IN ('vocab', 'listen', 'read', 'write', 'speak')),
    level TEXT DEFAULT 'A1',
    xp INTEGER DEFAULT 0,
    last_practiced TEXT,
    session_count INTEGER DEFAULT 0
);

-- Daily logs pointer to markdown files
CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    log_path TEXT NOT NULL
);

-- Content cache from scrapers
CREATE TABLE IF NOT EXISTS content_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    title TEXT,
    transcript TEXT,
    cefr_level TEXT,
    fetched_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Vicios (linguistic vices) patterns tracking
CREATE TABLE IF NOT EXISTS vicios_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL UNIQUE,
    description TEXT,
    threshold REAL NOT NULL,
    count INTEGER DEFAULT 0,
    last_seen TEXT
);

-- Streak tracking
CREATE TABLE IF NOT EXISTS streaks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_active_date TEXT,
    start_date TEXT NOT NULL DEFAULT (date('now'))
);

-- External platforms tracking
CREATE TABLE IF NOT EXISTS platforms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    url TEXT,
    streak INTEGER DEFAULT 0,
    level TEXT,
    metrics TEXT,
    last_updated TEXT
);

-- Sessions log
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    duration_seconds INTEGER,
    date TEXT NOT NULL DEFAULT (date('now')),
    self_rating INTEGER CHECK(self_rating BETWEEN 1 AND 5),
    notes TEXT
);
