# Piramid-Tongue Skills — Internal AI Execution

> **IMPORTANT**: These skills are read by AI agents to execute commands directly. When user says `/pt <command>` or `/pt-<command>`, AI reads the corresponding skill file and follows the instructions.

## Command Routing

| User Input | Skill File | Internal Command |
|------------|------------|-----------------|
| `/pt new-day` or `/pt-new-day` | `skills/new-day.md` | `new-day` |
| `/pt vocab` or `/pt-vocab` | `skills/vocab.md` | `vocab` |
| `/pt listen` or `/pt-listen` | `skills/listen.md` | `listen` |
| `/pt read` or `/pt-read` | `skills/read.md` | `read` |
| `/pt write` or `/pt-write` | `skills/write.md` | `write` |
| `/pt speak` or `/pt-speak` | `skills/speak.md` | `speak` |
| `/pt practice` or `/pt-practice` | `skills/practice.md` | `practice` |
| `/pt progress` or `/pt-progress` | `skills/progress.md` | `progress` |
| `/pt roadmap` or `/pt-roadmap` | `skills/roadmap.md` | `roadmap` |
| `/pt vicios` or `/pt-vicios` | `skills/vicios.md` | `vicios` |
| `/pt init` or `/pt-init` | `skills/init.md` | `init` |

## Data Contract (CRITICAL)

**User Layer (NEVER auto-updated by AI unless explicitly requested):**
- `configs/profile.yml` — identity, level, objectives, streak, platforms
- `configs/vicios_patterns.yaml` — custom vice patterns
- `data/progress.db` — SQLite database (vocabulary, skills, sessions)
- `logs/YYYY-MM-DD.md` — daily markdown session logs

**System Layer (auto-updatable by AI):**
- `src/` — all source code
- `skills/` — skill instruction files (this directory)
- `configs/config.yaml.example` — system configuration template

## Pyramid Context

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

## CEFR Levels

- **A1** — Beginner (can use basic phrases)
- **A2** — Elementary (can handle simple transactions)
- **B1** — Intermediate (can deal with most travel situations)
- **B2** — Upper Intermediate (can interact with native speakers)
- **C1** — Advanced (can express ideas fluently)
- **C2** — Proficient (can match native speakers)

## Vicios Detection Patterns

| Vice | Example | Suggestion |
|------|---------|------------|
| Repeated "the" | "The the problem..." | "The problem..." |
| "very + adj" | "very good" | "excellent", "outstanding" |
| "I think that" | Repeated 3+ times | Vary: "I believe", "In my opinion" |
| "In order to" | "In order to improve" | "To improve" |
| "Due to the fact" | "Due to the fact that..." | "Because..." |
| "a lot of" | "a lot of people" | "many", "numerous" |
| "actually" | "actually, I think..." | Often unnecessary or use "in fact" |
| "thing" | "the thing is..." | Be specific about what thing |

Patterns are configured in `configs/vicios_patterns.yaml`.

## Key Implementation Files

| File | Purpose |
|------|---------|
| `src/core/config.py` | Config class for loading profile settings |
| `src/core/pyramid_engine.py` | PyramidState class with skill dependencies |
| `src/core/spaced_repetition.py` | SM-2 algorithm implementation |
| `src/core/leitner.py` | Leitner box system for weakness tracking |
| `src/db/__init__.py` | DB class for SQLite operations |
| `src/db/schema.sql` | Database schema |
| `src/logs/writer.py` | LogWriter class (utility — AI writes logs directly to markdown) |
| `src/test_questions.py` | Hidden level test with SHA256-hashed answers |
| `src/analysis/structural.py` | Rule-based writing analysis |
| `src/platforms/gap_detector.py` | Platform-vs-skill gap detection |

## AI Execution Workflow

1. User triggers `/pt <command>`
2. AI reads `skills/<command>.md` and `skills/_shared.md`
3. AI reads user data from `configs/profile.yml` and database
4. AI asks user for input when required
5. AI logs results to `logs/YYYY-MM-DD.md`
6. AI updates SQLite database
7. AI shows user results and next steps

## Onboarding Flow (First Run)

When `configs/profile.yml` has `level: null` or doesn't exist:

1. Tell user: "Let's set up your profile first!"
2. Execute `/pt init` by reading `skills/init.md` and following the instructions
3. The init skill runs the adaptive level test directly
4. After init, user should run `/pt new-day`

## Internal Test for Init

The init command uses `src/test_questions.py` which contains:
- Questions per CEFR level (5-7 each)
- A1: basic be, articles, simple present
- A2: past tense, conditionals
- B1: past perfect, wish
- B2: inversion, gerunds
- C1: subjunctive, advanced inversion
- C2: advanced idioms, complex structures

Answers are stored as SHA256 hashes for validation.

## Dependencies

```
PYRAMID_DEPENDENCIES = {
    "vocab": [],
    "read": ["vocab"],
    "listen": ["read"],
    "write": ["listen"],
    "speak": ["write"],
}
UNLOCK_XP_THRESHOLD = 100
```

Skills require 100 XP in prerequisites before unlocking.