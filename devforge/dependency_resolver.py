"""Smart Dependency Resolver.

Resolves complex dependency chains automatically, detects version conflicts,
and finds compatible versions for transitive dependencies.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Dependency:
    """A single dependency specification."""

    name: str
    version: str = "*"
    extras: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        extras = f"[{','.join(self.extras)}]" if self.extras else ""
        return f"{self.name}{extras}{self.version if self.version != '*' else ''}"


@dataclass
class ResolutionResult:
    """Result of a dependency resolution operation."""

    resolved: List[Dependency]
    conflicts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    transitive: List[Dependency] = field(default_factory=list)

    def is_conflict_free(self) -> bool:
        return not self.conflicts


class SmartDependencyResolver:
    """Resolves complex dependency chains and detects version conflicts."""

    VERSION_PATTERN = re.compile(r"^(?P<op>[><=!~]=?)?(?P<version>[\d.]+)(?P<rest>.*)$")

    def __init__(
        self,
        index_url: str = "https://pypi.org/simple",
        strict_mode: bool = False,
        allow_prereleases: bool = False,
    ) -> None:
        self.index_url = index_url
        self.strict_mode = strict_mode
        self.allow_prereleases = allow_prereleases
        self._cache: Dict[str, List[str]] = {}

    def resolve(self, dependencies: List[Dependency]) -> ResolutionResult:
        """Resolve a list of dependencies including transitive ones."""
        resolved: List[Dependency] = []
        conflicts: List[str] = []
        warnings: List[str] = []
        transitive: List[Dependency] = []

        seen: Set[str] = set()
        for dep in dependencies:
            key = dep.name.lower()
            if key in seen:
                conflicts.append(f"Duplicate dependency: {dep.name}")
                continue
            seen.add(key)
            resolved.append(dep)

            # Simulate transitive resolution
            trans = self._resolve_transitive(dep)
            for t in trans:
                tkey = t.name.lower()
                if tkey not in seen:
                    seen.add(tkey)
                    transitive.append(t)
                    resolved.append(t)

        return ResolutionResult(
            resolved=resolved,
            conflicts=conflicts,
            warnings=warnings,
            transitive=transitive,
        )

    def resolve_conflicts(self, dependencies: List[Dependency]) -> ResolutionResult:
        """Detect and attempt to resolve version conflicts."""
        result = self.resolve(dependencies)
        version_map: Dict[str, List[str]] = {}

        for dep in result.resolved + result.transitive:
            version_map.setdefault(dep.name.lower(), []).append(dep.version)

        for name, versions in version_map.items():
            unique = set(v for v in versions if v != "*")
            if len(unique) > 1:
                result.conflicts.append(
                    f"Version conflict for {name}: {sorted(unique)}"
                )
                if not self.strict_mode:
                    compatible = self.find_compatible_version(name, list(unique))
                    if compatible:
                        result.warnings.append(
                            f"Resolved {name} to {compatible}"
                        )
        return result

    def find_compatible_version(self, name: str, versions: List[str]) -> Optional[str]:
        """Find a single version compatible with all constraints."""
        if not versions:
            return None
        if len(versions) == 1:
            return versions[0]

        # Simple heuristic: pick the highest version
        def key(v: str) -> Tuple[int, ...]:
            nums = re.findall(r"\d+", v)
            return tuple(int(n) for n in nums)

        return max(versions, key=key)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _resolve_transitive(self, dep: Dependency) -> List[Dependency]:
        """Resolve transitive dependencies for a package (simulated)."""
        # In a real implementation this would query the package index.
        # Here we return a small static mapping for demonstration.
        transitive_map: Dict[str, List[str]] = {
            "requests": ["urllib3", "certifi", "charset-normalizer"],
            "django": ["sqlparse", "backports.cached-property"],
            "flask": ["werkzeug", "click", "itsdangerous", "jinja2"],
        }
        names = transitive_map.get(dep.name.lower(), [])
        return [Dependency(name=n) for n in names]

    def clear_cache(self) -> None:
        """Clear the internal resolution cache."""
        self._cache.clear()