"""Progress tracker: stats computation and persistence for Piramid-Tongue."""

from dataclasses import dataclass
from typing import Any


@dataclass
class SkillStats:
    """Statistics for a single skill."""
    name: str
    level: str
    xp: int
    session_count: int
    total_duration_seconds: int
    average_rating: float | None
    last_practiced: str | None


class ProgressTracker:
    """Compute and aggregate progress statistics."""

    def __init__(self, db):
        self.db = db

    def get_skill_stats(self, skill_name: str) -> SkillStats | None:
        """Get comprehensive stats for a skill."""
        progress = self.db.fetchone(
            "SELECT * FROM skills_progress WHERE skill_name = ?",
            (skill_name,),
        )
        if not progress:
            return None

        sessions = self.db.fetchall(
            "SELECT * FROM sessions WHERE skill_name = ?",
            (skill_name,),
        )

        total_duration = sum(s["duration_seconds"] or 0 for s in sessions)
        ratings = [s["self_rating"] for s in sessions if s["self_rating"]]
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        return SkillStats(
            name=skill_name,
            level=progress["level"],
            xp=progress["xp"],
            session_count=progress["session_count"],
            total_duration_seconds=total_duration,
            average_rating=avg_rating,
            last_practiced=progress["last_practiced"],
        )

    def get_all_skills_stats(self) -> list[SkillStats]:
        """Get stats for all skills."""
        skills = ["vocab", "listen", "read", "write", "speak"]
        stats = []
        for skill in skills:
            s = self.get_skill_stats(skill)
            if s:
                stats.append(s)
        return stats

    def get_total_stats(self) -> dict[str, Any]:
        """Get aggregate stats across all skills."""
        total_sessions = self.db.fetchone("SELECT COUNT(*) as c FROM sessions")
        total_words = self.db.fetchone("SELECT COUNT(*) as c FROM vocab")
        acquired_words = self.db.fetchone(
            "SELECT COUNT(*) as c FROM vocab WHERE status = 'acquired'"
        )
        streak = self.db.fetchone("SELECT * FROM streaks ORDER BY id DESC LIMIT 1")

        return {
            "total_sessions": total_sessions["c"],
            "total_words": total_words["c"],
            "acquired_words": acquired_words["c"],
            "current_streak": streak["current_streak"] if streak else 0,
            "longest_streak": streak["longest_streak"] if streak else 0,
        }
