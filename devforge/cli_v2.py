"""DevForge 2.0 Enhanced CLI.

Revolutionary command-line interface with intelligent commands for
predictive analysis, code translation, self-healing pipelines,
AI code generation, and dependency resolution.

Existing commands: new, build, check, fix, info
New commands: predict, translate, heal, generate, resolve
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from devforge import __version__
from devforge.ai_generator import AICodeGenerator
from devforge.android_builder import AndroidBuilder, BuildVariant
from devforge.code_translator import UniversalCodeTranslator
from devforge.config import DevForgeConfig
from devforge.dependency_resolver import Dependency, SmartDependencyResolver
from devforge.predictive_engine import PredictiveErrorEngine
from devforge.project_forge import ProjectForge, ProjectType
from devforge.self_healing_pipeline import FailureType, SelfHealingPipeline
from devforge.smart_build import BuildTarget, SmartBuild

logger = logging.getLogger(__name__)

COMMANDS: Sequence[str] = (
    "new", "build", "check", "fix", "info",
    "predict", "translate", "heal", "generate", "resolve",
)


def _setup_logging(level: str = "INFO") -> None:
    """Configure root logging with a consistent format."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


# ---------------------------------------------------------------------- #
# Existing commands
# ---------------------------------------------------------------------- #
def cmd_new(args: argparse.Namespace) -> int:
    """Create a new project scaffold."""
    project_type = ProjectType(args.type or "python")
    forge = ProjectForge(project_root=".")
    try:
        result = forge.forge(args.name, project_type, args.description or "")
    except ValueError as exc:
        logger.error("Invalid project name: %s", exc)
        return 1

    base = Path(args.output or args.name)
    base.mkdir(parents=True, exist_ok=True)
    paths = result.write_all(str(base))
    print(f"Created project '{args.name}' ({project_type.value}) in {base}")
    for p in paths:
        print(f"  - {p}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    """Build the current project."""
    target = BuildTarget(args.target) if args.target else BuildTarget.AUTO
    builder = SmartBuild(project_root=".")
    result = builder.build(target)
    print(f"Build {'succeeded' if result.success else 'failed'} "
          f"(target={result.target.value}, exit={result.exit_code})")
    if result.stderr:
        print(result.stderr[:500])
    return 0 if result.success else 1


def cmd_check(args: argparse.Namespace) -> int:
    """Run predictive analysis on the project."""
    engine = PredictiveErrorEngine(confidence_threshold=args.threshold)
    try:
        predictions = engine.analyze_project(args.path or ".")
    except FileNotFoundError as exc:
        logger.error("Project not found: %s", exc)
        return 1

    if not predictions:
        print("No high-confidence bug predictions found.")
        return 0

    print(f"Found {len(predictions)} potential issues:")
    for p in predictions:
        print(f"  [{p.severity}] {p.file}:{p.line} - {p.message}")
        print(f"       fix: {p.suggested_fix}")
    return 0


def cmd_fix(args: argparse.Namespace) -> int:
    """Run a self-healing build pipeline."""
    pipeline = SelfHealingPipeline()
    command = args.command or "python -m compileall -q ."
    result = pipeline.run(command, cwd=args.cwd)
    print(f"Build {'succeeded' if result.success else 'failed'} "
          f"(attempts={result.attempts}, exit={result.exit_code})")
    return 0 if result.success else 1


def cmd_info(args: argparse.Namespace) -> int:
    """Print DevForge version and configuration info."""
    print(f"DevForge {__version__}")
    cfg = DevForgeConfig.from_env()
    print("\nConfiguration:")
    for key in (
        "log_level", "predictive_enabled", "selfheal_enabled",
        "translator_default_target", "resolver_strict_mode",
    ):
        print(f"  {key} = {getattr(cfg, key)}")
    return 0


# ---------------------------------------------------------------------- #
# Revolutionary new commands
# ---------------------------------------------------------------------- #
def cmd_predict(args: argparse.Namespace) -> int:
    """Run predictive error analysis on a project."""
    engine = PredictiveErrorEngine(confidence_threshold=args.threshold)
    try:
        predictions = engine.analyze_project(args.path)
    except FileNotFoundError as exc:
        logger.error("Project not found: %s", exc)
        return 1

    if args.json:
        print(json.dumps([p.to_dict() for p in predictions], indent=2))
        return 0

    if not predictions:
        print("No high-confidence bug predictions found.")
        return 0

    print(f"Predicted {len(predictions)} potential issues:")
    for p in predictions:
        print(f"  [{p.severity}] {p.file}:{p.line}:{p.column} - {p.message}")
        print(f"       pattern: {p.pattern}")
        print(f"       fix: {p.suggested_fix}")
    return 0


def cmd_translate(args: argparse.Namespace) -> int:
    """Translate code between languages."""
    translator = UniversalCodeTranslator(default_target=args.target)
    if args.file:
        path = Path(args.file)
        if not path.exists():
            logger.error("File not found: %s", args.file)
            return 1
        result = translator.translate_file(str(path), args.target)
    else:
        source = sys.stdin.read()
        result = translator.translate(source, args.source, args.target)

    print(f"// Translated {result.source_language} -> {result.target_language}")
    print(result.translated_code)
    for w in result.warnings:
        logger.warning(w)
    return 0


def cmd_heal(args: argparse.Namespace) -> int:
    """Run a self-healing CI/CD pipeline."""
    pipeline = SelfHealingPipeline()
    command = args.command
    if not command:
        logger.error("Heal requires --command")
        return 2
    result = pipeline.run(command, cwd=args.cwd)
    print(f"Self-healing pipeline {'succeeded' if result.success else 'failed'}")
    print(f"  attempts: {result.attempts}")
    print(f"  exit_code: {result.exit_code}")
    print(f"  failure_type: {result.failure_type.value}")
    if result.stderr:
        print(f"  stderr: {result.stderr[:300]}")
    return 0 if result.success else 1


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate code from natural language."""
    generator = AICodeGenerator()
    if args.scaffold:
        result = generator.scaffold_project(
            args.description, project_name=args.name or "new_project",
            language=args.language,
        )
    else:
        result = generator.generate(args.description, language=args.language)

    base = Path(args.output or ".")
    base.mkdir(parents=True, exist_ok=True)
    paths = result.write_all(str(base))
    print(f"Generated {len(paths)} file(s) in {base}:")
    for p in paths:
        print(f"  - {p}")
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    """Resolve dependency conflicts."""
    deps: List[Dependency] = []
    for spec in args.dependencies:
        name, _, version = spec.partition("==")
        deps.append(Dependency(name=name.strip(), version=version or "*"))

    resolver = SmartDependencyResolver(strict_mode=args.strict)
    result = resolver.resolve_conflicts(deps)

    print(f"Resolved {len(result.resolved)} dependencies:")
    for d in result.resolved:
        print(f"  - {d}")
    if result.conflicts:
        print("\nConflicts:")
        for c in result.conflicts:
            print(f"  ! {c}")
    if result.warnings:
        print("\nWarnings:")
        for w in result.warnings:
            print(f"  ? {w}")
    return 1 if result.conflicts else 0


# ---------------------------------------------------------------------- #
# Argument parsing
# ---------------------------------------------------------------------- #
def _build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="devforge2",
        description="DevForge 2.0 - Intelligent Development Environment",
    )
    parser.add_argument("--version", action="version", version=f"DevForge {__version__}")
    parser.add_argument("--log-level", default="INFO", help="Logging level (default: INFO)")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")

    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # new
    p_new = sub.add_parser("new", help="Create a new project scaffold")
    p_new.add_argument("name", help="Project name")
    p_new.add_argument("--type", choices=[t.value for t in ProjectType],
                       default="python", help="Project type")
    p_new.add_argument("--description", default="", help="Project description")
    p_new.add_argument("--output", default=None, help="Output directory")

    # build
    p_build = sub.add_parser("build", help="Build the current project")
    p_build.add_argument("--target", choices=[t.value for t in BuildTarget],
                         default=None, help="Build target (default: auto)")

    # check
    p_check = sub.add_parser("check", help="Run predictive analysis")
    p_check.add_argument("path", nargs="?", default=".", help="Project path")
    p_check.add_argument("--threshold", type=float, default=0.7,
                         help="Confidence threshold (0-1)")

    # fix
    p_fix = sub.add_parser("fix", help="Run self-healing build")
    p_fix.add_argument("--command", default=None, help="Build command")
    p_fix.add_argument("--cwd", default=".", help="Working directory")

    # info
    sub.add_parser("info", help="Show DevForge version and configuration")

    # predict
    p_predict = sub.add_parser("predict", help="Predict bugs in a project")
    p_predict.add_argument("path", help="Project path to analyze")
    p_predict.add_argument("--threshold", type=float, default=0.7,
                           help="Confidence threshold (0-1)")
    p_predict.add_argument("--json", action="store_true", help="Output JSON")

    # translate
    p_translate = sub.add_parser("translate", help="Translate code between languages")
    p_translate.add_argument("--file", default=None, help="Source file (default: stdin)")
    p_translate.add_argument("--source", default="python",
                             choices=["python", "go", "rust", "typescript", "java"],
                             help="Source language")
    p_translate.add_argument("--target", default="python",
                             choices=["python", "go", "rust", "typescript", "java"],
                             help="Target language")

    # heal
    p_heal = sub.add_parser("heal", help="Run self-healing CI/CD pipeline")
    p_heal.add_argument("--command", default=None, help="Build command to run")
    p_heal.add_argument("--cwd", default=".", help="Working directory")

    # generate
    p_generate = sub.add_parser("generate", help="Generate code from natural language")
    p_generate.add_argument("description", help="Natural language description")
    p_generate.add_argument("--language", default="python",
                            choices=["python", "go", "rust", "typescript", "java"],
                            help="Target language")
    p_generate.add_argument("--name", default=None, help="Project name (for scaffold)")
    p_generate.add_argument("--scaffold", action="store_true",
                            help="Create a full project scaffold")
    p_generate.add_argument("--output", default=None, help="Output directory")

    # resolve
    p_resolve = sub.add_parser("resolve", help="Resolve dependency conflicts")
    p_resolve.add_argument("dependencies", nargs="+", help="Dependencies (e.g. requests==2.31)")
    p_resolve.add_argument("--strict", action="store_true", help="Strict mode")

    return parser


# ---------------------------------------------------------------------- #
# Interactive mode
# ---------------------------------------------------------------------- #
def _interactive_loop() -> int:
    """Run an interactive REPL with DevForge commands."""
    print("DevForge 2.0 Interactive Mode")
    print("Commands: " + ", ".join(COMMANDS) + ", exit")
    parser = _build_parser()
    while True:
        try:
            line = input("devforge> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line or line in ("exit", "quit"):
            return 0
        try:
            ns = parser.parse_args(line.split())
        except SystemExit:
            continue
        rc = _dispatch(ns)
        if rc:
            return rc


# ---------------------------------------------------------------------- #
# Dispatch
# ---------------------------------------------------------------------- #
_HANDLERS = {
    "new": cmd_new,
    "build": cmd_build,
    "check": cmd_check,
    "fix": cmd_fix,
    "info": cmd_info,
    "predict": cmd_predict,
    "translate": cmd_translate,
    "heal": cmd_heal,
    "generate": cmd_generate,
    "resolve": cmd_resolve,
}


def _dispatch(args: argparse.Namespace) -> int:
    """Dispatch a parsed command to its handler."""
    handler = _HANDLERS.get(args.command)
    if handler is None:
        logger.error("Unknown command: %s", args.command)
        return 2
    try:
        return handler(args)
    except Exception as exc:
        logger.error("Command failed: %s", exc)
        return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point for the DevForge 2.0 CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    if args.interactive or args.command is None:
        return _interactive_loop()

    return _dispatch(args)


if __name__ == "__main__":
    sys.exit(main())
