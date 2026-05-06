"""Generic web scraper with rate limiting for Piramid-Tongue."""

import time
import random
from typing import Optional
from urllib.parse import urlparse

# Common browser user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
]


class WebScraper:
    """Generic web scraper with rate limiting and user-agent rotation."""

    def __init__(self, rate_limit_delay: int = 2):
        self.rate_limit_delay = rate_limit_delay
        self._last_request = 0.0
        self._ua_index = 0

    def _get_user_agent(self) -> str:
        """Get next user agent from rotation pool."""
        ua = USER_AGENTS[self._ua_index % len(USER_AGENTS)]
        self._ua_index += 1
        return ua

    def _rate_limit(self) -> None:
        """Enforce rate limiting with jitter."""
        now = time.time()
        elapsed = now - self._last_request
        delay = self.rate_limit_delay + random.uniform(0, 1)
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_request = time.time()

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch and clean article text from a URL.

        Args:
            url: The URL to scrape.

        Returns:
            Clean article text, or None if failed.
        """
        self._rate_limit()
        # TODO: Implement with requests + readability-lxml fallback
        return None

    def is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
