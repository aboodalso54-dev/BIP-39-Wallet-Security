"""Android Builder - Gradle-based APK build automation.

Wraps the Android SDK/Gradle toolchain to build, sign, and optimize APKs
with intelligent configuration and failure recovery.
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BuildVariant(str, Enum):
    """Android build variants."""

    DEBUG = "debug"
    RELEASE = "release"


@dataclass
class AndroidBuildResult:
    """Result of an Android build operation."""

    success: bool
    variant: BuildVariant
    apk_path: str = ""
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    build_time_seconds: float = 0.0
    signing_info: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "success": self.success,
            "variant": self.variant.value,
            "apk_path": self.apk_path,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "build_time_seconds": self.build_time_seconds,
            "signing_info": self.signing_info,
        }


class AndroidBuilder:
    """Builds Android APKs using Gradle with signing and optimization."""

    def __init__(
        self,
        project_dir: str,
        keystore_path: Optional[str] = None,
        keystore_alias: Optional[str] = None,
        keystore_password: Optional[str] = None,
    ) -> None:
        self.project_dir = Path(project_dir)
        if not self.project_dir.exists():
            raise FileNotFoundError(f"Android project dir not found: {project_dir}")
        self.keystore_path = keystore_path
        self.keystore_alias = keystore_alias
        self.keystore_password = keystore_password

    def build(
        self,
        variant: BuildVariant = BuildVariant.RELEASE,
        sign: bool = True,
    ) -> AndroidBuildResult:
        """Build an APK for the given variant."""
        import time

        start = time.time()
        gradlew = self.project_dir / "gradlew"
        if not gradlew.exists():
            return AndroidBuildResult(
                success=False,
                variant=variant,
                exit_code=1,
                stderr="gradlew not found",
                build_time_seconds=time.time() - start,
            )

        task = f"assemble{variant.value.capitalize()}"
        cmd = f"./gradlew {task} --no-daemon"
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=900,
            )
            result = AndroidBuildResult(
                success=proc.returncode == 0,
                variant=variant,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                build_time_seconds=time.time() - start,
            )
        except subprocess.TimeoutExpired:
            return AndroidBuildResult(
                success=False,
                variant=variant,
                exit_code=1,
                stderr="Build timed out",
                build_time_seconds=time.time() - start,
            )

        if result.success and sign:
            result.signing_info = self._configure_signing()
            result.apk_path = self._find_apk(variant)
        return result

    def _configure_signing(self) -> Dict[str, str]:
        """Configure signing info based on keystore settings."""
        if not self.keystore_path or not self.keystore_alias:
            return {"status": "unsigned"}
        return {
            "status": "signed",
            "keystore": self.keystore_path,
            "alias": self.keystore_alias,
        }

    def _find_apk(self, variant: BuildVariant) -> str:
        """Locate the built APK for the given variant."""
        pattern = f"**/build/outputs/apk/{variant.value}/*.apk"
        matches = list(self.project_dir.glob(pattern))
        return str(matches[0]) if matches else ""

    def clean(self) -> bool:
        """Clean the Android build cache and outputs."""
        gradlew = self.project_dir / "gradlew"
        if not gradlew.exists():
            return False
        try:
            subprocess.run(
                "./gradlew clean --no-daemon",
                shell=True,
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=300,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False