"""Command: pt read — Reading practice."""

import typer


def run_read(ctx: dict) -> None:
    """Run reading practice session."""
    config = ctx["config"]
    if config.level is None:
        typer.echo("❌ Run 'pt init' first.")
        raise typer.Exit(1)

    db = ctx["db"]
    pyramid = ctx["pyramid"]

    if not pyramid.is_skill_available("read"):
        reason = pyramid.blocked_reason("read")
        typer.echo(f"🔒 Reading is locked. {reason}")
        raise typer.Exit(1)

    typer.echo("📖 Reading Practice")
    typer.echo("1. Get text recommendation")
    typer.echo("2. Start reading session")

    choice = typer.prompt("Choose (1/2)", default="1")

    if choice == "1":
        typer.echo(f"\n📰 Recommended texts for level {config.level}:")
        typer.echo("  - BBC News (simplified)")
        typer.echo("  - Project Gutenberg (abridged)")
        typer.echo("\nPaste a URL or text to begin.")
    elif choice == "2":
        duration = typer.prompt("Reading duration (minutes)", type=int, default=15)
        comprehension = typer.prompt("Comprehension score (1-5)", type=int, default=3)
        db.log_session("read", duration_seconds=duration * 60, self_rating=comprehension)
        db.update_skill_progress("read", xp=10)
        typer.echo(f"✅ Session logged. +10 XP!")
