"""
Platform Registry Module

Loads and provides access to platform definitions from configs/platforms.yaml.
Handles missing files gracefully and provides convenient lookup methods.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any


class PlatformRegistry:
    """
    Registry for learning platform definitions.
    
    Loads platform definitions from a YAML file and provides methods
    to query platform information, metrics, and CEFR mappings.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the platform registry.
        
        Args:
            config_path: Path to platforms.yaml. If None, uses default path:
                        configs/platforms.yaml relative to project root.
        """
        self._platforms: Dict[str, Any] = {}
        self._config_path = config_path
        
        if config_path is None:
            # Default path: configs/platforms.yaml
            project_root = Path(__file__).parent.parent.parent
            self._config_path = project_root / "configs" / "platforms.yaml"
        
        self._load_platforms()
    
    def _load_platforms(self) -> None:
        """Load platforms from YAML file. Handles missing files gracefully."""
        try:
            import yaml
            
            config_file = Path(self._config_path)
            if not config_file.exists():
                # Try absolute path or fall back to empty
                return
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._platforms = yaml.safe_load(f) or {}
                
        except (yaml.YAMLError, ImportError, OSError):
            # Handle missing PyYAML, file errors, or parse errors gracefully
            self._platforms = {}
    
    def get_platform(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a platform definition by name.
        
        Args:
            name: Platform name (e.g., 'youtalk', 'duolingo')
            
        Returns:
            Platform definition dict or None if not found
        """
        return self._platforms.get(name.lower())
    
    def get_metrics(self, platform_name: str) -> List[Dict[str, Any]]:
        """
        Get metric definitions for a platform.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            List of metric definitions, each containing:
            - name: metric identifier
            - type: 'number', 'select', 'date', etc.
            - options: list of valid options (for select type)
            - questions: list of questions to ask
        """
        platform = self.get_platform(platform_name)
        if platform is None:
            return []
        
        metrics = platform.get('metrics', {})
        # Convert metrics dict to list of dicts with 'name' key
        return [
            {'name': name, **{k: v for k, v in config.items()}}
            for name, config in metrics.items()
        ]
    
    def get_onboarding_questions(self, platform_name: str) -> List[Dict[str, Any]]:
        """
        Get onboarding questions for a platform.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            List of question dicts with:
            - metric_name: which metric this question is for
            - question: the question text
            - type: metric type
            - options: valid options (for select type)
            - min/max: bounds (for number type)
        """
        platform = self.get_platform(platform_name)
        if platform is None:
            return []
        
        questions = []
        metrics = platform.get('metrics', {})
        
        for metric_name, config in metrics.items():
            for question_text in config.get('questions', []):
                questions.append({
                    'metric_name': metric_name,
                    'question': question_text,
                    'type': config.get('type'),
                    'options': config.get('options'),
                    'min': config.get('min'),
                    'max': config.get('max'),
                })
        
        return questions
    
    def get_cefr_mapping(self, platform_name: str, level: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get CEFR mapping for a platform level.
        
        Args:
            platform_name: Name of the platform
            level: Specific level to map (e.g., 'Intermediate'). 
                   If None, returns all mappings.
                   
        Returns:
            Dict with 'cefr' and 'confidence' keys, or None if not found.
            If level is None, returns dict of all level mappings.
        """
        platform = self.get_platform(platform_name)
        if platform is None:
            return None
        
        level_to_cefr = platform.get('level_to_cefr', {})
        
        if level is None:
            return level_to_cefr
        
        mapping = level_to_cefr.get(level)
        if mapping is None:
            return None
        
        return mapping
    
    def list_platforms(self) -> List[str]:
        """
        Get list of all available platform names.
        
        Returns:
            List of platform name strings (lowercase keys)
        """
        return list(self._platforms.keys())
    
    def get_display_name(self, platform_name: str) -> Optional[str]:
        """
        Get the display name for a platform.
        
        Args:
            platform_name: Platform name (e.g., 'youtalk')
            
        Returns:
            Human-readable display name or None if platform not found
        """
        platform = self.get_platform(platform_name)
        if platform is None:
            return None
        return platform.get('display_name')
    
    def reload(self) -> None:
        """Reload platforms from file."""
        self._load_platforms()
    
    def get_curriculum(self, platform_name: str) -> Optional[Dict[str, Any]]:
        """
        Get curriculum definition for a platform.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            Curriculum dict with naming_convention, videos_per_unit, unit_types, levels,
            or None if platform not found or has no curriculum.
        """
        platform = self.get_platform(platform_name)
        if platform is None:
            return None
        return platform.get('curriculum')
    
    def get_unit_topics(self, platform_name: str, level: str, unit_number: int) -> List[str]:
        """
        Get topics for a specific unit in a platform's curriculum.
        
        Args:
            platform_name: Name of the platform
            level: Level name (e.g., 'Basic', 'Intermediate')
            unit_number: Unit number
            
        Returns:
            List of topic strings for the unit, or empty list if not found.
        """
        curriculum = self.get_curriculum(platform_name)
        if curriculum is None:
            return []
        
        levels = curriculum.get('levels', {})
        level_data = levels.get(level)
        if level_data is None:
            return []
        
        topics = level_data.get('topics', {})
        unit_key = str(unit_number)
        return topics.get(unit_key, [])
