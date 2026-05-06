"""Project Gutenberg books scraper for Piramid-Tongue."""

from typing import Optional


class BooksScraper:
    """Fetch public domain books from Project Gutenberg by CEFR level."""

    GUTENBERG_URL = "https://www.gutenberg.org"

    def fetch_book(self, book_id: str) -> Optional[dict]:
        """Fetch a book by Gutenberg ID.

        Args:
            book_id: Project Gutenberg book ID.

        Returns:
            Dict with title, author, text, and chapter splits.
        """
        # TODO: Implement HTTP fetch + plain text extraction
        return None

    def search_by_level(self, level: str, limit: int = 5) -> list[dict]:
        """Search for books appropriate for a CEFR level."""
        # TODO: Implement search with CEFR classification
        return []
