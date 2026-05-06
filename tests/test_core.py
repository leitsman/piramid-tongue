"""Tests for src/core modules: pyramid_engine, spaced_repetition, config."""

import tempfile
from pathlib import Path

import pytest

from src.core.pyramid_engine import PyramidState, SkillState, PYRAMID_DEPENDENCIES, UNLOCK_XP_THRESHOLD
from src.core.spaced_repetition import SM2Card, calculate_interval, quality_description
from src.core.config import Config, deep_merge, load_yaml, DEFAULTS


class TestPyramidEngine:
    """Test pyramid dependency enforcement."""

    def test_pyramid_dependencies_structure(self):
        """PYRAMID_DEPENDENCIES defines correct order."""
        assert PYRAMID_DEPENDENCIES["vocab"] == []
        assert PYRAMID_DEPENDENCIES["read"] == ["vocab"]
        assert PYRAMID_DEPENDENCIES["listen"] == ["read"]
        assert PYRAMID_DEPENDENCIES["write"] == ["listen"]
        assert PYRAMID_DEPENDENCIES["speak"] == ["write"]

    def test_vocab_is_always_unlocked(self, pyramid):
        """vocab skill is always available."""
        assert pyramid.is_skill_available("vocab") is True

    def test_read_blocked_without_vocab(self, pyramid):
        """read skill is blocked when vocab has no XP."""
        assert pyramid.is_skill_available("read") is False

    def test_read_unlocks_after_vocab_threshold(self, pyramid):
        """read unlocks when vocab reaches XP threshold."""
        pyramid.update_skill("vocab", xp_gained=UNLOCK_XP_THRESHOLD)
        assert pyramid.is_skill_available("read") is True

    def test_blocked_reason_returns_explanation(self, pyramid):
        """blocked_reason() explains why a skill is locked."""
        reason = pyramid.blocked_reason("read")
        assert reason is not None
        assert "vocab" in reason

    def test_blocked_reason_none_when_available(self, pyramid):
        """blocked_reason() returns None when skill is available."""
        pyramid.update_skill("vocab", xp_gained=UNLOCK_XP_THRESHOLD)
        assert pyramid.blocked_reason("read") is None

    def test_update_skill_increments_xp(self, pyramid):
        """update_skill() increments XP correctly."""
        pyramid.update_skill("vocab", xp_gained=50)
        assert pyramid.skills["vocab"].xp == 50

    def test_update_skill_increments_session_count(self, pyramid):
        """update_skill() increments session count."""
        pyramid.update_skill("vocab", xp_gained=10)
        pyramid.update_skill("vocab", xp_gained=20)
        assert pyramid.skills["vocab"].session_count == 2

    def test_update_skill_respects_level_param(self, pyramid):
        """update_skill() updates level when provided."""
        pyramid.update_skill("vocab", xp_gained=100, level="A2")
        assert pyramid.skills["vocab"].level == "A2"

    def test_propograte_unlocks(self, pyramid):
        """_propagate_unlocks() unlocks dependent skills."""
        pyramid.update_skill("vocab", xp_gained=UNLOCK_XP_THRESHOLD)
        pyramid.update_skill("read", xp_gained=UNLOCK_XP_THRESHOLD)
        # listen should now be available
        assert pyramid.is_skill_available("listen") is True

    def test_get_next_skill_returns_locked_skill(self, pyramid):
        """get_next_skill() returns first locked skill."""
        next_skill = pyramid.get_next_skill()
        assert next_skill == "vocab"

    def test_get_pyramid_status(self, pyramid):
        """get_pyramid_status() returns all skills."""
        status = pyramid.get_pyramid_status()
        assert len(status) == 5
        skill_names = [s["name"] for s in status]
        assert "vocab" in skill_names
        assert "speak" in skill_names


class TestSpacedRepetition:
    """Test SM-2 spaced repetition algorithm."""

    def test_sm2_card_initialization(self):
        """SM2Card initializes with correct defaults."""
        card = SM2Card(word_id=1)
        assert card.interval == 0
        assert card.ease_factor == 2.5
        assert card.repetitions == 0

    def test_sm2_review_failed_recall(self):
        """Quality < 3 resets repetitions and interval to 1."""
        card = SM2Card(word_id=1)
        card.review(2)  # Failed recall
        assert card.repetitions == 0
        assert card.interval == 1

    def test_sm2_review_first_successful(self):
        """First successful review sets interval to 1."""
        card = SM2Card(word_id=1)
        card.review(4)
        assert card.interval == 1
        assert card.repetitions == 1

    def test_sm2_review_second_successful(self):
        """Second successful review sets interval to 6."""
        card = SM2Card(word_id=1)
        card.review(4)
        card.review(4)
        assert card.interval == 6
        assert card.repetitions == 2

    def test_sm2_review_maintains_interval_growth(self):
        """Successful reviews increase interval multiplicatively."""
        card = SM2Card(word_id=1)
        card.review(4)  # rep=1, interval=1
        card.review(4)  # rep=2, interval=6
        old_interval = card.interval
        card.review(4)  # rep=3, interval=6 * 2.5
        assert card.interval == int(old_interval * card.ease_factor)

    def test_sm2_ease_factor_minimum(self):
        """Ease factor never goes below 1.3."""
        card = SM2Card(word_id=1)
        card.review(0)  # Worst possible
        assert card.ease_factor >= 1.3

    def test_sm2_invalid_quality_raises(self):
        """Quality outside 0-5 raises ValueError."""
        card = SM2Card(word_id=1)
        with pytest.raises(ValueError):
            card.review(6)
        with pytest.raises(ValueError):
            card.review(-1)

    def test_calculate_interval_quality_below_3(self):
        """calculate_interval returns interval=1 for quality < 3."""
        interval, ease, reps = calculate_interval(2.5, 5, 30, 2)
        assert interval == 1
        assert reps == 0

    def test_calculate_interval_first_success(self):
        """calculate_interval for first success."""
        interval, ease, reps = calculate_interval(2.5, 0, 0, 4)
        assert interval == 1
        assert reps == 1

    def test_calculate_interval_second_success(self):
        """calculate_interval for second success."""
        interval, ease, reps = calculate_interval(2.5, 1, 1, 4)
        assert interval == 6
        assert reps == 2

    def test_quality_description_complete_blackout(self):
        """quality_description returns correct text."""
        assert "blackout" in quality_description(0).lower()

    def test_quality_description_perfect_recall(self):
        """quality_description returns correct text for 5."""
        assert "perfect" in quality_description(5).lower()


class TestConfig:
    """Test configuration loading and merging."""

    def test_defaults_exist(self):
        """DEFAULT_CONFIG has all required keys."""
        assert "db_path" in DEFAULTS
        assert "logs_dir" in DEFAULTS
        assert "level" in DEFAULTS

    def test_load_yaml_missing_file_returns_empty_dict(self):
        """load_yaml returns empty dict for missing files."""
        result = load_yaml(Path("/nonexistent/path.yml"))
        assert result == {}

    def test_load_yaml_parses_existing_file(self):
        """load_yaml correctly parses YAML files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("level: B2\nobjectives:\n  - fluency\n")
            f.flush()
            result = load_yaml(Path(f.name))
            assert result["level"] == "B2"
            assert "fluency" in result["objectives"]

    def test_deep_merge_override(self):
        """deep_merge correctly overrides base values."""
        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"d": 3}, "e": 4}
        result = deep_merge(base, override)
        assert result["a"] == 1
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 3
        assert result["e"] == 4

    def test_deep_merge_no_mutation(self):
        """deep_merge doesn't mutate original dicts."""
        base = {"a": 1}
        override = {"b": 2}
        deep_merge(base, override)
        assert "b" not in base

    def test_config_initializes_with_defaults(self, sample_config):
        """Config initializes with default values."""
        assert sample_config.db_path is not None
        assert sample_config.logs_dir is not None

    def test_config_update(self, sample_config):
        """Config.update() changes values."""
        sample_config.update("level", "C1")
        assert sample_config.level == "C1"

    def test_config_save_profile(self, sample_config):
        """Config.save_profile() writes to file."""
        sample_config.save_profile()
        assert sample_config.profile_file.exists()
