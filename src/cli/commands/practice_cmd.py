"""Command: pt practice — Log external platform practice."""

import typer


def run_practice(ctx: dict) -> None:
    """Log practice on external platforms."""
    config = ctx["config"]
    if config.level is None:
        typer.echo("❌ Run 'pt init' first.")
        raise typer.Exit(1)

    db = ctx["db"]

    platforms = config.platforms
    if not platforms:
        typer.echo("📱 No platforms configured. Run 'pt init' to add platforms.")
        return

    typer.echo("📱 Select platform:")
    for i, p in enumerate(platforms, 1):
        typer.echo(f"  {i}. {p['name']} (streak: {p.get('streak', 0)})")

    choice = typer.prompt("Platform number", type=int)
    if 1 <= choice <= len(platforms):
        platform = platforms[choice - 1]
        typer.echo(f"\nLogging practice for {platform['name']}")
        duration = typer.prompt("Duration (minutes)", type=int, default=15)
        notes = typer.prompt("Notes (optional)", default="")

        db.log_session("practice", duration_seconds=duration * 60, notes=f"{platform['name']}: {notes}")

        typer.echo(f"✅ Practice logged for {platform['name']}!")
    else:
        typer.echo("Invalid selection.")
