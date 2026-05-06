"""Tests for src/skills modules and CLI commands."""

import pytest

from src.core.cefr_detector import CEFRDetector, SkillCEFRProfile, CEFR_LEVELS


class TestCEFRDetector:
    """Test CEFR level detection."""

    def test_detect_skill_cefr_no_data(self, db):
        """Returns A1 with 0 confidence when no data."""
        detector = CEFRDetector(db)
        profile = detector.detect_skill_cefr("vocab")
        assert profile.detected_level == "A1"
        assert profile.confidence == 0.0
        assert profile.session_count == 0

    def test_detect_skill_cefr_with_progress(self, populated_db):
        """Correctly detects level from XP."""
        detector = CEFRDetector(populated_db)
        profile = detector.detect_skill_cefr("vocab")
        # vocab has 150 XP which is A2 level
        assert profile.detected_level == "A2"
        assert profile.xp_total == 150
        # session_count comes from skills_progress.session_count
        assert profile.session_count >= 1

    def test_detect_skill_cefr_average_rating(self, populated_db):
        """Correctly calculates average rating."""
        detector = CEFRDetector(populated_db)
        profile = detector.detect_skill_cefr("vocab")
        # Ratings are 4 and 5
        assert profile.average_rating == 4.5

    def test_detect_skill_cefr_confidence_low_with_few_sessions(self, db):
        """Confidence is low with few sessions."""
        db.update_skill_progress("vocab", xp=50)
        db.log_session("vocab", self_rating=3)
        detector = CEFRDetector(db)
        profile = detector.detect_skill_cefr("vocab")
        assert profile.confidence < 1.0

    def test_detect_all_skills(self, populated_db):
        """Returns profiles for all skills."""
        detector = CEFRDetector(populated_db)
        profiles = detector.detect_all_skills()
        assert len(profiles) == 5
        skill_names = [p.skill_name for p in profiles]
        assert "vocab" in skill_names
        assert "speak" in skill_names

    def test_get_skill_comprehension_trend(self, populated_db):
        """Returns comprehension trend data."""
        detector = CEFRDetector(populated_db)
        trend = detector.get_skill_comprehension_trend("vocab", limit=5)
        assert len(trend) >= 2
        assert "date" in trend[0]
        assert "rating" in trend[0]


class TestSkillCEFRProfile:
    """Test SkillCEFRProfile dataclass."""

    def test_profile_creation(self):
        """Profile stores all data correctly."""
        profile = SkillCEFRProfile(
            skill_name="read",
            detected_level="B1",
            confidence=0.8,
            session_count=10,
            average_rating=3.5,
            xp_total=300,
            recommendation="Keep practicing",
        )
        assert profile.skill_name == "read"
        assert profile.detected_level == "B1"
        assert profile.confidence == 0.8
        assert profile.session_count == 10
        assert profile.average_rating == 3.5
        assert profile.xp_total == 300


class TestCEFROverall:
    """Test CEFR level boundaries."""

    def test_all_levels_defined(self):
        """All CEFR levels are defined."""
        assert "A1" in CEFR_LEVELS
        assert "A2" in CEFR_LEVELS
        assert "B1" in CEFR_LEVELS
        assert "B2" in CEFR_LEVELS
        assert "C1" in CEFR_LEVELS
        assert "C2" in CEFR_LEVELS

    def test_level_order(self):
        """Levels are in correct order."""
        assert CEFR_LEVELS.index("A1") < CEFR_LEVELS.index("A2")
        assert CEFR_LEVELS.index("A2") < CEFR_LEVELS.index("B1")
        assert CEFR_LEVELS.index("B1") < CEFR_LEVELS.index("B2")
        assert CEFR_LEVELS.index("B2") < CEFR_LEVELS.index("C1")
        assert CEFR_LEVELS.index("C1") < CEFR_LEVELS.index("C2")
