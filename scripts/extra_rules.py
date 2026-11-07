"""Extra repo rules: generic names, dependency docs, TODO format.

Each function returns violation messages. check_repo_rules.py reports them.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

GENERIC_NAMES = {
    "process",
    "process_item",
    "handle_data",
    "do_stuff",
    "helper",
    "helpers",
    "util",
    "utils",
    "misc",
    "data2",
    "tmp",
    "final",
}
GENERIC_PREFIX = "new_"

PY_DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")
TS_FUNCTION_RE = re.compile(r"\bfunction\s+(\w+)")
TS_CONST_FN_RE = re.compile(r"\b(?:const|let)\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s*)?(?:\(|\w+\s*=>)")
TODO_RE = re.compile(r"\bTODO\b")
TODO_OK_RE = re.compile(r"\bTODO\(M\d+\)")
DOC_ENTRY_RE = re.compile(r"^- `([^`]+)`:")


def is_generic(name: str) -> bool:
    return name in GENERIC_NAMES or name.startswith(GENERIC_PREFIX)


def generic_name_violations(path: Path, lines: list[str]) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    if is_generic(path.stem):
        found.append((1, f"generic file name: {path.stem}"))
    for number, line in enumerate(lines, start=1):
        names = [m.group(1) for m in PY_DEF_RE.finditer(line)]
        names += [m.group(1) for m in TS_FUNCTION_RE.finditer(line)]
        names += [m.group(1) for m in TS_CONST_FN_RE.finditer(line)]
        found.extend((number, f"generic function name: {n}") for n in names if is_generic(n))
    return found


def todo_violations(lines: list[str]) -> list[tuple[int, str]]:
    return [
        (number, "TODO must name a milestone, like TODO(M6)")
        for number, line in enumerate(lines, start=1)
        if TODO_RE.search(line) and not TODO_OK_RE.search(line)
    ]


def normalize(name: str) -> str:
    return name.lower().replace("_", "-")


def requirement_name(requirement: str) -> str:
    return normalize(re.split(r"[<>=!~\[ ;@]", requirement.strip(), maxsplit=1)[0])


def declared_python(pyproject: Path) -> set[str]:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    names = {requirement_name(r) for r in data.get("project", {}).get("dependencies", [])}
    for group in data.get("project", {}).get("optional-dependencies", {}).values():
        names.update(requirement_name(r) for r in group)
    for group in data.get("dependency-groups", {}).values():
        names.update(requirement_name(r) for r in group if isinstance(r, str))
    return names


def declared_node(package_json: Path) -> set[str]:
    data = json.loads(package_json.read_text(encoding="utf-8"))
    return {normalize(name) for section in ("dependencies", "devDependencies") for name in data.get(section, {})}


def documented(doc: Path) -> set[str]:
    if not doc.exists():
        return set()
    names: set[str] = set()
    for line in doc.read_text(encoding="utf-8").splitlines():
        match = DOC_ENTRY_RE.match(line)
        if match:
            names.add(normalize(match.group(1)))
    return names


def dependency_doc_violations(root: Path) -> list[str]:
    declared: set[str] = set()
    pyproject = root / "pyproject.toml"
    package_json = root / "web" / "package.json"
    if pyproject.exists():
        declared |= declared_python(pyproject)
    if package_json.exists():
        declared |= declared_node(package_json)
    listed = documented(root / "docs" / "DEPENDENCIES.md")
    problems = [
        f"docs/DEPENDENCIES.md:1: declared dependency has no entry: {name}" for name in sorted(declared - listed)
    ]
    problems += [
        f"docs/DEPENDENCIES.md:1: entry is not a declared dependency: {name}" for name in sorted(listed - declared)
    ]
    return problems
