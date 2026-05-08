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

1. Import MICRO_TESTS from `src/test_questions.py`
2. Check if 'write' skill has < 100 XP in skills_progress table
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

### Step 5: Structural Analysis

After user provides their text (creation or translation):

1. Import `StructuralAnalyzer` from `src/analysis/structural.py`
2. Run `analyzer.analyze(text)` on the user's written text
3. Display results in natural language:
   ```
   📝 Structural Analysis:
   - Score: X/100
   - Issues found: [list with suggestions]
   - Main areas to improve: [summary]
   ```
4. If issues found, log in daily log under `## Structural Analysis`
5. Ask user what to do next:
   ```
   Options after analysis:
   1. Continue to vicios detection
   2. Get detailed explanations of issues
   3. Práctica adaptativa mixta — basada en tus debilidades detectadas
   ```
6. If user selects option 3, follow **Step 6: Adaptive Mixed Practice**

### Step 6: Adaptive Mixed Practice (Option 3)

If user selects option 3:

1. **SKILL: Load `skills/_shared/adaptive-practice.md` before starting.**
2. Query `weaknesses` table for active categories (from DB)
3. If weaknesses found:
   - Follow adaptive-practice.md flow (mixed exercises)
   - Update weaknesses table after completion
4. If no weaknesses:
   - "No weaknesses detected. Try the mixed exercises from these common areas:"
   - Generate a mixed set from MIXED_EXERCISE_BANKS (expletive_it, modal_might, preposition_by)
5. Log results in daily log under "## Adaptive Practice"
6. After practice, proceed to Step 7 (Vicios Detection)

### Step 7: Vicios Detection

1. Read `configs/vicios_patterns.yaml`
2. Analyze user's written text for patterns:
   - Repeated "the" (threshold: 0.12)
   - "very + adjective" (threshold: 0.05)
   - "in order to" (threshold: 0.02)
   - "a lot of" (threshold: 0.05)
   - "actually" filler (threshold: 0.03)
   - Vague "thing" (threshold: 0.08)
3. Report detected vicios with suggestions

### Step 8: Log Session and Update

1. Use `src/logs/writer.py` → LogWriter
2. Append to today's log under "## Writing Exercise":
   ```
   - Mode: {mode}, Topic: {topic}
   - Structural Analysis: Score {score}/100, Issues: {n}
   - Vicios detected: {n}
   ```
3. Update SQLite `sessions` table
4. Update SQLite `skills_progress`:
   ```sql
   UPDATE skills_progress SET xp = xp + ?, session_count = session_count + 1 WHERE skill_name = 'write'
   ```
5. Award XP:
   - Transcription: 10 XP
   - Creation: 15-25 XP based on self-rating
   - Translation: 15 XP

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
