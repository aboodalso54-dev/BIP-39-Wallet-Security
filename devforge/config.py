"""Centralized configuration for DevForge.

Manages all DevForge settings with support for environment variables,
defaults, and runtime overrides.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class DevForgeConfig:
    """Centralized configuration for all DevForge components.

    Supports loading from environment variables (prefixed with DEVFORGE_),
    sensible defaults, and runtime overrides via attribute assignment.
    """

    # --- General ---
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    project_root: Path = field(default_factory=lambda: Path.cwd())
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".devforge" / "cache")
    temp_dir: Path = field(default_factory=lambda: Path.home() / ".devforge" / "tmp")

    # --- Predictive Engine ---
    predictive_enabled: bool = True
    predictive_confidence_threshold: float = 0.7
    predictive_max_file_size: int = 1_000_000  # bytes
    predictive_patterns_dir: Optional[Path] = None

    # --- Code Translator ---
    translator_default_target: str = "python"
    translator_preserve_comments: bool = True
    translator_preserve_docstrings: bool = True
    translator_max_file_size: int = 500_000  # bytes

    # --- Self-Healing Pipeline ---
    selfheal_enabled: bool = True
    selfheal_max_retries: int = 3
    selfheal_retry_delay: float = 2.0
    selfheal_auto_rollback: bool = True
    selfheal_network_fallbacks: list = field(default_factory=list)

    # --- AI Generator ---
    ai_generator_model: str = "gpt-4o"
    ai_generator_temperature: float = 0.2
    ai_generator_max_tokens: int = 4096
    ai_generator_api_key: Optional[str] = None
    ai_generator_api_base: Optional[str] = None

    # --- Dependency Resolver ---
    resolver_cache_ttl: int = 3600  # seconds
    resolver_strict_mode: bool = False
    resolver_allow_prereleases: bool = False
    resolver_index_url: str = "https://pypi.org/simple"

    # --- Internal state ---
    _overrides: Dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    # ------------------------------------------------------------------ #
    # Construction & loading
    # ------------------------------------------------------------------ #
    @classmethod
    def from_env(cls, env_prefix: str = "DEVFORGE_") -> "DevForgeConfig":
        """Build a config instance, overriding defaults with environment variables."""
        cfg = cls()
        for key in os.environ:
            if not key.startswith(env_prefix):
                continue
            attr = key[len(env_prefix):].lower()
            if not hasattr(cfg, attr):
                continue
            raw = os.environ[key]
            current = getattr(cfg, attr)
            try:
                setattr(cfg, attr, cls._coerce(raw, current))
            except (ValueError, TypeError) as exc:
                logger.warning("Failed to apply env var %s: %s", key, exc)
        return cfg

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "DevForgeConfig":
        """Load config from a JSON file if provided, otherwise from environment."""
        cfg = cls.from_env()
        if path is not None and Path(path).exists():
            import json

            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                for k, v in data.items():
                    if hasattr(cfg, k):
                        setattr(cfg, k, v)
            except (OSError, ValueError) as exc:
                logger.warning("Failed to load config from %s: %s", path, exc)
        return cfg

    # ------------------------------------------------------------------ #
    # Overrides
    # ------------------------------------------------------------------ #
    def override(self, key: str, value: Any) -> None:
        """Apply a runtime override."""
        if not hasattr(self, key):
            raise AttributeError(f"Unknown config key: {key}")
        setattr(self, key, value)
        self._overrides[key] = value

    def reset_overrides(self) -> None:
        """Clear all runtime overrides."""
        for key, value in self._overrides.items():
            setattr(self, key, value)
        self._overrides.clear()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _coerce(value: str, target: Any) -> Any:
        """Coerce a string env value to the type of *target*."""
        if isinstance(target, bool):
            return value.lower() in {"1", "true", "yes", "on"}
        if isinstance(target, int) and not isinstance(target, bool):
            return int(value)
        if isinstance(target, float):
            return float(value)
        if isinstance(target, Path):
            return Path(value)
        if isinstance(target, list):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #
    def validate(self) -> None:
        """Validate configuration values; raises ValueError on invalid settings."""
        if not (0.0 <= self.predictive_confidence_threshold <= 1.0):
            raise ValueError("predictive_confidence_threshold must be between 0 and 1")
        if self.selfheal_max_retries < 0:
            raise ValueError("selfheal_max_retries must be >= 0")
        if self.selfheal_retry_delay < 0:
            raise ValueError("selfheal_retry_delay must be >= 0")
        if self.ai_generator_max_tokens <= 0:
            raise ValueError("ai_generator_max_tokens must be positive")
        if self.predictive_max_file_size <= 0:
            raise ValueError("predictive_max_file_size must be positive")

    # ------------------------------------------------------------------ #
    # Directory helpers
    # ------------------------------------------------------------------ #
    def ensure_dirs(self) -> None:
        """Create configured directories if they do not exist."""
        for attr in ("cache_dir", "temp_dir"):
            path = getattr(self, attr)
            path.mkdir(parents=True, exist_ok=True)