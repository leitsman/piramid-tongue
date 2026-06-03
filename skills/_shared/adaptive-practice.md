# Shared Adaptive Practice Instructions

> This file is imported by skill files that support word-specific adaptive practice.
> **IMPORTANT**: This file now uses the Leitner box system and word-specific weakness tracking.
> For the old category-based flow, see git history.

## When to Use
- After structural analysis detects issues (in write mode) — auto-detection saves to weakness DB
- After micro-test shows weaknesses
- User explicitly says "I don't understand X" or "practicar X"

## Flow

### Step 1: Check Due Words (Leitner)
1. Read `src/test_questions.py` y extrae `EXERCISE_TEMPLATES` para generar ejercicios por error_type
2. Query due words from weaknesses table via sqlite3:
   ```bash
   sqlite3 data/progress.db "SELECT id, word, error_type, context_example, box_level, consecutive_correct FROM weaknesses WHERE status = 'active' AND box_level < 5 AND (next_review IS NULL OR datetime(next_review) <= datetime('now')) ORDER BY box_level ASC, next_review ASC LIMIT 5;"
   ```
3. If no due words and user didn't request practice → skip this flow
4. If due words exist → present as "Quick review before starting:"

### Step 2: Generate Exercises Per Word
For each due word:
1. Read `EXERCISE_TEMPLATES[error_type]` from `src/test_questions.py`
2. Select 2 random templates from the list
3. Each template is: `(question_template, correct_answer, [distractors])`
4. Build a list with 4 options: correct_answer + 3 distractors (shuffled)
5. Collect all exercises into a single list

### Step 3: Present Mixed Exercises (SHUFFLED)
1. **SKILL: Load `skills/_shared/exercise-design.md`** for format guidelines
2. Shuffle all exercises so error types are NOT grouped
3. Present ONE question at a time:
   ```
   Fill in the blank:

   "___ is raining heavily today."
   A) It  B) There  C) Here  D) This
   ```
4. **Do NOT reveal error_type to user** — no category labels shown
5. Wait for user's answer

### Step 4: Feedback (AFTER each answer)
After user answers:
1. Show immediate result:
   ```
   ✅ Correct! (expletive "it")
   ❌ Not quite. The correct answer is "might". ("might" expresses possibility)
   ```
2. For wrong answers: give 1 short explanation
3. **Do NOT reveal the category name**

### Step 5: Update Boxes
After all exercises:
1. For each answer, determine box movement:
   - correct=True → +1 box (max 5), increment consecutive_correct
   - correct=False, minor severity → -1 box (min 1), reset consecutive_correct
   - correct=False, major severity → -2 boxes (min 1), reset consecutive_correct
2. Severity determination:
   - If user's wrong answer was a plausible distractor → "minor"
   - If user's answer shows fundamental misunderstanding → "major"
3. Update via sqlite3:
   ```bash
   # Correct answer
   sqlite3 data/progress.db "UPDATE weaknesses SET box_level = MIN(box_level + 1, 5), consecutive_correct = consecutive_correct + 1, last_practiced = datetime('now'), next_review = date('now', '+${interval} days') WHERE id = ${id};"
   # Wrong answer
   sqlite3 data/progress.db "UPDATE weaknesses SET box_level = MAX(box_level - ${drop}, 1), consecutive_correct = 0, last_practiced = datetime('now'), next_review = date('now', '+1 days') WHERE id = ${id};"
   ```
   **Leitner intervals by box**: Box 1=1d, Box 2=2d, Box 3=4d, Box 4=7d, Box 5=14d

### Step 6: Retry Logic
After session:
1. Calculate score (correct / total)
2. If score < 50%:
   - Offer: "Want to try another set?"
   - Yes → generate new exercises for same words
   - No → save and continue
3. If score >= 50%:
   - "Good progress! Keep practicing."
   - Continue to next step

### Step 7: Update Database
- Box levels are already updated via sqlite3 (Step 5)
- Log results in daily log under "## Weakness Review"
- Mark as mastered if box 5 + 3 consecutive correct:
  ```bash
  sqlite3 data/progress.db "UPDATE weaknesses SET status = 'mastered' WHERE id = ${id} AND box_level >= 5 AND consecutive_correct >= 3;"
  ```

## Key Differences from Old Flow

| Old Flow | New Flow |
|----------|----------|
| Category-based (article_usage) | Word-specific ("the", "it") |
| Static MIXED_EXERCISE_BANKS | Dynamic `generate_exercises_for_word()` |
| increment_pass/fail | `update_box()` with Leitner intervals |
| pass_count >= 5 | box_level=5 + consecutive_correct>=3 |

## Integration Points

- `skills/write.md`: After structural analysis → auto-detects and saves to weakness DB
- `skills/new-day.md`: Between checks and recommendations → presents due words for review

## Exercise Templates Source

Use the `EXERCISE_TEMPLATES` dict from `src/test_questions.py` to generate exercises.
Each template has format: `(question_template, correct_answer, [distractors])`.
The AI reads the file directly (no Python execution).
