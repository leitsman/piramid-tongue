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

Use `sqlite3` via bash to query the database:

```bash
sqlite3 data/progress.db "SELECT skill_name, level, xp, session_count, last_practiced FROM skills_progress;"
sqlite3 data/progress.db "SELECT COUNT(*) FROM vocab WHERE status = 'learning' AND (last_review IS NULL OR datetime('now') >= datetime(last_review, '+' || interval || ' days'));"
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

### Step 5b: Weakness Review (Between checks and recommendations)

1. Read `src/test_questions.py` y extrae el dict `EXERCISE_TEMPLATES` para generar ejercicios
2. Query due words from `weaknesses` table using sqlite3:
   ```bash
   sqlite3 data/progress.db "SELECT id, word, error_type, context_example, box_level, consecutive_correct FROM weaknesses WHERE status = 'active' AND box_level < 5 AND (next_review IS NULL OR datetime(next_review) <= datetime('now')) ORDER BY box_level ASC, next_review ASC LIMIT 5;"
   ```
3. If no due words: skip to Step 6 (no interruption to flow)
4. If due words exist: present "Quick review before starting:"
   - For each due word, generate 2 exercises usando los templates en `EXERCISE_TEMPLATES[error_type]` de `src/test_questions.py`
   - Present mixed (shuffled) exercises
   - Process user's answers
   - Update boxes via sqlite3 — correct=+1, fail minor=-1, fail major=-2
   - Log results in daily log under "## Weakness Review"
5. If score < 50%, offer retry with new exercises
6. If >= 50%, continue to recommendations

**Leitner Box Intervals**:
- Box 1: 1 day interval
- Box 2: 2 days
- Box 3: 4 days
- Box 4: 7 days
- Box 5: 14 days
- Correct answer: advance 1 box (max 5)
- Minor failure: drop 1 box (min 1)
- Major failure: drop 2 boxes (min 1)
- Box 5 + 3 consecutive correct: status = 'mastered'

### Step 6: Platform-Pyramid Gap Display

If user has platforms configured in profile.yml:
1. Query all skill XP from `skills_progress`:
   ```bash
   sqlite3 data/progress.db "SELECT skill_name, xp FROM skills_progress;"
   ```
2. Compare each platform's estimated CEFR level (from `platform_level_to_cefr`) against the user's actual skill XP:
   - If platform level suggests higher proficiency than the user's lowest skill XP → gap detected
3. If gaps found, show:
   ```
   ⚠️ Gap Detected:
   
   Your [Platform] progress suggests [CEFR level], but your [Skill] is at [lower level].
   This means you're consuming content but not applying it enough.
   
   Today I recommend focusing on: [affected skill]
   ```
4. If no gaps or platforms empty: skip this section

### Step 8: Calculate Skills Needing Attention

Use the pyramid dependency rules (inline — no Python module needed):

**Pyramid Dependencies**:
```
vocab: (unlocked) — requires 0 XP
read: requires vocab (100 XP)
listen: requires read (100 XP)
write: requires listen (100 XP)
speak: requires write (100 XP)
```

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
