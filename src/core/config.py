"""Configuration loader for Piramid-Tongue.

Hierarchical config: defaults -> ~/.config/piramid-tongue/config.yaml -> env vars.
"""

import os
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_DIR = Path.home() / ".config" / "piramid-tongue"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
DEFAULT_PROFILE_FILE = DEFAULT_CONFIG_DIR / "profile.yml"

DEFAULTS: dict[str, Any] = {
    "db_path": str(Path.home() / ".piramid-tongue" / "piramid-tongue.db"),
    "logs_dir": str(Path.home() / "piramid-tongue" / "logs"),
    "level": None,
    "objectives": [],
    "streak": {"current": 0, "longest": 0, "last_active": None},
    "platforms": [],
    "content_cache_ttl_hours": 24,
    "rate_limit_delay_seconds": 2,
}


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file, returning empty dict if not found."""
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base (non-destructive)."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    """Hierarchical configuration for Piramid-Tongue."""

    def __init__(self, config_dir: Path | None = None):
        self.config_dir = config_dir or DEFAULT_CONFIG_DIR
        self.config_file = self.config_dir / "config.yaml"
        self.profile_file = self.config_dir / "profile.yml"

        # Load layers
        config = load_yaml(self.config_file)
        profile = load_yaml(self.profile_file)

        # Merge: defaults <- config.yaml <- profile.yml
        self._data = deep_merge(DEFAULTS, config)
        self._data = deep_merge(self._data, profile)

        # Env vars override
        if os.getenv("PIRAMID_TONGUE_DB"):
            self._data["db_path"] = os.environ["PIRAMID_TONGUE_DB"]
        if os.getenv("PIRAMID_TONGUE_LOGS"):
            self._data["logs_dir"] = os.environ["PIRAMID_TONGUE_LOGS"]

    @property
    def db_path(self) -> str:
        return str(self._data["db_path"])

    @property
    def logs_dir(self) -> str:
        return str(self._data["logs_dir"])

    @property
    def level(self) -> str | None:
        return self._data.get("level")

    @property
    def objectives(self) -> list[str]:
        return self._data.get("objectives", [])

    @property
    def streak(self) -> dict:
        return self._data.get("streak", {})

    @property
    def platforms(self) -> list[dict]:
        return self._data.get("platforms", [])

    @property
    def content_cache_ttl_hours(self) -> int:
        return int(self._data.get("content_cache_ttl_hours", 24))

    @property
    def rate_limit_delay_seconds(self) -> int:
        return int(self._data.get("rate_limit_delay_seconds", 2))

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def save_profile(self) -> None:
        """Save current profile to profile.yml."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.profile_file, "w") as f:
            yaml.dump(self._data, f, default_flow_style=False, sort_keys=False)

    def update(self, key: str, value: Any) -> None:
        """Update a config value in memory."""
        self._data[key] = value
