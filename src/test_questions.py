"""Hidden level test with SHA256 hashed answers.

This module provides an internal function run_level_test() that AI agents
can use to determine a user's CEFR level without showing the questions
or answers directly.

Questions per level:
- A1 (7 questions): basic be, articles, simple present
- A2 (6 questions): past tense, conditionals
- B1 (6 questions): past perfect, wish
- B2 (5 questions): inversion, gerunds
- C1 (4 questions): subjunctive, advanced inversion
- C2 (0 questions): if passed C1, user is C2

Answers are stored as SHA256 hashes for validation.
"""

import hashlib
import random
from typing import Literal

CEFRLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
PASS_THRESHOLD = 0.6  # 60% to pass a level


def _hash_answer(answer: str) -> str:
    """Hash an answer with SHA256 for storage."""
    return hashlib.sha256(answer.strip().lower().encode()).hexdigest()


# Questions with hashed answers
# Format: (question, [options], hashed_correct_answer)
LEVEL_QUESTIONS = {
    "A1": [
        (
            "What ___ your name?",
            ["is", "are", "am", "be"],
            _hash_answer("is"),
        ),
        (
            "She ___ a teacher.",
            ["are", "is", "am", "were"],
            _hash_answer("is"),
        ),
        (
            "I ___ from Brazil.",
            ["am", "is", "are", "be"],
            _hash_answer("am"),
        ),
        (
            "___ you speak English?",
            ["Do", "Does", "Are", "Is"],
            _hash_answer("do"),
        ),
        (
            "There ___ two cats on the table.",
            ["is", "are", "has", "was"],
            _hash_answer("are"),
        ),
        (
            "This is ___ apple.",
            ["a", "an", "the", "one"],
            _hash_answer("an"),
        ),
        (
            "He ___ to school every day.",
            ["go", "goes", "going", "went"],
            _hash_answer("goes"),
        ),
    ],
    "A2": [
        (
            "If I ___ you, I would study more.",
            ["was", "were", "am", "be"],
            _hash_answer("were"),
        ),
        (
            "She ___ English for 2 years.",
            ["studies", "has studied", "is studying", "studied"],
            _hash_answer("has studied"),
        ),
        (
            "They ___ to the cinema yesterday.",
            ["go", "went", "gone", "going"],
            _hash_answer("went"),
        ),
        (
            "I ___ never been to Paris.",
            ["have", "has", "had", "am"],
            _hash_answer("have"),
        ),
        (
            "He asked me where I ___.",
            ["live", "lived", "living", "lives"],
            _hash_answer("lived"),
        ),
        (
            "You ___ wear a uniform at school.",
            ["must", "must to", "have", "should to"],
            _hash_answer("must"),
        ),
    ],
    "B1": [
        (
            "By the time I arrived, they ___.",
            ["had left", "have left", "were leaving", "leaved"],
            _hash_answer("had left"),
        ),
        (
            "I wish I ___ more time.",
            ["have", "had", "having", "has"],
            _hash_answer("had"),
        ),
        (
            "She told me she ___ coming.",
            ["was", "is", "were", "be"],
            _hash_answer("was"),
        ),
        (
            "If it ___ tomorrow, we'll stay home.",
            ["rains", "will rain", "rained", "raining"],
            _hash_answer("rains"),
        ),
        (
            "The book ___ by millions of people.",
            ["has been read", "has read", "is reading", "was reading"],
            _hash_answer("has been read"),
        ),
        (
            "He's the man ___ helped me.",
            ["who", "which", "whose", "whom"],
            _hash_answer("who"),
        ),
    ],
    "B2": [
        (
            "I wish I ___ his number.",
            ["knew", "know", "had known", "knowing"],
            _hash_answer("knew"),
        ),
        (
            "Had I known, I ___ differently.",
            ["would have acted", "would act", "will act", "acted"],
            _hash_answer("would have acted"),
        ),
        (
            "She denied ___ the money.",
            ["taking", "to take", "take", "taken"],
            _hash_answer("taking"),
        ),
        (
            "Not until he arrived ___ the truth.",
            ["did he discover", "he discovered", "did he discovers", "he discovers"],
            _hash_answer("did he discover"),
        ),
        (
            "The meeting ___ off until next week.",
            ["has been put", "has put", "is putting", "was putting"],
            _hash_answer("has been put"),
        ),
    ],
    "C1": [
        (
            "Seldom ___ such a brilliant performance.",
            ["have I seen", "I have seen", "I saw", "did I saw"],
            _hash_answer("have I seen"),
        ),
        (
            "He spoke as though he ___ an expert.",
            ["were", "was", "is", "be"],
            _hash_answer("were"),
        ),
        (
            "The proposal, ___ was approved, needs revision.",
            ["which", "that", "what", "who"],
            _hash_answer("which"),
        ),
        (
            "No sooner had she left ___ it started raining.",
            ["than", "when", "that", "after"],
            _hash_answer("than"),
        ),
    ],
}


def run_level_test(estimated_level: str) -> str:
    """Run adaptive level test starting from estimated level.

    This function is called internally. It simulates the test
    by returning the detected level based on the estimated level.

    The actual test with user interaction is in init_cmd.py.
    This function exists so AI agents can programmatically get
    a level estimate.

    Args:
        estimated_level: User's self-assessed CEFR level

    Returns:
        Detected CEFR level based on adaptive testing logic
    """
    # Simple logic: if estimated level is provided, test starts there
    # In actual use (init_cmd.py), this is an interactive test
    # This function provides a non-interactive fallback

    if estimated_level not in CEFR_LEVELS:
        estimated_level = "B1"  # Default

    # For non-interactive use, return the estimated level
    # The actual adaptive testing happens in init_cmd.py
    return estimated_level


def get_questions_for_level(level: str, count: int = 5) -> list:
    """Get questions for a specific level.

    Args:
        level: CEFR level (A1, A2, B1, B2, C1)
        count: Number of questions to return

    Returns:
        List of (question, options, hashed_answer) tuples
    """
    questions = LEVEL_QUESTIONS.get(level, [])
    if len(questions) <= count:
        return questions
    return questions[:count]


def check_answer(question_hash: str, user_answer: str) -> bool:
    """Check if user's answer matches the hashed answer.

    Args:
        question_hash: SHA256 hash stored with the question
        user_answer: User's submitted answer

    Returns:
        True if answer is correct
    """
    return _hash_answer(user_answer) == question_hash


# Verification hashes for known answers (used in tests)
KNOWN_ANSWERS = {
    "A1_is": _hash_answer("is"),
    "A1_am": _hash_answer("am"),
    "A1_are": _hash_answer("are"),
    "A1_do": _hash_answer("do"),
    "A1_an": _hash_answer("an"),
    "A1_goes": _hash_answer("goes"),
    "A2_were": _hash_answer("were"),
    "A2_has studied": _hash_answer("has studied"),
    "A2_went": _hash_answer("went"),
    "A2_have": _hash_answer("have"),
    "A2_must": _hash_answer("must"),
    "B1_had left": _hash_answer("had left"),
    "B1_had": _hash_answer("had"),
    "B1_was": _hash_answer("was"),
    "B1_rains": _hash_answer("rains"),
    "B1_has been read": _hash_answer("has been read"),
    "B1_who": _hash_answer("who"),
    "B2_knew": _hash_answer("knew"),
    "B2_would have acted": _hash_answer("would have acted"),
    "B2_taking": _hash_answer("taking"),
    "B2_did he discover": _hash_answer("did he discover"),
    "B2_has been put": _hash_answer("has been put"),
    "C1_have I seen": _hash_answer("have I seen"),
    "C1_were": _hash_answer("were"),
    "C1_which": _hash_answer("which"),
    "C1_than": _hash_answer("than"),
}


# Micro-tests for skill diagnostics (4+2 format)
# Format: (question_text, [option_a, option_b, option_c, option_d], correct_index)
# HARDER questions (bonus 2) are from the NEXT CEFR level
MICRO_TESTS = {
    "vocab": {
        "A1": [
            ("What is the opposite of 'hot'?", ["cold", "warm", "big", "fast"], 0),
            ("Complete: She ___ a student.", ["is", "are", "am", "be"], 0),
            ("Choose the correct word: I have two ___", ["children", "childs", "childrens", "child"], 0),
            ("What does 'book' mean?", ["something to read", "something to eat", "a type of car", "a color"], 0),
            ("Complete: ___ name is John.", ["My", "I", "Me", "Mine"], 0),
            ("What is the plural of 'book'?", ["books", "bookes", "bookies", "book-s"], 0),
        ],
        "A2": [
            ("Complete: I ___ to the store yesterday.", ["went", "go", "going", "gone"], 0),
            ("Choose the correct option: She ___ already left.", ["has", "have", "is", "are"], 0),
            ("What does 'immediately' mean?", ["right now", "never", "slowly", "maybe"], 0),
            ("Complete: If I ___ rich, I would travel.", ["were", "was", "am", "be"], 0),
            ("Which word means 'a place where you live'?", ["house", "car", "book", "tree"], 0),
            ("Complete: He ___ playing football since morning.", ["has been", "have", "is", "was"], 0),
            ("What is the past of 'go'?", ["went", "gone", "going", " goed"], 0),
        ],
        "B1": [
            ("'I ___ to the store yesterday.' — Choose correct:", ["went", "go", "going", "gone"], 0),
            ("If I ___ rich, I would travel.", ["were", "was", "am", "be"], 0),
            ("What does 'take for granted' mean?", ["appreciate less than deserved", "take something literally", "grant permission", "take notes"], 0),
            ("Complete: By the time I arrived, they ___.", ["had left", "have left", "leaving", "left"], 0),
            ("Which word means 'to make something better'?", ["improve", "worsen", "keep", "remove"], 0),
            ("'The book ___ by millions.' — Choose correct:", ["has been read", "has read", "is reading", "reading"], 0),
            ("What does 'get along with' mean?", ["have a good relationship", "get away", "understand", "catch up"], 0),
        ],
        "B2": [
            ("'Had I known, I ___ differently.' — Choose:", ["would have acted", "would act", "will act", "acted"], 0),
            ("What does 'ripple effect' mean?", ["chain reaction", "water sound", "payment method", "music genre"], 0),
            ("Complete: She denied ___ the money.", ["taking", "to take", "take", "taken"], 0),
            ("'Not until he arrived ___ the truth.' — Choose:", ["did he discover", "he discovered", "discovered he", "he did discover"], 0),
            ("What does 'cut corners' mean?", ["do minimum effort", "reduce size", "speed up", "corner tool"], 0),
            ("Which word means 'extremely large'?", ["enormous", "tiny", "short", "thin"], 0),
            ("'The meeting ___ off until next week.' — Choose:", ["has been put", "has put", "putting", "was put"], 0),
        ],
        "C1": [
            ("'Seldom ___ such a brilliant performance.' — Choose:", ["have I seen", "I have seen", "I saw", "did I saw"], 0),
            ("What does 'dichotomy' mean?", ["division into two", "agreement", "combination", "expansion"], 0),
            ("'No sooner had she left ___ it started raining.' — Choose:", ["than", "when", "that", "after"], 0),
            ("What does 'paradigm shift' mean?", ["fundamental change in thinking", "parade change", "paradise change", "pattern shift"], 0),
            ("Which word means 'to make something less severe'?", ["mitigate", "aggravate", "escalate", "intensify"], 0),
            ("'He spoke as though he ___ an expert.' — Choose:", ["were", "was", "is", "be"], 0),
            ("What does 'inception' mean?", ["beginning", "ending", "middle", "outcome"], 0),
        ],
    },
    "read": {
        "A1": [
            ("What did the cat do in the story?", ["sat on the mat", "ran away", "sang a song", "read a book"], 0),
            ("Where was the ball?", ["in the box", "under the bed", "on the roof", "in the garden"], 0),
            ("How many apples were there?", ["five", "three", "seven", "ten"], 0),
            ("What color was the car?", ["blue", "green", "red", "yellow"], 0),
            ("What time did the story happen?", ["morning", "evening", "night", "afternoon"], 0),
            ("Who was in the story?", ["mom and kid", "only a dog", "teacher", "doctor"], 0),
        ],
        "A2": [
            ("What was the main topic of the article?", ["travel", "cooking", "sports", "music"], 0),
            ("What happened in the middle of the text?", ["a surprise", "nothing", "the end", "the beginning"], 0),
            ("What can you infer about the character?", ["they were happy", "they were sad", "they were angry", "they were confused"], 0),
            ("What was the author's purpose?", ["inform", "entertain", "persuade", "confuse"], 0),
            ("What does the ending suggest?", ["resolution", "problem continues", "new problem", "no ending"], 0),
            ("What context clue helps understand 'ancient'?", ["thousands of years old", "brand new", "modern", "broken"], 0),
            ("What was the tone of the text?", ["serious", "funny", "sad", "neutral"], 0),
        ],
        "B1": [
            ("What is the main argument of the author?", ["technology impacts work", "AI is bad", "computers think", "robots replace humans"], 0),
            ("What evidence supports the main point?", ["statistics and examples", "only opinions", "no evidence", "unrelated data"], 0),
            ("How is the text structured?", ["problem-solution", "chronological", "random", "comparison"], 0),
            ("What can be concluded from the text?", ["conclusion is implied", "literal meaning only", "no conclusion", "author unknown"], 0),
            ("What does 'overwhelming' mean in context?", ["too much to handle", "underwhelming", "exciting", "boring"], 0),
            ("What is the relationship between paragraphs?", ["cause and effect", "two opposites", "unrelated", "same topic"], 0),
            ("What bias might the author have?", ["pro-technology", "anti-change", "neutral", "political"], 0),
        ],
        "B2": [
            ("What nuanced interpretation is possible?", ["multiple valid readings", "only one meaning", "no interpretation", "wrong interpretation"], 0),
            ("What literary device is used?", ["metaphor", "only literal", "spelling error", "grammar mistake"], 0),
            ("How does the author build credibility?", ["citing experts", "making claims", "using emotions", "attacking others"], 0),
            ("What underlying assumption exists?", ["readers know background", "everyone agrees", "no context needed", "topic is simple"], 0),
            ("What counterargument does the author address?", ["environmental cost", "no counterargument", "only one view", "irrelevant points"], 0),
            ("How does the conclusion impact the thesis?", ["strengthens it", "weakens it", "ignores it", "contradicts it"], 0),
            ("What is the significance of the title?", ["ironic", "literal", "misleading", "unimportant"], 0),
        ],
        "C1": [
            ("What philosophical stance emerges?", ["existentialist", "naive realist", "no stance", "uncertain"], 0),
            ("How does subtext reveal character?", ["hidden motivations", "only words", "surface level", "obvious"], 0),
            ("What structural analysis applies?", ["dialectical", "linear", "circular", "fragmented"], 0),
            ("What intertextual reference is made?", ["classical allusion", "no reference", "recent meme", "random"], 0),
            ("How does the prose style convey meaning?", ["stream of consciousness", "strict form", "no style", "simple language"], 0),
            ("What ideological critique is present?", ["capitalism", "no critique", "praise capitalism", "economic theory"], 0),
            ("What is the epistemological claim?", ["knowledge is contextual", "knowledge is absolute", "no knowledge", "uncertain"], 0),
        ],
    },
    "listen": {
        "A1": [
            ("What did the speaker say about the weather?", ["it's nice", "it's bad", "it's cold", "it's hot"], 0),
            ("How many times did they mention a name?", ["once", "twice", "three times", "never"], 0),
            ("What was the first thing mentioned?", ["hello", "goodbye", "maybe", "sorry"], 0),
            ("Did the speaker sound happy or sad?", ["happy", "sad", "angry", "confused"], 0),
            ("What was the main topic?", ["family", "food", "work", "school"], 0),
            ("How long did they speak?", ["a minute", "ten minutes", "an hour", "all day"], 0),
        ],
        "A2": [
            ("What happened in the conversation?", ["made plans", "argued", "said goodbye", "introduced themselves"], 0),
            ("What was the speaker's main point?", ["to invite", "to complain", "to inform", "to ask"], 0),
            ("How did the listener respond?", ["agreed", "disagreed", "was confused", "left"], 0),
            ("What specific details were mentioned?", ["time and place", "only time", "only place", "no details"], 0),
            ("What can you infer about the relationship?", ["acquaintances", "family", "strangers", "enemies"], 0),
            ("What was the tone?", ["friendly", "formal", "cold", "angry"], 0),
            ("What topic came up second?", ["work", "travel", "food", "hobbies"], 0),
        ],
        "B1": [
            ("What is the speaker's opinion on the topic?", ["skeptical", "supportive", "neutral", "unclear"], 0),
            ("What evidence does the speaker provide?", ["examples and data", "no evidence", "opinions only", "unrelated"], 0),
            ("How would you describe the speaker's accent?", ["clear", "strong native", "hard to understand", "no accent"], 0),
            ("What was the main idea missed initially?", ["environmental impact", "economic growth", "political view", "simple fact"], 0),
            ("What does the phrase 'at the end of the day' mean?", ["ultimately", "literally at dusk", "never", "some day"], 0),
            ("How many points were made?", ["three", "two", "five", "seven"], 0),
            ("What was the conclusion?", ["needs more research", "no conclusion", "problem solved", "action required"], 0),
        ],
        "B2": [
            ("What rhetorical technique is used?", ["analogy", "only facts", "repetition", "no technique"], 0),
            ("What assumption underlies the argument?", ["public good matters", "profit is key", "no assumption", "individual focus"], 0),
            ("How does intonation convey meaning?", ["sarcasm detected", "sincerity", "no nuance", "confusion"], 0),
            ("What is the speaker's credibility based on?", ["expertise and experience", "title only", "confidence", "charisma"], 0),
            ("What counterpoint was addressed?", ["feasibility concerns", "no counterpoint", "minor issues", "unrelated"], 0),
            ("How does background noise affect understanding?", ["minimal impact", "major barrier", "no effect", "improved focus"], 0),
            ("What is the practical implication?", ["behavior change needed", "no action", "ignore it", "wait and see"], 0),
        ],
        "C1": [
            ("What subtle nuance was conveyed?", ["cynicism", "naivety", "no nuance", "obviousness"], 0),
            ("How does the speaker use silence?", ["for emphasis", "awkward pause", "no purpose", "to confuse"], 0),
            ("What unstated conclusion follows?", ["societal change needed", "maintain status quo", "no conclusion", "individual action"], 0),
            ("What dialectal variation is present?", ["regional accent", "standard English", "non-native", "artificial"], 0),
            ("How does register shift mid-speech?", ["more formal", "casual", "no shift", "inconsistent"], 0),
            ("What implied criticism is embedded?", ["institutional critique", "no criticism", "obvious critique", "praise"], 0),
            ("What is the discourse function of hedging?", ["uncertainty display", "certainty", "confusion", "emphasis"], 0),
        ],
    },
    "write": {
        "A1": [
            ("Choose the correct: She ___ to school.", ["goes", "go", "going", "went"], 0),
            ("Complete: The cat is ___ the table.", ["on", "in", "at", "by"], 0),
            ("Which is a complete sentence?", ["I like apples.", "Like apples", "The apples", "Go"], 0),
            ("What is the correct plural?", ["children", "childs", "childrens", "child"], 0),
            ("Complete: This is ___ apple.", ["an", "a", "the", "some"], 0),
            ("Which word is a verb?", ["run", "beautiful", "quick", "house"], 0),
        ],
        "A2": [
            ("Complete: I ___ English for 2 years.", ["have studied", "study", "studied", "studying"], 0),
            ("Which sentence is correct?", ["She don't like it.", "She doesn't like it.", "She not like it.", "She no like it."], 1),
            ("What does 'yesterday' tell us?", ["past tense", "future", "present", "never"], 0),
            ("Complete: If I ___ you, I'd help.", ["were", "was", "am", "be"], 0),
            ("Which is a proper paragraph?", ["Topic sentence + details", "Random sentences", "One word", "List of words"], 0),
            ("What tense is 'will go'?", ["future simple", "past", "present", "present continuous"], 0),
            ("Choose the correct: They ___ their homework.", ["finished", "finish", "finishing", "finishes"], 0),
        ],
        "B1": [
            ("'By the time I arrived, they ___.' — Choose:", ["had left", "have left", "leaving", "left"], 0),
            ("What makes a good topic sentence?", ["clear main idea", "long and complex", "question", "quote"], 0),
            ("Which transition shows contrast?", ["however", "also", "furthermore", "moreover"], 0),
            ("What is 'relative clause'?", ["who/which/that clause", "about relatives", "short clause", "main clause"], 0),
            ("Complete: The book ___ by millions.", ["has been read", "has read", "is reading", "reads"], 0),
            ("What is active voice?", ["Subject does the action", "Subject receives action", "No subject", "Passive construction"], 0),
            ("Which sentence uses past perfect?", ["I had gone before.", "I went yesterday.", "I have gone.", "I go now."], 0),
        ],
        "B2": [
            ("'Had I known, I ___ differently.' — Choose:", ["would have acted", "would act", "will act", "acted"], 0),
            ("What is a dangling modifier?", ["word modifying wrong noun", "correct modifier", "missing word", "extra word"], 0),
            ("Which sentence is grammatically correct?", ["The reason is because.", "The reason is that.", "Because the reason.", "Reason is this."], 1),
            ("What is 'subjunctive mood'?", ["were, insisted, demanded", "was", "are", "is", "am"], 0),
            ("Which style is most academic?", ["formal and objective", "casual and fun", "emotional", "short fragments"], 0),
            ("'Not until he arrived ___ the truth.' — Choose:", ["did he discover", "he discovered", "discovered he", "he did discover"], 0),
            ("What is parallel structure?", ["consistent grammatical form", "poetry style", "opposites", "random"], 0),
        ],
        "C1": [
            ("'Seldom ___ such a brilliant performance.' — Choose:", ["have I seen", "I have seen", "I saw", "did I saw"], 0),
            ("What is an academic hedging expression?", ["it appears that", "definitely", "absolutely", "certainly"], 0),
            ("Which sentence shows syntactic complexity?", ["Despite having studied, I failed.", "I studied. I failed.", "I failed.", "Studying, failing."], 0),
            ("What does 'in order to' obscure?", ["purpose clarity", "nothing", "verb clarity", "noun clarity"], 0),
            ("Which structure is most sophisticated?", ["Despite X, Y although Z.", "X and Y.", "X but Y.", "X because Y."], 0),
            ("What is a cleft sentence?", ["It was X that Y", "X and Y", "X or Y", "Neither X nor Y"], 0),
            ("What rhetorical device is 'At the end of the day'?", ["metaphor/cliche", "literal truth", "statistic", "contrast"], 0),
        ],
    },
    "speak": {
        "A1": [
            ("How do you pronounce 'cat'?", ["/kæt/", "/kat/", "/ket/", "/kait/"], 0),
            ("Which word has short 'a' sound?", ["hat", "father", "late", "make"], 0),
            ("Is 'she's' a contraction of 'she is' or 'she has'?", ["both possible", "only she is", "only she has", "neither"], 0),
            ("What sound does 'th' make in 'think'?", ["/θ/", "/ð/", "/t/", "/d/"], 0),
            ("How do you read 'world'?", ["/wɜːld/", "/worold/", "/wild/", "/waild/"], 0),
            ("Which is correct intonation for a question?", ["rising", "falling", "flat", "random"], 0),
        ],
        "A2": [
            ("What is the third sound in 'three'?", ["/r/", "/iː/", "/θ/", "/e/"], 2),
            ("Does 'read' rhyme with 'bed' or 'seed'?", ["seed", "bed", "both", "neither"], 0),
            ("Which sentence has word stress on second syllable?", ["deVELop", "REpeat", "FORget", "COming"], 0),
            ("What does rising intonation at end mean?", ["question or uncertainty", "statement finished", "command", "excitement only"], 0),
            ("How is 'could've' actually pronounced?", ["/kʊdəv/", "/kʊd-ev/", "/kuld-ave/", "/koud-av/"], 0),
            ("Which word has stress on first syllable?", ["TABLE", "beGIN", "deCIDE", "aBOUT"], 0),
            ("What is a schwa sound?", ["/ə/", "/æ/", "/e/", "/a/"], 0),
        ],
        "B1": [
            ("What does linking sound mean?", ["words connect", "words separate", "sounds drop", "emphasis changes"], 0),
            ("In 'I could've' — what actually gets pronounced?", ["/aɪ kʊdəv/", "/aɪ kʊd ev/", "/aɪ kud-ve/", "/aɪ kʊd ev/"], 0),
            ("What is reduced speech?", ["unstressed words shortened", "speaking slowly", "louder speech", "formal speech"], 0),
            ("Which phrase has liaison between words?", ["an apple", "go in", "sit on", "read it"], 0),
            ("What does intonation pattern convey?", ["emotion and attitude", "only grammar", "nothing", "pronunciation"], 0),
            ("How is the 't' in 'water' typically pronounced?", ["/ɾ/ (flap)", "/t/", "/d/", "silent"], 0),
            ("What is sentence stress for emphasis?", ["stressing key content words", "stressing all words", "no stress", "random stress"], 0),
        ],
        "B2": [
            ("What does pitch movement indicate?", ["meaning and attitude", "only volume", "nothing", "grammar only"], 0),
            ("What is the phonological process in 'gonna'?", ["reduplication", "assimilation", "deletion", "insertion"], 0),
            ("How does 'do you' become in natural speech?", ["/dʒuː/", "/duː juː/", "/dʒə/", "/duj/"], 0),
            ("What does 'weak form' mean?", ["unstressed pronunciation", "quiet speaking", "formal style", "incorrect form"], 0),
            ("Which rhythm pattern is typical?", ["stress-timed", "syllable-timed", "irregular", "no pattern"], 0),
            ("What is aspiration in English?", ["puff of air on /p,t,k/", "speaking slowly", "voicing", "whispering"], 0),
            ("How does context affect pronunciation?", ["sounds blend and change", "no effect", "only spelling matters", "always clear"], 0),
        ],
        "C1": [
            ("What does 'interdental' mean for 'th'?", ["tongue between teeth", "tongue behind teeth", "no tongue", "teeth together"], 0),
            ("What is allophonic variation?", ["different sounds, same phoneme", "different phonemes", "same sound", "no variation"], 0),
            ("How does register affect pronunciation?", ["formality shifts sounds", "no effect", "only vocabulary", "only grammar"], 0),
            ("What is the IPA symbol for 'ng' in 'sing'?", ["/ŋ/", "/n/", "/g/", "/nk/"], 0),
            ("What does 'minimal pair' test?", ["phoneme distinction", "grammar", "vocabulary", "spelling"], 0),
            ("How does connected speech work?", ["assimilation, elision, linking", "each word separate", "no rules", "only linking"], 0),
            ("What is suprasegmental feature?", ["stress, intonation, rhythm", "individual sounds", "spelling", "grammar"], 0),
        ],
    },
}


def get_micro_tests_for_skill(skill: str, level: str) -> list:
    """Get micro-test questions for a specific skill and CEFR level.

    Args:
        skill: Skill name ('vocab', 'read', 'listen', 'write', 'speak')
        level: CEFR level ('A1', 'A2', 'B1', 'B2', 'C1')

    Returns:
        List of (question, options, correct_index) tuples, or empty list if not found
    """
    if skill not in MICRO_TESTS:
        return []
    if level not in MICRO_TESTS[skill]:
        return []
    return MICRO_TESTS[skill][level]


def get_bonus_questions_for_level(skill: str, level: str) -> list:
    """Get bonus (harder) questions from the next CEFR level.

    Args:
        skill: Skill name
        level: Current CEFR level

    Returns:
        List of 2 bonus questions from next level, or empty list if at C1
    """
    levels_order = ["A1", "A2", "B1", "B2", "C1"]
    if level not in levels_order:
        return []
    try:
        next_level_idx = levels_order.index(level) + 1
        if next_level_idx >= len(levels_order):
            return []  # No next level for C1
        next_level = levels_order[next_level_idx]
        all_questions = MICRO_TESTS.get(skill, {}).get(next_level, [])
        # Return up to 2 random questions
        return all_questions[:2]
    except (ValueError, IndexError):
        return []


# Maps questions to practice categories (for micro-test → weakness mapping)
QUESTION_CATEGORIES = {
    "write": {
        "had left": "past_perfect",
        "however": "transition_words",
        "also": "transition_words",
        "had": "past_perfect",
        "had known": "conditionals",
        "would have acted": "conditionals",
        "taking": "gerund_after_verb",
        "did he discover": "inversion",
        "has been put": "passive_voice",
        "had been read": "passive_voice",
        "clear main idea": "topic_sentence",
    }
}

# Mixed exercise banks (categories NOT revealed)
# Format: {category: [(question, correct_answer, [options])]}
MIXED_EXERCISE_BANKS = {
    "expletive_it": [
        ("___ is raining heavily today.", "It", ["It", "There", "Here", "This", "He"]),
        ("___ was a pleasure meeting you.", "It", ["It", "That", "There", "What"]),
        ("___ seems that he doesn't understand.", "It", ["It", "There", "He", "That"]),
        ("___ is important to practice every day.", "It", ["It", "That", "There", "This"]),
        ("___ is home to thousands of species.", "It", ["It", "There", "Here", "That"]),
    ],
    "modal_might": [
        ("You ___ want to consider this option.", "might", ["might", "must", "will", "can"]),
        ("It ___ rain later, so bring an umbrella.", "might", ["might", "must", "will not", "can"]),
        ("She hasn't arrived yet. She ___ be stuck in traffic.", "might", ["might", "must", "will", "should"]),
        ("I ___ go to the party, but I'm not sure yet.", "might", ["might", "must", "have to", "will"]),
        ("___ I ask you a personal question?", "Might", ["Might", "Must", "Will", "Shall"]),
    ],
    "preposition_by": [
        ("The book was written ___ Shakespeare.", "by", ["by", "for", "with", "from"]),
        ("This gift is ___ you, my friend.", "for", ["by", "for", "with", "to"]),
        ("The window was broken ___ the storm.", "by", ["by", "for", "with", "because"]),
        ("I came ___ car, not by bus.", "by", ["by", "for", "in", "on"]),
        ("The letter was sent ___ mistake.", "by", ["by", "for", "with", "in"]),
    ],
    "article_usage": [
        ("___ pollution is damaging ___ environment.", "No article; the", ["The; the", "No article; the", "The; no article", "No article; no article"]),
        ("She is ___ university student.", "a", ["a", "an", "the", "no article"]),
        ("I need ___ advice about my career.", "no article", ["a", "an", "the", "no article"]),
        ("___ Amazon is ___ longest river.", "The; the", ["The; the", "The; no article", "No article; the", "No article; no article"]),
        ("He's ___ honest person.", "an", ["a", "an", "the", "no article"]),
    ],
    "passive_voice": [
        ("The report ___ by the assistant yesterday.", "was written", ["was written", "wrote", "is writing", "has written"]),
        ("This bridge ___ in 1998.", "was built", ["builds", "was built", "built", "is building"]),
        ("English ___ around the world.", "is spoken", ["is spoken", "speaks", "speaking", "has spoken"]),
        ("The documents ___ already ___.", "have been signed", ["have been signed", "are signing", "were signing", "have signed"]),
        ("Smoking ___ in this area.", "is not allowed", ["does not allow", "is not allowed", "not allows", "has not allowed"]),
    ],
}


def get_mixed_exercise_set(categories: list, count_per_category: int = 2) -> list:
    """Returns a mixed exercise set from given categories.
    Each question is shuffled so user cannot guess the category.
    Returns list of dicts: {question, options, correct, category}
    Category field is for AI internal use (weakness DB updates).
    Do NOT display 'category' to the user.
    """
    all_exercises = []
    for cat in categories:
        if cat in MIXED_EXERCISE_BANKS:
            exercises = MIXED_EXERCISE_BANKS[cat][:count_per_category]
            for question, correct, options in exercises:
                all_exercises.append({
                    "question": question,
                    "options": options,
                    "correct": correct,
                    "category": cat,
                })
    
    # Shuffle so categories are mixed (not grouped)
    random.shuffle(all_exercises)
    return all_exercises
