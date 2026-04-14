from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = WORKSPACE_ROOT / "evidoc"


@dataclass(frozen=True)
class ForbiddenDependencyRule:
    name: str
    source_prefix: str
    forbidden_prefixes: tuple[str, ...]
    message: str


RULES = (
    ForbiddenDependencyRule(
        name="domain_isolation",
        source_prefix="evidoc.domain",
        forbidden_prefixes=(
            "evidoc.application",
            "evidoc.infrastructure",
            "evidoc.interfaces",
            "evidoc.api",
            "evidoc.listener",
            "evidoc.robot",
            "evidoc.documentation",
        ),
        message="Domain must remain isolated from outer layers.",
    ),
    ForbiddenDependencyRule(
        name="application_isolation",
        source_prefix="evidoc.application",
        forbidden_prefixes=(
            "evidoc.infrastructure",
            "evidoc.interfaces",
            "evidoc.api",
            "evidoc.listener",
            "evidoc.robot",
            "evidoc.documentation",
        ),
        message="Application must not depend on interfaces or infrastructure.",
    ),
    ForbiddenDependencyRule(
        name="infrastructure_boundary",
        source_prefix="evidoc.infrastructure",
        forbidden_prefixes=("evidoc.interfaces",),
        message="Infrastructure must not depend on interface adapters.",
    ),
)


def module_name_for(path: Path) -> str:
    relative = path.relative_to(WORKSPACE_ROOT).with_suffix("")
    return ".".join(relative.parts)


def imported_modules(tree: ast.AST) -> list[tuple[str, int]]:
    imports: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.module, node.lineno))
    return imports


def main() -> int:
    violations = 0

    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        module_name = module_name_for(path)
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

        for imported_module, lineno in imported_modules(tree):
            for rule in RULES:
                if not module_name.startswith(rule.source_prefix):
                    continue
                if any(imported_module.startswith(prefix) for prefix in rule.forbidden_prefixes):
                    relative_path = path.relative_to(WORKSPACE_ROOT).as_posix()
                    print(
                        f"{relative_path}:{lineno}:1: error: "
                        f"{rule.message} Forbidden import '{imported_module}' "
                        f"({rule.name})."
                    )
                    violations += 1

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
