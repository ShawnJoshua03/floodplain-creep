#!/usr/bin/env python3
"""Repo-wide rule checks that linters and type checkers do not cover.

Run from anywhere: python scripts/check_repo_rules.py
Exits with code 1 and a list of violations if any rule is broken.
The rules are described in CODE_RULES.md. Keep this file and that file in sync.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

import extra_rules

ROOT = Path(__file__).resolve().parent.parent

SOURCE_DIRS = ("pipeline", "api", "web/src", "scripts", "tests")
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}
SKIP_PARTS = {"node_modules", "dist", "build", ".venv", "__pycache__", "generated"}

MAX_FILE_LINES = 300
MAX_SUPPRESSIONS = 3

MAP_VIEW_PATH = "web/src/features/map/MapView.tsx"

BANNED_JS_PACKAGES = {
    "axios",
    "node-fetch",
    "request",
    "lodash",
    "moment",
    "redux",
    "@reduxjs/toolkit",
    "zustand",
    "mobx",
    "leaflet",
    "react-leaflet",
}
BANNED_PY_MODULES = {"requests", "aiohttp"}

FILLER_PATTERNS = [
    r"sure,? here",
    r"here is the (updated|revised|new)",
    r"here's the (updated|revised|new)",
    r"as an ai\b",
    r"let me know if",
    r"updated function",
    r"ensure you have installed",
    r"i('ve| have) (updated|changed|fixed)",
]
FILLER_RE = re.compile("|".join(FILLER_PATTERNS), re.IGNORECASE)

# Zero tolerance: these always fail.
TYPE_ESCAPE_PATTERNS = [
    r"@ts-ignore",
    r"@ts-expect-error",
    r"@ts-nocheck",
    r"\bas unknown as\b",
    r"\bas any\b",
    r":\s*any\b",
]
TYPE_ESCAPE_RE = re.compile("|".join(TYPE_ESCAPE_PATTERNS))

# Limited: each one needs a reason in docs/DECISIONS.md, and the repo-wide cap applies.
SUPPRESSION_PATTERNS = [
    r"#\s*noqa",
    r"#\s*type:\s*ignore",
    r"#\s*pyright:\s*ignore",
    r"eslint-disable",
]
SUPPRESSION_RE = re.compile("|".join(SUPPRESSION_PATTERNS))

# Words that must not appear in user-facing or generated copy.
# The approved misuse notice file is the only allowed exception.
BANNED_COPY_RE = re.compile(
    r"\b(illegal|encroach\w*|squatter\w*|slum\w*|evict\w*|demolish\w*|demolition\w*)\b|clear out",
    re.IGNORECASE,
)
COPY_ALLOWLIST_RE = re.compile(r"misuse[_-]?notice", re.IGNORECASE)
COPY_DIRS = ("api", "web/src")

violations: list[str] = []


def report(path: Path, line: int, message: str) -> None:
    rel = path.relative_to(ROOT).as_posix()
    violations.append(f"{rel}:{line}: {message}")


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    for directory in SOURCE_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
                continue
            if SKIP_PARTS.intersection(path.parts):
                continue
            files.append(path)
    return sorted(files)


def check_file_length(path: Path, lines: list[str]) -> None:
    if len(lines) > MAX_FILE_LINES:
        report(path, len(lines), f"file has {len(lines)} lines, limit is {MAX_FILE_LINES}")


def check_filler(path: Path, lines: list[str]) -> None:
    for number, line in enumerate(lines, start=1):
        if path.name == "check_repo_rules.py":
            continue
        if FILLER_RE.search(line):
            report(path, number, "conversational filler left in source")
        if line.strip().startswith("```"):
            report(path, number, "stray markdown code fence in source")


def check_type_escapes(path: Path, lines: list[str]) -> None:
    if path.name == "check_repo_rules.py":
        return
    for number, line in enumerate(lines, start=1):
        if TYPE_ESCAPE_RE.search(line):
            report(path, number, "type escape is not allowed (any, as unknown as, @ts-*)")


def count_suppressions(path: Path, lines: list[str]) -> list[tuple[Path, int]]:
    found: list[tuple[Path, int]] = []
    if path.name == "check_repo_rules.py":
        return found
    for number, line in enumerate(lines, start=1):
        if SUPPRESSION_RE.search(line):
            found.append((path, number))
    return found


def check_names_and_todos(path: Path, lines: list[str]) -> None:
    if path.name in {"check_repo_rules.py", "extra_rules.py"}:
        return
    for number, message in extra_rules.generic_name_violations(path, lines):
        report(path, number, message)
    for number, message in extra_rules.todo_violations(lines):
        report(path, number, message)


def check_except_handler(path: Path, node: ast.ExceptHandler) -> None:
    if node.type is None:
        report(path, node.lineno, "bare except is not allowed")
    only_silent = all(
        isinstance(stmt, ast.Pass) or (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
        for stmt in node.body
    )
    if only_silent:
        report(path, node.lineno, "except block swallows the error silently")


def check_import_node(path: Path, node: ast.AST) -> None:
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name.split(".")[0] in BANNED_PY_MODULES:
                report(path, node.lineno, f"banned module: {alias.name}")
    if isinstance(node, ast.ImportFrom) and node.module:
        if node.module.split(".")[0] in BANNED_PY_MODULES:
            report(path, node.lineno, f"banned module: {node.module}")


def check_python_ast(path: Path, text: str) -> None:
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        report(path, error.lineno or 1, f"syntax error: {error.msg}")
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            check_except_handler(path, node)
        check_import_node(path, node)


def check_typescript(path: Path, lines: list[str]) -> None:
    rel = path.relative_to(ROOT).as_posix()
    if not rel.startswith("web/src"):
        return
    if path.suffix in {".js", ".jsx"}:
        report(path, 1, "JavaScript file in web/src, use TypeScript")
    for number, line in enumerate(lines, start=1):
        if ".then(" in line:
            report(path, number, "use async/await, not .then() chains")
        if re.search(r"document\.(getElementById|querySelector)", line) and rel != MAP_VIEW_PATH:
            report(path, number, "direct DOM lookup outside MapView.tsx")
        if "console.log" in line:
            report(path, number, "console.log is not error handling or logging")
        match = re.search(r"""(?:from\s+|require\(\s*)["']([^"']+)["']""", line)
        if match:
            package = match.group(1)
            root_name = "/".join(package.split("/")[:2]) if package.startswith("@") else package.split("/")[0]
            if root_name in BANNED_JS_PACKAGES:
                report(path, number, f"banned package: {root_name}")


def check_banned_copy(path: Path, lines: list[str]) -> None:
    rel = path.relative_to(ROOT).as_posix()
    if not rel.startswith(COPY_DIRS):
        return
    if COPY_ALLOWLIST_RE.search(path.name) or rel.startswith("tests"):
        return
    for number, line in enumerate(lines, start=1):
        if BANNED_COPY_RE.search(line):
            report(path, number, "banned word in copy (see CLAUDE.md rule 3)")


def check_package_json() -> None:
    package_json = ROOT / "web" / "package.json"
    if not package_json.exists():
        return
    data = json.loads(package_json.read_text(encoding="utf-8"))
    declared = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    for name in sorted(BANNED_JS_PACKAGES.intersection(declared)):
        report(package_json, 1, f"banned dependency: {name}")


def check_python_requirements() -> None:
    for name in ("requirements.txt", "requirements-dev.txt"):
        path = ROOT / name
        if not path.exists():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            package = re.split(r"[<>=!~\[ ;]", line.strip(), maxsplit=1)[0].lower()
            if package in BANNED_PY_MODULES:
                report(path, number, f"banned dependency: {package}")


def main() -> int:
    suppressions: list[tuple[Path, int]] = []
    for path in iter_source_files():
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        check_file_length(path, lines)
        check_filler(path, lines)
        check_type_escapes(path, lines)
        check_banned_copy(path, lines)
        check_names_and_todos(path, lines)
        suppressions.extend(count_suppressions(path, lines))
        if path.suffix == ".py":
            check_python_ast(path, text)
        else:
            check_typescript(path, lines)
    check_package_json()
    check_python_requirements()
    violations.extend(extra_rules.dependency_doc_violations(ROOT))

    if len(suppressions) > MAX_SUPPRESSIONS:
        for path, number in suppressions:
            report(path, number, "suppression comment or type escape")
        violations.append(f"total suppressions: {len(suppressions)}, limit is {MAX_SUPPRESSIONS}")

    if violations:
        print("Repo rule violations:")
        for item in violations:
            print(f"  {item}")
        return 1
    print("Repo rules: all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
