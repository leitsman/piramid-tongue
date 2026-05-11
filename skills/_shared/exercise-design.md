# Exercise Design Guide for AI Generation

> This file provides guidelines for AI agents generating dynamic exercises for weakness practice.

## Core Format Rules

### Format Rule
- **Always multiple choice**
- **Exactly 4 options per question**
- **Exactly 1 correct answer**
- **3 plausible distractors** (errors of the same type)

### Distractor Rule
- Distractors must be **plausible errors of the same type**
- NOT random wrong answers
- Should reflect actual mistakes learners make
- Example (for expletive_usage): "There", "Here", "This" — not random words like "Dog", "House"

### Context Rule
- **Maximum 15 words per sentence**
- Real-world situations
- Match user's CEFR level (A1-C2)
- Use context from user's actual writing when available

### Word Rule
- Exercise **must use the user's actual weak word**
- If user struggles with "it" as expletive, the exercise should feature "it" as correct answer
- Never use generic placeholder words

### Mixing Rule
- When presenting multiple exercises, **shuffle so error types are NOT grouped**
- User should not be able to guess which type based on sequence
- Present in random order

### Feedback Rule
- Show **correct/incorrect only**
- On failure: provide **1 short explanation** (no category labels revealed)
- Do NOT show category names to user
- Example: "Correct! 'It seems that nobody is home.'" / "Not quite. 'It seems...' uses 'it' as a dummy subject."

## Error Type Templates

### expletive_usage
Dummy "it" as subject. Pattern: "___ is/are + adjective/verb"

Example patterns:
1. "___ is raining outside."
2. "___ seems that nobody is home."
3. "___ was a pleasure meeting you."

### modal_might
"might" for possibility. Pattern: "___ + base verb"

Example patterns:
1. "You ___ want to consider this option."
2. "It ___ rain later, so bring an umbrella."
3. "She hasn't arrived yet. She ___ be stuck in traffic."

### preposition_by
Agent in passive voice. Pattern: "was/were + past participle + ___ + agent"

Example patterns:
1. "The book was written ___ Shakespeare."
2. "The window was broken ___ the storm."
3. "The painting was sold ___ a collector."

### article_usage
Article selection (a/an/the/no article)

Example patterns:
1. "She's ___ university student." (a vs an based on sound)
2. "I need ___ advice about my career." (no article for uncountable)
3. "___ Amazon is ___ longest river." (the + the)

### gerund_infinitive
Verb patterns requiring -ing vs infinitive

Example patterns:
1. "I enjoy ___ to music while working." (listening vs to listen)
2. "He suggested ___ the meeting until tomorrow." (postponing vs to postpone)
3. "Stopping ___ is very difficult." (smoking vs to smoke)

### subject_verb
Subject-verb agreement with tricky subjects

Example patterns:
1. "Neither the teacher nor the students ___ aware." (are vs is)
2. "Each of the books ___ been read." (has vs have)
3. "Either my sisters or my brother ___ coming." (is vs are)

### omission
Missing words (that, if, why, what)

Example patterns:
1. "The reason is ___ she didn't study." (that)
2. "I don't know ___ she left early." (why)
3. "Tell me ___ you need help." (if)

### wrong_word
Common word confusion errors

Example patterns:
1. "I need to ___ an appointment." (make vs do/take)
2. "The movie was very ___." (enjoyable vs enjoy)
3. "Please ___ attention." (pay vs take/give)

### wrong_position
Word order errors

Example patterns:
1. "I ___ never been to Paris." (have vs has)
2. "She ___ always late." (is vs are)
3. "He ___ rarely complains." (rarely vs position error)

## Generation Checklist

When generating exercises, verify:
- [ ] 4 options per question
- [ ] 1 correct, 3 plausible distractors
- [ ] Max 15 words per sentence
- [ ] User's weak word is the correct answer
- [ ] Error type pattern matches template
- [ ] Context is appropriate for CEFR level
- [ ] No category labels shown to user

## Example Output Format

```
Fill in the blank:

"___ is raining heavily today."
A) It  B) There  C) Here  D) This

"___ seems that nobody is home."
A) It  B) That  C) There  D) This

"You ___ want to consider this option."
A) might  B) must  C) will  D) can
```
