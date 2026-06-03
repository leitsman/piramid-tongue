# Skill: listen

## Trigger
User says `/pt listen` or `/pt-listen`

## Purpose
Listening practice with 4 progressive levels and YouGlish integration for unknown words.

## 4 Levels of Listen

| Level | Description | Content |
|-------|-------------|---------|
| 1 | Con subtítulos | Videos con subtitles |
| 2 | Alternar con/sin subtítulos | Basado en resultados del día anterior |
| 3 | Sin subtítulos | Videos sin subtitles |
| 4 | Podcasts | Solo audio, sin referencia visual |

## Steps

### Step 1: Check User Profile and Listen Level

1. Read `configs/profile.yml` for CEFR level
2. Query `listening_progress` table for current listen_level:
   ```bash
   sqlite3 data/progress.db "SELECT listen_level FROM listening_progress ORDER BY id DESC LIMIT 1;"
   ```
   - If no records, default to level 1
3. Get last session info for level 2 logic:
   ```bash
   sqlite3 data/progress.db "SELECT * FROM listening_progress WHERE listen_level = 2 ORDER BY id DESC LIMIT 1;"
   ```

### Step 2: Suggest Content Based on Level

**Level 1 — Con subtítulos:**
- BBC Learning English
- VOA Learning English
- ESLPod
- TED-Ed (simple topics)
- YouTalk videos

**Level 2 — Alternar:**
- Apply alternation logic based on last session:
  - If last session had used_subtitles = TRUE and rating >= 4 → suggest WITHOUT subtitles today
  - If last session had used_subtitles = TRUE and rating < 4 → suggest WITH subtitles (repeat)
  - If last session had used_subtitles = FALSE and rating >= 4 → suggest WITHOUT subtitles (continue)
  - If last session had used_subtitles = FALSE and rating < 4 → suggest WITH subtitles
- Content: Same sources as Level 1

**Level 3 — Sin subtítulos:**
- BBC World Service
- Native YouTube content
- Documentaries

**Level 4 — Podcasts:**
- NPR (All Things Considered, Fresh Air)
- This American Life
- BBC Radio 4
- Tech podcasts if objective is technical

### Step 3: User Practices Listening

User reports after practice:
1. Content name/source
2. Duration (minutes)
3. Did you use subtitles? (for level 2)
4. Comprehension self-rating (1-5):
   - 1: Complete struggle (<30%)
   - 2: Difficult (30-50%)
   3: Moderate (50-70%)
   - 4: Good (70-90%)
   - 5: Excellent (>90%)

### Step 4: Report Unknown Words

Ask user to list words they didn't understand.

For EACH word, ask:
```
"{word}" — Options:
A) YouGlish only (practice pronunciation)
B) Add to vocab + YouGlish (add to SRS + practice)
```

Record user's choice for each word.

### Step 5: Evaluate Progression

**Level 2 logic:**
- If comprehension rating >= 4 for 3 consecutive sessions → suggest level up to 3

**Level 3-4 logic:**
- If rating >= 4: remain at current level
- If rating < 3: suggest returning to previous level

### Step 6: Calculate XP

XP based on level and rating:

| Level | Rating 1 | Rating 2 | Rating 3 | Rating 4 | Rating 5 |
|-------|----------|----------|----------|----------|----------|
| 1 | 5 | 10 | 15 | 20 | 25 |
| 2 | 8 | 13 | 18 | 23 | 28 |
| 3 | 12 | 17 | 22 | 27 | 32 |
| 4 | 15 | 20 | 25 | 30 | 35 |

### Step 7: Log Session

1. Insert into `listening_progress`:
   ```bash
   sqlite3 data/progress.db "INSERT INTO listening_progress (listen_level, content_type, content_source, content_title, duration_minutes, used_subtitles, comprehension_rating, unknown_words, unknown_word_count, words_to_youglish, words_to_vocab_youglish, xp_earned) VALUES (${listen_level}, '${content_type}', '${source}', '${title}', ${duration}, ${subtitles}, ${rating}, '${unknown_words}', ${unknown_count}, '${youglish}', '${vocab_youglish}', ${xp});"
   ```

2. Update `skills_progress` for listen skill:
   ```bash
   sqlite3 data/progress.db "UPDATE skills_progress SET xp = xp + ${xp}, session_count = session_count + 1 WHERE skill_name = 'listen';"
   ```

3. Append to `logs/YYYY-MM-DD.md`:
   ```markdown
   ## Listening Practice
   
   **Session**: {YYYY-MM-DD HH:MM}
   **Level**: {listen_level}
   **Content**: {source} - {title}
   **Duration**: {n} min
   **Subtitles**: {yes/no}
   **Comprehension**: {rating}/5
   
   **Unknown Words**: {count}
   - YouGlish only: {n} words
   - Added to Vocab + YouGlish: {n} words
   
   **XP Earned**: {n}
   ```

4. Update streak in `configs/profile.yml` if this is the first session of the day:
   - Read current streak values from `configs/profile.yml`
   - Apply same streak logic as in `new-day.md` Step 3b:
     - If `last_active IS NULL`: set `current = 1`, `longest = 1`, `last_active = today`
     - If `last_active == today`: no change (already counted)
     - If `last_active == yesterday`: increment `current += 1`, update `longest` if needed, `last_active = today`
     - If `last_active < yesterday` (missed days): reset `current = 1`, `last_active = today`
   - Write updated values back to `configs/profile.yml`

### Step 8: YouGlish Suggestions

After logging, show:
```
🎯 Practice in YouGlish:
{word1} — {choice A or B}
{word2} — {choice A or B}
...
```

Links format: `https://youglish.com/pronounce/{word}/english`

## What to Ask User

1. "What content did you listen to?" (source + title)
2. "How long?" (minutes)
3. "Did you use subtitles?" (for level 2)
4. "How well did you understand?" (1-5)
5. "What words did you not understand?" (list)
6. For each word: "YouGlish only (A) or Add to vocab + YouGlish (B)?"