"""Command: pt init — Initialize profile and level test."""

import typer
from datetime import date

from src.core.config import Config

LEVEL_QUESTIONS = {
    "A1": [
        ("What ___ your name?", ["is", "are", "am"], "is"),
        ("She ___ a teacher.", ["is", "are", "am"], "is"),
        ("I ___ from Spain.", ["am", "is", "are"], "am"),
        ("They ___ students.", ["are", "is", "am"], "are"),
        ("___ you speak English?", ["Do", "Does", "Are"], "Do"),
        ("He ___ not like coffee.", ["does", "do", "is"], "does"),
        ("We ___ to school every day.", ["go", "goes", "going"], "go"),
        ("My mother ___ in a hospital.", ["works", "work", "working"], "works"),
        ("I ___ breakfast at 7 AM.", ["have", "has", "having"], "have"),
        ("___ she a doctor?", ["Is", "Are", "Do"], "Is"),
        ("There ___ a book on the table.", ["is", "are", "am"], "is"),
        ("I ___ English every day.", ["study", "studies", "studying"], "study"),
        ("She ___ to music in the evening.", ["listens", "listen", "listening"], "listens"),
        ("We ___ TV on weekends.", ["watch", "watches", "watching"], "watch"),
        ("He ___ football on Sundays.", ["plays", "play", "playing"], "plays"),
        ("They ___ in a big house.", ["live", "lives", "living"], "live"),
        ("I ___ a car.", ["have", "has", "having"], "have"),
        ("She ___ three cats.", ["has", "have", "having"], "has"),
        ("___ they at home?", ["Are", "Is", "Do"], "Are"),
        ("I ___ happy today.", ["am", "is", "are"], "am"),
    ],
}


def run_init(ctx: dict) -> None:
    """Run the initialization flow: level test, objectives, profile creation."""
    config: Config = ctx["config"]
    db = ctx["db"]

    typer.echo("🏔️  Piramid-Tongue — Initialization")
    typer.echo("=" * 40)

    # Step 1: Ask if user wants to take level test
    skip_test = typer.confirm(
        "Would you like to take a level test? (recommended)", default=True
    )

    if not skip_test:
        level = typer.prompt(
            "Enter your CEFR level (A1/A2/B1/B2/C1/C2)",
            default="A1",
        )
    else:
        level = _run_level_test(db)

    # Step 2: Configure objectives
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

    # Step 3: External platforms
    typer.echo("\n📱 External platforms (optional):")
    platforms = []
    while typer.confirm("Add a platform to track?", default=False):
        name = typer.prompt("Platform name (e.g., Duolingo)")
        url = typer.prompt("URL", default="")
        platforms.append({"name": name, "url": url, "streak": 0, "metrics": {}})

    # Step 4: Save profile
    config.update("level", level)
    config.update("objectives", objectives)
    config.update("platforms", platforms)
    config.update("streak", {"current": 0, "longest": 0, "last_active": None})
    config.save_profile()

    # Step 5: Initialize DB
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


def _run_level_test(db) -> str:
    """Run a simplified level test and return CEFR level."""
    typer.echo("\n📝 Level Test (A1)")
    typer.echo("Answer with the correct option (a/b/c):\n")

    questions = LEVEL_QUESTIONS["A1"]
    correct = 0
    total = len(questions)

    for i, (question, options, answer) in enumerate(questions, 1):
        typer.echo(f"  {i}. {question}")
        for j, opt in enumerate(options, 1):
            typer.echo(f"     {j}) {opt}")
        user_input = typer.prompt("  Your answer (number)", type=int)
        selected = options[user_input - 1] if 1 <= user_input <= 3 else ""
        if selected == answer:
            correct += 1

    score = correct / total
    typer.echo(f"\nScore: {correct}/{total} ({score:.0%})")

    # Simple level assignment based on A1 score
    if score >= 0.9:
        typer.echo("Great! You can start at A2 or higher.")
        level = typer.prompt("Enter your level (A2/B1/B2/C1/C2)", default="A2")
    elif score >= 0.7:
        level = "A1"
        typer.echo("Level assigned: A1")
    else:
        level = "A1"
        typer.echo("Level assigned: A1 (Beginner)")

    return level
