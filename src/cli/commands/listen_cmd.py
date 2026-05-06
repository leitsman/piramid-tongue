"""Command: pt listen — Listening practice."""

import typer


def run_listen(ctx: dict) -> None:
    """Run listening practice session."""
    config = ctx["config"]
    if config.level is None:
        typer.echo("❌ Run 'pt init' first.")
        raise typer.Exit(1)

    db = ctx["db"]
    pyramid = ctx["pyramid"]

    if not pyramid.is_skill_available("listen"):
        reason = pyramid.blocked_reason("listen")
        typer.echo(f"🔒 Listening is locked. {reason}")
        raise typer.Exit(1)

    typer.echo("🎧 Listening Practice")
    typer.echo("1. Get content recommendation")
    typer.echo("2. Start timed session")
    typer.echo("3. Self-evaluate")

    choice = typer.prompt("Choose (1/2/3)", default="1")

    if choice == "1":
        typer.echo(f"\n📺 Recommended content for level {config.level}:")
        typer.echo("  - BBC Learning English (news)")
        typer.echo("  - YouTube: TED-Ed videos")
        typer.echo("\nUse 'pt listen' with a URL to start a session.")
    elif choice == "2":
        duration = typer.prompt("Session duration (minutes)", type=int, default=15)
        typer.echo(f"\n⏱️  Listening session started: {duration} minutes")
        typer.echo("(Timer not implemented in CLI mode — track manually)")
        db.log_session("listen", duration_seconds=duration * 60)
        db.update_skill_progress("listen", xp=10)
        typer.echo("✅ Session logged. +10 XP!")
    elif choice == "3":
        rating = typer.prompt("Self-rating (1-5)", type=int)
        if 1 <= rating <= 5:
            db.log_session("listen", self_rating=rating)
            db.update_skill_progress("listen", xp=5)
            typer.echo(f"✅ Rating {rating}/5 saved. +5 XP!")
