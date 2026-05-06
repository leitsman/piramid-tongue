# Skill: vicios

## Trigger
User says `/pt vicios` or `/pt-vicios`

## Purpose
Analyze text for linguistic vices, show user history, and provide suggestions.

## Steps

### Step 1: Load Vicios Patterns

1. Read `configs/vicios_patterns.yaml`
2. Load patterns into memory for detection

### Step 2: Ask User for Text

Ask user to provide text to analyze:
- "Paste the text you want me to check for vicios"
- Or ask to analyze from recent writing log

### Step 3: Analyze Text

For each pattern in vicios_patterns.yaml:

1. Count occurrences of pattern
2. Calculate density (occurrences / total words)
3. Compare against threshold
4. Flag if exceeds threshold

### Step 4: Report Findings

Display detected vicios in format:

```
⚠️  Vicios Detected in Your Text
==============================

Found 3 issues:

1. "very + adjective" — 2 occurrences
   📍 "very good" → Suggestion: "excellent"
   📍 "very bad" → Suggestion: "terrible"

2. Overuse of "the" — 15% (threshold: 12%)
   📍 Consider using 'a/an' or omitting when appropriate

3. "in order to" — 1 occurrence
   📍 "In order to understand" → "To understand"
```

### Step 5: Show User History

Query SQLite for vicios history:
```sql
SELECT pattern, SUM(count) as total FROM vicios_history GROUP BY pattern ORDER BY total DESC
```

Display:
```
📊 Your Vicios History:
   - "very + adj": detected 45 times total
   - "in order to": detected 23 times total
   - "the" overuse: detected 18 times total
   - "a lot of": detected 12 times total
```

### Step 6: Provide Suggestions

Based on detected vicios, provide targeted advice:

**For "very + adj":**
- Keep a list of strong alternatives
- Examples: very good → excellent, very bad → terrible, very big → enormous

**For "in order to":**
- Always replace with "to"
- "In order to learn" → "To learn"

**For "the" overuse:**
- Review article usage rules
- Count "the" vs total words before writing

**For "a lot of":**
- Use more specific quantifiers
- "a lot of people" → "many people", "numerous individuals"

## Vicios Patterns Reference

From `configs/vicios_patterns.yaml`:

| Vice | Pattern | Threshold | Suggestion |
|------|---------|-----------|------------|
| "the" overuse | `\bthe\b` | 0.12 | Try 'a/an' or omitting |
| "very + adj" | `\bvery\s+\w+` | 0.05 | Stronger adjectives |
| "actually" | `\bactually\b` | 0.03 | Often unnecessary |
| "thing" | `\bthing\b` | 0.08 | Be more specific |
| "good" | `\bgood\b` | 0.06 | More precise adjectives |
| "in order to" | `\bin\s+order\s+to\b` | 0.02 | Just use 'to' |
| "a lot of" | `\b(a\|an)\s+lot\s+of\b` | 0.05 | 'many', 'much', 'numerous' |

## Example Interaction

```
Paste your text for vicios analysis:
> "The the problem is that I actually think that very good writers use very 
> many techniques in order to make their writing good. I think that actually
> learning about writing is a thing that requires a lot of practice."

⚠️  Vicios Detected:
====================

1. "the" repetition — 1 occurrence
   📍 "The the problem" → "The problem"

2. "very + adjective" — 2 occurrences
   📍 "very good" → "excellent"
   📍 "very many" → "numerous"

3. "actually" filler — 2 occurrences
   📍 Often unnecessary in written English

4. "in order to" — 1 occurrence
   📍 "in order to make" → "to make"

5. "a lot of" — 1 occurrence
   📍 "a lot of practice" → "extensive practice"

💡 Tip: Your most common vicios are "very + adj" and "actually". 
   Try reading your text aloud before submitting to catch filler words.
```

## What to Update

1. Log detected vicios to SQLite vicios_history table
2. Update pattern counts in vicios_patterns table