# Skill: speak

## Trigger
User says `/pt speak` or `/pt-speak`

## Purpose
Speaking practice with read-aloud, shadowing, and tandem reminders.

## Steps

### Step 1: Check Profile for CEFR Level

1. Read `configs/profile.yml`
2. Get user's `level` (CEFR level)

### Pre-Session Micro-Test

**SKILL: Load `skills/_shared/micro-test.md` before starting.**

1. Read `src/test_questions.py` y extrae `MICRO_TESTS["speak"][cefr_level]`
2. Check if speak skill has < 100 XP in `skills_progress` table:
   ```bash
   sqlite3 data/progress.db "SELECT xp FROM skills_progress WHERE skill_name = 'speak';"
   ```
3. If (speak_xp < 100) OR (user says "test me" / "ponme a prueba"):
   a. Select 4 random questions from `MICRO_TESTS["speak"][cefr_level]`
   b. Present questions one by one, wait for answer (A/B/C/D)
   c. Track score
   d. If score == 4/4: offer 2 bonus questions from next level
   e. Log result in today's daily log under "## Micro-Test: speak"
   f. If score < 3/4: recommend practicing prerequisites (e.g., /pt vocab, /pt read, /pt listen)
4. If speak_xp >= 100 OR user says "skip": proceed to main session

### Step 2: Ask User to Choose Mode

Ask user which mode they want:
1. **Read-aloud** — Read a text out loud to practice pronunciation
2. **Shadowing** — Listen and repeat simultaneously (mimicking intonation)
3. **Tandem** — Practice with a partner (set up reminders)

### Step 3: Execute Chosen Mode

**Read-aloud Mode:**
1. Provide or ask for a text at user's level
2. User reads out loud
3. User self-assesses: What was hard? Which words?

**Shadowing Mode:**
1. Provide audio/video content with transcript
2. User listens to a sentence, immediately repeats
3. User tries to match pace and intonation
4. Repeat for 5-10 segments

**Tandem Mode:**
1. Ask user if they have a tandem partner
2. Set reminders for tandem sessions
3. Suggest conversation topics

### Step 4: Self-Rating

Ask user to rate their speaking (1-5):
1. Complete struggle (barely could speak)
2. Difficult (many pauses, pronunciation issues)
3. Moderate (some pauses, generally understandable)
4. Good (few pauses, clear pronunciation)
5. Excellent (fluent, natural intonation)

### Step 5: Log Session and Update

1. Open `logs/YYYY-MM-DD.md` and append under "## Speaking Drill":
   ```markdown
   ## Speaking Drill
   
   **Session**: {YYYY-MM-DD HH:MM}
   **Mode**: {mode}
   **Duration**: {n} min
   **Self-rating**: {rating}/5
   
   **Challenging Words/Sounds**:
   - {word1}
   - {word2}
   
   **XP Earned**: {n}
   ```

2. Update SQLite `sessions` table.

3. Update SQLite `skills_progress`:
   ```bash
   sqlite3 data/progress.db "UPDATE skills_progress SET xp = xp + ${xp}, session_count = session_count + 1 WHERE skill_name = 'speak';"
   ```

4. Award XP:
   - Read-aloud: 10-20 XP based on self-rating
   - Shadowing: 15-25 XP based on self-rating
   - Tandem: 20-30 XP based on self-rating

5. Update streak in `configs/profile.yml` if this is the first session of the day:
   - Read current streak values from `configs/profile.yml`
   - Apply same streak logic as in `new-day.md` Step 3b:
     - If `last_active IS NULL`: set `current = 1`, `longest = 1`, `last_active = today`
     - If `last_active == today`: no change (already counted)
     - If `last_active == yesterday`: increment `current += 1`, update `longest` if needed, `last_active = today`
     - If `last_active < yesterday` (missed days): reset `current = 1`, `last_active = today`
   - Write updated values back to `configs/profile.yml`

## Shadowing Sources

| Source | Level | Notes |
|--------|-------|-------|
| ESLPod | A1-B1 | Slow, clear speech |
| BBC Learning English | A1-B2 | Structured content |
| TED Talks | B1-C2 | Various accents |
| Native podcasts | B2-C2 | Natural speed |

## Read-aloud Texts by Level

**A1-A2:**
- Simple sentences
- Dialogues with basic phrases
- Children's stories

**B1-B2:**
- News headlines
- Short articles
- Dialogues with varied emotions

**C1-C2:**
- Literary excerpts
- Speeches
- Complex argumentative texts

## What to Ask User

1. "Which mode? (read-aloud/shadowing/tandem)"
2. "What did you practice?" (text/topic/source)
3. "How long did you practice?" (minutes)
4. "How would you rate your speaking?" (1-5)
5. "Any specific sounds or words that were challenging?"

## Tandem Partner Tips

If user doesn't have a tandem partner, suggest:
- Tandem.org
- HelloTalk app
- Local language exchange groups
- Video call with a friend who wants to learn Spanish