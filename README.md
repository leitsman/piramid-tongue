# Piramid-Tongue

English learning CLI with pyramid methodology. Track your journey from vocabulary to fluency.

> Spent months learning English without direction. So I built the system that always tells you **what to do next**.

## How It Works

```
You run /pt init (level test)
        │
        ▼
┌──────────────────┐
│  Pyramid Engine  │  vocab → listen → read → write → speak
└────────┬─────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
 Daily  CEFR  Vicios
 Log    Level  Detection
```

**Two flows:**
- 🟢 **Ascent (learning)**: vocabulary → reading → listening → writing → speaking
- 🔴 **Descent (perfecting)**: want to improve listening? Focus on listening + reading + vocabulary

## Features

| Feature | Description |
|---------|-------------|
| **Level Test** | Initial CEFR evaluation (A1-C2) per skill |
| **Daily Tracker** | `/pt new-day` — start session, get recommendations based on progress |
| **Vocabulary** | Spaced repetition (SM-2), technical vocab support |
| **Listening** | Content by CEFR level, timed sessions, self-rating |
| **Reading** | Texts by level, comprehension exercises |
| **Writing** | 3 modes (transcription, creation, translation) + vicios detection |
| **Speaking** | Read-aloud, shadowing, tandem reminders |
| **Vicios Detection** | Detects repeated words, weak intensifiers, redundant phrases |
| **External Platforms** | Track Duolingo, courses, any resource you use |
| **Content Sources** | BBC Learning English, YouTube transcripts, public books, web scraping |
| **Progress Pyramid** | Visual ASCII pyramid showing your level per skill |
| **Streak Tracking** | Daily consistency counter |

## Quick Start

### 1. Clone and install

```bash
git clone <your-repo>
cd piramid-tongue

# Create virtual environment
python -m venv .venv

# Activate it
# Windows (cmd/PowerShell):
.venv\Scripts\activate
# Windows (Git Bash):
source .venv/Scripts/activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Check setup

```bash
python -m pytest --tb=short -q
```

### 3. Initialize your profile

```bash
python -m src.cli.main init
```

The level test evaluates your vocabulary, reading, listening, writing, and speaking. You can skip it if you already know your CEFR level.

### 4. Configure your profile

Edit `configs/profile.yml` with your details, objectives, and external platforms:

```yaml
user:
  name: Your Name
  objectives: ["technical", "conversational"]
  
platforms:
  - name: Duolingo
    url: https://duolingo.com
    metrics: { streak: 0, level: "" }
  - name: YoTalkTV
    url: https://youtube.com/youtalktv
    metrics: { level: "", topics_completed: [] }
```

### 5. Start learning

```bash
# Start your first day
python -m src.cli.main new-day

# Follow the recommendations
python -m src.cli.main vocab
python -m src.cli.main listen
python -m src.cli.main read

# Check your progress
python -m src.cli.main progress
python -m src.cli.main roadmap
```

## Commands

| Command | Description |
|---------|-------------|
| `pt init` | Level test + profile setup |
| `pt new-day` | Start daily session + get recommendations |
| `pt vocab` | Vocabulary (learn new words / SRS review) |
| `pt listen` | Listening practice |
| `pt read` | Reading practice |
| `pt write` | Writing practice (transcription, creation, translation) |
| `pt speak` | Speaking practice (read-aloud, shadowing, tandem) |
| `pt practice` | Log external platform practice |
| `pt progress` | Visual pyramid + stats + streak |
| `pt roadmap` | Next steps with dependencies and time estimates |
| `pt vicios` | Analyze text for linguistic vices |

## Vicios Detection

The system detects common English writing vices:

| Vice | Example | Suggestion |
|------|---------|------------|
| Repeated "the" | "The the problem..." | "The problem..." |
| "very + adj" | "very good" | "excellent", "outstanding" |
| "I think that" | Repeated 3+ times | Vary: "I believe", "In my opinion" |
| "In order to" | "In order to improve" | "To improve" |
| "Due to the fact" | "Due to the fact that..." | "Because..." |
| Sentence starters | Always starting with "I" or "The" | Vary sentence structure |
| Overused verbs | Too much "get", "make", "do" | Use more specific verbs |
| Redundant phrases | "free gift", "end result" | Remove redundancy |

Patterns are configurable in `configs/vicios_patterns.yaml`. Add your own!

## Project Structure

```
piramid-tongue/
├── configs/
│   ├── profile.yml          # Your profile and platforms
│   ├── vicios_patterns.yaml # Configurable vices detection
│   └── config.yaml.example  # System configuration template
├── src/
│   ├── cli/commands/        # CLI commands (Typer)
│   ├── core/                # Pyramid engine, SM-2, CEFR detection
│   ├── db/                  # SQLite schema and CRUD
│   ├── scrapers/            # BBC, YouTube, Books, Web
│   ├── logs/                # Daily markdown logs
│   └── skills/              # Skill modules
├── tests/                   # 102 passing tests
├── logs/                    # Daily session logs (gitignored)
├── data/                    # SQLite database (gitignored)
└── requirements.txt
```

## Persistence

| Layer | Format | Content |
|-------|--------|---------|
| **Logs** | Markdown (`logs/YYYY-MM-DD.md`) | Daily session records, human-readable |
| **Stats** | SQLite (`data/progress.db`) | Vocabulary, skills, vicios, sessions — queryable |
| **Config** | YAML | Profile, platforms, vicios patterns |

## Tech Stack

- **CLI**: Python + Typer
- **Persistence**: SQLite + Markdown
- **Scraping**: BeautifulSoup4 + requests + yt-dlp
- **Testing**: pytest
- **Algorithms**: SM-2 (spaced repetition), CEFR detection, vicios frequency analysis

## License

MIT
