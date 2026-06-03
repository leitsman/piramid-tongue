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

-- Weaknesses tracking for adaptive practice
CREATE TABLE IF NOT EXISTS weaknesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    description TEXT,
    detected_date TEXT NOT NULL DEFAULT (datetime('now')),
    last_practiced TEXT,
    fail_count INTEGER DEFAULT 0,
    pass_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'mastered', 'ignored')),
    source TEXT DEFAULT 'structural_analysis' CHECK(source IN ('micro_test', 'structural_analysis', 'user_reported', 'transcription')),
    -- New word-specific tracking columns (Leitner box system)
    word TEXT NOT NULL DEFAULT '',
    error_type TEXT NOT NULL DEFAULT '',
    context_example TEXT,
    box_level INTEGER DEFAULT 3,
    consecutive_correct INTEGER DEFAULT 0,
    next_review TEXT
);

-- Migration: Add new columns to existing weaknesses table
-- Using ALTER TABLE for existing installations (backward compatibility)
-- New records will have word='', error_type='', box_level=3, consecutive_correct=0, next_review=NULL

-- Listening practice tracking with 4-level progression
CREATE TABLE IF NOT EXISTS listening_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listen_level INTEGER DEFAULT 1 CHECK(listen_level IN (1,2,3,4)),
    session_date TEXT NOT NULL DEFAULT (date('now')),
    content_type TEXT NOT NULL CHECK(content_type IN ('video', 'podcast')),
    content_source TEXT,
    content_title TEXT,
    duration_minutes INTEGER,
    used_subtitles BOOLEAN,  -- solo para nivel 2
    comprehension_rating INTEGER CHECK(comprehension_rating BETWEEN 1 AND 5),
    unknown_words TEXT,  -- JSON array de palabras
    unknown_word_count INTEGER DEFAULT 0,
    words_to_youglish TEXT,  -- JSON array
    words_to_vocab_youglish TEXT,  -- JSON array
    xp_earned INTEGER DEFAULT 0,
    notes TEXT
);

-- Platform-specific progress tracking (YouTalk, Duolingo, etc.)
CREATE TABLE IF NOT EXISTS platform_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT NOT NULL,
    level TEXT NOT NULL,
    unit_number INTEGER NOT NULL,
    unit_type TEXT NOT NULL CHECK(unit_type IN ('grammar', 'vocab', 'sentences')),
    video_number INTEGER NOT NULL,
    completed_at TEXT DEFAULT (datetime('now')),
    self_rating INTEGER CHECK(self_rating BETWEEN 1 AND 5),
    notes TEXT,
    UNIQUE(platform_name, level, unit_number, unit_type, video_number)
);

-- Vocab 3-level system and repetition counting
ALTER TABLE vocab ADD COLUMN vocab_level INTEGER DEFAULT 1 CHECK(vocab_level IN (1,2,3));
ALTER TABLE vocab ADD COLUMN technical INTEGER DEFAULT 0;
ALTER TABLE vocab ADD COLUMN repetition_count INTEGER DEFAULT 0;
