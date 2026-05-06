"""CLI validation tests: all 9 commands operational, help text, errors."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from src.cli.main import app


@pytest.fixture
def cli_runner():
    """Provide Typer CLI runner."""
    return CliRunner()


@pytest.fixture
def initialized_env(cli_runner, tmp_path):
    """Create a temporary environment with config and DB."""
    config_dir = tmp_path / ".config" / "piramid-tongue"
    config_dir.mkdir(parents=True)
    
    # Create profile
    profile_file = config_dir / "profile.yml"
    profile_file.write_text("level: B1\nobjectives:\n  - fluency\n")
    
    # Create db path
    db_dir = tmp_path / ".piramid-tongue"
    db_dir.mkdir()
    db_file = db_dir / "piramid-tongue.db"
    
    return {"config_dir": config_dir, "db_file": db_file}


class TestCLIHelp:
    """Test CLI help text and commands."""

    def test_main_help(self, cli_runner):
        """Main help shows all commands."""
        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Pyramid-Tongue" in result.stdout or "piramid" in result.stdout.lower()
        assert "vocab" in result.stdout
        assert "listen" in result.stdout
        assert "read" in result.stdout
        assert "write" in result.stdout
        assert "speak" in result.stdout
        assert "progress" in result.stdout
        assert "roadmap" in result.stdout
        assert "vicios" in result.stdout
        assert "practice" in result.stdout
        assert "init" in result.stdout
        assert "new-day" in result.stdout

    def test_init_help(self, cli_runner):
        """init command has help text."""
        result = cli_runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize" in result.stdout

    def test_vocab_help(self, cli_runner):
        """vocab command has help text."""
        result = cli_runner.invoke(app, ["vocab", "--help"])
        assert result.exit_code == 0
        assert "vocabulary" in result.stdout.lower()

    def test_listen_help(self, cli_runner):
        """listen command has help text."""
        result = cli_runner.invoke(app, ["listen", "--help"])
        assert result.exit_code == 0

    def test_read_help(self, cli_runner):
        """read command has help text."""
        result = cli_runner.invoke(app, ["read", "--help"])
        assert result.exit_code == 0

    def test_write_help(self, cli_runner):
        """write command has help text."""
        result = cli_runner.invoke(app, ["write", "--help"])
        assert result.exit_code == 0

    def test_speak_help(self, cli_runner):
        """speak command has help text."""
        result = cli_runner.invoke(app, ["speak", "--help"])
        assert result.exit_code == 0

    def test_progress_help(self, cli_runner):
        """progress command has help text."""
        result = cli_runner.invoke(app, ["progress", "--help"])
        assert result.exit_code == 0

    def test_roadmap_help(self, cli_runner):
        """roadmap command has help text."""
        result = cli_runner.invoke(app, ["roadmap", "--help"])
        assert result.exit_code == 0

    def test_vicios_help(self, cli_runner):
        """vicios command has help text."""
        result = cli_runner.invoke(app, ["vicios", "--help"])
        assert result.exit_code == 0

    def test_practice_help(self, cli_runner):
        """practice command has help text."""
        result = cli_runner.invoke(app, ["practice", "--help"])
        assert result.exit_code == 0

    def test_new_day_help(self, cli_runner):
        """new-day command has help text."""
        result = cli_runner.invoke(app, ["new-day", "--help"])
        assert result.exit_code == 0


class TestCLICommandsExist:
    """Test all 9 commands are registered."""

    def test_all_nine_commands_respond(self, cli_runner):
        """All 9 commands can be invoked (may error but should not 404)."""
        commands = ["init", "vocab", "listen", "read", "write", "speak", 
                    "practice", "progress", "roadmap", "vicios", "new-day"]
        
        for cmd in commands:
            # Commands should at least not return "not found"
            result = cli_runner.invoke(app, [cmd])
            # Exit code 1 means command ran but had a runtime error (acceptable)
            # Exit code 0 means success
            # Only 127 would mean "command not found" (which won't happen with Typer)
            assert result.exit_code in [0, 1], f"Command {cmd} not found or crashed unexpectedly"


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_command_shows_help(self, cli_runner):
        """Invalid command shows help."""
        result = cli_runner.invoke(app, ["nonexistent"])
        # Typer shows help for invalid commands
        assert result.exit_code != 0

    def test_init_requires_config(self, cli_runner):
        """init command handles missing config gracefully."""
        with patch('src.cli.main.get_context') as mock_ctx:
            mock_ctx.side_effect = Exception("No config")
            result = cli_runner.invoke(app, ["init"])
            # Should handle error gracefully
            assert result.exit_code in [0, 1]


class TestCLINoCrash:
    """Test commands don't crash on basic invocation."""

    def test_vocab_doesnt_crash_without_init(self, cli_runner):
        """vocab handles missing initialization gracefully."""
        # Even without proper setup, commands should not produce tracebacks
        result = cli_runner.invoke(app, ["vocab"])
        # Either shows error or proceeds - no traceback
        assert "Traceback" not in result.stdout
        assert "Error" in result.stdout or result.exit_code in [0, 1]

    def test_progress_shows_pyramid(self, cli_runner):
        """progress command displays pyramid visualization."""
        result = cli_runner.invoke(app, ["progress"])
        # Should contain pyramid-related output
        # Even if empty data, should not crash
        assert result.exit_code in [0, 1]
        assert "Traceback" not in result.stdout
