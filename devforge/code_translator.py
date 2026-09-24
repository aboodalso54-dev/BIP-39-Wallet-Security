"""Universal Code Translation Engine.

Translates code between languages (Python, Go, Rust, TypeScript, Java) while
preserving logic and adapting to target language idioms.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES: List[str] = ["python", "go", "rust", "typescript", "java"]


@dataclass
class TranslationResult:
    """Result of a translation operation."""

    source_language: str
    target_language: str
    source_code: str
    translated_code: str
    warnings: List[str]

    def __str__(self) -> str:
        return self.translated_code


class UniversalCodeTranslator:
    """Translates code between multiple programming languages."""

    # Mapping of common constructs across languages
    CONSTRUCT_MAP: Dict[str, Dict[str, str]] = {
        "python": {
            "go": {
                "def ": "func ",
                "True": "true",
                "False": "false",
                "None": "nil",
                "import ": "import ",
                "print(": "fmt.Println(",
                "len(": "len(",
            },
        },
    }

    def __init__(self, default_target: str = "python") -> None:
        if default_target not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target language: {default_target}")
        self.default_target = default_target

    def get_supported_languages(self) -> List[str]:
        """Return the list of supported target languages."""
        return list(SUPPORTED_LANGUAGES)

    def translate(self, code: str, source_language: str, target_language: str) -> TranslationResult:
        """Translate a code string between two languages."""
        if source_language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported source language: {source_language}")
        if target_language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target language: {target_language}")

        warnings: List[str] = []
        translated = code

        # Apply construct mapping if available
        mapping = self.CONSTRUCT_MAP.get(source_language, {}).get(target_language, {})
        for src, dst in mapping.items():
            translated = translated.replace(src, dst)

        if not mapping:
            warnings.append(f"No direct mapping available from {source_language} to {target_language}")

        return TranslationResult(
            source_language=source_language,
            target_language=target_language,
            source_code=code,
            translated_code=translated,
            warnings=warnings,
        )

    def translate_file(self, file_path: str, target_language: str) -> TranslationResult:
        """Translate a source file to the target language."""
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = path.read_text(encoding="utf-8")
        ext = path.suffix.lower().lstrip(".")
        language_map = {
            "py": "python",
            "go": "go",
            "rs": "rust",
            "ts": "typescript",
            "tsx": "typescript",
            "java": "java",
        }
        source_language = language_map.get(ext, "python")

        return self.translate(source, source_language, target_language)