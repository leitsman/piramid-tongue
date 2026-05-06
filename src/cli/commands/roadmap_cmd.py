"""Command: pt roadmap — Show next steps and dependencies."""

import typer


def run_roadmap(ctx: dict) -> None:
    """Show roadmap: next step, dependencies, time estimate."""
    config = ctx["config"]
    if config.level is None:
        typer.echo("❌ Run 'pt init' first.")
        raise typer.Exit(1)

    pyramid = ctx["pyramid"]

    typer.echo("🗺️  Your Learning Roadmap")
    typer.echo("=" * 50)

    # Current level progression
    cefr_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
    current_idx = cefr_order.index(config.level) if config.level in cefr_order else 0

    typer.echo(f"\n📊 Current level: {config.level}")
    if current_idx < len(cefr_order) - 1:
        next_level = cefr_order[current_idx + 1]
        typer.echo(f"🎯 Next level: {next_level}")
        # Rough estimate: ~200 guided hours per CEFR level
        hours_needed = 200
        hours_per_day = 1  # Assuming 1 hour daily
        days = hours_needed / hours_per_day
        typer.echo(f"⏱️  Estimated time: ~{int(days)} days at {hours_per_day}h/day")
    else:
        typer.echo("🏆 You're at the highest level! Focus on maintenance.")

    # Skill dependencies
    typer.echo("\n📋 Skill Dependencies:")
    status = pyramid.get_pyramid_status()
    for s in status:
        icon = "✅" if s["unlocked"] else "🔒"
        xp_progress = min(s["xp"], 100)
        typer.echo(f"  {icon} {s['name'].upper()}: {xp_progress}/100 XP to unlock next")
        if s["blocked_reason"]:
            typer.echo(f"     {s['blocked_reason']}")

    # Recommendations
    next_skill = pyramid.get_next_skill()
    if next_skill:
        typer.echo(f"\n💡 Next recommended: Practice **{next_skill.upper()}**")
    else:
        typer.echo("\n💡 All skills unlocked! Focus on your weakest area.")
