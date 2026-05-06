"""Command: pt init — Initialize profile and level test."""

import random
import typer
from datetime import date
from src.core.config import Config
from src.test_questions import (
    LEVEL_QUESTIONS,
    CEFR_LEVELS,
    PASS_THRESHOLD,
    _hash_answer,
)


def run_level_test(estimated_level: str) -> str:
    """Run adaptive level test starting from estimated level.

    Uses SHA256-hashed questions from test_questions.py.

    Args:
        estimated_level: User's self-assessed CEFR level

    Returns:
        Detected CEFR level based on test performance
    """
    typer.echo("\n📝 Adaptive Level Test")
    typer.echo("=" * 40)
    typer.echo("I'll ask you questions starting from your estimated level.")
    typer.echo("If you pass, we move to the next level.")
    typer.echo("If you struggle, we stop and confirm your current level.")
    typer.echo(f"Pass threshold: {PASS_THRESHOLD*100:.0f}% per level\n")

    current_level_idx = CEFR_LEVELS.index(estimated_level)
    failed_level = None

    while current_level_idx < len(CEFR_LEVELS):
        level = CEFR_LEVELS[current_level_idx]
        questions = _get_random_questions(level, QUESTIONS_PER_LEVEL)

        typer.echo(f"\n{'='*40}")
        typer.echo(f"📖 Level {level} — {len(questions)} questions")
        typer.echo(f"{'='*40}")

        correct = 0
        for i, (question, options, hashed_answer) in enumerate(questions, 1):
            typer.echo(f"\n  Question {i}:")
            typer.echo(f"  {question}")

            # Show options with randomized positions
            shuffled_options, answer_idx = _shuffle_options(options, hashed_answer)
            for j, opt in enumerate(shuffled_options, 1):
                typer.echo(f"    {j}) {opt}")

            # Get user answer
            user_answer_num = typer.prompt(
                "  Your answer (number)",
                type=int,
                default=0,
            )

            # Validate input
            if user_answer_num < 1 or user_answer_num > len(shuffled_options):
                typer.echo(f"  ⚠️  Invalid choice. Skipping question.")
                continue

            selected = shuffled_options[user_answer_num - 1]

            # Check against hashed answer
            if _hash_answer(selected) == hashed_answer:
                correct += 1
                typer.echo(f"  ✅ Correct!")
            else:
                typer.echo(f"  ❌ Wrong.")

        # Calculate score for this level
        score = correct / len(questions)
        typer.echo(f"\n  📊 Score: {correct}/{len(questions)} ({score:.0%})")

        if score >= PASS_THRESHOLD:
            typer.echo(f"  ✅ Passed {level}! Moving to next level...")
            current_level_idx += 1
        else:
            typer.echo(f"  ❌ Did not pass {level}. This is your current level.")
            failed_level = level
            break

    # If they passed all levels
    if failed_level is None:
        return CEFR_LEVELS[-1]  # C2

    return failed_level


QUESTIONS_PER_LEVEL = 5


def run_init(ctx: dict) -> None:
    """Run the initialization flow: level test, objectives, profile creation."""
    config: Config = ctx["config"]
    db = ctx["db"]

    typer.echo("🏔️  Piramid-Tongue — Initialization")
    typer.echo("=" * 40)

    # Step 1: Ask user their estimated level
    typer.echo("\n📊 First, tell me your estimated English level:")
    typer.echo("   A1 — Beginner (can use basic phrases)")
    typer.echo("   A2 — Elementary (can handle simple transactions)")
    typer.echo("   B1 — Intermediate (can deal with most travel situations)")
    typer.echo("   B2 — Upper Intermediate (can interact with native speakers)")
    typer.echo("   C1 — Advanced (can express ideas fluently)")
    typer.echo("   C2 — Proficient (can match native speakers)")

    estimated_level = typer.prompt(
        "\nWhat's your estimated level?",
        default="B1",
    ).upper()

    # Validate input
    while estimated_level not in CEFR_LEVELS:
        typer.echo(f"Invalid level. Please enter one of: {', '.join(CEFR_LEVELS)}")
        estimated_level = typer.prompt("What's your estimated level?").upper()

    # Step 2: Ask if they want to take a test to validate
    typer.echo(f"\nYou selected: {estimated_level}")
    validate = typer.confirm(
        f"Would you like to take a test to validate your {estimated_level} level? "
        "(If you skip, we'll use your estimated level directly)",
        default=True,
    )

    if validate:
        detected_level = run_level_test(estimated_level)
        level = detected_level
        typer.echo(f"\n🎯 Detected level: {level}")
    else:
        level = estimated_level
        typer.echo(f"\n✅ Using your estimated level: {level}")

    # Step 3: Configure objectives
    typer.echo("\n📋 Configure your objectives:")
    technical = typer.confirm("Technical English (work/documentation)?", default=True)
    conversational = typer.confirm("Conversational English (travel/social)?", default=True)

    objectives = []
    if technical:
        objectives.append("technical")
    if conversational:
        objectives.append("conversational")
    if not objectives:
        objectives = ["both"]

    # Step 4: External platforms
    typer.echo("\n📱 External platforms (optional):")
    platforms = []
    while typer.confirm("Add a platform to track?", default=False):
        name = typer.prompt("Platform name (e.g., Duolingo)")
        url = typer.prompt("URL", default="")
        platforms.append({"name": name, "url": url, "streak": 0, "metrics": {}})

    # Step 5: Save profile
    config.update("level", level)
    config.update("objectives", objectives)
    config.update("platforms", platforms)
    config.update("streak", {"current": 0, "longest": 0, "last_active": None})
    config.save_profile()

    # Step 6: Initialize DB
    db.init_schema()
    db.execute(
        "INSERT OR IGNORE INTO streaks (current_streak, longest_streak, last_active_date, start_date) VALUES (0, 0, ?, ?)",
        (None, str(date.today())),
    )

    typer.echo("\n✅ Profile created successfully!")
    typer.echo(f"   Level: {level}")
    typer.echo(f"   Objectives: {', '.join(objectives)}")
    typer.echo(f"   Platforms: {len(platforms)} configured")
    typer.echo("\nRun 'pt new-day' to start your first day!")


def _get_random_questions(level: str, count: int) -> list:
    """Get random questions from a level, up to 'count' questions."""
    all_questions = LEVEL_QUESTIONS.get(level, [])
    if len(all_questions) <= count:
        return all_questions
    return random.sample(all_questions, count)


def _shuffle_options(options: list, correct_answer_hash: str) -> tuple[list, int]:
    """Shuffle options and return (shuffled_options, new_correct_index)."""
    # Create list of (option, is_correct)
    option_pairs = [(opt, _hash_answer(opt) == correct_answer_hash) for opt in options]
    random.shuffle(option_pairs)

    shuffled = [opt for opt, _ in option_pairs]
    new_correct_idx = next(i for i, (_, is_correct) in enumerate(option_pairs) if is_correct)

    return shuffled, new_correct_idx
