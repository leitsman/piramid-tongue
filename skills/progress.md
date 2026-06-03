# Skill: progress

## Trigger
User says `/pt progress` or `/pt-progress`

## Purpose
Display ASCII pyramid, streak info, words learned, and vicios history.

## Steps

### Step 1: Load User Data

1. Read `configs/profile.yml` for streak and level
2. Query skills_progress for all skills via sqlite3:
   ```bash
   sqlite3 data/progress.db "SELECT skill_name, xp, session_count, last_practiced FROM skills_progress;"
   ```

### Step 2: Build ASCII Pyramid

Create visual pyramid based on skill XP:

```
              Speak (200 XP) 🔓
             /           \
    Write (150 XP)      [locked]
      /        \            \
Listen (120 XP)           Vocab (80 XP)
   |    \    /    |
   |     \  /     |
   v      Read     v
   └──────────────┘
```

XP threshold for unlocking: 100 XP

### Step 3: Show Streak Information

Display from `configs/profile.yml`:
```
📅 Streak: {current} days (best: {longest})
Last active: {last_active_date}
```

### Step 4: Show Vocabulary Stats

Query SQLite for vocab stats:
```bash
sqlite3 data/progress.db "SELECT status, COUNT(*) as count FROM vocab GROUP BY status;"
```

Display:
```
📚 Vocabulary:
   New: {n} words
   Learning: {n} words
   Acquired: {n} words
   Total: {total} words
```

### Step 5: Show Skills Progress

Query SQLite for skills_progress:
```bash
sqlite3 data/progress.db "SELECT skill_name, xp, session_count, last_practiced FROM skills_progress;"
```

Display for each skill:
```
🎯 {skill_name}:
    XP: {xp} / 100 to unlock next
    Sessions: {count}
    Last: {date}
```

### Step 5b: Show Listen Level

Query SQLite for listen level progress:
```bash
sqlite3 data/progress.db "SELECT listen_level, COUNT(*) as sessions, AVG(comprehension_rating) as avg_rating FROM listening_progress GROUP BY listen_level ORDER BY MAX(session_date) DESC LIMIT 1;"
```

Display:
```
🎧 Listen Level: {n}/4
   - Level description: {Con subtítulos / Alternando / Sin subtítulos / Podcasts}
   - Sessions at this level: {count}
    - Average comprehension: {avg}/5
```

### Step 5d: Show Vocab Level Progress

Query:
```bash
sqlite3 data/progress.db "SELECT vocab_level, COUNT(*) as total, SUM(CASE WHEN repetition_count >= 100 THEN 1 ELSE 0 END) as integradas FROM vocab WHERE technical = 0 GROUP BY vocab_level;"
sqlite3 data/progress.db "SELECT COUNT(*) as technical_count, SUM(CASE WHEN repetition_count >= 100 THEN 1 ELSE 0 END) as technical_integradas FROM vocab WHERE technical = 1;"
```

Display:
```
📚 Vocab Progress:

Nivel 1 (Basic): {integrated}/{total} → {pct}%
Nivel 2 (Intermediate): {integrated}/{total} → {pct}%  
Nivel 3 (Technical + Extra): {tech_integrated}/{tech_count} words integrated → {pct}%

Status: Nivel 1: {"✅ Ready for level 2" if >=90% or "In progress"}
        Nivel 2: {"✅ Ready for level 3" if >=90% or "In progress"}
        Nivel 3: {pct}% completed
```

### Step 6: Show Vicios History

Query SQLite for vicios patterns:
```bash
sqlite3 data/progress.db "SELECT pattern, COUNT(*) as count FROM vicios_history GROUP BY pattern ORDER BY count DESC LIMIT 5;"
```

Display top detected vicios:
```
⚠️ Top Vicios:
   - "very + adj": detected 15 times
   - "in order to": detected 8 times
   - "the" overuse: detected 5 times
```

## Full Output Format

```
🏔️  Piramid-Tongue Progress
==========================

📅 Streak: 7 days (best: 14)
Last active: 2025-05-05

📊 Pyramid Status:
              Speak (200 XP) 🔓
             /           \
    Write (150 XP)      [locked - need 100 XP in listen]
      /        \            \
 Listen (120 XP)           Vocab (80 XP)
   |    \    /    |
   |     \  /     |
   v      Read     v
   └──────────────┘

📚 Vocabulary:
   New: 25 words
   Learning: 45 words
   Acquired: 120 words
   Total: 190 words

🎯 Skills:
   vocab:    80 XP (20 to next) | 15 sessions | last: today
   read:     60 XP (40 to next) | 8 sessions  | last: yesterday
   listen:   40 XP (60 to next) | 5 sessions  | last: 2 days ago
   write:    20 XP (80 to next) | 3 sessions  | last: 3 days ago
   speak:     0 XP (blocked)    | 0 sessions  | last: never

⚠️ Top Vicios:
   - "very + adj": 15 times
   - "in order to": 8 times

🎯 Next recommended: /pt listen (increase listen XP to unlock write)
```

## What to Update

No database updates needed for progress display. This is read-only.