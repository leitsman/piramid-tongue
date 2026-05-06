# Piramid-Tongue for AI Agents

> Your personal English learning pyramid — always tells you **what to do next**.

## Origin

Built by [santifer](https://santifer.io) after months of learning English without direction. The pyramid methodology provides structure: ascent (learning new skills) and descent (perfecting weak areas). Every session produces a clear recommendation.

**It will work out of the box, but it's designed to be made yours.** The pyramid adapts to your level, objectives, and platforms. You (AI Agent) can edit user files directly.

---

## Quick Start

1. **First time?** Run `/pt init` — I will execute the level test directly
2. **Start daily session:** `/pt new-day` or `/pt-new-day`
3. **Practice a skill:** `/pt vocab`, `/pt listen`, `/pt read`, `/pt write`, `/pt speak`

---

## Command Reference

| Command | Skill File | Description |
|---------|------------|-------------|
| `/pt init` | `skills/init.md` | Level test + profile setup |
| `/pt new-day` | `skills/new-day.md` | Start daily session + recommendations |
| `/pt vocab` | `skills/vocab.md` | Vocabulary (SRS review + new words) |
| `/pt listen` | `skills/listen.md` | Listening practice with self-rating |
| `/pt read` | `skills/read.md` | Reading comprehension exercises |
| `/pt write` | `skills/write.md` | Writing (transcription, creation, translation) |
| `/pt speak` | `skills/speak.md` | Speaking (read-aloud, shadowing, tandem) |
| `/pt practice` | `skills/practice.md` | Log external platform practice |
| `/pt progress` | `skills/progress.md` | ASCII pyramid + stats + streak |
| `/pt roadmap` | `skills/roadmap.md` | Next steps with dependencies + time |
| `/pt vicios` | `skills/vicios.md` | Analyze text for linguistic vices |

**Both syntaxes work:** `/pt new-day` (slash) and `/pt-new-day` (hyphen)

---

## Data Contract (CRITICAL)

**User Layer (NEVER auto-updated by AI unless explicitly requested):**
- `configs/profile.yml` — identity, level, objectives, streak, platforms
- `configs/vicios_patterns.yaml` — custom vice patterns
- `data/progress.db` — SQLite database (vocabulary, skills, sessions)
- `logs/YYYY-MM-DD.md` — daily markdown session logs

**System Layer (auto-updatable):**
- `src/` — all source code
- `skills/` — AI skill execution files
- `configs/config.yaml.example` — system configuration template

---

## How Commands Work (CRITICAL)

When the user says `/pt <command>`, I execute it **DIRECTLY**:

1. **I read** the corresponding `skills/<command>.md` file
2. **I follow** the instructions IN that file
3. **I update** `configs/profile.yml` and `data/progress.db` as needed
4. **I NEVER spawn a Python process** or run `python -m src.cli.main`

The AI IS the executor. The `skills/*.md` files contain instructions that I (the AI) carry out.

## AI Execution Model

AI agents read `skills/*.md` files to execute commands. When user says `/pt <command>`:

1. AI reads `skills/<command>.md` and `skills/_shared.md`
2. AI reads user data from `configs/profile.yml` and database
3. AI asks user for input when required
4. AI logs results to `logs/YYYY-MM-DD.md`
5. AI updates SQLite database
6. AI shows user results and next steps

---

## First Run Onboarding

**Before doing ANYTHING else, check if the system is set up:**

1. Does `configs/profile.yml` exist (not just profile.yml.example)?
2. Does `data/` directory exist with SQLite database?

**If profile is missing, enter onboarding mode:**

#### Step 1: Initialize Profile
I execute the level test **directly** following `skills/init.md`:
1. Ask user for their estimated CEFR level (A1-C2)
2. Offer an optional validation test
3. If test accepted: ask questions per level (5-7), verify answers via SHA256 hash
4. Save detected level to `configs/profile.yml`

#### Step 2: Configure Platforms
Edit `configs/profile.yml` if user wants to track external platforms:

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

---

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

### Dependencies

```
vocab: (unlocked)
read: requires vocab
listen: requires read
write: requires listen
speak: requires write
```

Skills require 100 XP in prerequisites before unlocking.

---

## CEFR Levels

- **A1** — Beginner (can use basic phrases)
- **A2** — Elementary (can handle simple transactions)
- **B1** — Intermediate (can deal with most travel situations)
- **B2** — Upper Intermediate (can interact with native speakers)
- **C1** — Advanced (can express ideas fluently)
- **C2** — Proficient (can match native speakers)

---

## Internal Level Test

The init command uses `src/test_questions.py` which contains:
- Questions per CEFR level (5-7 each)
- Answers stored as SHA256 hashes
- A1: basic be, articles, simple present
- A2: past tense, conditionals
- B1: past perfect, wish
- B2: inversion, gerunds
- C1: subjunctive, advanced inversion
- C2: if user passes C1, they reach C2

---

## Vicios Detection

The system detects common English writing vices:

| Vice | Example | Suggestion |
|------|---------|------------|
| Repeated "the" | "The the problem..." | "The problem..." |
| "very + adj" | "very good" | "excellent", "outstanding" |
| "I think that" | Repeated 3+ times | Vary: "I believe", "In my opinion" |
| "In order to" | "In order to improve" | "To improve" |
| "Due to the fact" | "Due to the fact that..." | "Because..." |
| "a lot of" | "a lot of people" | "many", "numerous" |

Patterns are configurable in `configs/vicios_patterns.yaml`.

---

**Remember:** The pyramid always tells you what to do next. Trust the flow.
