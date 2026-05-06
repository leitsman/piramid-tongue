"""Spaced Repetition System (SRS) using SM-2 algorithm for vocabulary.

SM-2 algorithm:
- Each card has an ease_factor (starts at 2.5), interval (days), and repetitions count.
- After each review, the user rates quality (0-5).
- interval and ease_factor are updated based on the rating.
"""

from dataclasses import dataclass


@dataclass
class SM2Card:
    """Represents a flashcard with SM-2 state."""
    word_id: int
    interval: int = 0
    ease_factor: float = 2.5
    repetitions: int = 0

    @property
    def is_due(self) -> bool:
        """Whether this card is due for review (simplified check)."""
        return self.interval <= 0

    def review(self, quality: int) -> None:
        """Process a review with given quality (0-5).

        Args:
            quality: 0=complete blackout, 5=perfect recall
        """
        if quality < 0 or quality > 5:
            raise ValueError(f"Quality must be 0-5, got {quality}")

        if quality < 3:
            # Failed recall: reset
            self.repetitions = 0
            self.interval = 1
        else:
            # Successful recall
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)
            self.repetitions += 1

        # Update ease factor
        self.ease_factor = max(
            1.3,
            self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
        )

    def next_review_days(self) -> int:
        """Estimated days until next review."""
        return self.interval


def calculate_interval(ease_factor: float, repetitions: int, current_interval: int, quality: int) -> tuple[int, float, int]:
    """Calculate new SM-2 values without mutating a card.

    Returns:
        (new_interval, new_ease_factor, new_repetitions)
    """
    if quality < 3:
        return 1, max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))), 0

    new_repetitions = repetitions + 1
    if repetitions == 0:
        new_interval = 1
    elif repetitions == 1:
        new_interval = 6
    else:
        new_interval = int(current_interval * ease_factor)

    new_ease = max(
        1.3,
        ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )

    return new_interval, new_ease, new_repetitions


def quality_description(quality: int) -> str:
    """Human-readable description of quality rating."""
    descriptions = {
        0: "Complete blackout",
        1: "Incorrect response, but remembered when shown",
        2: "Incorrect response, but easy to recall",
        3: "Correct response, required serious effort",
        4: "Correct response, slight hesitation",
        5: "Perfect recall",
    }
    return descriptions.get(quality, "Unknown")
