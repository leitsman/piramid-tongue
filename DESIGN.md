# Technical Design: piramid-tongue

> Last Updated: 2026-05-11

## 1. Directory Structure

```
piramid-tongue/
├── skills/                     # AI-executed skill instruction files
│   ├── _shared.md             # Shared pyramid context (CEFR, dependencies, vicios)
│   ├── _shared/               # Shared skill modules
│   │   ├── adaptive-practice.md   # Leitner-based weakness practice flow
│   │   ├── exercise-design.md     # AI exercise generation guide
│   │   └── micro-test.md          # Pre-session diagnostic tests
│   ├── init.md                # Level test + profile setup
│   ├── new-day.md             # Daily session + gap detection + recommendations
│   ├── vocab.md               # Vocabulary (SM-2 review + new words)
│   ├── listen.md              # Listening practice + micro-test
│   ├── read.md                # Reading practice + micro-test
│   ├── write.md               # Writing (structural analysis + vicios + micro-test)
│   ├── speak.md               # Speaking practice + micro-test
│   ├── practice.md            # External platform logging
│   ├── progress.md            # ASCII pyramid + stats + streak
│   ├── roadmap.md             # Next steps with dependencies
│   └── vicios.md             # Vice pattern analysis
├── src/                       # Backend modules (not executed by AI directly)
│   ├── core/                  # Core engine and utilities
│   │   ├── __init__.py
│   │   ├── pyramid_engine.py  # Skill dependencies and flow (ASCENSO/DESCENSO)
│   │   ├── spaced_repetition.py # SM-2 algorithm for vocabulary
│   │   ├── leitner.py        # Leitner box system for weakness tracking
│   │   ├── progress_tracker.py # Stats computation and persistence
│   │   ├── cefr_detector.py  # CEFR level inference
│   │   └── config.py         # YAML config loading
│   ├── db/                    # SQLite persistence layer
│   │   ├── __init__.py       # DB class + CRUD helpers
│   │   └── schema.sql        # Table definitions
│   ├── analysis/              # Text processing
│   │   ├── __init__.py
│   │   └── structural.py     # Rule-based writing analysis (vicios, issues)
│   ├── platforms/             # External platform integration
│   │   ├── __init__.py
│   │   ├── platform_registry.py # Platform definitions and onboarding
│   │   └── gap_detector.py    # Platform-vs-skill gap detection
│   ├── logs/                  # Logging utilities
│   │   ├── __init__.py
│   │   └── writer.py         # LogWriter class (optional utility)
│   ├── scrapers/              # Content connectors (defined but not skill-integrated)
│   │   ├── __init__.py
│   │   ├── bbc.py            # BBC Learning English scraper
│   │   ├── youtube.py        # YouTube transcript extraction (yt-dlp)
│   │   ├── books.py          # Gutenberg/Standard Ebooks fetcher
│   │   └── web.py            # Generic web scraper with rate limiting
│   └── test_questions.py      # Level test + micro-test question banks
├── configs/                   # User configuration
│   ├── profile.yml            # Identity, level, platforms, streak
│   ├── platforms.yaml        # Platform definitions and metric schemas
│   ├── vicios_patterns.yaml # Vice detection patterns
│   └── config.yaml.example   # System configuration template
├── data/                      # SQLite database (gitignored)
│   └── progress.db
├── logs/                      # Daily session logs (gitignored)
│   └── YYYY-MM-DD.md
├── tests/                     # Unit tests
├── requirements.txt
├── README.md
├── AGENTS.md                  # Agent instructions (AI executes skills)
└── DESIGN.md                  # This file
```

## 2. AI Execution Architecture

The system is designed for **AI-executed skills** — no Python processes are spawned when the user runs commands.

### How It Works

```
User: "/pt new-day"
       │
       ▼
AI reads skills/new-day.md + skills/_shared.md
       │
       ▼
AI reads configs/profile.yml and data/progress.db
       │
       ▼
AI executes instructions directly (no Python subprocess)
       │
       ▼
AI updates SQLite, writes logs, shows results
```

### Skill Files

Each skill file (`skills/<command>.md`) contains:
- Step-by-step instructions for the AI to execute
- When to query the database
- What to log and where
- How to present results to the user

The AI follows these instructions like a recipe. The `src/` directory provides helper modules the AI can import if needed, but the primary execution path is reading skill files and following their instructions.

### Backend Modules

The `src/` directory contains Python modules that provide:
- Database operations (`src/db/__init__.py`)
- Algorithms (SM-2, Leitner, CEFR detection)
- Analysis (structural writing analysis)
- Configuration loading

These are **helper libraries**, not execution endpoints. The AI uses them indirectly when implementing skill logic.

## 3. Data Flows

### SQLite Database (`data/progress.db`)

**Tables**:
- `vocab(id, word, definition, example, added_date, last_review, interval, ease_factor, status, cefr_level)`
- `skills_progress(id, skill_name, level, xp, last_practiced, session_count)`
- `weaknesses(id, word, error_type, context_example, box_level, consecutive_correct, next_review, fail_count, pass_count, status, source, ...)`
- `platform_progress(id, platform_name, level, unit_number, unit_type, video_number, completed_at, self_rating, notes)`
- `sessions(id, skill_name, duration_seconds, date, self_rating, notes)`
- `vicios_patterns(id, pattern, description, threshold, count, last_seen)`
- `streaks(id, current_streak, longest_streak, last_active_date, start_date)`
- `daily_logs(id, date, log_path)`
- `content_cache(id, source, url, title, transcript, cefr_level, fetched_at)`

### Markdown Logs (`logs/YYYY-MM-DD.md`)

- Created automatically when a session starts
- AI appends section results directly to the file
- Format:
  ```markdown
  # Log for 2026-05-11

  ## Vocab Review
  - Reviewed 15 words due. 3 new words added.

  ## Weakness Review
  - Practiced "it" (expletive_usage) — 2/2 correct

  ## Writing Exercise
  - Score: 85/100. Issues: article_overuse, preposition_error

  ## Notes
  -
  ```

### Configuration Files (`configs/`)

- `profile.yml` — User identity, CEFR level, objectives, streak, platform config
- `platforms.yaml` — Platform definitions with metric schemas
- `vicios_patterns.yaml` — Regex patterns for vice detection with thresholds

## 4. Pyramid Engine

### Skill Dependencies

```
vocab: (unlocked)
read: requires vocab
listen: requires read
write: requires listen
speak: requires write
```

Skills require 100 XP in prerequisites before unlocking.

### Ascent / Descent

- **Ascent**: vocab → read → listen → write → speak (learning new skills)
- **Descent**: focus on weak skill + its dependencies (perfecting)

## 5. Spaced Repetition Systems

### SM-2 (Vocabulary)

Standard SM-2 algorithm with ease factor adjustment:
- Initial ease factor: 2.5
- Correct answer: increase interval
- Wrong answer: reset to 1 day, reduce ease factor

### Leitner System (Weakness Tracking)

5-box spaced repetition for word-specific weaknesses:
- Box 1: Review daily (1 day interval)
- Box 2: Every 2 days
- Box 3: Every 4 days
- Box 4: Every 7 days
- Box 5: Every 14 days

Box updates happen the day after practice (not immediately).

**Box movement**:
- Correct answer → advance 1 box (max 5)
- Minor failure → drop 1 box (min 1)
- Major failure → drop 2 boxes (min 1)
- Box 5 with 3+ consecutive correct → status = 'mastered'

## 6. Structural Analysis (`src/analysis/structural.py`)

Rule-based writing analysis without NLP libraries. Detects:
- Article misuse (overuse of "the", missing "a/an")
- Run-on sentences (> 3 conjunctions)
- Sentence fragments (very short without proper subject)
- Spanish interference (false friends: actually, sensible, embarrassed, etc.)
- Verb tense inconsistency
- Preposition errors (Spanish-influenced: depend of, think in, etc.)

Each detected issue maps to an `error_type` and includes the specific `word` involved.

## 7. Platform Tracking (`src/platforms/`)

### Platform Registry

Defines platform structures and onboarding flows for:
- YouTalk (Basic 1-15, Intermediate 16-30)
- Duolingo (streak, league, weekly goal)

### Gap Detection

Compares platform progress against actual skill levels:
- Platform suggests B1 level
- But skill micro-tests show A2 in writing
- → Gap detected: consume vs apply

## 8. Vicios Detection

Configurable regex-based vice detection:
- Pattern registry in `configs/vicios_patterns.yaml`
- Thresholds per pattern (e.g., "the" > 12% of tokens = vice)
- Per-session tracking and trend analysis

## 9. Tech Stack

- **Python 3.11+**: Backend modules
- **SQLite**: Persistence (via `src/db/__init__.py`)
- **SM-2 + Leitner**: Spaced repetition algorithms
- **Regex-based analysis**: Structural writing analysis
- **pytest**: Testing
- **No framework**: Pure Python utilities

## 10. Future Work

- [ ] Integrate scrapers (`src/scrapers/`) into skill flows
- [ ] Voice input for speaking skill
- [ ] Gamification (badges, leaderboard)
- [ ] Plugin system for community-contributed skills
