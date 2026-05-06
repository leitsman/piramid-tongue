"""YouTube transcript scraper for Piramid-Tongue using yt-dlp."""

import subprocess
from typing import Optional


class YouTubeScraper:
    """Extract YouTube video transcripts and metadata."""

    def __init__(self, rate_limit_delay: int = 2):
        self.rate_limit_delay = rate_limit_delay

    def get_transcript(self, url: str) -> Optional[dict]:
        """Extract transcript from a YouTube video.

        Args:
            url: YouTube video URL.

        Returns:
            Dict with title, transcript, language, and timestamps.
        """
        try:
            result = subprocess.run(
                ["yt-dlp", "--skip-download", "--write-auto-sub", "--sub-lang", "en",
                 "--sub-format", "vtt", "--output", "-", url],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                return {"title": "", "transcript": result.stdout, "language": "en"}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def get_video_metadata(self, url: str) -> Optional[dict]:
        """Get video metadata (title, duration, channel)."""
        import json
        try:
            result = subprocess.run(
                ["yt-dlp", "--dump-json", url],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "title": data.get("title", ""),
                    "duration": data.get("duration", 0),
                    "channel": data.get("channel", ""),
                }
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        return None
