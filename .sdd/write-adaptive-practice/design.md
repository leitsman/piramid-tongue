# Technical Design: write-adaptive-practice

## Architecture
```
/pt write
  │
  ├── micro-test → save weaknesses to DB
  │
  ├── mode: transcription / creation / translation
  │
  ├── structural analysis → save issues to weaknesses
  │
  └── mixed practice option
        │
        ├── check weaknesses table for active categories
        ├── generate mixed exercise set (it + might + by)
        ├── present without hints
        ├── user completes ALL
        ├── show feedback per question
        └── if fail > 3: more tips + retry
```

## File Changes
- `skills/_shared/adaptive-practice.md` (new) — Mixed exercise framework
- `skills/write.md` — Option 3 → mixed practice
- `skills/_shared/micro-test.md` — Save weaknesses after failed questions
- `src/test_questions.py` — MIXED_EXERCISE_BANKS + QUESTION_CATEGORIES
- `src/db/schema.sql` — weaknesses table
- `src/db/__init__.py` — weakness CRUD
- `src/analysis/structural.py` — Map issues to categories

## Key Decisions
- Why shared markdown (not Python): follows existing pattern, AI executes directly
- Why mixed exercises are hardcoded in test_questions.py: allows AI to read question sets
- Why weaknesses table (not profile.yml): queryable, trackable statistics