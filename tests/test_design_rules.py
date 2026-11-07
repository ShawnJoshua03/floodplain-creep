"""Tests for scripts/check_design_rules.py. Each rule must fire on a violation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

TOKENS_CSS = """:root { color-scheme: light dark; --accent: #007aff; --text-body: 1.0625rem; }
@media (prefers-color-scheme: dark) { :root { --accent: #0a84ff; } }
"""
BASE_CSS = "button:focus-visible { outline: var(--focus-ring); outline-offset: var(--space-1); }\n"
MOTION_CSS = "@media (prefers-reduced-motion: reduce) { :root { --duration-base: 0ms; } }\n"
MATERIALS_CSS = (
    "@supports (backdrop-filter: blur(1px)) { .chrome { backdrop-filter: blur(var(--blur)); } }\n"
    "@media (prefers-reduced-transparency: reduce) { .chrome { background: var(--bg); } }\n"
)
GOOD_COMPONENT_CSS = (
    ".row { padding: var(--space-3); color: var(--label); font-size: var(--text-body);\n"
    "  border-block-end: 1px solid var(--separator);\n"
    "  transition: opacity var(--duration-base) var(--ease-standard); }\n"
)


def load_checker() -> ModuleType:
    path = Path(__file__).resolve().parent.parent / "scripts" / "check_design_rules.py"
    spec = importlib.util.spec_from_file_location("check_design_rules", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_clean_tree(root: Path) -> None:
    write(root, "web/src/styles/tokens.css", TOKENS_CSS)
    write(root, "web/src/styles/base.css", BASE_CSS)
    write(root, "web/src/styles/motion.css", MOTION_CSS)
    write(root, "web/src/styles/materials.css", MATERIALS_CSS)
    write(root, "web/src/features/sheet/Row.module.css", GOOD_COMPONENT_CSS)
    write(
        root,
        "web/src/features/sheet/Row.tsx",
        'export function Row() { return <div style={{ "--fill": 0.4 }}>Exposed</div>; }\n',
    )


def test_clean_tree_has_no_violations(tmp_path: Path) -> None:
    make_clean_tree(tmp_path)
    assert load_checker().check_tree(tmp_path) == []


VIOLATIONS = [
    ("color literal", "web/src/features/a/A.module.css", ".a { color: #ff0000; }\n"),
    ("color literal", "web/src/features/a/A.module.css", ".a { color: rgb(1, 2, 3); }\n"),
    ("named color", "web/src/features/a/A.module.css", ".a { color: white; }\n"),
    ("gradients", "web/src/features/a/A.module.css", ".a { background: linear-gradient(red, blue); }\n"),
    ("box-shadow", "web/src/features/a/A.module.css", ".a { box-shadow: 0 0 4px var(--label); }\n"),
    ("text-shadow", "web/src/features/a/A.module.css", ".a { text-shadow: none; }\n"),
    ("backdrop-filter", "web/src/features/a/A.module.css", ".a { backdrop-filter: blur(var(--blur)); }\n"),
    ("font-family", "web/src/features/a/A.module.css", ".a { font-family: serif; }\n"),
    ("web fonts", "web/src/features/a/A.module.css", "@import url(https://fonts.googleapis.com/css2);\n"),
    ("letter-spacing", "web/src/features/a/A.module.css", ".a { letter-spacing: 0.1em; }\n"),
    ("uppercase", "web/src/features/a/A.module.css", ".a { text-transform: uppercase; }\n"),
    ("tokens", "web/src/features/a/A.module.css", ".a { font-weight: 700; }\n"),
    ("tokens", "web/src/features/a/A.module.css", ".a { line-height: 1.4; }\n"),
    ("side borders", "web/src/features/a/A.module.css", ".a { border-left: 4px solid var(--accent); }\n"),
    ("animation belongs", "web/src/features/a/A.module.css", ".a { animation: spin var(--duration-slow); }\n"),
    ("infinite", "web/src/styles/motion.css", ".a { animation-iteration-count: infinite; }\n"),
    ("transition: all", "web/src/features/a/A.module.css", ".a { transition: all var(--duration-base); }\n"),
    ("duration token", "web/src/features/a/A.module.css", ".a { transition: opacity 200ms; }\n"),
    ("durations and delays", "web/src/features/a/A.module.css", ".a { transition-duration: 200ms; }\n"),
    ("focus outline", "web/src/features/a/A.module.css", ".a:focus { outline: none; }\n"),
    ("raw length", "web/src/features/a/A.module.css", ".a { padding: 12px; }\n"),
    ("emoji", "web/src/features/a/A.tsx", "export const label = 'Done \u2728';\n"),
    ("inline style", "web/src/features/a/A.tsx", "export const a = <div style={{ color: 'red' }} />;\n"),
    ("marketing", "web/src/features/a/A.tsx", "export const t = 'Seamless insights';\n"),
    ("image files", "web/src/assets/hero.png", "binary placeholder\n"),
]


@pytest.mark.parametrize(("fragment", "rel", "text"), VIOLATIONS)
def test_each_rule_fires(tmp_path: Path, fragment: str, rel: str, text: str) -> None:
    make_clean_tree(tmp_path)
    write(tmp_path, rel, text)
    report = load_checker().check_tree(tmp_path)
    assert any(fragment in item for item in report), report


def test_hex_color_is_allowed_in_tokens_file(tmp_path: Path) -> None:
    make_clean_tree(tmp_path)
    assert load_checker().check_tree(tmp_path) == []


def test_marketing_words_are_allowed_in_tests(tmp_path: Path) -> None:
    make_clean_tree(tmp_path)
    write(tmp_path, "web/src/features/a/A.test.tsx", "const sample = 'seamless';\n")
    assert load_checker().check_tree(tmp_path) == []


def test_missing_token_file_is_reported(tmp_path: Path) -> None:
    write(tmp_path, "web/src/features/a/A.module.css", GOOD_COMPONENT_CSS)
    report = load_checker().check_tree(tmp_path)
    assert any("token file is missing" in item for item in report)


def test_missing_reduced_motion_support_is_reported(tmp_path: Path) -> None:
    make_clean_tree(tmp_path)
    write(tmp_path, "web/src/styles/motion.css", ".a { opacity: 1; }\n")
    report = load_checker().check_tree(tmp_path)
    assert any("prefers-reduced-motion" in item for item in report)


def test_banned_design_dependency_is_reported(tmp_path: Path) -> None:
    make_clean_tree(tmp_path)
    write(tmp_path, "web/package.json", '{"dependencies": {"framer-motion": "1.0.0", "react": "19.0.0"}}')
    report = load_checker().check_tree(tmp_path)
    assert any("framer-motion" in item for item in report)
    assert not any("react:" in item for item in report)


ALLOWED_FORMS = (
    ".a { box-shadow: var(--shadow-floating); }\n"
    ".b { box-shadow: none; }\n"
    ".c { border-left: none; }\n"
    ".d { font-weight: var(--weight-semibold); line-height: var(--line-body); }\n"
    ".e { transition-duration: var(--duration-fast); }\n"
    ".f { font-size: inherit; }\n"
)


def test_valid_token_usage_is_not_flagged(tmp_path: Path) -> None:
    make_clean_tree(tmp_path)
    write(tmp_path, "web/src/features/a/Allowed.module.css", ALLOWED_FORMS)
    assert load_checker().check_tree(tmp_path) == []
