"""Command: pt progress — Show progress and pyramid visualization."""

import typer


def run_progress(ctx: dict) -> None:
    """Show progress: level per skill, pyramid visualization, streak."""
    config = ctx["config"]
    if config.level is None:
        typer.echo("❌ Run 'pt init' first.")
        raise typer.Exit(1)

    db = ctx["db"]
    pyramid = ctx["pyramid"]

    # Get skill status
    status = pyramid.get_pyramid_status()

    typer.echo("🏔️  Your Pyramid Progress")
    typer.echo("=" * 50)

    # ASCII pyramid visualization (top = speak, bottom = vocab)
    pyramid_order = ["speak", "write", "listen", "read", "vocab"]
    for i, skill_name in enumerate(pyramid_order):
        s = next((x for x in status if x["name"] == skill_name), None)
        if s:
            xp_bar = _xp_bar(s["xp"], width=20)
            icon = "✅" if s["unlocked"] else "🔒"
            padding = " " * (i * 2)
            typer.echo(f"{padding}{icon} {s['name'].upper():6s} {s['level']} {xp_bar} {s['xp']} XP")
            if s["blocked_reason"]:
                typer.echo(f"{padding}   → {s['blocked_reason']}")

    # Streak
    streak = db.fetchone("SELECT * FROM streaks ORDER BY id DESC LIMIT 1")
    if streak:
        typer.echo(f"\n🔥 Streak: {streak['current_streak']} days (longest: {streak['longest_streak']})")

    # Stats
    total_sessions = db.fetchone("SELECT COUNT(*) as count FROM sessions")
    total_words = db.fetchone("SELECT COUNT(*) as count FROM vocab WHERE status = 'acquired'")
    typer.echo(f"📊 Total sessions: {total_sessions['count']}")
    typer.echo(f"📚 Words acquired: {total_words['count']}")


def _xp_bar(xp: int, width: int = 20) -> str:
    """Draw a simple XP progress bar."""
    threshold = 100  # XP to unlock next level
    filled = min(int(xp / threshold * width), width)
    empty = width - filled
    return "[" + "█" * filled + "░" * empty + "]"
