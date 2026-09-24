"""AI-Powered Code Generator.

Generates code from natural language descriptions, creates complete project
scaffolds from requirements, and generates tests from implementations.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GeneratedFile:
    """A file produced by the generator."""

    path: str
    content: str
    description: str = ""

    def write(self, base_dir: str) -> Path:
        """Write the file to disk under base_dir."""
        full_path = Path(base_dir) / self.path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(self.content, encoding="utf-8")
        return full_path


@dataclass
class GenerationResult:
    """Result of a generation operation."""

    prompt: str
    files: List[GeneratedFile]
    model: str = ""
    raw_response: str = ""

    def write_all(self, base_dir: str) -> List[Path]:
        """Write all generated files to disk."""
        paths: List[Path] = []
        for f in self.files:
            paths.append(f.write(base_dir))
        return paths


class AICodeGenerator:
    """Generates code, scaffolds, and tests using an AI backend."""

    DEFAULT_SYSTEM_PROMPT = (
        "You are an expert software engineer. Generate clean, production-ready "
        "code following best practices for the requested language."
    )

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.api_base = api_base or os.environ.get("OPENAI_API_BASE")
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        description: str,
        language: str = "python",
        style: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:
        """Generate code from a natural language description."""
        prompt = self._build_code_prompt(description, language, style)
        raw = self._call_llm(prompt)
        files = self._parse_files(raw, language)
        return GenerationResult(
            prompt=description,
            files=files,
            model=self.model,
            raw_response=raw,
        )

    def scaffold_project(
        self,
        requirements: str,
        project_name: str = "new_project",
        language: str = "python",
    ) -> GenerationResult:
        """Create a complete project scaffold from requirements."""
        prompt = (
            f"Create a complete {language} project named '{project_name}' based on "
            f"these requirements: {requirements}. Include main module, tests, "
            f"configuration, and a README. Respond with file paths and contents."
        )
        raw = self._call_llm(prompt)
        files = self._parse_files(raw, language)
        return GenerationResult(
            prompt=requirements,
            files=files,
            model=self.model,
            raw_response=raw,
        )

    def generate_tests(self, source_code: str, language: str = "python") -> GenerationResult:
        """Generate unit tests for the given source code."""
        prompt = (
            f"Generate comprehensive unit tests for the following {language} code. "
            f"Cover edge cases and error paths.\n\n{source_code}"
        )
        raw = self._call_llm(prompt)
        files = self._parse_files(raw, language)
        return GenerationResult(
            prompt="Generate tests",
            files=files,
            model=self.model,
            raw_response=raw,
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _build_code_prompt(
        self,
        description: str,
        language: str,
        style: Optional[Dict[str, Any]],
    ) -> str:
        style_str = ""
        if style:
            style_str = f"\nStyle preferences: {style}"
        return f"Generate {language} code for: {description}{style_str}"

    def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM backend. Falls back to a template response."""
        if not self.api_key:
            logger.warning("No API key configured; returning template response")
            return self._template_response(prompt)

        try:
            import urllib.request
            import json

            body = json.dumps({
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.DEFAULT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.api_base or 'https://api.openai.com/v1/chat/completions'}",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.error("LLM call failed: %s", exc)
            return self._template_response(prompt)

    def _template_response(self, prompt: str) -> str:
        return f"# AI generation unavailable for prompt: {prompt[:80]}...\n"

    def _parse_files(self, raw: str, language: str) -> List[GeneratedFile]:
        """Parse LLM output into file objects. Handles markdown code blocks."""
        files: List[GeneratedFile] = []
        ext = self._extension_for(language)

        # Try to extract fenced code blocks
        blocks = self._extract_code_blocks(raw)
        if not blocks:
            files.append(GeneratedFile(
                path=f"generated{ext}",
                content=raw,
                description="Auto-generated code",
            ))
            return files

        for idx, block in enumerate(blocks):
            files.append(GeneratedFile(
                path=f"generated_{idx}{ext}",
                content=block,
                description=f"Generated file {idx}",
            ))
        return files

    @staticmethod
    def _extract_code_blocks(text: str) -> List[str]:
        import re

        pattern = re.compile(r"```(?:\w+)?\n?(.*?)```", re.DOTALL)
        return [m.group(1).strip() for m in pattern.finditer(text)]

    @staticmethod
    def _extension_for(language: str) -> str:
        mapping = {
            "python": ".py",
            "go": ".go",
            "rust": ".rs",
            "typescript": ".ts",
            "java": ".java",
        }
        return mapping.get(language.lower(), ".txt")