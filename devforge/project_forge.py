"""Project Forge - Intelligent project scaffolding engine.

Generates complete project structures from templates with best practices,
standardized layouts, and configuration files.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ProjectType(str, Enum):
    """Supported project types."""

    PYTHON = "python"
    WEB = "web"
    MOBILE = "mobile"
    LIBRARY = "library"
    CLI = "cli"
    API = "api"


@dataclass
class ProjectFile:
    """A single file in a generated project."""

    path: str
    content: str
    description: str = ""

    def write(self, base_dir: str) -> Path:
        full = Path(base_dir) / self.path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(self.content, encoding="utf-8")
        return full


@dataclass
class ForgeResult:
    """Result of a project forge operation."""

    project_name: str
    project_type: ProjectType
    files: List[ProjectFile]
    root_dir: str = ""

    def write_all(self, base_dir: str) -> List[Path]:
        paths: List[Path] = []
        for f in self.files:
            paths.append(f.write(base_dir))
        return paths


class ProjectForge:
    """Scaffolds projects from templates with intelligent defaults."""

    TEMPLATES: Dict[ProjectType, Dict[str, str]] = {
        ProjectType.PYTHON: {
            "init": "__init__.py",
            "main": "main.py",
            "readme": "README.md",
        },
        ProjectType.WEB: {
            "index": "index.html",
            "app": "app.js",
            "style": "style.css",
        },
        ProjectType.CLI: {
            "main": "cli.py",
            "readme": "README.md",
        },
    }

    def __init__(self, project_root: str = ".") -> None:
        self.project_root = Path(project_root)

    def forge(
        self,
        name: str,
        project_type: ProjectType = ProjectType.PYTHON,
        description: str = "",
    ) -> ForgeResult:
        """Create a new project scaffold."""
        if not re.match(r"^[a-zA-Z0-9_\-]+$", name):
            raise ValueError("Project name must be alphanumeric with dashes/underscores")

        files = self._build_files(name, project_type, description)
        return ForgeResult(
            project_name=name,
            project_type=project_type,
            files=files,
            root_dir=name,
        )

    def _build_files(
        self,
        name: str,
        project_type: ProjectType,
        description: str,
    ) -> List[ProjectFile]:
        files: List[ProjectFile] = []
        pkg_name = name.replace("-", "_")

        if project_type == ProjectType.PYTHON:
            files.append(ProjectFile(
                path=f"{pkg_name}/__init__.py",
                content=f'"""{name} package."""\n\n__version__ = "0.1.0"\n',
                description="Package init",
            ))
            files.append(ProjectFile(
                path=f"{pkg_name}/main.py",
                content=(
                    '"""Entry point for {name}."""\n\n\ndef main() -> None:\n'
                    '    """Run the application."""\n    print("Hello from {name}")\n\n\n'
                    'if __name__ == "__main__":\n    main()\n'
                ).format(name=name),
                description="Main entry point",
            ))
            files.append(ProjectFile(
                path="README.md",
                content=f"# {name}\n\n{description or 'A Python project.'}\n",
                description="Project readme",
            ))
            files.append(ProjectFile(
                path="pyproject.toml",
                content=self._python_pyproject(name, description),
                description="Project metadata",
            ))
        elif project_type == ProjectType.WEB:
            files.append(ProjectFile(
                path="index.html",
                content=f"<!DOCTYPE html>\n<html><head><title>{name}</title></head>\n"
                        f"<body><div id=\"root\"></div><script src=\"app.js\"></script></body>\n</html>\n",
                description="HTML entry",
            ))
            files.append(ProjectFile(
                path="app.js",
                content=f"// {name}\nconsole.log('Hello from {name}');\n",
                description="Application script",
            ))
            files.append(ProjectFile(
                path="style.css",
                content=f"/* {name} styles */\nbody {{ margin: 0; }}\n",
                description="Stylesheet",
            ))
        elif project_type == ProjectType.CLI:
            files.append(ProjectFile(
                path="cli.py",
                content=(
                    '"""CLI for {name}."""\n\nimport argparse\n\n\ndef main() -> None:\n'
                    '    parser = argparse.ArgumentParser(prog="{name}")\n'
                    '    parser.parse_args()\n\n\nif __name__ == "__main__":\n    main()\n'
                ).format(name=name),
                description="CLI entry point",
            ))
            files.append(ProjectFile(
                path="README.md",
                content=f"# {name}\n\n{description or 'A CLI tool.'}\n",
                description="Project readme",
            ))
        return files

    @staticmethod
    def _python_pyproject(name: str, description: str) -> str:
        return (
            f"[project]\nname = \"{name}\"\nversion = \"0.1.0\"\n"
            f"description = \"{description or 'A Python project.'}\"\n"
            f"requires-python = \">=3.9\"\n\n"
            f"[build-system]\nrequires = [\"setuptools>=61\"]\n"
            f"build-backend = \"setuptools.build_meta\"\n"
        )