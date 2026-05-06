"""Command: pt new-day — Start daily tracking."""

import typer
from datetime import date

from src.core.config import Config
from src.logs.writer import LogWriter


def run_new_day(ctx: dict) -> None:
    """Read logs, calculate skills needing attention, create daily log."""
    config: Config = ctx["config"]
    db = ctx["db"]
    pyramid = ctx["pyramid"]

    # Check if initialized
    if config.level is None:
        typer.echo("❌ You haven't initialized yet. Run 'pt init' first.")
        raise typer.Exit(1)

    # Get existing logs
    logs_dir = config.logs_dir
    log_writer = LogWriter(logs_dir)
    existing_logs = log_writer.get_existing_logs()

    if existing_logs:
        last_log = existing_logs[-1]
        typer.echo(f"📖 Last active: {last_log.isoformat()}")
    else:
        typer.echo("📖 This is your first day!")

    # Calculate skills to practice
    typer.echo("\n🎯 Recommended skills for today:")
    status = pyramid.get_pyramid_status()
    for s in status:
        icon = "✅" if s["unlocked"] else "🔒"
        typer.echo(f"   {icon} {s['name'].upper()}: {s['level']} (XP: {s['xp']})")
        if s["blocked_reason"]:
            typer.echo(f"      → {s['blocked_reason']}")

    # Create daily log
    today = date.today()
    log_path = log_writer.create_daily_log(today)

    # Update streak
    streak_row = db.fetchone("SELECT * FROM streaks ORDER BY id DESC LIMIT 1")
    if streak_row:
        current = streak_row["current_streak"]
        longest = streak_row["longest_streak"]
        last_active = streak_row["last_active_date"]

        if last_active and date.fromisoformat(last_active) == today:
            typer.echo("\n⚠️  You already started today's log.")
        else:
            current += 1
            if current > longest:
                longest = current
            db.execute(
                "UPDATE streaks SET current_streak = ?, longest_streak = ?, last_active_date = ? WHERE id = ?",
                (current, longest, str(today), streak_row["id"]),
            )
            typer.echo(f"\n🔥 Streak: {current} day{'s' if current != 1 else ''}!")

    typer.echo(f"\n📝 Daily log created: {log_path}")
    typer.echo("Use 'pt vocab', 'pt listen', etc. to practice!")
