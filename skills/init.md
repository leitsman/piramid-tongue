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

    c. Convert letter to answer and verify SHA256 hash via bash:
       ```bash
       echo -n "${answer}" | sha256sum
       ```
       Compare the result with `hashed_answer` from `LEVEL_QUESTIONS`

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

### Step 6: Platform Onboarding

This step collects information about external learning platforms the user wants to track.

**Step 6.1**: Ask about platforms

Say:
> "¿Qué plataformas de aprendizaje de inglés usas? Por ejemplo:
> - **YouTalk** (plataforma de video/audio con unidades estructuradas)
> - **Duolingo** (app gamificada)
> - Otra que uses (Coursera, Busuu, etc.)"

Wait for response. If user says "none" or "ninguna", skip to Step 6.4.

**Step 6.2**: Parse platforms mentioned

For each platform the user mentions:
1. Check if it's in `configs/platforms.yaml` (known platforms: youtalk, duolingo)
2. If known: use the platform's defined metrics
3. If unknown: ask generic questions

**Step 6.3**: Collect metrics for each platform

For **YouTalk** (if mentioned):
Ask each question and wait for response:
> "¿En qué nivel estás actualmente en YouTalk? (Basic/Intermediate/Advanced)"
> "¿En qué unidad estás ahora mismo? (1-15)"
> "¿Cuántas unidades has completado en total?"
> "¿Cuál es tu meta semanal de sesiones en YouTalk?"
> "¿Cuántas sesiones has hecho esta semana en YouTalk?"

For **Duolingo** (if mentioned):
Ask each question and wait for response:
> "¿Cuál es tu racha actual en días?"
> "¿En qué liga estás actualmente? (Bronze/Silver/Gold/Sapphire/Ruby/Diamond/Obsidian)"
> "¿Cuál es tu meta semanal de XP?"
> "¿Cuántos XP has ganado esta semana?"

For **Other platforms** (if mentioned):
Ask:
> "¿Qué métricas quieres seguir para [platform]?"
> "¿Cuál es tu nivel actual en [platform]?"
> "¿Qué otras métricas relevantes tienes?"

**Step 6.4**: Weekly goals

After collecting platform data (or if user has no platforms), ask:
> "¿Tienes alguna meta semanal de práctica en general? (ej: 5 sesiones, 30 minutos diarios)"

Wait for response.

**Step 6.5**: Structure the data

Build a platforms list like:
```yaml
platforms:
  - name: "YouTalk"
    enabled: true
    metrics:
      current_level: "Intermediate"
      current_unit: 17
      total_units_completed: 31
      last_practice: null
      weekly_goal: 5
      sessions_this_week: 0
    platform_level_to_cefr: "B1"
    mapping_confidence: 0.7
    user_override_cefr: null
  - name: "Duolingo"
    enabled: true
    metrics:
      streak: 378
      total_xp: 0
      league: "Sapphire"
      last_practice: null
      weekly_goal: 50
      xp_this_week: 0
    platform_level_to_cefr: null
    mapping_confidence: 0.3
    user_override_cefr: null
```

### Step 7: Save to profile.yml

Write to `configs/profile.yml`:
```yaml
level: [DETECTED_LEVEL]
objectives: [SELECTED_OBJECTIVES]
streak:
  current: 0
  longest: 0
  last_active: null
platforms: [STRUCTURED_PLATFORMS_DATA]
roadmap: []
```

### Step 8: Confirm

Say:
> "Your profile is set up!
> - Level: [DETECTED_LEVEL]
> - Objectives: [OBJECTIVES]
> - Platforms: [PLATFORM_SUMMARY]
> 
> Run `/pt new-day` to start your first daily session!"
