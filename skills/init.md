# Piramid-Tongue — `/pt init` Skill

Execute this when user says `/pt init` or `/pt-init`.

## Steps

### Step 1: Check current state

Read `configs/profile.yml`:
- If `level: null` → system not initialized, proceed
- If level exists → inform user they're already initialized

### Step 2: Ask estimated level

Say:
> "Let's set up your profile! What do you estimate your English level is?
> Options: A1, A2, B1, B2, C1, C2"

Wait for response.

### Step 3: Offer validation test

Say:
> "You estimated [LEVEL]. Want me to run a quick validation test to confirm? (5-7 questions per level, multiple choice)"

Wait for Y/n response.

### Step 4: Run validation test (if accepted)

**IMPORTANT**: The questions and answer verification logic is in `src/test_questions.py`.

To run the test:

1. Import the questions:
   - Read `src/test_questions.py` to get `LEVEL_QUESTIONS` dictionary
   - Each entry: `(question, [options], hashed_answer)`

2. For each level from estimated level upward (A1→A2→B1→...):

   a. Show 5 questions from that level:
      ```
      Question 1/5: [question]
      A) [option1]
      B) [option2]
      C) [option3]
      D) [option4]
      ```

   b. Wait for user's answer (A, B, C, or D)

   c. Convert letter to answer and verify using `check_answer()`

   d. Track score

3. If score >= 60% (3/5 correct):
   - Move to next level
   - Repeat questions

4. If score < 60%:
   - Detected level = current level
   - Stop test

### Step 5: Ask objectives

Once level is determined, ask:
> "What are your learning goals? (Choose one or more)
> - Technical: English for work/tech
> - Conversational: Everyday English speaking
> - Both: Combination"

Wait for response.

### Step 6: Ask about external platforms

Ask:
> "Do you want to track any external platforms for English learning? (e.g., Duolingo, YoTalkTV, Coursera)
> 
> If yes, tell me which platforms and what metrics you want to track (streak, level, topics, etc.)"

Wait for response.

If user provides platforms, store them in the profile.

### Step 7: Save to profile.yml

Write to `configs/profile.yml`:
```yaml
level: [DETECTED_LEVEL]
objectives: [SELECTED_OBJECTIVES]
streak:
  current: 0
  longest: 0
  last_active: null
platforms: [USER_PROVIDED_PLATFORMS or empty list]
roadmap: []
```

### Step 8: Confirm

Say:
> "Your profile is set up!
> - Level: [DETECTED_LEVEL]
> - Objectives: [OBJECTIVES]
> - Platforms: [PLATFORMS if any]
> 
> Run `/pt new-day` to start your first daily session!"
