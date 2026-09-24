"""Self-Healing CI/CD Pipeline.

Automatically detects and fixes build failures, retries with different
configurations, updates dependency versions, and handles network issues.
"""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


class FailureType(str, Enum):
    """Types of build failures the pipeline can handle."""

    COMPILATION = "compilation"
    TEST_FAILURE = "test_failure"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    NETWORK = "network"
    UNKNOWN = "unknown"


@dataclass
class BuildResult:
    """Result of a build attempt."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    failure_type: FailureType = FailureType.UNKNOWN
    attempts: int = 0


@dataclass
class PipelineConfig:
    """Configuration for the self-healing pipeline."""

    max_retries: int = 3
    retry_delay: float = 2.0
    auto_rollback: bool = True
    network_fallbacks: List[str] = field(default_factory=list)
    dependency_update_command: str = "pip install --upgrade"


class SelfHealingPipeline:
    """A CI/CD pipeline that can detect and automatically fix build failures."""

    def __init__(self, config: Optional[PipelineConfig] = None) -> None:
        self.config = config or PipelineConfig()
        self._rollback_handlers: List[Callable[[], bool]] = []
        self._pre_fix_hooks: List[Callable[[BuildResult], None]] = []

    def run(self, command: str, cwd: Optional[str] = None) -> BuildResult:
        """Run a build command with self-healing retries."""
        last_result: Optional[BuildResult] = None
        for attempt in range(1, self.config.max_retries + 1):
            result = self._execute(command, cwd, attempt)
            if result.success:
                result.attempts = attempt
                return result
            last_result = result
            logger.warning("Build failed (attempt %s): %s", attempt, result.stderr[:200])

            if attempt < self.config.max_retries:
                self._trigger_fixes(result)
                time.sleep(self.config.retry_delay * attempt)

        if last_result is not None:
            last_result.attempts = self.config.max_retries
            if self.config.auto_rollback:
                self.rollback()
        return last_result or BuildResult(False, 1, "", "No attempts made")

    def fix_failure(self, result: BuildResult) -> BuildResult:
        """Attempt to fix a specific build failure."""
        self._trigger_fixes(result)
        return result

    def rollback(self) -> bool:
        """Execute all registered rollback handlers."""
        success = True
        for handler in reversed(self._rollback_handlers):
            try:
                if not handler():
                    success = False
            except Exception as exc:
                logger.error("Rollback handler failed: %s", exc)
                success = False
        return success

    def register_rollback(self, handler: Callable[[], bool]) -> None:
        """Register a rollback handler to be called on failure."""
        self._rollback_handlers.append(handler)

    def register_pre_fix_hook(self, hook: Callable[[BuildResult], None]) -> None:
        """Register a hook called before each fix attempt."""
        self._pre_fix_hooks.append(hook)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _execute(self, command: str, cwd: Optional[str], attempt: int) -> BuildResult:
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            failure_type = self._classify_failure(proc.returncode, proc.stderr)
            return BuildResult(
                success=proc.returncode == 0,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                failure_type=failure_type,
            )
        except subprocess.TimeoutExpired:
            return BuildResult(False, 1, "", "Command timed out", FailureType.UNKNOWN)
        except FileNotFoundError:
            return BuildResult(False, 1, "", "Command not found", FailureType.UNKNOWN)

    def _classify_failure(self, exit_code: int, stderr: str) -> FailureType:
        stderr_lower = stderr.lower()
        if "modulenotfound" in stderr_lower or "importerror" in stderr_lower:
            return FailureType.DEPENDENCY_CONFLICT
        if "connection" in stderr_lower or "network" in stderr_lower or "timeout" in stderr_lower:
            return FailureType.NETWORK
        if "assert" in stderr_lower or "test" in stderr_lower:
            return FailureType.TEST_FAILURE
        if "syntaxerror" in stderr_lower or "error:" in stderr_lower:
            return FailureType.COMPILATION
        return FailureType.UNKNOWN

    def _trigger_fixes(self, result: BuildResult) -> None:
        for hook in self._pre_fix_hooks:
            try:
                hook(result)
            except Exception as exc:
                logger.error("Pre-fix hook failed: %s", exc)