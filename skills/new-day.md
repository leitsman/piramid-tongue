# Skill: new-day

## Trigger
User says `/pt new-day` or `/pt-new-day`

## Purpose
Start a daily session, check progress, and recommend 2-3 skills to practice.

## Steps

### Step 1: Check Profile Existence

1. Read `configs/profile.yml`
2. If `level` is `null` or file doesn't exist:
   - Tell user: "Let's set up your profile first! Run `python -m src.cli.main init` to start."
   - Stop here

### Step 2: Read Previous Logs

1. Check `logs/` directory for existing logs using LogWriter from `src/logs/writer.py`
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

### Step 4: Calculate Skills Needing Attention

Use pyramid engine from `src/core/pyramid_engine.py`:

1. **Priority calculation**:
   - Skills with lowest XP
   - Skills not practiced recently (longest time since `last_practiced`)
   - Skills with lowest CEFR level
   - Dependencies not met

2. **Recommendation logic**:
   - If vocab words due for review → include vocab
   - If a skill is blocked → include its dependencies first
   - If ascending: recommend vocab → read → listen → write → speak in order
   - If descending (user wants to improve specific skill): recommend that skill + its dependencies

3. **Output 2-3 recommended commands** based on:
   - Current streak status
   - User's objectives (technical/conversational)
   - Time of day (morning = vocab/listen, afternoon = read/write, evening = speak)

### Step 5: Create Today's Log

1. Use `src/logs/writer.py` → LogWriter class
2. Call `create_daily_log()` with today's date
3. Template:
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
   
   ## Vicios Detected
   -
   
   ## Notes
   -
   ```

### Step 6: Show User Recommendations

Output format:
```
🏔️  Buenos días! Based on your progress...

📊 Current streak: {streak} days
🎯 Your level: {CEFR level}

Today I recommend:
1. /pt vocab — You have {n} words to review
2. /pt read — Improve reading comprehension
3. /pt listen — Practice listening skills

Ready to start? Just say /pt vocab, /pt read, etc.
```

## What to Update After Sessions

After user completes a session, update:
1. SQLite `skills_progress` table with new XP
2. SQLite `sessions` table with session info
3. Today's log with session notes
4. `configs/profile.yml` streak if applicable