"""Command: pt vocab — Vocabulary practice with spaced repetition."""

import typer

from src.core.config import Config
from src.db import DB
from src.core.spaced_repetition import SM2Card, quality_description


def run_vocab(ctx: dict) -> None:
    """Run vocabulary practice: learn new words or review."""
    config: Config = ctx["config"]

    if config.level is None:
        typer.echo("❌ Run 'pt init' first to set up your profile.")
        raise typer.Exit(1)

    db: DB = ctx["db"]

    mode = typer.prompt(
        "Choose mode: (l)earn new words, (r)eview with SRS, (a)dd word",
        default="r",
    )

    if mode == "l":
        _learn_new_words(db, config.level)
    elif mode == "r":
        _review_words(db)
    elif mode == "a":
        _add_word(db)
    else:
        typer.echo("Invalid mode. Use 'l', 'r', or 'a'.")


def _learn_new_words(db: DB, level: str) -> None:
    """Present new words for the user's level."""
    typer.echo(f"\n📚 Learning new words (Level: {level})")
    typer.echo("Type 'quit' to exit.\n")

    while True:
        word = typer.prompt("Enter a new word (or 'quit')")
        if word.lower() == "quit":
            break
        definition = typer.prompt("Definition")
        example = typer.prompt("Example sentence (optional)", default="")

        db.insert_vocab(word, definition, example, level)
        typer.echo(f"✅ '{word}' saved!\n")

    typer.echo(f"Session complete!")


def _review_words(db: DB) -> None:
    """Review words due for spaced repetition."""
    due = db.get_vocab_due(limit=20)
    if not due:
        typer.echo("📚 No words due for review. Great job!")
        return

    typer.echo(f"\n🔄 {len(due)} words due for review:\n")

    reviewed = 0
    for row in due:
        typer.echo(f"  Word: {row['word']}")
        if row["example"]:
            typer.echo(f"  Example: {row['example']}")
        typer.echo(f"  Definition: {row['definition']}")

        quality = typer.prompt(
            "How well did you recall? (0=blackout, 5=perfect)",
            type=int,
        )
        if 0 <= quality <= 5:
            card = SM2Card(
                word_id=row["id"],
                interval=row["interval"],
                ease_factor=row["ease_factor"],
                repetitions=row.get("last_review") and 1 or 0,
            )
            card.review(quality)
            db.update_vocab_review(row["id"], card.interval, card.ease_factor)
            db.update_skill_progress("vocab", xp=5)
            reviewed += 1
            typer.echo(f"  → {quality_description(quality)} (next: {card.interval} days)\n")
        else:
            typer.echo("  Invalid rating. Skipping.\n")

    typer.echo(f"Reviewed {reviewed} words. +{reviewed * 5} XP!")


def _add_word(db: DB) -> None:
    """Manually add a single word."""
    word = typer.prompt("Word")
    definition = typer.prompt("Definition")
    example = typer.prompt("Example (optional)", default="")
    db.insert_vocab(word, definition, example)
    typer.echo(f"✅ '{word}' added to vocabulary.")
