# Skill: roadmap

## Trigger
User says `/pt roadmap` or `/pt-roadmap`

## Purpose
Show next steps with dependencies, time estimates, and learning path.

## Steps

### Step 1: Load User Data

1. Read `configs/profile.yml` for level and objectives
2. Initialize DB from `src/db/__init__.py`
3. Query skills_progress for all skills

### Step 2: Calculate Pyramid State

Use `src/core/pyramid_engine.py` PyramidState:

```python
pyramid = PyramidState()
# Load from DB...
# Calculate which skills are unlocked/blocked
```

### Step 3: Determine Next Steps

Based on pyramid dependencies and user progress:

**If ascending (learning new skills):**
1. Find lowest XP skill that is available
2. Recommend practicing that skill
3. Show what unlocking it enables

**If user has specific goal:**
1. Identify target skill
2. Calculate what needs to be practiced first
3. Show dependency chain

### Step 4: Calculate Time Estimates

Use standard time estimates per skill:

| Skill | Daily Practice | To Reach 100 XP |
|-------|---------------|-----------------|
| vocab | 15-20 min | ~2 weeks |
| read | 20-30 min | ~3-4 weeks |
| listen | 20-30 min | ~3-4 weeks |
| write | 30-45 min | ~4-6 weeks |
| speak | 30-45 min | ~4-6 weeks |

### Step 5: Generate Roadmap

Output format:
```
🏔️  Your Learning Roadmap
========================

Current level: {CEFR level}
Objective: {technical/conversational/both}

📍 Next Milestone: Unlock "write" skill
   Requires: 100 XP in "listen" (currently {listen_xp} XP)
   Time estimate: ~{weeks} weeks at 30 min/day

🎯 Recommended sequence:
   1. /pt listen — Build 60 more XP (focus on listening)
   2. /pt read — Reinforce comprehension while gaining XP
   3. /pt vocab — Support with vocabulary (quick sessions)

🔓 When you unlock "write":
   - Can practice transcription, creation, translation
   - Enables progression to "speak" skill

💡 Tips for your objective ({objective}):
   - Technical: Focus on reading tech articles, listening to tech podcasts
   - Conversational: Focus on shadowing, tandem practice

📅 Weekly commitment: ~2-3 hours total
   Monday: vocab + listen
   Wednesday: read + write
   Friday: speak + review
   Weekend: Light practice or tandem
```

## Dependency Chain Display

Show the path to a specific skill:

```
To unlock "speak" (final skill):

speak (target)
   ↑
write (need 100 XP)
   ↑
listen (need 100 XP)
   ↑
read (need 100 XP)
   ↑
vocab (always unlocked)
```

## Milestone Tracking

| Milestone | Requirement | Estimated Time |
|-----------|-------------|----------------|
| Foundation | 100 XP in vocab | 2 weeks |
| Reader | 100 XP in read | 3 weeks |
| Listener | 100 XP in listen | 3 weeks |
| Writer | 100 XP in write | 4 weeks |
| Speaker | 100 XP in speak | 4 weeks |
| Full Pyramid | All skills 100+ XP | 3-4 months |

## What to Update

No database updates needed for roadmap display. This is read-only.