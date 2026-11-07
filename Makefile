# Run `make check` before every commit and at every gate in PLAN.md.
# The tool commands below are the intended setup. In milestone M0, confirm each one
# against that tool's current docs and create the config files so every target passes.
PY := uv run

.PHONY: check py-check web-check repo-check design-check types

check: py-check web-check repo-check design-check

py-check:
	$(PY) ruff check .
	$(PY) ruff format --check .
	$(PY) mypy --strict pipeline api tests
	$(PY) pytest -q
	$(PY) vulture pipeline api --min-confidence 80
	$(PY) deptry .

web-check:
	npm --prefix web run typecheck
	npm --prefix web run lint
	npm --prefix web run test -- --run
	npm --prefix web run knip

repo-check:
	$(PY) python scripts/check_repo_rules.py

# Visual rules from DESIGN_RULES.md (tokens, banned styles, design dependencies).
design-check:
	$(PY) python scripts/check_design_rules.py

# Regenerates web/src/api/generated from the API OpenAPI schema (script set up in M0).
types:
	$(PY) python scripts/dump_openapi.py web/openapi.json
	npm --prefix web run generate:types
