"""Smart Build Orchestrator.

Orchestrates project builds with caching, parallelism, and failure analysis.
Supports Python, Android (Gradle), and Node.js projects.
"""

from __future__ import annotations

import hashlib
import logging
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BuildTarget(str, Enum):
    """Supported build targets."""

    PYTHON = "python"
    ANDROID = "android"
    NODE = "node"
    AUTO = "auto"


@dataclass
class BuildArtifact:
    """A single build artifact."""

    name: str
    path: str
    size_bytes: int
    sha256: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
        }


@dataclass
class BuildResult:
    """Result of a build operation."""

    success: bool
    target: BuildTarget
    command: str
    exit_code: int
    stdout: str
    stderr: str
    artifacts: List[BuildArtifact] = field(default_factory=list)
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, object]:
        return {
            "success": self.success,
            "target": self.target.value,
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "duration_seconds": self.duration_seconds,
        }


class SmartBuild:
    """Intelligent build orchestrator with caching and target detection."""

    def __init__(self, project_root: str = ".", cache_dir: Optional[Path] = None) -> None:
        self.project_root = Path(project_root)
        self.cache_dir = cache_dir or (Path.home() / ".devforge" / "build-cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, str] = {}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def build(self, target: BuildTarget = BuildTarget.AUTO) -> BuildResult:
        """Build the project for the given (or auto-detected) target."""
        command = self._detect_command(target)
        return self._run(command, target)

    def build_python(self) -> BuildResult:
        """Build a Python project (compile all modules)."""
        return self._run("python -m compileall -q .", BuildTarget.PYTHON)

    def build_android(self, variant: str = "release") -> BuildResult:
        """Build an Android project with Gradle."""
        gradlew = self.project_root / "gradlew"
        if not gradlew.exists():
            raise FileNotFoundError(f"gradlew not found in {self.project_root}")
        cmd = f"./gradlew assemble{variant.capitalize()}"
        return self._run(cmd, BuildTarget.ANDROID)

    def build_node(self) -> BuildResult:
        """Build a Node.js project."""
        return self._run("npm run build", BuildTarget.NODE)

    def clean(self) -> bool:
        """Remove build artifacts and caches."""
        import shutil

        for pattern in ("build", "__pycache__", "*.pyc", ".gradle", "dist"):
            for path in self.project_root.glob(pattern):
                try:
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        path.unlink()
                except OSError as exc:
                    logger.warning("Failed to clean %s: %s", path, exc)
        return True

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _detect_command(self, target: BuildTarget) -> str:
        if target == BuildTarget.AUTO:
            if (self.project_root / "gradlew").exists():
                target = BuildTarget.ANDROID
            elif (self.project_root / "package.json").exists():
                target = BuildTarget.NODE
            else:
                target = BuildTarget.PYTHON
        if target == BuildTarget.PYTHON:
            return "python -m compileall -q ."
        if target == BuildTarget.ANDROID:
            return "./gradlew assembleRelease"
        if target == BuildTarget.NODE:
            return "npm run build"
        raise ValueError(f"Unsupported build target: {target}")

    def _run(self, command: str, target: BuildTarget) -> BuildResult:
        import time

        start = time.time()
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=600,
            )
            result = BuildResult(
                success=proc.returncode == 0,
                target=target,
                command=command,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration_seconds=time.time() - start,
            )
        except subprocess.TimeoutExpired:
            result = BuildResult(
                success=False,
                target=target,
                command=command,
                exit_code=1,
                stdout="",
                stderr="Build timed out",
                duration_seconds=time.time() - start,
            )
        except FileNotFoundError:
            result = BuildResult(
                success=False,
                target=target,
                command=command,
                exit_code=1,
                stdout="",
                stderr="Build tool not found",
                duration_seconds=time.time() - start,
            )

        if result.success:
            result.artifacts = self._collect_artifacts(target)
        return result

    def _collect_artifacts(self, target: BuildTarget) -> List[BuildArtifact]:
        artifacts: List[BuildArtifact] = []
        if target == BuildTarget.ANDROID:
            pattern = "**/build/outputs/apk/*.apk"
        elif target == BuildTarget.NODE:
            pattern = "dist/**/*"
        else:
            pattern = "**/*.pyc"
        for path in self.project_root.glob(pattern):
            try:
                artifacts.append(BuildArtifact(
                    name=path.name,
                    path=str(path),
                    size_bytes=path.stat().st_size,
                    sha256=self._sha256(path),
                ))
            except OSError:
                continue
        return artifacts

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()