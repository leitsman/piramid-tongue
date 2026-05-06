"""Command: pt vicios — Analyze writing for linguistic vices."""

import typer

from src.cli.commands.write_cmd import detect_vicios


def run_vicios(ctx: dict) -> None:
    """Analyze text for linguistic vices."""
    config = ctx["config"]
    if config.level is None:
        typer.echo("❌ Run 'pt init' first.")
        raise typer.Exit(1)

    typer.echo("🔍 Vicios Detector")
    typer.echo("Paste your text to analyze (empty line to finish):\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "" and lines:
            break
        lines.append(line)

    text = "\n".join(lines)
    word_count = len(text.split())

    if word_count < 10:
        typer.echo("⚠️  Text too short (< 10 words). Vicios detection works better with longer texts.")
        return

    typer.echo(f"\n📝 Analyzing {word_count} words...\n")

    vicios = detect_vicios(text)

    if not vicios:
        typer.echo("✅ No vicios detected! Your writing looks clean.")
        return

    typer.echo(f"⚠️  {len(vicios)} vicio(s) detected:\n")
    for i, v in enumerate(vicios, 1):
        typer.echo(f"  {i}. **{v['description']}**")
        typer.echo(f"     Frequency: {v['frequency']:.1%} (threshold: {v['threshold']:.0%})")
        typer.echo(f"     Matches: {v['count']}")
        if v["suggestion"]:
            typer.echo(f"     → {v['suggestion']}")
        typer.echo("")

    # Store in DB for tracking
    db = ctx["db"]
    for v in vicios:
        db.execute(
            """INSERT INTO vicios_patterns (pattern, description, threshold, count, last_seen)
               VALUES (?, ?, ?, 1, datetime('now'))
               ON CONFLICT(pattern) DO UPDATE SET
                   count = count + 1,
                   last_seen = datetime('now')""",
            (v["pattern"], v["description"], v["threshold"]),
        )

    typer.echo("📊 Vicios tracked. Run '/pt vicios' regularly to monitor improvement!")
