#!/usr/bin/env python3
"""Design rule checks for the web app.

Run from anywhere: python scripts/check_design_rules.py
Exits with code 1 and a list of violations if any rule is broken.
The rules are described in DESIGN_RULES.md. Keep this file and that file in sync.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WEB_SRC = "web/src"
CSS = frozenset({".css"})
CODE = frozenset({".ts", ".tsx"})
ALL_STYLED = CSS | CODE
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"}
SKIP_PARTS = {"node_modules", "dist", "build", "generated"}

TOKENS = "web/src/styles/tokens.css"
MATERIALS = "web/src/styles/materials.css"
MOTION = "web/src/styles/motion.css"
BASE = "web/src/styles/base.css"

NAMED_COLORS = (
    "white|black|red|blue|green|gray|grey|silver|navy|teal|purple|pink|orange|yellow|cyan|"
    "magenta|maroon|olive|lime|aqua|fuchsia|gold|brown|coral|indigo|violet"
)

BANNED_PACKAGES = {
    "tailwindcss",
    "styled-components",
    "antd",
    "bootstrap",
    "react-bootstrap",
    "framer-motion",
    "motion",
    "react-spring",
    "lottie-web",
    "lottie-react",
    "react-icons",
    "lucide-react",
    "daisyui",
}
BANNED_PACKAGE_PREFIXES = (
    "@emotion/",
    "@mui/",
    "@chakra-ui/",
    "@fortawesome/",
    "@heroicons/",
    "@radix-ui/",
    "@fontsource/",
    "@headlessui/",
)


@dataclass(frozen=True)
class LineRule:
    message: str
    pattern: re.Pattern[str]
    suffixes: frozenset[str]
    allowed_files: frozenset[str] = field(default_factory=frozenset)
    skip_tests: bool = False


def rule(
    message: str,
    pattern: str,
    suffixes: frozenset[str],
    allowed: tuple[str, ...] = (),
    skip_tests: bool = False,
    flags: int = 0,
) -> LineRule:
    return LineRule(message, re.compile(pattern, flags), suffixes, frozenset(allowed), skip_tests)


LINE_RULES: tuple[LineRule, ...] = (
    rule(
        "color literal outside tokens.css, use a token",
        r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(|color-mix\(",
        ALL_STYLED,
        (TOKENS,),
    ),
    rule("named color outside tokens.css", rf":\s*(?:{NAMED_COLORS})\b", CSS, (TOKENS,)),
    rule("gradients are not allowed", r"gradient\(", ALL_STYLED),
    rule(
        "box-shadow must be none or a shadow token",
        r"box-shadow\s*:(?!\s*(?:none\b|var\(--shadow-))",
        CSS,
    ),
    rule("text-shadow is not allowed", r"text-shadow\s*:", CSS),
    rule("drop-shadow outside tokens.css", r"drop-shadow\(", ALL_STYLED, (TOKENS,)),
    rule("backdrop-filter only belongs in materials.css", r"backdrop-filter", ALL_STYLED, (MATERIALS,)),
    rule("font-family only belongs in tokens.css", r"font-family\s*:", CSS, (TOKENS,)),
    rule(
        "web fonts are not allowed, use the system font stack",
        r"@font-face|fonts\.googleapis|fonts\.gstatic|@import\s+url\(",
        ALL_STYLED,
    ),
    rule("letter-spacing only belongs in tokens.css", r"letter-spacing\s*:", CSS, (TOKENS,)),
    rule(
        "uppercase text and gradient text are not allowed",
        r"text-transform\s*:\s*uppercase|background-clip\s*:\s*text|-webkit-text-fill-color",
        CSS,
    ),
    rule(
        "font-size, font-weight, and line-height must use tokens",
        r"(?:font-size|font-weight|line-height)\s*:(?!\s*(?:var\(|inherit\b|normal\b))",
        CSS,
        (TOKENS,),
    ),
    rule(
        "colored side borders are not allowed",
        r"border-(?:left|inline-start)(?:-width|-color)?\s*:(?!\s*(?:none\b|0\b|inherit\b))|border-image",
        CSS,
    ),
    rule(
        "animation belongs in motion.css",
        r"@keyframes|animation(?:-name)?\s*:",
        CSS,
        (MOTION,),
    ),
    rule("infinite animation is not allowed", r"\binfinite\b", CSS),
    rule("transition: all is not allowed", r"transition\s*:\s*all\b", CSS),
    rule(
        "transitions must use a duration token",
        r"transition\s*:(?!.*var\(--duration-)",
        CSS,
        (TOKENS,),
    ),
    rule(
        "durations and delays must use tokens",
        r"(?:transition|animation)-(?:duration|delay)\s*:(?!\s*(?:var\(|0))",
        CSS,
        (TOKENS, MOTION),
    ),
    rule(
        "do not remove the focus outline",
        r"outline\s*:\s*(?:none|0)\b|outline-style\s*:\s*none",
        CSS,
    ),
    rule(
        "emoji and symbol glyphs are not allowed, use an icon component",
        "[\U0001f000-\U0001faff\u2600-\u27bf\u2b00-\u2bff\ufe0f]",
        ALL_STYLED,
    ),
    rule(
        "inline style may only set CSS variables",
        r"style=\{(?!\{\s*['\"]?--)",
        frozenset({".tsx"}),
    ),
    rule(
        "marketing wording is not allowed in the interface",
        r"\b(?:ai[- ]powered|powered by (?:ai|gemini)|magic(?:al)?|seamless(?:ly)?|supercharg\w*|"
        r"unlock\w*|revolutioni[sz]\w*|game[- ]chang\w*|cutting[- ]edge|next[- ]gen(?:eration)?)\b",
        ALL_STYLED,
        skip_tests=True,
        flags=re.IGNORECASE,
    ),
)

LENGTH_RE = re.compile(r"(?<![\w.#-])(?:\d+\.\d+|\d+)(?:px|rem|em)\b")
LENGTH_SKIP_RE = re.compile(r"^\s*@(?:media|container|supports)\b")


def is_test_file(rel: str) -> bool:
    name = rel.rsplit("/", 1)[-1]
    return ".test." in name or ".spec." in name


def iter_web_files(root: Path) -> list[Path]:
    base = root / WEB_SRC
    if not base.exists():
        return []
    files = [p for p in base.rglob("*") if p.is_file() and not SKIP_PARTS.intersection(p.parts)]
    return sorted(files)


def check_lines(root: Path, path: Path, report: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        for item in LINE_RULES:
            if path.suffix not in item.suffixes or rel in item.allowed_files:
                continue
            if item.skip_tests and is_test_file(rel):
                continue
            if item.pattern.search(line):
                report.append(f"{rel}:{number}: {item.message}")
        if path.suffix == ".css" and rel != TOKENS and not LENGTH_SKIP_RE.search(line):
            for match in LENGTH_RE.finditer(line):
                if match.group(0) != "1px":
                    report.append(f"{rel}:{number}: raw length {match.group(0)}, use a token")


def check_images(root: Path, files: list[Path], report: list[str]) -> None:
    for path in files:
        if path.suffix in IMAGE_SUFFIXES:
            rel = path.relative_to(root).as_posix()
            report.append(f"{rel}:1: image files are not allowed in web/src, use icon components")


def check_package_json(root: Path, report: list[str]) -> None:
    package_json = root / "web" / "package.json"
    if not package_json.exists():
        return
    data = json.loads(package_json.read_text(encoding="utf-8"))
    declared = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    for name in sorted(declared):
        if name in BANNED_PACKAGES or name.startswith(BANNED_PACKAGE_PREFIXES):
            report.append(f"web/package.json:1: banned design dependency: {name}")


def require(root: Path, rel: str, needles: tuple[str, ...], report: list[str]) -> None:
    path = root / rel
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            report.append(f"{rel}:1: must contain {needle}")


def check_required_features(root: Path, files: list[Path], report: list[str]) -> None:
    if not any(p.suffix == ".css" for p in files):
        return
    if not (root / TOKENS).exists():
        report.append(f"{TOKENS}:1: token file is missing")
    require(root, TOKENS, ("color-scheme", "prefers-color-scheme: dark"), report)
    require(root, BASE, (":focus-visible",), report)
    require(root, MOTION, ("prefers-reduced-motion",), report)
    require(root, MATERIALS, ("prefers-reduced-transparency", "@supports"), report)


def check_tree(root: Path) -> list[str]:
    report: list[str] = []
    files = iter_web_files(root)
    for path in files:
        if path.suffix in ALL_STYLED:
            check_lines(root, path, report)
    check_images(root, files, report)
    check_package_json(root, report)
    check_required_features(root, files, report)
    return report


def main() -> int:
    report = check_tree(ROOT)
    if report:
        print("Design rule violations:")
        for item in report:
            print(f"  {item}")
        return 1
    print("Design rules: all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
