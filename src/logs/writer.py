"""Daily log writer for Piramid-Tongue.

Creates and appends to markdown daily logs in the configured logs directory.
"""

from pathlib import Path
from datetime import date


DAILY_TEMPLATE = """# Log for {date}

## Vocab Review
-

## Listening Practice
-

## Reading Session
-

## Writing Exercise
-

## Speaking Drill
-

## Vicios Detected
-

## Notes
-
"""


class LogWriter:
    """Append-only daily log writer."""

    def __init__(self, logs_dir: str | Path):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _log_path(self, d: date) -> Path:
        return self.logs_dir / f"{d.isoformat()}.md"

    def create_daily_log(self, d: date | None = None) -> Path:
        """Create a new daily log from template. Returns path to the file."""
        d = d or date.today()
        path = self._log_path(d)
        if path.exists():
            return path  # Already exists, don't overwrite
        path.write_text(DAILY_TEMPLATE.format(date=d.isoformat()))
        return path

    def append_section(self, d: date, section_name: str, content: str) -> Path:
        """Append content to a specific section in today's log.

        Creates the log if it doesn't exist.
        """
        path = self._log_path(d)
        if not path.exists():
            self.create_daily_log(d)

        lines = path.read_text().splitlines()
        new_lines = []
        in_section = False
        section_found = False

        for line in lines:
            if line.startswith(f"## {section_name}"):
                in_section = True
                section_found = True
                new_lines.append(line)
                continue
            elif line.startswith("## ") and in_section:
                in_section = False
            if in_section and line.strip() == "-":
                # Replace the placeholder dash with content
                new_lines.append(content)
                in_section = False
                continue
            new_lines.append(line)

        if not section_found:
            # Section doesn't exist, append it
            new_lines.append("")
            new_lines.append(f"## {section_name}")
            new_lines.append(content)

        path.write_text("\n".join(new_lines) + "\n")
        return path

    def get_log(self, d: date | None = None) -> str | None:
        """Read the daily log for a given date."""
        d = d or date.today()
        path = self._log_path(d)
        if path.exists():
            return path.read_text()
        return None

    def get_existing_logs(self) -> list[date]:
        """Return list of dates that have log files."""
        logs = []
        if self.logs_dir.exists():
            for f in self.logs_dir.glob("*.md"):
                try:
                    logs.append(date.fromisoformat(f.stem))
                except ValueError:
                    pass
        return sorted(logs)
