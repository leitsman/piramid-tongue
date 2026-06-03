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
├── src/                       # Reference modules (not executed by AI)
│   └── test_questions.py      # Level test + micro-test question banks (SHA256)
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
- When to query the database via `sqlite3` bash commands
- What to log and where
- How to present results to the user

The AI follows these instructions like a recipe. The `src/` directory provides reference data (test questions, exercise templates) that the AI reads directly. All algorithms (SM-2, Leitner) are documented inline in the skill files.

### Backend Modules

The `src/` directory contains only `src/test_questions.py` — a data file with:
- `LEVEL_QUESTIONS`: Level test question banks with SHA256-hashed answers
- `MICRO_TESTS`: Pre-session diagnostic questions for each skill
- `EXERCISE_TEMPLATES`: Templates for generating adaptive practice exercises

This file is **read-only reference data**, not executable code. The AI reads it directly via the Read tool.

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

## 6. Structural Analysis (AI-executed)

Rule-based writing analysis executed directly by the AI using regex patterns:
- Article misuse (overuse of "the" >12% of tokens, missing "a/an")
- Run-on sentences (> 3 conjunctions)
- Sentence fragments (very short without proper subject)
- Spanish interference (false friends: actually, sensible, embarrassed, etc.)
- Verb tense inconsistency
- Preposition errors (Spanish-influenced: depend of, think in, etc.)

Each detected issue maps to an `error_type` and includes the specific `word` involved. Patterns are applied by the AI directly — no Python module needed.

## 7. Platform Tracking (AI-executed)

### Platform Registry

Defined in `configs/profile.yml` and `configs/platforms.yaml`:
- YouTalk (Basic 1-15, Intermediate 16-30)
- Duolingo (streak, league, weekly goal)

### Gap Detection (AI-executed)

AI compares platform progress against actual skill levels:
- Read platform's `platform_level_to_cefr` from profile.yml
- Query actual skill XP from `skills_progress` table
- If platform level > skill level → gap detected: consume vs apply

## 8. Vicios Detection

Configurable regex-based vice detection:
- Pattern registry in `configs/vicios_patterns.yaml`
- Thresholds per pattern (e.g., "the" > 12% of tokens = vice)
- Per-session tracking and trend analysis

## 9. Tech Stack

- **SQLite**: Persistence via `sqlite3` bash commands
- **SM-2 + Leitner**: Algorithms executed directly by AI (documented in skills)
- **Regex-based analysis**: Structural writing analysis done by AI directly
- **No Python runtime**: All execution is AI-native

## 10. Future Work

- [ ] Voice input for speaking skill
- [ ] Gamification (badges, leaderboard)
- [ ] Plugin system for community-contributed skills
