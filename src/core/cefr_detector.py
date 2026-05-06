"""CEFR level detection per skill based on session analysis.

Analyzes session history and comprehension scores to detect the user's
current CEFR level for each skill (vocab, listen, read, write, speak).
"""

from dataclasses import dataclass
from typing import Literal

from src.db import DB


CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

# CEFR thresholds based on session data
CEFR_XP_THRESHOLDS = {
    "vocab": {"A1": 0, "A2": 100, "B1": 300, "B2": 600, "C1": 1000, "C2": 1500},
    "read": {"A1": 0, "A2": 100, "B1": 300, "B2": 600, "C1": 1000, "C2": 1500},
    "listen": {"A1": 0, "A2": 100, "B1": 300, "B2": 600, "C1": 1000, "C2": 1500},
    "write": {"A1": 0, "A2": 150, "B1": 400, "B2": 800, "C1": 1200, "C2": 1800},
    "speak": {"A1": 0, "A2": 200, "B1": 500, "B2": 1000, "C1": 1500, "C2": 2000},
}

# Minimum sessions needed for reliable CEFR detection
MIN_SESSIONS_FOR_DETECTION = 3


@dataclass
class SkillCEFRProfile:
    """Detected CEFR profile for a skill."""
    skill_name: str
    detected_level: str
    confidence: float  # 0.0 to 1.0
    session_count: int
    average_rating: float | None
    xp_total: int
    recommendation: str


class CEFRDetector:
    """Detect CEFR level per skill by analyzing session history."""

    def __init__(self, db: DB):
        self.db = db

    def detect_skill_cefr(self, skill_name: Literal["vocab", "listen", "read", "write", "speak"]) -> SkillCEFRProfile:
        """Detect CEFR level for a specific skill."""
        sessions = self.db.fetchall(
            "SELECT * FROM sessions WHERE skill_name = ? ORDER BY date DESC",
            (skill_name,),
        )
        
        progress = self.db.fetchone(
            "SELECT * FROM skills_progress WHERE skill_name = ?",
            (skill_name,),
        )
        
        if not progress:
            return SkillCEFRProfile(
                skill_name=skill_name,
                detected_level="A1",
                confidence=0.0,
                session_count=0,
                average_rating=None,
                xp_total=0,
                recommendation="Start practicing to establish baseline.",
            )
        
        xp_total = progress["xp"]
        session_count = progress["session_count"]
        
        # Calculate average rating from sessions
        ratings = [s["self_rating"] for s in sessions if s["self_rating"]]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        
        # Detect level based on XP thresholds
        detected_level = self._detect_level_from_xp(skill_name, xp_total)
        
        # Calculate confidence based on session count and rating consistency
        confidence = self._calculate_confidence(session_count, ratings)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(skill_name, detected_level, session_count, avg_rating)
        
        return SkillCEFRProfile(
            skill_name=skill_name,
            detected_level=detected_level,
            confidence=confidence,
            session_count=session_count,
            average_rating=avg_rating,
            xp_total=xp_total,
            recommendation=recommendation,
        )

    def _detect_level_from_xp(self, skill_name: str, xp: int) -> str:
        """Detect CEFR level based on XP thresholds."""
        thresholds = CEFR_XP_THRESHOLDS.get(skill_name, CEFR_XP_THRESHOLDS["vocab"])
        
        detected = "A1"
        for level in reversed(CEFR_LEVELS):
            if xp >= thresholds.get(level, 0):
                detected = level
                break
        return detected

    def _calculate_confidence(self, session_count: int, ratings: list[int]) -> float:
        """Calculate detection confidence (0.0 to 1.0)."""
        if session_count < MIN_SESSIONS_FOR_DETECTION:
            # Not enough sessions
            base_confidence = session_count / MIN_SESSIONS_FOR_DETECTION
        else:
            base_confidence = 1.0
        
        # Reduce confidence if ratings are inconsistent
        if len(ratings) >= 3:
            avg = sum(ratings) / len(ratings)
            variance = sum((r - avg) ** 2 for r in ratings) / len(ratings)
            # High variance reduces confidence
            if variance > 2.0:
                base_confidence *= 0.6
            elif variance > 1.0:
                base_confidence *= 0.8
        
        return min(1.0, max(0.0, base_confidence))

    def _generate_recommendation(self, skill_name: str, level: str, session_count: int, avg_rating: float | None) -> str:
        """Generate a learning recommendation based on detected level."""
        if session_count < MIN_SESSIONS_FOR_DETECTION:
            return f"Continue practicing {skill_name} to improve CEFR detection accuracy."
        
        if avg_rating is not None and avg_rating < 2.5:
            return f"Your comprehension scores suggest focusing on easier {level} content before advancing."
        elif avg_rating is not None and avg_rating >= 4.5:
            if level != "C2":
                return f"Excellent performance! Consider trying harder content to advance from {level}."
        
        return f"Continue practicing at {level} level to maintain progress."

    def detect_all_skills(self) -> list[SkillCEFRProfile]:
        """Detect CEFR levels for all skills."""
        skills = ["vocab", "listen", "read", "write", "speak"]
        return [self.detect_skill_cefr(skill) for skill in skills]

    def get_skill_comprehension_trend(self, skill_name: str, limit: int = 10) -> list[dict]:
        """Get comprehension trend for a skill over recent sessions."""
        sessions = self.db.fetchall(
            """SELECT date, self_rating, duration_seconds 
               FROM sessions 
               WHERE skill_name = ? AND self_rating IS NOT NULL
               ORDER BY date DESC
               LIMIT ?""",
            (skill_name, limit),
        )
        return [
            {
                "date": s["date"],
                "rating": s["self_rating"],
                "duration": s["duration_seconds"],
            }
            for s in sessions
        ]
