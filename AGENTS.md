# Piramid-Tongue for AI Agents

> Your personal English learning pyramid — always tells you **what to do next**.

## Origin

Built by [santifer](https://santifer.io) after months of learning English without direction. The pyramid methodology provides structure: ascent (learning new skills) and descent (perfecting weak areas). Every session produces a clear recommendation.

**It will work out of the box, but it's designed to be made yours.** The pyramid adapts to your level, objectives, and platforms. You (AI Agent) can edit user files directly.

## Data Contract (CRITICAL)

**User Layer (NEVER auto-updated, personalization goes HERE):**
- `configs/profile.yml` — identity, level, objectives, streak, platforms
- `configs/vicios_patterns.yaml` — custom vice patterns
- `data/` — SQLite database (vocabulary, skills, sessions)
- `logs/` — daily markdown session logs

**System Layer (auto-updatable, DON'T put user data here):**
- `src/` — all source code
- `configs/config.yaml.example` — system configuration template
- `AGENTS.md`, `README.md`, `DESIGN.md`
- `tests/` — test suite

## What is piramid-tongue

English learning CLI with pyramid methodology. Track your journey from vocabulary to fluency.

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

## Commands Table

| Command | Description |
|---------|-------------|
| `/pt init` | Level test + profile setup |
| `/pt new-day` | Start daily session + get recommendations |
| `/pt vocab` | Vocabulary (learn new words / SRS review) |
| `/pt listen` | Listening practice |
| `/pt read` | Reading practice |
| `/pt write` | Writing practice (transcription, creation, translation) |
| `/pt speak` | Speaking practice (read-aloud, shadowing, tandem) |
| `/pt practice` | Log external platform practice |
| `/pt progress` | Visual pyramid + stats + streak |
| `/pt roadmap` | Next steps with dependencies and time estimates |
| `/pt vicios` | Analyze text for linguistic vices |

## First Run Onboarding

**Before doing ANYTHING else, check if the system is set up:**

1. Does `configs/profile.yml` exist (not just profile.yml.example)?
2. Does `data/` directory exist with SQLite database?

**If profile is missing, enter onboarding mode:**

#### Step 1: Initialize Profile
Ask the user to run:
```bash
python -m src.cli.main init
```

This runs the CEFR level test (A1-C2) for vocabulary, reading, listening, writing, and speaking.

#### Step 2: Configure Platforms
If the user uses external platforms (Duolingo, YoTalkTV, etc.), edit `configs/profile.yml`:

```yaml
platforms:
  - name: Duolingo
    metrics: { streak: 0, level: "" }
  - name: YoTalkTV
    metrics: { level: "", topics_completed: [] }
```

#### Step 3: Set Objectives
Ask the user about their learning goals:
- **Technical**: English for work/tech roles
- **Conversational**: Everyday English speaking
- **Both**: Combination of technical and conversational

Update `configs/profile.yml` with `objectives: [technical, conversational]` or similar.

#### Step 4: Ready
> "You're all set! Run `/pt new-day` to start your daily session and get recommendations based on your pyramid progress."

## Pyramid Methodology

### The Five Skills (bottom to top)

```
         Speak
        /     \
      Write   Speak
     /    \   /    \
  Listen  Write  Listen
    |   \/    \/
    |   /\    /\
    v  Read  Vocab
    └──────────────┘
```

| Level | Skill | Focus |
|-------|-------|-------|
| 1 | Vocab | Spaced repetition (SM-2), technical vocabulary |
| 2 | Read | CEFR-level texts, comprehension exercises |
| 3 | Listen | Content by level, timed sessions, self-rating |
| 4 | Write | 3 modes (transcription, creation, translation) + vicios |
| 5 | Speak | Read-aloud, shadowing, tandem reminders |

### Ascent (Learning New Skills)
When starting or at a new level: follow vocab → read → listen → write → speak

### Descent (Perfecting Weak Areas)
When you want to improve a skill: focus on that skill + its dependencies
- Improve listening? → Practice listening + reading + vocabulary

## Skill Modes

| If the user... | Mode |
|----------------|------|
| Starts a new day | `new-day` — daily recommendations |
| Adds vocabulary | `vocab` — SRS review, new words |
| Practices listening | `listen` — content suggestions, self-rating |
| Reads texts | `read` — level detection, comprehension |
| Writes text | `write` — vicios analysis, correction |
| Practices speaking | `speak` — read-aloud, shadowing |
| Logs platform practice | `practice` — external platform sync |
| Checks progress | `progress` — visual pyramid + streak |
| Plans next steps | `roadmap` — dependencies + estimates |
| Analyzes text | `vicios` — linguistic vice detection |

## Vicios Detection

The system detects common English writing vices:

| Vice | Example | Suggestion |
|------|---------|------------|
| Repeated "the" | "The the problem..." | "The problem..." |
| "very + adj" | "very good" | "excellent", "outstanding" |
| "I think that" | Repeated 3+ times | Vary: "I believe", "In my opinion" |
| "In order to" | "In order to improve" | "To improve" |
| "Due to the fact" | "Due to the fact that..." | "Because..." |

Patterns are configurable in `configs/vicios_patterns.yaml`.

---

**Remember:** The pyramid always tells you what to do next. Trust the flow.
