# Skill: new-day

## Trigger
User says `/pt new-day` or `/pt-new-day`

## Purpose
Start a daily session, check progress, and recommend 2-3 skills to practice.

## Steps

### Step 1: Check Profile Existence

1. Read `configs/profile.yml`
2. If `level` is `null` or file doesn't exist:
   - Tell user: "Let's set up your profile first! Run `/pt init` or `/pt-init` to set up your profile."
   - Stop here

### Step 2: Read Previous Logs

1. Check `logs/` directory for existing log files
2. Read the most recent log (if any) to understand what was practiced yesterday
3. Get streak information from `configs/profile.yml`

### Step 3: Read SQLite Data for Skill Levels

1. Initialize DB from `src/db/__init__.py` → DB class
2. Query `skills_progress` table for all skills:
   ```sql
   SELECT skill_name, level, xp, session_count, last_practiced FROM skills_progress
   ```
3. Query `vocab` table for words due for review:
   ```sql
   SELECT COUNT(*) FROM vocab WHERE status = 'learning' AND (last_review IS NULL OR datetime('now') >= datetime(last_review, '+' || interval || ' days'))
   ```

### Step 3b: Update Streak

Before displaying the streak, update it based on `last_active`:

1. Read `configs/profile.yml` to get current streak values
2. Get today's date in YYYY-MM-DD format
3. Compare `last_active` with today:
   - If `last_active IS NULL` (first time): set `current = 1`, `longest = 1`, `last_active = today`
   - If `last_active == today`: do NOT change (already counted for today)
   - If `last_active == yesterday`: increment `current += 1`, update `longest` if needed, `last_active = today`
   - If `last_active < yesterday` (missed days): reset `current = 1`, `last_active = today`
4. Write the updated values back to `configs/profile.yml`:
   ```yaml
   streak:
     current: {new_current}
     longest: {new_longest}
     last_active: {today}
   ```
5. Use the NEW current/longest values for the display in Step 4

### Step 4: Display Streak and Level

Show user current status:
```
🏔️  Buenos días! 

📊 Current streak: {streak} days
🎯 Your level: {CEFR level}
```

### Step 5: Self-Report Diagnostic

Ask the user:
> "Before we start — what felt hardest in your last session? Or is there any area where you feel stuck? (Be specific — grammar, vocabulary, sentence structure, pronunciation, etc.)"

Wait for response.

Analyze the response:
- Identify skill area (vocab/read/listen/write/speak)
- Identify specific difficulty
- Adjust today's recommendations based on this

If user says "nothing" / "todo bien" / "skip" / "omitir" → proceed with normal recommendations.

### Step 5b: Weakness Review (NEW — Between checks and recommendations)

1. Import `LeitnerEngine` from `src/core/leitner.py`
2. Import `generate_exercises_for_word` from `src/test_questions.py`
3. Initialize `LeitnerEngine` with DB
4. Query due words: `engine.get_due_reviews(limit=5)`
5. If no due words: skip to Step 6 (no interruption to flow)
6. If due words exist: present "Quick review before starting:"
   - For each due word, generate 2 exercises via `generate_exercises_for_word()`
   - Present mixed (shuffled) exercises
   - Process user's answers
   - Update boxes via `engine.update_box()` — correct=+1, fail minor=-1, fail major=-2
   - Log results in daily log under "## Weakness Review"
7. If score < 50%, offer retry with new exercises
8. If >= 50%, continue to recommendations

### Step 6: Platform-Pyramid Gap Display

If user has platforms configured in profile.yml:
1. Import `PyramidState` from `src/core/pyramid_engine.py`
2. Build pyramid_skills dict from DB query
3. Run `pyramid_state.get_gap_report(profile_data, pyramid_skills)`
4. If gaps found (gaps list not empty), show:
   ```
   ⚠️ Gap Detected:
   
   Your [Platform] progress suggests [CEFR level], but your [Skill] is at [lower level].
   This means you're consuming content but not applying it enough.
   
   Today I recommend focusing on: [affected skill]
   ```
5. If no gaps or platforms empty: skip this section

### Step 8: Calculate Skills Needing Attention

Use pyramid engine from `src/core/pyramid_engine.py`:

1. **Priority calculation** (with gap influence):
   - Skills with gaps (from Step 6) get highest priority
   - Skills with lowest XP
   - Skills not practiced recently (longest time since `last_practiced`)
   - Skills with lowest CEFR level
   - Dependencies not met

2. **Recommendation logic**:
   - If vocab words due for review → include vocab
   - If a skill is blocked → include its dependencies first
   - If ascending: recommend vocab → read → listen → write → speak in order
   - If descending (user wants to improve specific skill): recommend that skill + its dependencies
   - Gap detection modifies priority: affected skills rise to top

3. **Output 2-3 recommended commands** based on:
   - Current streak status
   - User's objectives (technical/conversational)
   - Self-reported difficulty (from Step 5)
   - Gap detection results (from Step 6)
   - Time of day (morning = vocab/listen, afternoon = read/write, evening = speak)

### Step 9: Create Today's Log

1. Open `logs/YYYY-MM-DD.md` and create the log file if it doesn't exist:
   ```markdown
   # Log for {date}
   
   ## Vocab Review
   -
   
   ## Listening Practice
   -
   
   ## Reading Session
   -
   
   ## Writing Exercise
   -
   
   ## Speaking Drill
   -
   
   ## Weakness Review
   -
   
   ## Notes
   -
   ```
### Step 10: Show User Recommendations

Output format:
```
🏔️  Buenos días! Based on your progress...

📊 Current streak: {streak} days
🎯 Your level: {CEFR level}

{Self-Report Response Analysis if provided}
{Gap Detection Warning if applicable}

Today I recommend:
1. /pt vocab — {reason}
2. /pt read — {reason}
3. /pt listen — {reason}

Ready to start? Just say /pt vocab, /pt read, etc.
```

## What to Update After Sessions

After user completes a session, update:
1. SQLite `skills_progress` table with new XP
2. SQLite `sessions` table with session info
3. Today's log with session notes
4. `configs/profile.yml` streak if applicable
