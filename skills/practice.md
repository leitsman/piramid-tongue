# Skill: practice

## Trigger
User says `/pt practice` or `/pt-practice`

## Purpose
Log external platform practice (Duolingo, YoTalkTV, etc.) and sync with profile.

## Steps

### Step 1: Check Profile for Existing Platforms

1. Read `configs/profile.yml`
2. Get user's existing platforms list

### Step 2: Ask User About Platform Practice

Ask user:
1. "Which platform did you practice on?" (list existing or add new)
2. "What did you do?" (streak update, lesson completed, topic finished)
3. "Any metrics to update?" (streak, level, topics completed)

### Step 3: Update Platform Metrics

For existing platforms:
```yaml
platforms:
  - name: Duolingo
    metrics:
      streak: {new_streak}
      level: "{new_level}"
```

For new platforms:
```yaml
platforms:
  - name: {platform_name}
    url: "{url}"
    metrics:
      streak: 0
      level: ""
      topics_completed: []
```

### Step 4: Ask About Session Details

1. "How long did you practice?" (minutes)
2. "How would you rate this session?" (1-5)
3. "Any notes about what you learned?"

### Step 5: Log Session and Update

1. Use `src/logs/writer.py` → LogWriter
2. Append to today's log under "## Notes" or create "## External Practice" section:
   ```
   - Platform: {name}, Duration: {n} min, Rating: {rating}/5, Notes: {notes}
   ```
3. Update SQLite `sessions` table with platform info
4. Save updated `configs/profile.yml`

## Supported Platforms

| Platform | Metrics to Track |
|----------|-----------------|
| Duolingo | streak, level, league |
| YoTalkTV | topics_completed, level |
| italki | lessons_completed, hours_practiced |
| Cambly | hours_practiced, topics_discussed |
| Custom | user-defined |

## Example Interaction

```
Which platform did you practice on?
1. Duolingo (existing)
2. Add new platform

> 1

Duolingo streak: 15 → 16
Duolingo level: 2 → 2

Did you complete any specific lesson or topic?
> Unit 3: Past Tense

How long did you practice? (minutes)
> 20

How would you rate this session? (1-5)
> 4

Any notes?
> Past tense is getting easier, but still struggle with irregular verbs

✅ Logged 20 min on Duolingo (streak: 16)
```

## What to Update

1. `configs/profile.yml` platforms list with updated metrics
2. Today's log with session details
3. SQLite `sessions` table (if applicable)