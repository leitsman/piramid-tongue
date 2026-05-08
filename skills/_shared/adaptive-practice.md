# Shared Adaptive Practice Instructions

> This file is imported by skill files that support adaptive mixed practice.

## When to Use
- After structural analysis detects issues (in write mode)
- After micro-test shows weaknesses (score < 3/4 or category-specific fail)
- User explicitly says "I don't understand X" or "practicar X"

## Flow

### Step 1: Check Weaknesses
1. Query `weaknesses` table for active categories sorted by fail_count DESC
2. Select top 3 categories (if fewer, use all available)
3. If no weaknesses exist and user didn't request practice → skip this flow

### Step 2: Brief Explanation (user-requested only)
If user said "I don't understand X":
- Give 2-3 sentence explanation with 2 example sentences
- Do NOT give practice questions yet

### Step 3: Present Mixed Exercise
1. Import `get_mixed_exercise_set` from `src/test_questions.py`
2. Call `get_mixed_exercise_set(categories, count_per_category=2)`
3. Shuffle all questions so categories are NOT grouped
4. Present ONE set:
   ```
   Fill in the blank with the correct word/phrase:
   
   1. "___ seems that nobody is home."
      A) It  B) There  C) He  D) That
   
   2. "You ___ want to check the weather first."
      A) must  B) might  C) will  D) can
   
   3. "The painting was sold ___ a collector."
      A) by  B) for  C) to  D) with
   
   (Questions continue mixed)
   ```
5. **Do NOT reveal which category each question tests**
6. Wait for user's answers for ALL questions

### Step 4: Feedback (AFTER all answers)
After user answers ALL questions:
1. Show results:
   ```
   Results:
   ✅ Q1: "It seems..." — Correct! (expletive "it")
   ❌ Q2: You said "can". Correct is "might".
   ✅ Q3: "sold by a collector" — Correct! (passive voice agent)
   ```
2. For each wrong answer: give 1-sentence explanation
3. Calculate score:
   - >= 80%: "Great! Weakness improving."
   - 50-79%: "Keep practicing — [categories] still need work."
   - < 50%: Show more tips and offer to retry

### Step 5: Retry Logic
If score < 50%:
- Give 1 additional tip per weak category
- Offer: "Want to try another set?"
  - Yes → generate new set with same categories
  - No → save to weaknesses table and continue

### Step 6: Update Database
- For each correct answer: increment pass_count
- For each wrong answer: increment fail_count
- If pass_count >= 5 for any category → status = 'mastered'
- Log results in daily log under "## Adaptive Practice"
