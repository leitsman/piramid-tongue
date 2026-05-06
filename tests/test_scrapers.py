"""Tests for src/scrapers modules."""

import time
from unittest.mock import patch, MagicMock

import pytest

from src.scrapers.bbc import BBCScraper
from src.scrapers.youtube import YouTubeScraper
from src.scrapers.books import BooksScraper
from src.scrapers.web import WebScraper


class TestBBCScraper:
    """Test BBC Learning English scraper."""

    def test_initialization(self):
        """BBCScraper initializes with rate limit delay."""
        scraper = BBCScraper(rate_limit_delay=3)
        assert scraper.rate_limit_delay == 3
        assert scraper._last_request == 0.0

    def test_rate_limit_enforced(self):
        """Rate limiting delays between requests."""
        scraper = BBCScraper(rate_limit_delay=1)
        start = time.time()
        scraper._rate_limit()
        scraper._rate_limit()  # Second call should be delayed
        elapsed = time.time() - start
        assert elapsed >= 0.9  # Allow small margin

    def test_fetch_articles_returns_list(self):
        """fetch_articles returns a list."""
        scraper = BBCScraper()
        articles = scraper.fetch_articles(level="intermediate", limit=5)
        assert isinstance(articles, list)

    def test_fetch_article_content_returns_dict_or_none(self):
        """fetch_article_content returns dict or None."""
        scraper = BBCScraper()
        result = scraper.fetch_article_content("https://example.com")
        assert result is None or isinstance(result, dict)


class TestYouTubeScraper:
    """Test YouTube transcript scraper."""

    def test_initialization(self):
        """YouTubeScraper initializes with rate_limit_delay."""
        scraper = YouTubeScraper(rate_limit_delay=3)
        assert scraper.rate_limit_delay == 3

    def test_get_transcript_returns_dict_or_none(self):
        """get_transcript returns dict or None."""
        scraper = YouTubeScraper()
        # Without actual yt-dlp, should return None
        result = scraper.get_transcript("https://youtube.com/watch?v=test")
        assert result is None or isinstance(result, dict)

    def test_get_video_metadata_returns_dict_or_none(self):
        """get_video_metadata returns dict or None."""
        scraper = YouTubeScraper()
        result = scraper.get_video_metadata("https://youtube.com/watch?v=test")
        assert result is None or isinstance(result, dict)


class TestBooksScraper:
    """Test Gutenberg books scraper."""

    def test_initialization(self):
        """BooksScraper initializes correctly."""
        scraper = BooksScraper()
        assert scraper.GUTENBERG_URL == "https://www.gutenberg.org"

    def test_search_by_level_returns_list(self):
        """search_by_level returns a list."""
        scraper = BooksScraper()
        results = scraper.search_by_level("B1", limit=5)
        assert isinstance(results, list)
        assert len(results) == 0  # Not implemented yet

    def test_fetch_book_returns_dict_or_none(self):
        """fetch_book returns dict or None."""
        scraper = BooksScraper()
        result = scraper.fetch_book("1342")
        # Not implemented yet
        assert result is None


class TestWebScraper:
    """Test generic web scraper."""

    def test_initialization(self):
        """WebScraper initializes with rotation state."""
        scraper = WebScraper()
        assert scraper._last_request == 0.0
        assert scraper._ua_index == 0
        assert scraper.rate_limit_delay == 2

    def test_rate_limit_enforced(self):
        """Rate limiting is enforced."""
        scraper = WebScraper(rate_limit_delay=1)
        start = time.time()
        scraper._rate_limit()
        scraper._rate_limit()
        elapsed = time.time() - start
        assert elapsed >= 0.9

    def test_fetch_page_returns_none_without_implementation(self):
        """fetch_page returns None for unimplemented scraping."""
        scraper = WebScraper()
        result = scraper.fetch_page("https://example.com")
        # Without implementation, returns None
        assert result is None

    def test_is_valid_url(self):
        """is_valid_url correctly validates URLs."""
        scraper = WebScraper()
        assert scraper.is_valid_url("https://example.com") is True
        assert scraper.is_valid_url("http://test.org/path") is True
        assert scraper.is_valid_url("not-a-url") is False
        assert scraper.is_valid_url("") is False


class TestScraperRateLimiting:
    """Test rate limiting across scrapers."""

    def test_rate_limit_timing(self):
        """Rate limit delay is respected."""
        scraper = BBCScraper(rate_limit_delay=2)
        start = time.time()
        scraper._rate_limit()
        scraper._rate_limit()
        elapsed = time.time() - start
        assert elapsed >= 1.8  # Allow small margin

    def test_different_scrapers_have_independent_limits(self):
        """Each scraper instance has independent rate limiting."""
        scraper1 = BBCScraper(rate_limit_delay=1)
        scraper2 = BBCScraper(rate_limit_delay=5)
        
        scraper1._rate_limit()
        
        # scraper2 should not be affected
        start = time.time()
        scraper2._rate_limit()
        elapsed = time.time() - start
        assert elapsed < 1.0  # scraper2 has 5s delay but should be instant first call
