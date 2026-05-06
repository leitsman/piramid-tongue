"""Pyramid engine: enforces skill dependency flow (vocab -> read -> listen -> write -> speak).

The pyramid methodology requires building vocabulary first, then reading,
then listening, then writing, and finally speaking. Skills can only be
practiced if their dependencies are met.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional

SkillName = Literal["vocab", "read", "listen", "write", "speak"]

# Dependency graph: skill -> list of prerequisite skills
PYRAMID_DEPENDENCIES: dict[SkillName, list[SkillName]] = {
    "vocab": [],
    "read": ["vocab"],
    "listen": ["read"],
    "write": ["listen"],
    "speak": ["write"],
}

# XP thresholds to unlock next skill level
UNLOCK_XP_THRESHOLD = 100


@dataclass
class SkillState:
    """Current state of a single skill."""
    name: SkillName
    level: str = "A1"  # CEFR level
    xp: int = 0
    session_count: int = 0
    is_unlocked: bool = True  # vocab is always unlocked


@dataclass
class PyramidState:
    """Full state of the pyramid."""
    skills: dict[SkillName, SkillState] = field(default_factory=dict)

    def __post_init__(self):
        if not self.skills:
            self.skills = {
                "vocab": SkillState(name="vocab"),
                "read": SkillState(name="read"),
                "listen": SkillState(name="listen"),
                "write": SkillState(name="write"),
                "speak": SkillState(name="speak"),
            }

    def is_skill_available(self, skill: SkillName) -> bool:
        """Check if a skill can be practiced based on pyramid dependencies."""
        deps = PYRAMID_DEPENDENCIES.get(skill, [])
        for dep in deps:
            dep_state = self.skills.get(dep)
            if dep_state is None:
                return False
            if not dep_state.is_unlocked:
                return False
            # Must have at least UNLOCK_XP_THRESHOLD XP in prerequisite
            if dep_state.xp < UNLOCK_XP_THRESHOLD:
                return False
        return True

    def blocked_reason(self, skill: SkillName) -> str | None:
        """Return reason why a skill is blocked, or None if available."""
        if self.is_skill_available(skill):
            return None
        deps = PYRAMID_DEPENDENCIES.get(skill, [])
        blocked_deps = []
        for dep in deps:
            dep_state = self.skills.get(dep)
            if dep_state is None:
                blocked_deps.append(f"'{dep}' not initialized")
            elif not dep_state.is_unlocked:
                blocked_deps.append(f"'{dep}' is locked")
            elif dep_state.xp < UNLOCK_XP_THRESHOLD:
                blocked_deps.append(
                    f"'{dep}' needs {UNLOCK_XP_THRESHOLD - dep_state.xp} more XP "
                    f"(current: {dep_state.xp})"
                )
        if blocked_deps:
            return "Blocked by: " + "; ".join(blocked_deps)
        return None

    def update_skill(self, skill: SkillName, xp_gained: int = 0, level: str | None = None) -> None:
        """Update a skill's progress."""
        state = self.skills.get(skill)
        if state is None:
            raise ValueError(f"Unknown skill: {skill}")
        state.xp += xp_gained
        state.session_count += 1
        state.is_unlocked = True
        if level:
            state.level = level
        # Unlock dependent skills if threshold met
        self._propagate_unlocks()

    def _propagate_unlocks(self) -> None:
        """Unlock skills whose dependencies are met."""
        for skill in PYRAMID_DEPENDENCIES:
            deps = PYRAMID_DEPENDENCIES[skill]
            if not deps:
                continue  # vocab is always unlocked
            all_met = all(
                self.skills.get(dep, SkillState(name=dep)).xp >= UNLOCK_XP_THRESHOLD
                for dep in deps
            )
            if all_met:
                self.skills[skill].is_unlocked = True

    def get_next_skill(self) -> SkillName | None:
        """Get the next skill in the pyramid that should be practiced."""
        for skill in ["vocab", "read", "listen", "write", "speak"]:
            skill_name: SkillName = skill  # type: ignore
            state = self.skills[skill_name]
            if state.xp < UNLOCK_XP_THRESHOLD:
                return skill_name
            if not self.is_skill_available(skill_name):
                return skill_name
        return None

    def get_pyramid_status(self) -> list[dict]:
        """Return status of all skills for display."""
        result = []
        for skill in ["vocab", "read", "listen", "write", "speak"]:
            skill_name: SkillName = skill  # type: ignore
            state = self.skills[skill_name]
            result.append({
                "name": skill_name,
                "level": state.level,
                "xp": state.xp,
                "sessions": state.session_count,
                "unlocked": self.is_skill_available(skill_name),
                "blocked_reason": self.blocked_reason(skill_name),
            })
        return result

    def get_gap_report(self, profile_data: dict, pyramid_skills: dict) -> dict:
        """Generate gap report combining pyramid state with platform data.
        
        Args:
            profile_data: Dict from profile.yml with platform info
            pyramid_skills: Dict from DB with skill data
            
        Returns:
            Dict with gap analysis:
            {
                "gaps": list[dict],  # From GapDetector.detect_gaps()
                "recommendations": list[str],
                "comparison": dict,  # From GapDetector.get_progress_comparison()
                "affected_skills": list[str],  # Skills with gaps
            }
        """
        try:
            from src.platforms.gap_detector import GapDetector
            
            detector = GapDetector(profile_data, pyramid_skills)
            
            gaps = detector.detect_gaps()
            recommendations = detector.get_recommendations(gaps)
            comparison = detector.get_progress_comparison()
            
            # Extract skills that have gaps (severity high or medium)
            affected_skills = list(set(
                g["skill"] for g in gaps 
                if g["severity"] in ("high", "medium")
            ))
            
            return {
                "gaps": gaps,
                "recommendations": recommendations,
                "comparison": comparison,
                "affected_skills": affected_skills,
            }
        except ImportError:
            # GapDetector not available
            return {
                "gaps": [],
                "recommendations": [],
                "comparison": {},
                "affected_skills": [],
            }

    def get_recommendations_with_gaps(
        self, 
        profile_data: dict, 
        pyramid_skills: dict,
        vocab_due: int = 0,
        time_of_day: str = "morning",
        user_objectives: Optional[list[str]] = None,
    ) -> list[dict]:
        """Get skill recommendations factoring in detected gaps.
        
        Args:
            profile_data: Profile data with platforms
            pyramid_skills: Skill data from DB
            vocab_due: Number of vocab words due for review
            time_of_day: "morning", "afternoon", or "evening"
            user_objectives: List of objectives ["technical", "conversational"]
            
        Returns:
            List of recommendation dicts with structure:
            {
                "skill": str,
                "reason": str,
                "priority": int,  # Lower = higher priority
            }
        """
        user_objectives = user_objectives or []
        
        # Get gap report
        gap_report = self.get_gap_report(profile_data, pyramid_skills)
        affected_skills = set(gap_report["affected_skills"])
        
        # Base recommendations from pyramid state
        recommendations: list[dict] = []
        
        # 1. Skills with gaps get highest priority
        for skill in affected_skills:
            state = self.skills.get(skill)
            if state:
                recommendations.append({
                    "skill": skill,
                    "reason": f"Gap detected: your platform progress is ahead of your {skill} skill",
                    "priority": 1,
                })
        
        # 2. Vocab due for review
        if vocab_due > 0:
            recommendations.append({
                "skill": "vocab",
                "reason": f"You have {vocab_due} words due for review",
                "priority": 2,
            })
        
        # 3. Skills blocked by dependencies
        for skill in ["vocab", "read", "listen", "write", "speak"]:
            skill_name: SkillName = skill  # type: ignore
            blocked = self.blocked_reason(skill_name)
            if blocked and skill not in affected_skills:
                # Extract which dependency is blocking
                if "vocab" in blocked.lower():
                    recommendations.append({
                        "skill": "vocab",
                        "reason": f"Needed to unlock {skill}",
                        "priority": 3,
                    })
        
        # 4. Low XP skills
        for skill in ["vocab", "read", "listen", "write", "speak"]:
            skill_name: SkillName = skill  # type: ignore
            state = self.skills[skill_name]
            if state.xp < UNLOCK_XP_THRESHOLD and skill not in affected_skills:
                recommendations.append({
                    "skill": skill,
                    "reason": f"Low XP ({state.xp}), needs practice",
                    "priority": 4,
                })
        
        # 5. Skills not practiced recently
        # (Would need last_practiced data from DB)
        
        # 6. Time-of-day based recommendations
        if time_of_day == "morning":
            if "vocab" not in affected_skills:
                recommendations.append({
                    "skill": "vocab",
                    "reason": "Morning is ideal for vocabulary review",
                    "priority": 5,
                })
            if "listen" not in affected_skills:
                recommendations.append({
                    "skill": "listen",
                    "reason": "Start with listening to warm up",
                    "priority": 6,
                })
        elif time_of_day == "afternoon":
            if "read" not in affected_skills:
                recommendations.append({
                    "skill": "read",
                    "reason": "Afternoon is good for reading comprehension",
                    "priority": 5,
                })
            if "write" not in affected_skills:
                recommendations.append({
                    "skill": "write",
                    "reason": "Writing practice in the afternoon",
                    "priority": 6,
                })
        else:  # evening
            if "speak" not in affected_skills:
                recommendations.append({
                    "skill": "speak",
                    "reason": "Evening speaking practice",
                    "priority": 5,
                })
        
        # Sort by priority and deduplicate
        # Keep highest priority for each skill
        seen: dict[str, dict] = {}
        for rec in sorted(recommendations, key=lambda x: x["priority"]):
            skill = rec["skill"]
            if skill not in seen:
                seen[skill] = rec
        
        return list(seen.values())[:3]  # Return top 3
