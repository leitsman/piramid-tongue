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

1. Import MICRO_TESTS from `src/test_questions.py`:
   ```python
   from src.test_questions import MICRO_TESTS, get_micro_tests_for_skill, get_bonus_questions_for_level
   ```
2. Check if read skill has < 100 XP in `skills_progress` table:
   ```sql
   SELECT xp FROM skills_progress WHERE skill_name = 'read'
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

1. Use `src/logs/writer.py` → LogWriter
2. Append to today's log under "## Reading Session":
   ```
   - Source: {title}, Duration: {n} min, Self-rating: {rating}/5, New words: {words}
   ```
3. Update SQLite `sessions` table
4. Update SQLite `skills_progress`:
   ```sql
   UPDATE skills_progress SET xp = xp + ?, session_count = session_count + 1 WHERE skill_name = 'read'
   ```
5. Award XP based on rating:
   - Rating 1: 5 XP
   - Rating 2: 10 XP
   - Rating 3: 15 XP
   - Rating 4: 20 XP
   - Rating 5: 30 XP

## Content Sources (from `src/scrapers/`)

| Source | Module | Level Range |
|--------|--------|-------------|
| BBC Learning English | `src/scrapers/bbc.py` | A1-B1 |
| Web articles | `src/scrapers/web.py` | B1-C2 |
| Books | `src/scrapers/books.py` | B1-C2 |

## What to Ask User

1. "What did you read?" (source + title)
2. "How long did you read?" (minutes)
3. "How well did you understand?" (1-5 rating)
4. "Any new words or phrases to add to vocab?"