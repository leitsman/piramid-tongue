# Skill: vocab

## Trigger
User says `/pt vocab` or `/pt-vocab`

## Purpose
Vocabulary practice with 3 progressive levels, SM-2 spaced repetition, and Anki-style testing.

## 3 Levels of Vocab

| Level | Name | Words | Complete |
|-------|------|-------|----------|
| 1 | Basic vocabulary | Primeras 1000 palabras | 90% con 100 repeticiones |
| 2 | Intermediate vocabulary | Siguientes 1000 palabras | 90% con 100 repeticiones |
| 3 | Technical + Extra | Palabras técnicas + extras | % según palabras con 100 reps |

## Steps

### Step 1: Check Profile and Vocab Level

1. Read `configs/profile.yml` for CEFR level and objectives (technical/conversational)
2. Query current vocab progress:
   ```sql
   SELECT vocab_level, COUNT(*) as total, 
          SUM(CASE WHEN repetition_count >= 100 THEN 1 ELSE 0 END) as integradas
   FROM vocab 
   WHERE technical = 0
   GROUP BY vocab_level
   ```
3. Calculate completion % for each level

### Step 2: Pre-Session Micro-Test

**SKILL: Load `skills/_shared/micro-test.md` before starting.**

1. Import MICRO_TESTS from `src/test_questions.py`
2. Check if vocab skill has < 100 XP in `skills_progress` table
3. If (vocab_xp < 100) OR (user says "test me"):
   a. Select 4 random questions from MICRO_TESTS["vocab"][cefr_level]
   b. Present one by one, wait for answer (A/B/C/D)
   c. Track score
   d. If score >= 4/4: offer 2 bonus from next level
   e. Log result in daily log
4. If vocab_xp >= 100 OR "skip": proceed to Step 3

### Step 3: Anki-Style Review Session

1. Query words from current active level:
   ```sql
   SELECT * FROM vocab 
   WHERE vocab_level = {current_level} 
     AND (status = 'learning' OR status = 'new')
     AND (last_review IS NULL OR datetime('now') >= datetime(last_review, '+' || interval || ' days'))
   ORDER BY last_review ASC
   LIMIT 15
   ```

2. **Anki-style test:**
   - Show: "Word: {definition}" (la definición/la palabra en español)
   - User says the word in English
   - AI verifies:
     - If correct: SM-2 update (rating 3-5)
     - If wrong: Show correct answer, SM-2 reset (rating 1-2)

3. Apply SM-2 formula from `src/core/spaced_repetition.py`:
   ```
   If rating < 3: interval = 1, ease_factor -= 0.2
   If rating >= 3: interval = interval * ease_factor, ease_factor += 0.1
   ```

4. Update `vocab` table with new interval and ease_factor:
   ```sql
   UPDATE vocab SET interval = ?, ease_factor = ?, last_review = datetime('now'), status = 'learning' WHERE id = ?
   ```

### Step 4: New Words (if user wants)

1. Ask user if they want to add new words
2. **Source A — User provides words:**
   - User pastes or types words with definitions
   - AI adds to database:
     ```sql
     INSERT INTO vocab (word, definition, example, vocab_level, ceFR_level, status)
     VALUES (?, ?, ?, {auto_level}, ?, 'new')
     ```
   - Auto-assign level:
     - Count words in nivel 1: `SELECT COUNT(*) FROM vocab WHERE vocab_level = 1 AND technical = 0`
     - Count words in nivel 2: `SELECT COUNT(*) FROM vocab WHERE vocab_level = 2 AND technical = 0`
     - If nivel 1 count < 1000 → assign level 1
     - Else if nivel 2 count < 1000 → assign level 2
     - Else → assign level 3
   
3. **Source B — AI suggests words based on user objectives:**
   - If objective includes 'technical': suggest tech/industry words
   - If objective includes 'conversational': suggest everyday words
   - Ask user to confirm each suggestion

4. **Technical words:**
   - When adding, ask if it's "technical" (bandera)
   - If yes: technical = 1 → va a nivel 3

### Step 5: Show Progress

Show vocab level summary:
```
📊 Vocab Progress

Nivel 1 (Basic): {integrated}/{total} words integrated → {pct}% (needs 90% to complete)
Nivel 2 (Intermediate): {integrated}/{total} words integrated → {pct}%
Nivel 3 (Technical): {integrated}/{total} words integrated → {pct}%

🔄 Next review: {count} words due for SM-2 review
```

### Step 6: Log Session

1. Append to `logs/YYYY-MM-DD.md`:
   ```
   ## Vocab Review
   - Level: {vocab_level}
   - Words reviewed: {n} (SM-2)
   - New words added: {n}
   - XP earned: {n}
   ```

2. Insert into `sessions` table

3. Update `skills_progress`:
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

## XP Awards

- SM-2 review word: 2 XP per word
- New word added: 5 XP
- Technical word added: 10 XP

## What to Ask User

1. "What is the English for: {definition}?" (Anki-style)
2. "Rate your recall: 1 (forgot) to 5 (perfect)"
3. "Want to add new words?"
4. "Is this word technical?" (for new words)
