# Piramid-Tongue

> Your personal English learning pyramid — always tells you **what to do next**.

## How It Works

**AI-Executed Skills** — no Python processes, no CLI. The AI reads skill files and follows instructions directly.

```
You say: /pt init
         │
         ▼
┌──────────────────────────────────┐
│  AI reads skills/init.md        │
│  AI executes level test          │
│  AI saves to configs/profile.yml │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Pyramid Engine                  │
│  vocab → read → listen           │
│    → write → speak               │
└────────┬─────────────────────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
 Daily  CEFR  Gap Detection
 Log    Level  (Platform vs Skill)
```

**Two flows:**
- 🟢 **Ascent (learning)**: vocabulary → reading → listening → writing → speaking
- 🔴 **Descent (perfecting)**: focus on weak skill + its dependencies

## Features

| Feature | Description |
|---------|-------------|
| **Level Test** | Adaptive CEFR evaluation (A1-C2) with SHA256-verified answers |
| **Platform Tracking** | YouTalk, Duolingo, and more — metric-specific onboarding |
| **Daily Tracker** | `/pt new-day` — self-report + gap detection + recommendations |
| **Vocabulary** | Spaced repetition (SM-2), technical vocab, micro-tests |
| **Listening** | Content by CEFR level, timed sessions, self-rating |
| **Reading** | Texts by level, comprehension exercises, micro-tests |
| **Writing** | Structural analysis + vicios detection + micro-tests |
| **Speaking** | Read-aloud, shadowing, tandem reminders, micro-tests |
| **Gap Detection** | Compares platform progress with actual skill levels |
| **Self-Report** | Daily diagnostic question about difficulties |
| **Micro-Tests** | 4 questions + 2 bonus before each skill session |
| **Progress Pyramid** | Visual ASCII pyramid showing your level per skill |
| **Streak Tracking** | Daily consistency counter |

## Quick Start

### 1. Clone and install dependencies

```bash
git clone <your-repo>
cd piramid-tongue
pip install -r requirements.txt
```

### 2. Check setup

```bash
python -m pytest --tb=short -q
```

### 3. Start learning

Open this project in an AI assistant (OpenCode, Cursor, etc.) and say:

```
/pt init
```

The AI will run the level test, set up your profile, ask about your learning platforms, and configure everything.

**Both syntaxes work:** `/pt init` or `/pt-init`

### 4. Follow the recommendations

```
/pt new-day      # Start daily session + get recommendations
/pt vocab        # Vocabulary (SM-2 review + new words)
/pt read         # Reading practice
/pt listen       # Listening practice
/pt write        # Writing (structural analysis + vicios)
/pt speak        # Speaking (read-aloud, shadowing)
/pt progress     # Visual pyramid + stats + streak
/pt roadmap      # Next steps with dependencies
/pt vicios       # Analyze text for linguistic vices
/pt practice     # Log external platform practice
```

## Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `/pt init` | `/pt-init` | Level test + profile + platform onboarding |
| `/pt new-day` | `/pt-new-day` | Daily session + self-report + recommendations |
| `/pt vocab` | `/pt-vocab` | Vocabulary (SM-2 review + micro-test) |
| `/pt listen` | `/pt-listen` | Listening practice + micro-test |
| `/pt read` | `/pt-read` | Reading practice + micro-test |
| `/pt write` | `/pt-write` | Writing (structural analysis + vicios + micro-test) |
| `/pt speak` | `/pt-speak` | Speaking practice + micro-test |
| `/pt practice` | `/pt-practice` | Log external platform practice |
| `/pt progress` | `/pt-progress` | Visual pyramid + stats + streak + gap detection |
| `/pt roadmap` | `/pt-roadmap` | Next steps with dependencies |
| `/pt vicios` | `/pt-vicios` | Analyze text for linguistic vices |

## How the AI Executes Skills

When you say `/pt <command>`:
1. AI reads `skills/<command>.md` and `skills/_shared.md`
2. AI reads your data from `configs/profile.yml` and the database
3. AI asks you for input when required
4. AI logs results to `logs/YYYY-MM-DD.md`
5. AI updates the SQLite database
6. AI shows you results and next steps

**No Python processes are spawned. The AI IS the executor.**

## Platform Tracking

The system supports structured platform tracking with metric-specific onboarding:

```yaml
platforms:
  - name: "YouTalk"
    enabled: true
    metrics:
      current_level: "Intermediate"
      current_unit: 17
      total_units_completed: 31
      weekly_goal: 5
    platform_level_to_cefr: "B1"
  - name: "Duolingo"
    enabled: true
    metrics:
      streak: 378
      league: "Sapphire"
      weekly_goal: 50
```

New platforms can be added by editing `configs/platforms.yaml`.

## Gap Detection

The system detects gaps between your platform progress and actual skill levels:

```
⚠️ Gap Detected:
Your YouTalk progress suggests B1, but your Writing is at A2.
This means you're consuming content but not applying it enough.
Focus on applying vocabulary in writing exercises.
```

## Vicios Detection

The system detects common English writing vices:

| Vice | Example | Suggestion |
|------|---------|------------|
| Repeated "the" | "The the problem..." | "The problem..." |
| "very + adj" | "very good" | "excellent", "outstanding" |
| "I think that" | Repeated 3+ times | Vary: "I believe", "In my opinion" |
| "In order to" | "In order to improve" | "To improve" |
| "Due to the fact" | "Due to the fact that..." | "Because..." |
| False friends | "actually" (for "currently") | Use "currently" or "in fact" |
| Preposition errors | "depend of" | "depend on" |

Patterns are configurable in `configs/vicios_patterns.yaml`.

## Project Structure

```
piramid-tongue/
├── configs/
│   ├── profile.yml           # Your profile, platforms, streak
│   ├── platforms.yaml        # Platform definitions & metric schemas
│   ├── vicios_patterns.yaml  # Configurable vices detection
│   └── config.yaml.example   # System configuration template
├── skills/                   # AI-executed skill files
│   ├── _shared.md            # Shared pyramid context
│   ├── _shared/
│   │   └── micro-test.md     # Shared micro-test instructions
│   ├── init.md               # Level test + profile setup
│   ├── new-day.md            # Daily session + recommendations
│   ├── vocab.md              # Vocabulary (SM-2 + micro-test)
│   ├── listen.md             # Listening + micro-test
│   ├── read.md               # Reading + micro-test
│   ├── write.md              # Writing + structural analysis
│   ├── speak.md              # Speaking + micro-test
│   ├── practice.md           # External platform logging
│   ├── progress.md           # ASCII pyramid + stats
│   ├── roadmap.md            # Next steps
│   └── vicios.md             # Vice pattern analysis
├── src/
│   ├── platforms/            # Platform registry & gap detection
│   ├── analysis/             # Structural writing analysis
│   ├── core/                 # Pyramid engine, SM-2, CEFR
│   ├── db/                   # SQLite schema and CRUD
│   ├── scrapers/             # BBC, YouTube, Books, Web
│   ├── logs/                 # Daily markdown logs
│   └── test_questions.py     # Level test + micro-test question bank
├── tests/                    # Test suite
├── logs/                     # Daily session logs (gitignored)
├── data/                     # SQLite database (gitignored)
└── openspec/                 # SDD artifacts (gitignored)
```

## Persistence

| Layer | Format | Content |
|-------|--------|---------|
| **Logs** | Markdown (`logs/YYYY-MM-DD.md`) | Daily session records, human-readable |
| **Stats** | SQLite (`data/progress.db`) | Vocabulary, skills, vicios, sessions — queryable |
| **Config** | YAML | Profile, platforms, vicios patterns, platform definitions |

## Tech Stack

- **Python**: Core modules (pyramid engine, SM-2, structural analysis, gap detection)
- **Persistence**: SQLite + Markdown
- **Scraping**: BeautifulSoup4 + requests + yt-dlp
- **Testing**: pytest
- **Algorithms**: SM-2 (spaced repetition), CEFR detection, structural analysis, gap detection

## License

MIT
