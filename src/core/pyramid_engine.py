"""Pyramid engine: enforces skill dependency flow (vocab -> read -> listen -> write -> speak).

The pyramid methodology requires building vocabulary first, then reading,
then listening, then writing, and finally speaking. Skills can only be
practiced if their dependencies are met.
"""

from dataclasses import dataclass, field
from typing import Literal

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
