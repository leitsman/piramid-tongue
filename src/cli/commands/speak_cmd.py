"""Command: pt speak — Speaking practice."""

import typer


def run_speak(ctx: dict) -> None:
    """Run speaking practice session."""
    config = ctx["config"]
    if config.level is None:
        typer.echo("❌ Run 'pt init' first.")
        raise typer.Exit(1)

    db = ctx["db"]
    pyramid = ctx["pyramid"]

    if not pyramid.is_skill_available("speak"):
        reason = pyramid.blocked_reason("speak")
        typer.echo(f"🔒 Speaking is locked. {reason}")
        raise typer.Exit(1)

    typer.echo("🗣️  Speaking Practice")
    typer.echo("1. Read-aloud mode")
    typer.echo("2. Shadowing mode")
    typer.echo("3. Tandem reminder")

    choice = typer.prompt("Choose (1/2/3)", default="1")

    if choice == "1":
        typer.echo("\n📖 Paste or type text to read aloud:")
        text = input()
        typer.echo(f"\nRead aloud: '{text[:100]}...'")
        duration = typer.prompt("Duration (minutes)", type=int, default=5)
        db.log_session("speak", duration_seconds=duration * 60, notes="Read-aloud")
        db.update_skill_progress("speak", xp=10)
        typer.echo(f"✅ +10 XP!")

    elif choice == "2":
        typer.echo("\n🎧 Shadowing: Listen to audio, then repeat.")
        typer.echo("(Audio playback not yet implemented in CLI)")
        duration = typer.prompt("Duration (minutes)", type=int, default=10)
        rating = typer.prompt("Self-rating (1-5)", type=int)
        db.log_session("speak", duration_seconds=duration * 60, self_rating=rating, notes="Shadowing")
        db.update_skill_progress("speak", xp=10)
        typer.echo(f"✅ +10 XP!")

    elif choice == "3":
        typer.echo("\n👥 Tandem Reminder:")
        typer.echo("  - Join a Discord English server")
        typer.echo("  - Find a language exchange partner")
        typer.echo("  - Practice for at least 15 minutes")
        db.log_session("speak", notes="Tandem reminder sent")
        db.update_skill_progress("speak", xp=5)
        typer.echo(f"✅ +5 XP!")
