# Skill: vocab

## Trigger
User says `/pt vocab` or `/pt-vocab`

## Purpose
Vocabulary practice with spaced repetition (SM-2) and new word learning.

## Steps

### Step 1: Check Profile and CEFR Level

1. Read `configs/profile.yml`
2. Get user's `level` (CEFR level: A1, A2, B1, B2, C1, C2)

### Pre-Session Micro-Test

**SKILL: Load `skills/_shared/micro-test.md` before starting.**

1. Import MICRO_TESTS from `src/test_questions.py`:
   ```python
   from src.test_questions import MICRO_TESTS, get_micro_tests_for_skill, get_bonus_questions_for_level
   ```
2. Check if vocab skill has < 100 XP in `skills_progress` table:
   ```sql
   SELECT xp FROM skills_progress WHERE skill_name = 'vocab'
   ```
3. If (vocab_xp < 100) OR (user says "test me" / "ponme a prueba"):
   a. Select 4 random questions from `MICRO_TESTS["vocab"][cefr_level]`
   b. Present questions one by one, wait for answer (A/B/C/D)
   c. Track score
   d. If score == 4/4: offer 2 bonus questions from next level
   e. Log result in today's daily log under "## Micro-Test: vocab"
   f. If score < 3/4: recommend practicing prerequisites (e.g., /pt vocab basics)
4. If vocab_xp >= 100 OR user says "skip": proceed to main session

### Step 2: Check for Words Due for Review (SM-2 Algorithm)

1. Read `src/core/spaced_repetition.py` for SM-2 algorithm
2. Query SQLite `vocab` table for words due:
   ```sql
   SELECT * FROM vocab 
   WHERE status = 'learning' 
   AND (last_review IS NULL OR datetime('now') >= datetime(last_review, '+' || interval || ' days'))
   ORDER BY last_review ASC
   LIMIT 20
   ```

### Step 3: Present Review or Learning Mode

**If words are due for review:**
1. Show user each word with definition and example
2. Ask user to rate recall: 1 (forgot), 2 (hard), 3 (good), 4 (easy), 5 (perfect)
3. Apply SM-2 formula:
   - If rating < 3: interval = 1, ease_factor -= 0.2
   - If rating >= 3: interval = interval * ease_factor, ease_factor += 0.1
4. Update `vocab` table with new interval and ease_factor

**If no words due, offer new words:**
1. Query for new words at user's CEFR level:
   ```sql
   SELECT * FROM vocab WHERE status = 'new' AND cefr_level = ? ORDER BY RANDOM() LIMIT 10
   ```
2. Present words with definition and example
3. Ask user to confirm they've learned it → mark as 'learning'

### Step 4: Log Session

1. Open `logs/YYYY-MM-DD.md` and append under "## Vocab Review":
   ```
   - Reviewed {n} words, {m} new words learned. Rating distribution: ...
   ```
3. Update SQLite `sessions` table:
   ```sql
   INSERT INTO sessions (skill_name, duration_seconds, self_rating, notes) VALUES ('vocab', ?, ?, ?)
   ```
4. Update SQLite `skills_progress`:
   ```sql
   UPDATE skills_progress SET xp = xp + ?, session_count = session_count + 1 WHERE skill_name = 'vocab'
   ```

## SM-2 Algorithm Reference

From `src/core/spaced_repetition.py`:

```
EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
where q = quality of response (0-5)

If q < 3: repetitions = 0, interval = 1
If q >= 3:
  - If repetitions = 0: interval = 1
  - If repetitions = 1: interval = 6
  - Else: interval = interval * EF
```

## What to Ask User

1. "Do you have words to review today?" (yes/no)
2. "How well did you remember each word?" (1-5 scale)
3. "Want to learn new words?" (yes/no)

## XP Awards

- Review session: 5-15 XP based on performance
- New word learned: 5 XP