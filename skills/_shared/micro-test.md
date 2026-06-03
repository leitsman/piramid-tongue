# Shared Micro-Test Instructions

> This file is imported by all skill files that support pre-session micro-tests.

## When to Run

- **Before starting any skill session** that has < 100 XP (skill not yet unlocked)
- **OR** if the user explicitly says "test me" / "ponme a prueba" / "test"
- **Skip** if the skill has >= 100 XP (already unlocked)
- **Skip** if the user says "skip" / "omitir" / "ya lo sé" — log as skipped in daily log

## Format

1. Show **4 questions** at the user's current CEFR level for this specific skill
2. Wait for each answer (A, B, C, or D)
3. Track score

## Question Source

- Read `src/test_questions.py` y extrae el dict `MICRO_TESTS`
- Select 4 random questions from `MICRO_TESTS[skill_name][cefr_level]`
- Each entry: `(question_text, [option_a, option_b, option_c, option_d], correct_index)`
- Select 2 bonus questions from the **next** CEFR level (if 4/4 correct)

## Results Interpretation

| Score | Message |
|-------|---------|
| **4/4 correct** | Offer 2 bonus harder questions (from next CEFR level) |
| **2/2 bonus correct** | "Excellent! You might be ready for the next level. Your skill level may be higher than [current]." |
| **1/2 or 0/2 bonus** | "Good! You're solid at [current level]." |
| **3/4 correct** | "Good, but review [weak area] to strengthen this skill." |
| **< 3/4 correct** | "You might want to practice prerequisites first. Consider /pt vocab or /pt read before this skill." |

## Micro-Test Flow Algorithm

```
1. Get user's CEFR level from configs/profile.yml
2. Check if skill has < 100 XP in skills_progress table
3. IF (skill_xp < 100) OR (user says "test me"):
   a. Select 4 random questions from MICRO_TESTS[skill][level]
   b. Present questions one by one
   c. Wait for user answer (A/B/C/D)
   d. Track correct answers
   e. IF score == 4:
      - Offer 2 bonus questions from MICRO_TESTS[skill][next_level]
      - IF bonus_score >= 2: suggest level may be higher
      - ELSE: confirm current level
   f. ELSE IF score >= 3:
      - Recommend focus areas
   g. ELSE:
      - Recommend prerequisites (vocab, read)
   h. Log result in today's daily log
4. IF skill_xp >= 100: skip micro-test, proceed to main session
5. IF user says "skip": log as skipped, proceed to main session
```

## Logging

Log micro-test results in daily log under `## Micro-Test`:

```
## Micro-Test: {skill}
- Level: {cefr_level}
- Score: {n}/4
- Bonus: {n}/2 (if applicable)
- Result: {passed/partial/failed/skipped}
- Recommendation: {text}
```

### Step 6: Save Weaknesses to Database

After showing results but BEFORE proceeding to main session:

1. For each INCORRECT answer in the micro-test:
   a. Map the question to a category using `QUESTION_CATEGORIES` from `src/test_questions.py`
   b. Save weakness via sqlite3:
      ```bash
      sqlite3 data/progress.db "INSERT INTO weaknesses (category, description, source, fail_count) VALUES ('${category}', '${description}', 'micro_test', 1) ON CONFLICT(category) DO UPDATE SET fail_count = fail_count + 1, last_practiced = datetime('now') WHERE status = 'active';"
      ```
   
2. If score < 3/4, note: "Weaknesses saved. You'll get adaptive practice for these areas."

## Skills Supporting Micro-Test

| Skill | File | Pre-Session Micro-Test |
|-------|------|------------------------|
| vocab | `skills/vocab.md` | Before Step 2 |
| read | `skills/read.md` | Before reading session |
| listen | `skills/listen.md` | Before listening session |
| speak | `skills/speak.md` | Before speaking session |

## Implementation in Skill Files

Each skill file should include:

```markdown
### Pre-Session Micro-Test

**SKILL: Load `skills/_shared/micro-test.md` before starting.**

1. Read `src/test_questions.py` y extrae MICRO_TESTS["{skill}"][level]
2. Check if this skill has < 100 XP:
   ```bash
   sqlite3 data/progress.db "SELECT xp FROM skills_progress WHERE skill_name = '{skill}';"
   ```
3. If (skill_xp < 100) OR (user says "test me"):
   a. Get user's CEFR level from profile.yml
   b. Select 4 random questions from MICRO_TESTS["{skill}"][level]
   c. Run micro-test per _shared/micro-test.md
   d. If score >= 4/4: offer 2 bonus questions from next level
   e. Log result in today's daily log
4. Proceed to main session
```
