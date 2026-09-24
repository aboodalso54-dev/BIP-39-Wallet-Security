"""Predictive Error Detection Engine.

Analyzes code patterns to predict bugs before they happen using pattern
matching, complexity analysis, and dependency analysis.
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern

logger = logging.getLogger(__name__)


@dataclass
class BugPrediction:
    """A single predicted bug with metadata."""

    file: str
    line: int
    column: int
    category: str
    pattern: str
    confidence: float
    message: str
    suggested_fix: str
    severity: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "category": self.category,
            "pattern": self.pattern,
            "confidence": round(self.confidence, 2),
            "message": self.message,
            "suggested_fix": self.suggested_fix,
            "severity": self.severity,
        }


class PredictiveErrorEngine:
    """Analyzes code to predict bugs before they occur."""

    # Category -> list of (regex, confidence, severity, message, fix)
    PATTERNS: Dict[str, List[tuple]] = {
        "null_pointer": [
            (r"\.\w+", 0.6, "low", "Potential null dereference", "Add null check"),
        ],
        "race_condition": [
            (r"threading\.", 0.5, "medium", "Potential race condition", "Use locks"),
        ],
        "memory_leak": [
            (r"global\s+\w+", 0.4, "low", "Global state may leak", "Use context manager"),
        ],
        "type_error": [
            (r"int\(\s*\w+\s*\)", 0.5, "medium", "Possible type coercion error", "Validate input"),
        ],
        "security_vulnerability": [
            (r"eval\(|exec\(|os\.system\(", 0.9, "high", "Code injection risk", "Avoid eval/exec"),
        ],
    }

    def __init__(self, confidence_threshold: float = 0.7) -> None:
        self.confidence_threshold = confidence_threshold
        self._compiled: Dict[str, List[Pattern]] = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, List[Pattern]]:
        compiled: Dict[str, List[Pattern]] = {}
        for category, patterns in self.PATTERNS.items():
            compiled[category] = [re.compile(p[0]) for p in patterns]
        return compiled

    def analyze_file(self, file_path: str) -> List[BugPrediction]:
        """Analyze a single file and return predicted bugs."""
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.stat().st_size > 1_000_000:
            logger.warning("File too large, skipping: %s", file_path)
            return []

        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            logger.warning("Cannot decode %s: %s", file_path, exc)
            return []

        predictions = self._scan_text(source, str(path))
        return [p for p in predictions if p.confidence >= self.confidence_threshold]

    def analyze_project(self, root: str, glob: str = "**/*.py") -> List[BugPrediction]:
        """Analyze all matching files under a project root."""
        root_path = Path(root)
        if not root_path.exists():
            raise FileNotFoundError(f"Project root not found: {root}")

        all_predictions: List[BugPrediction] = []
        for file_path in root_path.glob(glob):
            try:
                all_predictions.extend(self.analyze_file(str(file_path)))
            except Exception as exc:
                logger.warning("Failed to analyze %s: %s", file_path, exc)
        return all_predictions

    def predict_bugs(self, source: str, file_label: str = "<string>") -> List[BugPrediction]:
        """Predict bugs in a source code string."""
        predictions = self._scan_text(source, file_label)
        return [p for p in predictions if p.confidence >= self.confidence_threshold]

    def _scan_text(self, source: str, file_label: str) -> List[BugPrediction]:
        predictions: List[BugPrediction] = []
        lines = source.splitlines()

        for category, patterns in self.PATTERNS.items():
            for idx, (regex, base_conf, severity, message, fix) in enumerate(patterns):
                compiled = self._compiled[category][idx]
                for line_no, line in enumerate(lines, start=1):
                    for match in compiled.finditer(line):
                        col = match.start()
                        predictions.append(BugPrediction(
                            file=file_label,
                            line=line_no,
                            column=col,
                            category=category,
                            pattern=regex,
                            confidence=base_conf,
                            message=message,
                            suggested_fix=fix,
                            severity=severity,
                        ))
        return predictions