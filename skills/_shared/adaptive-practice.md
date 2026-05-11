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
1. Import `LeitnerEngine` from `src/core/leitner.py`
2. Import `generate_exercises_for_word` from `src/test_questions.py`
3. Initialize `LeitnerEngine` with DB path
4. Call `engine.get_due_reviews(limit=5)` to get words due for review
5. If no due words and user didn't request practice → skip this flow
6. If due words exist → present as "Quick review before starting:"

### Step 2: Generate Exercises Per Word
For each due word:
1. Call `generate_exercises_for_word(word, error_type, count=2)`
2. This creates 2 exercises per word using templates
3. Collect all exercises into a single list

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
1. For each answer: call `engine.update_box(weakness_id, correct, severity)`
   - correct=True → box advances +1
   - correct=False, minor severity → box drops -1
   - correct=False, major severity → box drops -2
2. Severity determination:
   - If user's wrong answer was a plausible distractor → "minor"
   - If user's answer shows fundamental misunderstanding → "major"

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
- Box levels are already updated via `engine.update_box()`
- Log results in daily log under "## Weakness Review"
- If box reaches 5 with consecutive_correct >= 3 → status = 'mastered'

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

## Deprecated

The old `get_mixed_exercise_set()` function and MIXED_EXERCISE_BANKS are deprecated.
Use `generate_exercises_for_word()` for all new exercise generation.
