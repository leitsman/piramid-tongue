# Skill: write

## Trigger
User says `/pt write` or `/pt-write`

## Purpose
Writing practice with 3 modes: transcription, creation, translation. Includes structural analysis and vicios detection.

## Steps

### Step 1: Check Profile for CEFR Level

1. Read `configs/profile.yml`
2. Get user's `level` (CEFR level)

### Step 2: Pre-Session Micro-Test

**SKILL: Load `skills/_shared/micro-test.md` before starting.**

1. Read `src/test_questions.py` y extrae `MICRO_TESTS["write"][level]`
2. Check if 'write' skill has < 100 XP in skills_progress table:
   ```bash
   sqlite3 data/progress.db "SELECT xp FROM skills_progress WHERE skill_name = 'write';"
   ```
3. If (skill_xp < 100) OR (user says "test me"):
   a. Get 4 random questions from `MICRO_TESTS["write"][level]`
   b. Present questions per _shared/micro-test.md
   c. If score >= 4/4: offer 2 bonus questions from next level
   d. Log result in today's daily log under `## Micro-Test: write`
4. Proceed to Step 3

### Step 3: Ask User to Choose Mode

Ask user which mode they want:
1. **Transcription** — Copy a text to practice handwriting/typing and observe sentence structure
2. **Creation** — Write original text on a given topic
3. **Translation** — Translate text from Spanish to English

### Step 4: Execute Chosen Mode

**Transcription Mode:**
1. Provide a short text (50-100 words) at user's CEFR level
2. User copies it by hand or types it
3. User notes any interesting patterns observed

**Creation Mode:**
1. Provide a writing prompt appropriate for user's level
2. User writes 50-200 words
3. Ask user to self-assess their writing

**Translation Mode:**
1. Provide a Spanish text (or ask user to provide one)
2. User translates to English
3. Discuss differences in structure/idioms

### Step 5: Track Vocabulary Usage for Repetition Count

After user submits their written text (creation or translation):

1. Extract all vocabulary words from the text
2. Query `vocab` table for matches:
   ```sql
   SELECT id, word, repetition_count FROM vocab WHERE status IN ('learning', 'new')
   ```
3. For each matched word used in the text:
   ```bash
   sqlite3 data/progress.db "UPDATE vocab SET repetition_count = repetition_count + 1 WHERE id = ${word_id};"
   ```
4. If any word reached repetition_count >= 100:
   - Update: `sqlite3 data/progress.db "UPDATE vocab SET status = 'acquired' WHERE id = ${word_id};"`
   - "🎉 Word '{word}' has been integrated into long-term memory (100+ uses)!"
5. Display summary:
   ```
   📝 Vocabulary Used Today:
   - Words used: {n}
   - New repetitions: {n}
   - Words now fully integrated (100+ reps): {n}
   - Total integrated: {n}
   ```

### Step 6: Structural Analysis

After user provides their text (creation or translation):

Apply structural analysis patterns **directly** (no Python module):

1. **Article overuse**: Count occurrences of `\bthe\b` vs total tokens. Flag if > 12%
2. **"very + adj"**: Count occurrences of `\bvery\s+\w+`
3. **"in order to"**: Count occurrences of `\bin\s+order\s+to\b`
4. **"a lot of"**: Count occurrences of `\b(a|an)\s+lot\s+of\b`
5. **"actually" filler**: Count `\bactually\b`
6. **Vague "thing"**: Count `\bthing\b`
7. **Run-on sentences**: Count sentences with > 3 conjunctions
8. **Sentence fragments**: Detect very short sentences without proper subject

Display results in natural language:
   ```
   📝 Structural Analysis:
   - Score: X/100
   - Issues found: [list with suggestions]
   - Main areas to improve: [summary]
   ```
5. If issues found, log in daily log under `## Structural Analysis`
6. **Auto-detection flow** (saves weaknesses silently):
   - For each detected issue with a specific word and error type:
     - Insert word-specific weakness via sqlite3:
       ```bash
       sqlite3 data/progress.db "INSERT INTO weaknesses (word, error_type, context_example, source, box_level, consecutive_correct, next_review) VALUES ('${word}', '${error_type}', '${context}', 'structural_analysis', 1, 0, date('now'));"
       ```
     - Log to daily log: `"Auto-detected weakness: {word} ({error_type})"`
   - **No confirmation prompt** — auto-saves silently
7. Ask user what to do next:
   ```
   Options after analysis:
   1. Continue to vicios detection
   2. Get detailed explanations of issues
   3. Práctica adaptativa mixta — basada en tus debilidades detectadas
   ```
8. If user selects option 3, follow **Step 7: Adaptive Mixed Practice**

### Step 7: Adaptive Mixed Practice (Option 3)

If user selects option 3:

1. **SKILL: Load `skills/_shared/adaptive-practice.md` before starting.**
2. **SKILL: Load `skills/_shared/exercise-design.md`** for exercise format guidelines.
3. Check for due reviews from weaknesses table:
   ```bash
   sqlite3 data/progress.db "SELECT id, word, error_type, context_example, box_level, consecutive_correct FROM weaknesses WHERE status = 'active' AND box_level < 5 AND (next_review IS NULL OR datetime(next_review) <= datetime('now')) ORDER BY box_level ASC, next_review ASC LIMIT 5;"
   ```
4. If due words found:
   - Read `src/test_questions.py`, extrae `EXERCISE_TEMPLATES[error_type]`
   - Generate 2 exercises per word usando los templates
   - Present mixed (shuffled) exercises following exercise-design.md
   - Update boxes via sqlite3 after each answer
5. If no due words:
   - "No words due for review today. Your weaknesses will be practiced when review is due."
6. Log results in daily log under "## Weakness Review"
7. After practice, proceed to Step 8 (Vicios Detection)

**Leitner Box Updates (via sqlite3):**
```bash
# Correct answer (+1 box, max 5, increment consecutive_correct)
sqlite3 data/progress.db "UPDATE weaknesses SET box_level = MIN(box_level + 1, 5), consecutive_correct = consecutive_correct + 1, last_practiced = datetime('now'), next_review = date('now', '+${interval} days') WHERE id = ${id};"
# Wrong answer minor (-1 box, min 1, reset consecutive)
sqlite3 data/progress.db "UPDATE weaknesses SET box_level = MAX(box_level - 1, 1), consecutive_correct = 0, last_practiced = datetime('now'), next_review = date('now', '+1 days') WHERE id = ${id};"
# Wrong answer major (-2 boxes, min 1, reset consecutive)
sqlite3 data/progress.db "UPDATE weaknesses SET box_level = MAX(box_level - 2, 1), consecutive_correct = 0, last_practiced = datetime('now'), next_review = date('now', '+1 days') WHERE id = ${id};"
# If box 5 + 3 consecutive correct → mastered
sqlite3 data/progress.db "UPDATE weaknesses SET status = 'mastered' WHERE id = ${id} AND box_level >= 5 AND consecutive_correct >= 3;"
```

### Step 8: Vicios Detection

1. Read `configs/vicios_patterns.yaml`
2. Analyze user's written text for patterns:
   - Repeated "the" (threshold: 0.12)
   - "very + adjective" (threshold: 0.05)
   - "in order to" (threshold: 0.02)
   - "a lot of" (threshold: 0.05)
   - "actually" filler (threshold: 0.03)
   - Vague "thing" (threshold: 0.08)
3. Report detected vicios with suggestions

### Step 9: Log Session and Update

1. Open `logs/YYYY-MM-DD.md` and append under "## Writing Exercise":
   ```markdown
   ## Writing Exercise
   
   **Session**: {YYYY-MM-DD HH:MM}
   **Mode**: {mode}
   **Topic**: {topic}
   **Structural Analysis**: Score {score}/100, Issues: {n}
   **Vicios detected**: {n}
   
   **Vocabulary Used**: {n} words used, {n} new repetitions
   **Words Integrated (100+ reps)**: {n}
   
   **XP Earned**: {n}
   ```

2. Update SQLite `sessions` table.

3. Update SQLite `skills_progress`:
   ```bash
   sqlite3 data/progress.db "UPDATE skills_progress SET xp = xp + ${xp_earned}, session_count = session_count + 1 WHERE skill_name = 'write';"
   ```

4. Award XP:
   - Transcription: 10 XP
   - Creation: 15-25 XP based on self-rating
   - Translation: 15 XP

5. Update streak in `configs/profile.yml` if this is the first session of the day:
   - Read current streak values from `configs/profile.yml`
   - Apply same streak logic as in `new-day.md` Step 3b:
     - If `last_active IS NULL`: set `current = 1`, `longest = 1`, `last_active = today`
     - If `last_active == today`: no change (already counted)
     - If `last_active == yesterday`: increment `current += 1`, update `longest` if needed, `last_active = today`
     - If `last_active < yesterday` (missed days): reset `current = 1`, `last_active = today`
   - Write updated values back to `configs/profile.yml`

## Writing Prompts by Level

**A1-A2:**
- "My day" (simple present)
- "My family" (basic descriptions)
- "What I did yesterday"

**B1:**
- "My goals for this year"
- "A memorable trip"
- "My opinion on [topic]"

**B2:**
- "The impact of technology on society"
- "A problem and its solution"
- "Should [controversial topic]?"

**C1-C2:**
- "Analyze the implications of [complex topic]"
- "Compare and contrast [two concepts]"
- "Argue for or against [nuanced position]"

## Vicios Patterns Reference

From `configs/vicios_patterns.yaml`:

| Pattern | Threshold | Suggestion |
|---------|-----------|------------|
| `\bthe\b` ( overuse) | 0.12 | Try 'a/an' or omit when appropriate |
| `\bvery\s+\w+` | 0.05 | Replace with stronger adjectives |
| `\bin\s+order\s+to\b` | 0.02 | Simplify to just 'to' |
| `\b(a\|an)\s+lot\s+of\b` | 0.05 | Use 'many', 'much', 'numerous' |

## What to Ask User

1. "Which mode? (transcription/creation/translation)"
2. For creation: "What's your topic?"
3. "How would you rate your writing?" (1-5)
4. "Paste your text for analysis"
