"""Piramid-Tongue CLI — Main entrypoint.

Usage:
    pt init          Initialize profile and level test
    pt new-day       Start daily tracking
    pt vocab         Vocabulary practice
    pt listen        Listening practice
    pt read          Reading practice
    pt write         Writing practice
    pt speak         Speaking practice
    pt practice      Log external platform practice
    pt progress      Show progress and pyramid visualization
    pt roadmap       Show next steps
    pt vicios        Analyze writing for linguistic vices
"""

from pathlib import Path
import sys

import typer

from src.core.config import Config
from src.db import DB
from src.core.pyramid_engine import PyramidState

app = typer.Typer(
    name="pt",
    help="Piramid-Tongue: CLI for English learning with pyramid methodology",
    add_completion=False,
)


def get_context() -> dict:
    """Build shared context (config, db, pyramid) for commands."""
    config = Config()
    db = DB(config.db_path)
    db.init_schema()
    pyramid = PyramidState()
    return {"config": config, "db": db, "pyramid": pyramid}


# --- Import commands (lazy to avoid circular imports) ---

@app.callback()
def callback():
    """Piramid-Tongue v0.1.0 — Learn English with the pyramid method."""
    pass


@app.command()
def init():
    """Initialize your profile: level test, objectives, and roadmap."""
    from src.cli.commands.init_cmd import run_init
    ctx = get_context()
    run_init(ctx)


@app.command("new-day")
def new_day():
    """Start a new day: read logs, calculate skills to practice, create daily log."""
    from src.cli.commands.new_day_cmd import run_new_day
    ctx = get_context()
    run_new_day(ctx)


@app.command()
def vocab():
    """Practice vocabulary: learn new words or review with spaced repetition."""
    from src.cli.commands.vocab_cmd import run_vocab
    ctx = get_context()
    run_vocab(ctx)


@app.command()
def listen():
    """Listening practice: get content by CEFR level, timed sessions."""
    from src.cli.commands.listen_cmd import run_listen
    ctx = get_context()
    run_listen(ctx)


@app.command()
def read():
    """Reading practice: texts by CEFR level, comprehension exercises."""
    from src.cli.commands.read_cmd import run_read
    ctx = get_context()
    run_read(ctx)


@app.command()
def write():
    """Writing practice: transcription, creation, translation, vicios detection."""
    from src.cli.commands.write_cmd import run_write
    ctx = get_context()
    run_write(ctx)


@app.command()
def speak():
    """Speaking practice: read-aloud, shadowing, tandem reminders."""
    from src.cli.commands.speak_cmd import run_speak
    ctx = get_context()
    run_speak(ctx)


@app.command()
def practice():
    """Log practice on external platforms (Duolingo, etc.)."""
    from src.cli.commands.practice_cmd import run_practice
    ctx = get_context()
    run_practice(ctx)


@app.command()
def progress():
    """Show your progress: level per skill, pyramid visualization, streak."""
    from src.cli.commands.progress_cmd import run_progress
    ctx = get_context()
    run_progress(ctx)


@app.command()
def roadmap():
    """Show your roadmap: next step, dependencies, time estimate."""
    from src.cli.commands.roadmap_cmd import run_roadmap
    ctx = get_context()
    run_roadmap(ctx)


@app.command()
def vicios():
    """Analyze writing for linguistic vices (repeated words, weak intensifiers, etc.)."""
    from src.cli.commands.vicios_cmd import run_vicios
    ctx = get_context()
    run_vicios(ctx)


if __name__ == "__main__":
    app()
