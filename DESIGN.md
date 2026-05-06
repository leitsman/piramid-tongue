# Technical Design: piramid-tongue

## 1. Directory Structure (career-ops inspired)

```
piramid-tongue/
├── src/
│   ├── cli/                 # CLI entrypoint and command router
│   │   ├── main.py          # Typer/Click based CLI
│   │   └── commands/        # Subcommand modules (init, new-day, vocab, listen, read, write, speak, practice, progress, roadmap, vicios)
│   ├── skills/              # Independent skill modules following the pyramid
│   │   ├── __init__.py
│   │   ├── vocab.py         # Vocabulary management with spaced repetition
│   │   ├── listen.py        # Audio processing, transcription, recommendations
│   │   ├── read.py          # CEFR level detection, content suggestion
│   │   ├── write.py         # Style analysis, vicios detection, correction
│   │   └── speak.py         # Recording, playback, self-evaluation
│   ├── core/                # Shared engine and utilities
│   │   ├── __init__.py
│   │   ├── pyramid_engine.py# Enforces skill dependencies and flow (ASCENSO/DESCENSO)
│   │   ├── spaced_repetition.py# SRS algorithm (SM-2 variant)
│   │   ├── progress_tracker.py# Stats computation and persistence
│   │   └── config.py        # YAML config loading (~/.config/piramid-tongue/)
│   ├── scrapers/            # Content discovery connectors
│   │   ├── __init__.py
│   │   ├── bbc.py           # BBC Learning English scraper
│   │   ├── youtube.py       # YouTube transcript extraction (via yt-dlp)
│   │   ├── books.py         # Public domain books (Gutenberg) fetcher
│   │   └── web.py           # Generic web scraping with rate limiting
│   ├── db/                  # SQLite persistence layer
│   │   ├── __init__.py
│   │   ├── schema.sql       # Table definitions
│   │   ├── migrations/      # Versioned migration scripts
│   │   └── db.py            # Connection wrapper and query helpers
│   └── logs/                # Markdown daily logs
│       ├── template.md      # Daily log template
│       └── writer.py        # Append-only log writer
├── tests/                   # Unit tests per module
│   ├── test_vocab.py
│   ├── test_listen.py
│   ├── test_read.py
│   ├── test_write.py
│   └── test_speak.py
├── configs/                 # Example config files
│   └── config.yaml.example
├── requirements.txt         # Python dependencies
├── README.md
└── LICENSE
```

## 2. CLI Module Architecture

- **Entrypoint**: `src/cli/main.py` uses Typer for command parsing.
- **Command Router**: Each subcommand lives in `src/cli/commands/` as a separate module, registered via `typer.Typer()`.
- **Dependency Injection**: Core services (DB, config, logger) are instantiated in `main.py` and passed to command handlers via context objects.
- **Skill Invocation**: Commands like `vocab`, `listen`, etc., delegate to corresponding skill modules in `src/skills/`.
- **Cross‑cutting Concerns**: Logging, error handling, and config loading are centralized in `core/`.

### Example Command Flow (`/pt vocab add`)

1. Typer parses command, calls `vocab_add` in `src/cli/commands/vocab.py`.
2. Handler receives `db: Session`, `cfg: Config` from context.
3. Calls `skills.vocab.add_word(word, metadata)`.
4. Skill validates, inserts into SQLite via `core.db.DB.insert_vocab()`.
5. Skill updates spaced‑repetition schedule via `core.spaced_repetition`.
6. Returns success message; CLI prints it.

## 3. Data Flows

### SQLite (Analytical & Fast Queries)

- **Tables**:
  - `vocab(id, word, definition, example, added_date, last_review, interval, ease_factor)`
  - `skills_progress(id, skill_name, level, xp, last_practiced)`
  - `daily_logs(id, date, log_path)` – pointer to markdown file.
  - `content_cache(id, source, url, title, transcript, fetched_at)` – for scraped items.
  - `vicios_patterns(id, user_id, pattern, count, last_seen)` – tracked linguistic vices.

- **Usage**:
  - Skill modules perform CRUD via `core.db.DB`.
  - Aggregated queries (e.g., progress reports) are executed directly in SQL for performance.
  - Migrations managed via Alembic‑like versioned scripts in `db/migrations/`.

### Markdown Logs (Human‑Readable Journal)

- **Location**: `~/piramid-tongue/logs/YYYY-MM-DD.md` (configurable).
- **Template** (`logs/template.md`):
  ```markdown
  # Log for {{date}}

  ## Vocab Review
  - ...

  ## Listening Practice
  - ...

  ## Reading Session
  - ...

  ## Writing Exercise
  - ...

  ## Speaking Drill
  - ...

  ## Vicios Detected
  - ...

  ## Notes
  ```
- **Writer**: `logs.writer.append_log(date, sections)` creates/appends the file.
- **Read‑Only**: CLI never mutates existing logs; only appends new sections.

### Sync Strategy

- After each skill practice session, the skill:
  1. Updates SQLite tables (instant).
  2. Calls `logs.writer` to add a section for that day.
  3. Returns a summary to the CLI, which prints it.

## 4. Content Connectors

| Connector | Source | Method | Output |
|-----------|--------|--------|--------|
| **BBC** | `bbc.co.uk/learningenglish` | HTTP GET + HTML parsing (BeautifulSoup) | Articles, audio clips, transcripts |
| **YouTube** | YouTube (search via API or scrape) | `yt-dlp` to extract auto‑generated captions or upload own subtitles | Transcript text, metadata |
| **Books** | Project Gutenberg, Standard Ebooks | HTTP GET + plain‑text extraction | Full text, chapter splitting |
| **Web Scraping** | Arbitrary blogs/news | Generic scraper with readability‑lxml fallback | Clean article text |

- **Rate Limiting**: Each connector respects `Retry-After` headers and implements exponential back‑off.
- **User‑Agent Rotation**: Pool of common browser UA strings to reduce blocking.
- **Caching**: Fetched content stored in `content_cache` SQLite table; subsequent requests check freshness (configurable TTL).
- **Fallback**: If primary source fails, connector tries secondary source (e.g., BBC → YouTube → Gutenberg).

## 5. Interface for Vicios Detection (skill-write)

### Purpose
Identify repetitive linguistic patterns that hinder natural English (e.g., overuse of "the", "very + adjective", filler words, literal translations from Spanish).

### Design

- **Pattern Registry**: YAML file `configs/vicios_patterns.yaml` (loaded at startup).
  ```yaml
  - pattern: "\\bthe\\b"
    flag: g
    description: Overuse of definite article
    threshold: 0.12  # >12% of tokens
  - pattern: "\\bvery\\s+\\w+"
    flag: g
    description: "very + adjective" intensifier
    threshold: 0.05
  - pattern: "\\bactually\\b"
    flag: g
    description: Filler word
    threshold: 0.03
  # ... more patterns
  ```

- **Detection Algorithm** (`skills/write.py`):
  1. Receive user‑provided text (from writing exercise or clipboard).
  2. Tokenize (simple regex split on whitespace/punctuation).
  3. For each pattern, count matches using compiled regex.
  4. Compute frequency = matches / total tokens.
  5. If frequency > threshold, flag as a vice.
  6. Store/update `vicios_patterns` table with count and timestamp.
  7. Return list of `{pattern, description, frequency, suggestion}`.

- **Feedback Loop**:
  - During `/pt write` command, after user submits text, CLI calls skill to analyze.
  - Results displayed with suggestions (e.g., replace "very good" with "excellent").
  - Over time, progress view shows reduction in vice frequency.

- **Extensibility**: New patterns added via YAML without code change; admin can reload config via `/pt config reload`.

## 6. Additional Architectural Decisions

- **Language Choice**: Python 3.11+ for rich ecosystem (typer, yt‑dlp, beautifulsoup4, pyyaml). Could be ported to Go later.
- **Testing**: Unit tests with `pytest`; mocks for external HTTP and filesystem.
- **Configuration**: Hierarchical: defaults → `~/.config/piramid-tongue/config.yaml` → env vars.
- **Security**: No execution of arbitrary code; scrapers only read public content.
- **Portability**: All paths relative to HOME or configurable base directory.

## 7. Open Issues & Future Work

- **Voice Input**: Integrate microphone capture for speaking skill.
- **Gamification**: Streams, badges, leaderboard stored in SQLite.
- **Plugin System**: Allow community‑contributed skills via entry points.
- **Off‑First Mode**: Pre‑download content for offline study.

---