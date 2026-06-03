# Skill: read

## Trigger
User says `/pt read` or `/pt-read`

## Purpose
Reading practice with CEFR-appropriate texts and comprehension exercises.

## Steps

### Step 1: Check Profile for CEFR Level

1. Read `configs/profile.yml`
2. Get user's `level` (CEFR level)

### Pre-Session Micro-Test

**SKILL: Load `skills/_shared/micro-test.md` before starting.**

1. Read `src/test_questions.py` y extrae `MICRO_TESTS["read"][cefr_level]`
2. Check if read skill has < 100 XP in `skills_progress` table:
   ```bash
   sqlite3 data/progress.db "SELECT xp FROM skills_progress WHERE skill_name = 'read';"
   ```
3. If (read_xp < 100) OR (user says "test me" / "ponme a prueba"):
   a. Select 4 random questions from `MICRO_TESTS["read"][cefr_level]`
   b. Present questions one by one, wait for answer (A/B/C/D)
   c. Track score
   d. If score == 4/4: offer 2 bonus questions from next level
   e. Log result in today's daily log under "## Micro-Test: read"
   f. If score < 3/4: recommend practicing prerequisites (e.g., /pt vocab)
4. If read_xp >= 100 OR user says "skip": proceed to main session

### Step 2: Suggest Content by Level

Based on user's level, suggest appropriate reading:

**A1-A2 Level:**
- Simple stories with basic vocabulary
- Graded readers
- BBC Learning English articles
- Short news items with images

**B1 Level:**
- Intermediate articles
- Short stories
- Blog posts
- News with some unknown vocabulary

**B2 Level:**
- Newspaper articles
- Non-fiction books
- Academic texts (introductory)
- Opinion pieces

**C1-C2 Level:**
- Complex articles (The Economist, academic papers)
- Literary works
- Technical documentation
- Opinion columns with nuanced arguments

### Step 3: User Reads Text

1. User selects or reads provided content
2. User notes:
   - Source/title
   - Time spent reading
   - Unknown words/phrases

### Step 4: Comprehension Check

Ask user to rate comprehension (1-5):
1. Complete struggle (understood <30%)
2. Difficult (understood 30-50%)
3. Moderate (understood 50-70%)
4. Good (understood 70-90%)
5. Excellent (understood >90%)

### Step 5: Log Session and Update

1. Open `logs/YYYY-MM-DD.md` and append under "## Reading Session":
   ```markdown
   ## Reading Session
   
   **Session**: {YYYY-MM-DD HH:MM}
   **Source**: {title}
   **Duration**: {n} min
   **Self-rating**: {rating}/5
   
   **New Words / Phrases**: 
   - {word1}
   - {word2}
   
   **XP Earned**: {n}
   ```

2. Update SQLite `sessions` table.

3. Update SQLite `skills_progress`:
   ```bash
   sqlite3 data/progress.db "UPDATE skills_progress SET xp = xp + ${xp}, session_count = session_count + 1 WHERE skill_name = 'read';"
   ```

4. Award XP based on rating:
   - Rating 1: 5 XP
   - Rating 2: 10 XP
   - Rating 3: 15 XP
   - Rating 4: 20 XP
   - Rating 5: 30 XP

5. Update streak in `configs/profile.yml` if this is the first session of the day:
   - Read current streak values from `configs/profile.yml`
   - Apply same streak logic as in `new-day.md` Step 3b:
     - If `last_active IS NULL`: set `current = 1`, `longest = 1`, `last_active = today`
     - If `last_active == today`: no change (already counted)
     - If `last_active == yesterday`: increment `current += 1`, update `longest` if needed, `last_active = today`
     - If `last_active < yesterday` (missed days): reset `current = 1`, `last_active = today`
   - Write updated values back to `configs/profile.yml`

## Content Sources

| Source | Level Range |
|--------|-------------|
| BBC Learning English | A1-B1 |
| Web articles | B1-C2 |
| Books | B1-C2 |

## What to Ask User

1. "What did you read?" (source + title)
2. "How long did you read?" (minutes)
3. "How well did you understand?" (1-5 rating)
4. "Any new words or phrases to add to vocab?"