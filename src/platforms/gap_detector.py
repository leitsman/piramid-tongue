"""Gap detection module for platform-pyramid alignment.

Compares platform-reported CEFR levels with pyramid skill levels
to identify gaps where a student may be consuming content but
not applying skills in practice.
"""

from typing import Optional

# CEFR level ordering for comparison
CEFR_ORDER = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5}
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


class GapDetector:
    """Detects gaps between platform progress and pyramid skill levels.
    
    Compares the CEFR level implied by platform metrics against
    the actual pyramid skill levels to identify:
    - HIGH gap: Platform CEFR > Skill CEFR by 2+ levels
    - MEDIUM gap: Platform CEFR > Skill CEFR by 1 level
    - OK: Platform CEFR == Skill CEFR
    - AHEAD: Platform CEFR < Skill CEFR (positive - student is ahead)
    """
    
    def __init__(self, profile_data: dict, pyramid_skills: dict):
        """
        Initialize gap detector.
        
        Args:
            profile_data: Dict from profile.yml containing:
                - platforms: list of platform configs with level info
                - level: user's self-assessed CEFR level
            pyramid_skills: Dict from DB with structure:
                {
                    "skill_name": {
                        "level": "B1",  # CEFR level
                        "xp": 100,
                        "session_count": 5,
                    },
                    ...
                }
        """
        self.profile_data = profile_data
        self.pyramid_skills = pyramid_skills
        self.platforms = profile_data.get("platforms", [])
    
    def _cefr_to_num(self, cefr: str) -> int:
        """Convert CEFR string to numeric value for comparison."""
        return CEFR_ORDER.get(cefr.upper().strip(), 0)
    
    def _num_to_cefr(self, num: int) -> str:
        """Convert numeric value to nearest CEFR level."""
        if num < 0:
            return "A1"
        if num > 5:
            return "C2"
        return CEFR_LEVELS[num]
    
    def _get_platform_cefr(self, platform: dict) -> Optional[str]:
        """Extract CEFR estimate from platform data.
        
        Priority:
        1. user_override_cefr (if set)
        2. platform_level_to_cefr mapping
        3. None (can't determine)
        """
        # User override takes precedence
        override = platform.get("user_override_cefr")
        if override:
            return override
        
        # Check platform's own CEFR mapping from their level
        platform_level = platform.get("metrics", {}).get("current_level")
        if platform_level:
            # The level_to_cefr is stored in the platform registry
            # but the profile stores a direct mapping
            platform_cefr = platform.get("platform_level_to_cefr")
            if platform_cefr:
                return platform_cefr
        
        # Try to infer from platform's internal mapping
        # (This would require access to PlatformRegistry, handled at detection time)
        return None
    
    def detect_gaps(self) -> list[dict]:
        """Detect gaps between platform CEFR and pyramid skill levels.
        
        Returns:
            List of gap dicts with structure:
            {
                "platform": str,
                "platform_cefr": str,
                "skill": str,
                "skill_cefr": str,
                "gap_size": int,  # positive = platform ahead
                "severity": "high" | "medium" | "ok" | "ahead",
            }
        """
        gaps = []
        
        for platform in self.platforms:
            platform_name = platform.get("name", "unknown")
            platform_cefr_str = self._get_platform_cefr(platform)
            
            if not platform_cefr_str:
                continue  # Can't determine platform CEFR
            
            platform_cefr = self._cefr_to_num(platform_cefr_str)
            
            # Compare with each pyramid skill
            for skill_name, skill_data in self.pyramid_skills.items():
                skill_cefr_str = skill_data.get("level", "A1")
                skill_cefr = self._cefr_to_num(skill_cefr_str)
                
                gap_size = platform_cefr - skill_cefr
                
                # Determine severity
                if gap_size >= 2:
                    severity = "high"
                elif gap_size == 1:
                    severity = "medium"
                elif gap_size == 0:
                    severity = "ok"
                else:
                    severity = "ahead"  # Student is ahead (positive)
                
                gaps.append({
                    "platform": platform_name,
                    "platform_cefr": platform_cefr_str,
                    "skill": skill_name,
                    "skill_cefr": skill_cefr_str,
                    "gap_size": gap_size,
                    "severity": severity,
                })
        
        return gaps
    
    def get_recommendations(self, gaps: list[dict]) -> list[str]:
        """Convert detected gaps to actionable recommendations.
        
        Args:
            gaps: List from detect_gaps()
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Group by severity
        high_gaps = [g for g in gaps if g["severity"] == "high"]
        medium_gaps = [g for g in gaps if g["severity"] == "medium"]
        
        if high_gaps:
            # Find the most significant gap (largest gap_size)
            worst = max(high_gaps, key=lambda g: g["gap_size"])
            recommendations.append(
                f"Your {worst['platform']} progress suggests {worst['platform_cefr']} level, "
                f"but your {worst['skill']} skill is at {worst['skill_cefr']}. "
                f"You're consuming {worst['platform_cefr']} content but not applying it in practice. "
                f"Focus on {worst['skill']} exercises to bridge this gap."
            )
        
        if medium_gaps:
            for gap in medium_gaps[:2]:  # Limit to 2
                recommendations.append(
                    f"Your {gap['skill']} ({gap['skill_cefr']}) could be improved to match "
                    f"your {gap['platform']} level ({gap['platform_cefr']}). "
                    f"Consider more {gap['skill']} practice."
                )
        
        # Check if student is ahead
        ahead_gaps = [g for g in gaps if g["severity"] == "ahead"]
        if ahead_gaps and not high_gaps and not medium_gaps:
            # Student is generally ahead - rare but positive
            recommendations.append(
                "Your pyramid skills are ahead of your platform progress. "
                "You're doing well! Consider challenging yourself with harder platform content."
            )
        
        return recommendations
    
    def get_progress_comparison(self) -> dict:
        """Get side-by-side comparison of platform levels vs pyramid levels.
        
        Returns:
            Dict with:
            {
                "platform_estimate": "B1" or None,
                "pyramid_average": "A2" or None,
                "strongest_skill": "Vocab (B1)" or None,
                "weakest_skill": "Speak (A1)" or None,
                "gap_severity": "none" | "low" | "medium" | "high",
            }
        """
        # Get platform estimate (average of platform CEFRs)
        platform_cefrs = []
        for platform in self.platforms:
            cefr = self._get_platform_cefr(platform)
            if cefr:
                platform_cefrs.append(self._cefr_to_num(cefr))
        
        platform_estimate = None
        if platform_cefrs:
            avg_num = sum(platform_cefrs) / len(platform_cefrs)
            platform_estimate = self._num_to_cefr(round(avg_num))
        
        # Calculate pyramid average
        pyramid_cefrs = []
        for skill_name, skill_data in self.pyramid_skills.items():
            level = skill_data.get("level", "A1")
            pyramid_cefrs.append((skill_name, self._cefr_to_num(level)))
        
        pyramid_average = None
        if pyramid_cefrs:
            avg_num = sum(c[1] for c in pyramid_cefrs) / len(pyramid_cefrs)
            pyramid_average = self._num_to_cefr(round(avg_num))
        
        # Find strongest and weakest skills
        strongest = None
        weakest = None
        if pyramid_cefrs:
            strongest_name, strongest_num = max(pyramid_cefrs, key=lambda x: x[1])
            weakest_name, weakest_num = min(pyramid_cefrs, key=lambda x: x[1])
            strongest = f"{strongest_name.capitalize()} ({self._num_to_cefr(strongest_num)})"
            weakest = f"{weakest_name.capitalize()} ({self._num_to_cefr(weakest_num)})"
        
        # Calculate overall gap severity
        gaps = self.detect_gaps()
        severities = [g["severity"] for g in gaps]
        
        gap_severity = "none"
        if "high" in severities:
            gap_severity = "high"
        elif "medium" in severities:
            gap_severity = "medium"
        elif gaps and all(s == "ahead" or s == "ok" for s in severities):
            gap_severity = "low"
        
        return {
            "platform_estimate": platform_estimate,
            "pyramid_average": pyramid_average,
            "strongest_skill": strongest,
            "weakest_skill": weakest,
            "gap_severity": gap_severity,
        }
