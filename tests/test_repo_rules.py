from pathlib import Path

import check_repo_rules
import extra_rules
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def run_checker(root: Path, monkeypatch: pytest.MonkeyPatch, files: dict[str, str]) -> list[str]:
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    monkeypatch.setattr(check_repo_rules, "ROOT", root)
    check_repo_rules.violations.clear()
    check_repo_rules.main()
    return list(check_repo_rules.violations)


def fixture_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


CASES = [
    ("pipeline/lib/big.py", "VALUE = 1\n" * 301, "limit is 300"),
    ("web/src/a.ts", fixture_text("type_escape.txt"), "type escape"),
    ("pipeline/lib/a.py", fixture_text("silent_catch.txt"), "swallows the error"),
    ("pipeline/lib/a.py", fixture_text("bare_except.txt"), "bare except"),
    ("pipeline/lib/a.py", fixture_text("filler.txt"), "conversational filler"),
    ("web/src/a.ts", fixture_text("banned_package.txt"), "banned package: axios"),
    ("web/src/a.ts", fixture_text("then_chain.txt"), "async/await"),
    ("web/src/a.ts", fixture_text("dom_lookup.txt"), "direct DOM lookup"),
    ("web/src/a.js", fixture_text("plain.txt"), "use TypeScript"),
    ("api/a.py", fixture_text("banned_copy.txt"), "banned word in copy"),
    ("pipeline/lib/utils.py", fixture_text("plain.txt"), "generic file name: utils"),
    ("pipeline/lib/a.py", fixture_text("generic_def.txt"), "generic function name: process"),
    ("pipeline/lib/a.py", fixture_text("todo_bad.txt"), "must name a milestone"),
]


@pytest.mark.parametrize(("target", "content", "expected"), CASES)
def test_rule_family_is_caught(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    content: str,
    expected: str,
) -> None:
    found = run_checker(tmp_path, monkeypatch, {target: content})
    assert any(expected in item for item in found), found


def test_clean_tree_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = {
        "pipeline/lib/grid.py": fixture_text("plain.txt"),
        "pipeline/lib/notes.py": fixture_text("todo_ok.txt"),
    }
    assert run_checker(tmp_path, monkeypatch, files) == []


def test_suppression_limit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = {f"pipeline/lib/m{n}.py": fixture_text("suppression.txt") for n in range(4)}
    found = run_checker(tmp_path, monkeypatch, files)
    assert any("limit is 3" in item for item in found), found


def test_three_suppressions_are_allowed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = {f"pipeline/lib/m{n}.py": fixture_text("suppression.txt") for n in range(3)}
    assert run_checker(tmp_path, monkeypatch, files) == []


def test_generic_names_in_typescript() -> None:
    lines = fixture_text("generic_ts.txt").splitlines()
    found = extra_rules.generic_name_violations(Path("web/src/lib/a.ts"), lines)
    assert [number for number, _ in found] == [1, 2]


def test_new_prefix_is_generic() -> None:
    assert extra_rules.is_generic("new_grid")
    assert not extra_rules.is_generic("renew_grid")


def write_dependency_files(root: Path, declared: str, documented_lines: str) -> None:
    (root / "docs").mkdir()
    (root / "pyproject.toml").write_text(f'[project]\nname = "x"\ndependencies = [{declared}]\n', encoding="utf-8")
    (root / "docs" / "DEPENDENCIES.md").write_text(documented_lines, encoding="utf-8")


def test_undocumented_dependency_fails(tmp_path: Path) -> None:
    write_dependency_files(tmp_path, '"foo>=1"', "# Dependencies\n")
    found = extra_rules.dependency_doc_violations(tmp_path)
    assert found == ["docs/DEPENDENCIES.md:1: declared dependency has no entry: foo"]


def test_documented_but_undeclared_dependency_fails(tmp_path: Path) -> None:
    write_dependency_files(tmp_path, "", "- `bar`: unused.\n")
    found = extra_rules.dependency_doc_violations(tmp_path)
    assert found == ["docs/DEPENDENCIES.md:1: entry is not a declared dependency: bar"]


def test_matching_dependencies_pass(tmp_path: Path) -> None:
    write_dependency_files(tmp_path, '"Foo_Bar>=1"', "- `foo-bar`: reason.\n")
    assert extra_rules.dependency_doc_violations(tmp_path) == []


def test_package_json_dependencies_are_checked(tmp_path: Path) -> None:
    write_dependency_files(tmp_path, "", "# Dependencies\n")
    (tmp_path / "web").mkdir()
    (tmp_path / "web" / "package.json").write_text(
        '{"dependencies": {"react": "1"}, "devDependencies": {"@scope/tool": "1"}}',
        encoding="utf-8",
    )
    found = extra_rules.dependency_doc_violations(tmp_path)
    assert len(found) == 2
