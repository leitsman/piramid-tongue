"""Command: pt write — Writing practice with vicios detection."""

import re
import typer
import yaml
from pathlib import Path

from src.core.config import Config


def run_write(ctx: dict) -> None:
    """Run writing practice session."""
    config: Config = ctx["config"]
    if config.level is None:
        typer.echo("❌ Run 'pt init' first.")
        raise typer.Exit(1)

    db = ctx["db"]
    pyramid = ctx["pyramid"]

    if not pyramid.is_skill_available("write"):
        reason = pyramid.blocked_reason("write")
        typer.echo(f"🔒 Writing is locked. {reason}")
        raise typer.Exit(1)

    typer.echo("✍️  Writing Practice")
    typer.echo("1. Transcription mode")
    typer.echo("2. Free writing mode")
    typer.echo("3. Translation mode")
    typer.echo("4. Analyze text for vicios")

    choice = typer.prompt("Choose (1/2/3/4)", default="2")

    if choice in ("1", "2", "3"):
        _writing_session(db, choice)
    elif choice == "4":
        _analyze_vicios(db, config)


def _writing_session(db, mode: str) -> None:
    """Run a writing session."""
    mode_names = {"1": "Transcription", "2": "Free writing", "3": "Translation"}
    typer.echo(f"\n📝 {mode_names[mode]} mode")
    typer.echo("Paste or type your text (empty line to finish):\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "" and lines:
            break
        lines.append(line)

    text = "\n".join(lines)
    if len(text.strip()) < 10:
        typer.echo("Text too short (< 10 words). Skipping vicios detection.")
        return

    # Log session
    db.log_session("write", notes=f"Mode: {mode_names[mode]}, Length: {len(text.split())} words")
    db.update_skill_progress("write", xp=15)

    # Run vicios detection
    vicios = detect_vicios(text)
    if vicios:
        typer.echo("\n⚠️  Vicios detected:")
        for v in vicios:
            typer.echo(f"  - {v['description']}: {v['frequency']:.1%} (threshold: {v['threshold']:.0%})")
            typer.echo(f"    → {v['suggestion']}")
    else:
        typer.echo("\n✅ No vicios detected! Great writing!")

    typer.echo(f"\n✅ Session logged. +15 XP!")


def detect_vicios(text: str, config_path: str | None = None) -> list[dict]:
    """Detect linguistic vicios in text.

    Args:
        text: The text to analyze.
        config_path: Path to vicios_patterns.yaml. Uses default if None.

    Returns:
        List of detected vicios with description, frequency, and suggestion.
    """
    if len(text.split()) < 10:
        return []

    if config_path is None:
        config_path = str(Path(__file__).parent.parent.parent.parent / "configs" / "vicios_patterns.yaml")

    try:
        with open(config_path) as f:
            patterns = yaml.safe_load(f) or []
    except FileNotFoundError:
        return []

    tokens = re.findall(r'\b\w+\b', text.lower())
    total_tokens = len(tokens)
    if total_tokens == 0:
        return []

    detected = []
    for p in patterns:
        regex = re.compile(p["pattern"], re.IGNORECASE)
        matches = regex.findall(text)
        count = len(matches)
        frequency = count / total_tokens

        if frequency > p["threshold"]:
            detected.append({
                "pattern": p["pattern"],
                "description": p["description"],
                "frequency": frequency,
                "threshold": p["threshold"],
                "suggestion": p.get("suggestion", ""),
                "count": count,
            })

    return detected
