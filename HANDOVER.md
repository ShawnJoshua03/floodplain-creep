# Handover

Written 2026-11-07 for a fresh Claude Code session. Read this first, then CLAUDE.md, CODE_RULES.md,
DESIGN_RULES.md and PLAN.md in that order. Those four files are binding.

## Where the project stands

Floodplain Creep shows, by neighborhood, how many new buildings appeared in modeled river flood
zones in Dhaka. The repo is `~/projects/floodplain-creep`, `main` branch. It is on GitHub as a private
repo, `ShawnJoshua03/floodplain-creep`.

| Milestone | State |
|---|---|
| M0 foundation and guardrails | Done |
| M1 data access | Done |
| M2 core computation | Done |
| M3 validation | Code done. Labels exist from an AI reviewer. A human audit of 30 cells is pending |
| M4 database | Done on plain PostgreSQL. Tiger Data is not set up |
| Design rules | Installed (DESIGN_RULES.md, `check_design_rules.py`, `make design-check`) |
| M5 API | Not started. This is the next task |
| M6 to M8 | Not started |

`make check` passes with 125 Python tests and 1 frontend test. Suppressions used: 0 of 3.

## Decisions already made (do not reopen without the human)

- **City:** Dhaka. Nairobi was the plan default, but the JRC flood layer had no river flooding in
  central Nairobi. Sixteen cities were scanned and Dhaka was chosen by the human.
- **Box:** lon 90.3425 to 90.4775, lat 23.6925 to 23.8275 (about 15 km square). Set in
  `config/city.yaml`. The first box cut off Old Dhaka and was moved south.
- **Baseline year: 2018.** The years are 2018 to 2023. The 2016 and 2017 building layers look unstable:
  zone buildings jump 35 percent by 2018, then stay flat. The human chose 2018. The limits text in
  the UI must say 2016 and 2017 are not used because detections are unstable.
- **Neighborhood means a thana** (geoBoundaries ADM3, CC BY 3.0 IGO). No open ward polygons exist.
  33 neighborhoods are kept, at least half inside the box.
- **Counting method:** sum of `building_fractional_count`, kept only where `building_presence` is at
  least 0.45. Counts are relative, not exact. Totals swing a lot with the threshold.
- **K rule:** K = 20, applied only in `pipeline/lib/suppression.py`. Change since 2018 is shown only
  when both the year and 2018 reach K, so a hidden baseline cannot be worked out.
- **Table columns** (these replace the PLAN.md names): `buildings_in_zone`, `new_buildings_in_zone`,
  `growth_pct`, `suppressed`, `change_available`. `year_start` in the database is a date such as
  2018-01-01. A decrease is real data. Show it as a signed number.
- **Database:** plain PostgreSQL with the same schema as Tiger Data would use. The Tiger Data
  hypertable syntax (`CREATE TABLE ... WITH (tsdb.hypertable ...)`) was read but never tried.
- **Python 3.12** is pinned (`.python-version`) because `pgserver`, used for local Postgres in tests,
  has no wheel for 3.14.
- **SpaceXSI raffle:** skipped. **Brief language:** English only.

## Findings the product must respect

- Validation (AI labels, not audited, do not publish): on 56 test cells, accuracy 0.55 (0.42 to 0.68),
  precision 0.30 (0.17 to 0.48), recall 0.69 (0.42 to 0.87). Precision never passes about 0.45 at any
  change threshold. A single 100 m cell showing more buildings is a weak sign of a visible new
  building. Neighborhood totals may hold up better, but that is untested.
- The accuracy card must read the stored validation result. Never hardcode a number (hard rule 5).
- The JRC flood layer marks about 57 percent of the box above 0.1 m. The modeled zone is wide
  because of shallow depths on a 90 m grid and taking the maximum when resampling to 100 m. Say so
  on screen. It is river flooding only.
- Several neighborhoods show net decreases since 2018 (for example Lalbagh, Adabor, Mohammadpur).
  This is detection noise or rebuilding. Do not hide it.

## What the human still has to do

1. Label `data/processed/audit_sheet.csv` (30 cells, blind). Compare imagery around 2018 and 2023.
   Allowed labels: `increase`, `no_clear_change`, `decrease`, `unclear`. Then run the merge and evaluate
   steps below. If the audit shows the AI labels are unreliable, the human labels the full
   `labeling_sheet.csv` by hand. A label typed there always wins.
2. Tiger Data or another Postgres. Create the service, copy `.env.example` to `.env`, set `DATABASE_URL`.
   Not needed for M5 or M6, which can use local Postgres. Needed before deploying.
3. Save the approved design mockup screenshots into `docs/design-reference/` (M6).
4. Add `GEMINI_API_KEY` to `.env` (M7). Fill `config/resources.yaml` with official preparedness links (M7).
5. Choose hosting for M8. The repo is private. The human flips it public, after a license is chosen.

## Next task: M5, the API

Follow PLAN.md M5 and the layers in CODE_RULES.md section 1. All handlers are plain `def`. Stop at the M5
gate and show example responses for one normal and one suppressed neighborhood, and show that
`make types` produces no diff. Things to know:

- `api/main.py` is a bare FastAPI app. `scripts/dump_openapi.py` writes `web/openapi.json`, and
  `npm --prefix web run generate:types` writes `web/src/api/generated/`. `make types` runs both.
- Settings must come through one object. `config/city.yaml` and `config/validation.yaml` are read by
  `pipeline/io/city_config.py` and `pipeline/io/validation_files.py`. The API needs its own settings
  module in `api/core/`. It may reuse the YAML but must not import from `pipeline/io`.
- `config/banned_terms.txt` and `config/misuse_notice.txt` are the only places banned words may
  appear. Banned words must not appear anywhere in `api/` or `web/src/`, even in comments. Tests are exempt.
- `GET /hazard/overlay` needs a new pipeline step `render_overlays.py`. It does not exist yet. The image
  shows modeled depth only. It must be built from cells or the JRC raster, never from buildings.
- `GET /validation` reads the `validation_result` table. `load_database` adds a row only when
  `data/processed/validation_result.json` exists. It exists now from the unaudited run, so rerun
  evaluation after the audit before loading anything meant to be shown.
- No response may hold geometry finer than a neighborhood, and suppressed rows return null counts.
  Both need tests.

## Setup on a fresh machine or shell

```
uv sync
git config core.hooksPath .githooks
cd web && npm install
```

`make` on this Windows machine is the winget package `ezwinports.make`. If `make` is not found, add
`$HOME/AppData/Local/Microsoft/WinGet/Packages/ezwinports.make_Microsoft.Winget.Source_8wekyb3d8bbwe/bin`
to PATH, or open a new terminal. The Makefile runs Python through `uv run`, because `python3` on this
machine is a Microsoft Store stub that does not run Python.

The `data/` folder is gitignored. To rebuild it, run these in order. Every step fails loudly.

```
uv run python -m pipeline.steps.fetch_flood
uv run python -m pipeline.steps.fetch_buildings          # about 3 minutes per year, 2016 to 2023
uv run python -m pipeline.steps.build_grid
uv run python -m pipeline.steps.aggregate_neighborhoods
```

Boundaries need `data/raw/boundaries/adm3.geojson`. Download it from the geoBoundaries URL in
`docs/SOURCES.md` (125 MB). Validation steps, only if redoing them:

```
uv run python -m pipeline.steps.make_validation_sample   # refuses if labeling_sheet.csv exists
uv run python -m pipeline.steps.rebase_validation_sample
uv run python -m pipeline.steps.render_labeling_images   # about 4 minutes, resumes after a failure
uv run python -m pipeline.steps.make_audit_sheet         # refuses if audit_sheet.csv exists
uv run python -m pipeline.steps.merge_labels
uv run python -m pipeline.steps.evaluate_validation
```

Load a database with `uv run --env-file .env python -m pipeline.steps.load_database`. Without a
`DATABASE_URL`, tests still run against a local Postgres started by `pgserver`.

## Where things are

- `docs/DECISIONS.md` is the full log: every decision, finding, fallback and the reason. Read it.
- `docs/SOURCES.md` has the data sources, URLs, dates checked, CRS, resolution and nodata values.
- `pipeline/lib/` pure functions, `pipeline/io/` files and database, `pipeline/steps/` thin scripts.
- `data/processed/` holds `cells.npz` (cell level, never published), `neighborhood_year_exposure.csv`,
  `neighborhoods.geojson`, the validation files, and the labeling images. Old 2017-start labels and
  images are kept as `ai_labels_2017start.csv` and `labeling_images_2017start/`.

## Gotchas that cost time

- Do not write files through bash heredocs when the content has backslashes or `\n` in strings.
  Use the Write or Edit tools. A bad heredoc once corrupted a test file.
- `ruff format` rewrites files. Run it before `make check`. Line length is 120.
- vulture reports a classmethod `cls` as unused. Use an instance `model_validator` instead of a
  suppression.
- mypy is strict. `rasterio` has no stubs, so it has a per-module override in `pyproject.toml`
  (recorded in DECISIONS.md). Never add an inline `type: ignore`.
- Background commands that finish are announced by the harness. Do not add an inner `&`.
- Wayback release dates are not capture dates. The renderer reads the real capture date per cell.
- Avoid a colon followed by the word "any" in prose comments. The type-escape check flags it.
- The design checker bans raw colors and lengths outside `web/src/styles/tokens.css`, inline styles
  that are not CSS variables, emoji, gradients and design packages.

## Rules to keep

Never weaken CODE_RULES.md or DESIGN_RULES.md. Search before creating a helper. Commit after each
milestone with the root causes of fixes in the message. Print the health report at every gate. Stop at
each gate and wait for the human. No push without being asked once the human has said otherwise.
