# Skill: listen

## Trigger
User says `/pt listen` or `/pt-listen`

## Purpose
Listening practice with content suggestions by CEFR level and self-rating.

## Steps

### Step 1: Check Profile for CEFR Level

1. Read `configs/profile.yml`
2. Get user's `level` (CEFR level)

### Step 2: Suggest Content by Level

Based on user's level, suggest appropriate content:

**A1-A2 Level:**
- BBC Learning English (simple videos)
- ESLPod
- Children's English content
- Slow, clear speech

**B1 Level:**
- BBC World Service
- VOA Learning English
- TED-Ed (simple topics)
- Native content with subtitles

**B2 Level:**
- TED Talks (various topics)
- Native podcasts
- News in slow English
- YouTube documentaries

**C1-C2 Level:**
- Native speed podcasts (This American Life, etc.)
- Netflix with English subtitles
- Native TED Talks
- Radio shows (NPR, BBC Radio 4)

### Step 3: User Practices Listening

1. User watches/listens to content
2. User notes:
   - Source/content name
   - Duration of practice
   - Any challenging parts

### Step 4: User Self-Rates Session

Ask user to rate their comprehension (1-5):
1. Complete struggle (understood <30%)
2. Difficult (understood 30-50%)
3. Moderate (understood 50-70%)
4. Good (understood 70-90%)
5. Excellent (understood >90%)

### Step 5: Log Session and Update

1. Use `src/logs/writer.py` → LogWriter
2. Append to today's log under "## Listening Practice":
   ```
   - Content: {source}, Duration: {n} min, Self-rating: {rating}/5
   ```
3. Update SQLite `sessions` table
4. Update SQLite `skills_progress`:
   ```sql
   UPDATE skills_progress SET xp = xp + ?, session_count = session_count + 1 WHERE skill_name = 'listen'
   ```
5. Award XP based on rating:
   - Rating 1: 5 XP
   - Rating 2: 10 XP
   - Rating 3: 15 XP
   - Rating 4: 20 XP
   - Rating 5: 30 XP

## Content Sources (from `src/scrapers/`)

| Source | Module | Level Range |
|--------|--------|-------------|
| BBC Learning English | `src/scrapers/bbc.py` | A1-B1 |
| YouTube | `src/scrapers/youtube.py` | B1-C2 |
| General web | `src/scrapers/web.py` | Various |
| Books | `src/scrapers/books.py` | B1-C2 |

## What to Ask User

1. "What content did you practice?" (source + title)
2. "How long did you practice?" (minutes)
3. "How well did you understand?" (1-5 rating)
4. "Any words or phrases you learned?"