"""Leitner Box System for word-specific weakness tracking.

Implements a 5-box spaced repetition system:
- Box 1: Review daily (interval = 1 day)
- Box 2: Review every 2 days (interval = 2 days)
- Box 3: Review every 4 days (interval = 4 days)
- Box 4: Review every 7 days (interval = 7 days)
- Box 5: Review every 14 days (interval = 14 days)

Box level updates:
- Correct answer: Advance 1 box (max box 5)
- Minor failure: Drop 1 box (min box 1)
- Major failure: Drop 2 boxes (min box 1)
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..db import DB


class LeitnerEngine:
    """Leitner box system engine for weakness review scheduling."""
    
    BOX_INTERVALS = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}  # days
    
    def __init__(self, db: DB | Path | str | None = None):
        """Initialize with database path or DB instance.
        
        Args:
            db: DB instance, or path to database, or None for default path
        """
        if isinstance(db, DB):
            self._db = db
        else:
            self._db = DB(db)
    
    def update_box(self, weakness_id: int, correct: bool, severity: str = "minor") -> int:
        """Update box level based on answer correctness and error severity.
        
        Args:
            weakness_id: ID of weakness record
            correct: Whether user answered correctly
            severity: Error severity ('minor' or 'major')
            
        Returns:
            New box level (1-5)
        """
        # Get current weakness data
        row = self._db.fetchone(
            "SELECT box_level, consecutive_correct FROM weaknesses WHERE id = ?",
            (weakness_id,),
        )
        if not row:
            raise ValueError(f"Weakness id {weakness_id} not found")
        
        current_box = row['box_level']
        current_correct_streak = row['consecutive_correct']
        
        if correct:
            # Correct answer: advance 1 box (max box 5)
            new_box = min(current_box + 1, 5)
            new_consecutive = current_correct_streak + 1
        else:
            # Incorrect: drop based on severity
            drop = 2 if severity == "major" else 1
            new_box = max(current_box - drop, 1)
            new_consecutive = 0  # Reset streak on failure
        
        # Update database
        self._db.update_box_level(weakness_id, new_box, new_consecutive)
        
        return new_box
    
    def get_due_reviews(self, limit: int = 5) -> list[dict[str, Any]]:
        """Get weaknesses due for review today.
        
        Args:
            limit: Maximum number of weaknesses to return
            
        Returns:
            List of weakness dictionaries with word, error_type, context_example, etc.
        """
        rows = self._db.get_words_due(limit=limit)
        return [
            {
                "id": row['id'],
                "word": row['word'],
                "error_type": row['error_type'],
                "context_example": row['context_example'],
                "box_level": row['box_level'],
                "consecutive_correct": row['consecutive_correct'],
                "next_review": row['next_review'],
            }
            for row in rows
        ]
    
    def calculate_next_review(self, box_level: int) -> str:
        """Calculate next review date based on box level.
        
        Args:
            box_level: Current box level (1-5)
            
        Returns:
            ISO format date string for next review
        """
        interval_days = self.BOX_INTERVALS.get(box_level, 1)
        next_date = datetime.now() + timedelta(days=interval_days)
        return next_date.strftime("%Y-%m-%d")
