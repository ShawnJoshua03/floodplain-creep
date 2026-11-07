# PLAN.md: Floodplain Creep

Read CLAUDE.md and CODE_RULES.md first. Items marked HUMAN need the person. Everything else
is for Claude Code. Do the milestones in order. At every GATE: run `make check`, print the
health report from CODE_RULES.md section 7, report results, and wait for the human.

## Decisions needed from the human (record in docs/DECISIONS.md)

1. City. Default: Nairobi, because a published study used this building dataset there and
   gives a validation benchmark. The ethics context is heavy, so the safeguards matter.
   Another city is fine if both datasets cover it.
2. SpaceXSI raffle. It requires using Cursor as the core AI coding agent, adding a Grok Bot
   automation, describing both in the project description, and opting in. Building mainly
   with Claude Code does not match that rule. Default: skip this prize.
3. Languages for briefs. Default: English only. Translation is extension E3.

## M0. Foundation and guardrails

Build the guardrails before any feature code.

- Create the layout from CLAUDE.md and CODE_RULES.md, including `db/schema.sql`, the four
  files in `config/`, and the five files in `docs/`. Fill in `docs/GLOSSARY.md` with the
  domain terms: cell, neighborhood, exposure, return period, suppressed, growth.
- Configure every tool in the Makefile so each target passes on the empty skeleton. Check each
  command and flag against the tool's current docs, and fix the Makefile if needed.
  - Python: ruff (include rules for naming, unused arguments, blind except, commented-out
    code, and complexity), mypy strict, pytest, vulture, deptry. For libraries that ship no
    type information, add per-module overrides in the config file. Do not use inline
    suppressions. Record each override in `docs/DECISIONS.md`.
  - Frontend: TypeScript with `strict`, `noUncheckedIndexedAccess`, `noUnusedLocals`,
    `noUnusedParameters`. ESLint rules for: no explicit any, no non-null assertion, no ts
    comments, naming convention, hooks exhaustive deps as error, no class components, async
    functions instead of promise chains, and `fetch` allowed only in `web/src/api/`.
    Vitest with Testing Library. knip.
  - `scripts/dump_openapi.py` and the `generate:types` script that writes
    `web/src/api/generated/`.
- Extend `scripts/check_repo_rules.py`, each addition with a test in `tests/`:
  - banned generic file and function names from CODE_RULES.md section 1,
  - every dependency in `pyproject` or `package.json` appears in `docs/DEPENDENCIES.md`, and
    the reverse,
  - `TODO` comments must match `TODO(M<number>)`.
- Add a pre-commit hook that runs ruff and `scripts/check_repo_rules.py`.
- Prove the guardrails work. For each rule family, add a scratch violation, confirm `make check`
  fails for the right reason, then remove it. Rule families: god file length, type escape,
  silent catch, unused import, unused parameter, conversational comment, banned package,
  `.then()` chain, direct DOM lookup, banned word in copy.

Known behaviors of the existing checker, so you do not trip them:
- It scans `api`, `pipeline`, `web/src`, `scripts`, and `tests` for source files only. Text
  files in `config/` are not scanned. That is why the banned word list and the misuse notice
  live there.
- Banned words must not appear anywhere in `api/` or `web/src/`, even in comments. Tests are
  exempt.
- Avoid prose comments that contain a colon followed by the word "any". The type escape
  pattern will flag it.

GATE M0: `make check` passes on the skeleton, and the scratch-violation proof is shown.

## M1. Data access check

Goal: prove both datasets can be read for the chosen area before building on them.

- Buildings: read the dataset page. Find the supported download path (Earth Engine export or
  direct download). Pull annual rasters 2016 to 2023 for a bounding box of about 15 km by
  15 km. Keep presence, fractional count, and height.
- Flood: read the README in the JRC folder. Download the tile(s) covering the box. Keep depth
  for return periods 10, 50, 100, 500, plus the permanent water and spurious depth layers.
- Write `pipeline/io/rasters.py` for reading, and `pipeline/steps/fetch_buildings.py` and
  `fetch_flood.py` as thin steps.
- Record CRS, resolution, and nodata values for each raster in `docs/SOURCES.md`.

Acceptance: a step prints, for each year and return period, the raster shape and value range.

Fallback: use a smaller box. If access still fails, stop and report what failed and which
alternative path to try.

GATE M1: the human confirms the data access path.

## M2. Core computation (pure functions first)

Put math in `pipeline/lib/`, with tests on small synthetic arrays. Steps stay thin.

- `grid.py`: align rasters to a common 100 m grid.
- `exposure.py`: building count per cell per year (follow the dataset's example method, mask
  low-confidence presence), and flood exposure per cell per return period (depth above the
  dataset minimum, excluding permanent water and spurious-depth cells).
- `aggregation.py`: roll cells up to neighborhoods by year and return period. Output exposed
  buildings, total buildings in the zone, and growth since 2016.
- `suppression.py`: the one place the K rule is applied. Suppressed rows get null counts and a
  `suppressed` flag.
- `pipeline/io/boundaries.py`: load the neighborhood boundaries. Record the source.
- Steps: `build_grid.py` and `aggregate_neighborhoods.py`. Cell-level output goes to
  `data/processed/` only.

Acceptance: `data/processed/neighborhood_year_exposure.csv` exists. Tests prove the K rule
suppresses small counts and that no cell-level field is present in this file.

GATE M2: show the top and bottom five neighborhoods and a sanity check against the imagery.

## M3. Validation (produces the accuracy number)

Run the Claude Code tasks alongside M4 while the human labels.

Claude Code:
- `pipeline/lib/sampling.py` and `validation_metrics.py`, with tests.
- `make_validation_sample.py`: sample cells inside the 100-year flood zone. At least 100
  random cells, plus 40 extra cells the algorithm flags as "increase" so there are enough
  positives. Record the sampling design. Export `labeling_sheet.csv` with cell id, latitude,
  longitude, and a link to view the place. Do not include the algorithm's prediction. Shuffle
  the order.
- `evaluate_validation.py`: after labels exist, compute the confusion matrix, accuracy,
  precision, recall, and Wilson 95 percent intervals. Tune the change threshold on the first
  60 percent of labels. Report final metrics only on the remaining 40 percent. Write a
  validation result file with the sampling note and the count of excluded "unclear" cells.

HUMAN: for each sampled cell, compare imagery from about 2016 and about 2023. Label it
`increase`, `no_clear_change`, `decrease`, or `unclear`. Use any imagery source with dates, and
write the source and dates in `docs/DECISIONS.md`.

Acceptance: the validation result file exists and includes all metrics and the sampling note.

## M4. Database

- Write `db/schema.sql`. Tables: `neighborhoods` (id, name, boundary_source, geometry as
  GeoJSON), `neighborhood_year_exposure` (neighborhood_id, year_start, return_period,
  exposed_buildings, total_buildings_in_zone, suppressed), `validation_result` (payload,
  created_at), and `briefs` (neighborhood_id, return_period, text, source, created_at).
  No table holds cell-level data.
- Read the Tiger Data docs for connection and for hypertable syntax before writing SQL. Use a
  hypertable on `year_start` only if the documented path works. Otherwise use plain Postgres
  and record why.
- `pipeline/io/database.py` writes data. `pipeline/steps/load_database.py` calls it.
- Tests use a throwaway schema and check that the suppression rule holds for every stored row.

Acceptance: a clean database loads from the processed files with one command.

## M5. API

Follow the layers in CODE_RULES.md. All handlers are plain `def`.

- `GET /city/summary?return_period=100`: counts by year for the whole city.
- `GET /neighborhoods?return_period=100&year=2023`: GeoJSON with exposed counts, growth, and a
  `suppressed` flag. Nothing finer than a neighborhood.
- `GET /hazard/overlay?return_period=100`: image URL, bounds, and depth bins. The image shows
  modeled depth only, with no buildings. Pipeline step `render_overlays.py` creates the images.
- `GET /validation`: the stored validation result.
- `GET /brief/{neighborhood_id}?return_period=100`: the stored brief, or a generated one (M7).
- `GET /limits`: the limits text, banned terms, and the misuse notice, read from `config/`.
- Pydantic schemas are the single source of truth. Run `make types` to regenerate the frontend
  types. Create the database pool once at startup. Read settings through one object.
- Tests: no response contains geometry finer than a neighborhood, and suppressed rows return
  null counts.

GATE M5: show example responses for one normal and one suppressed neighborhood. Show that
`make types` produces no diff.

## M6. Frontend

Follow the layers and state rules in CODE_RULES.md section 5.

- `web/src/api/`: the fetch client, TanStack Query hooks, and generated types.
- `web/src/state/SelectionProvider.tsx`: `year`, `returnPeriod`, `neighborhoodId`, `overlayOn`.
- `web/src/features/map/MapView.tsx`: the only file that uses the map library's imperative
  API, through refs. Neighborhood choropleth of exposed buildings.
- `features/timelapse/`: year slider with play. `features/scenario/`: return period buttons.
- Depth overlay toggle with a legend and a human-height silhouette (about 1.7 m) that shows
  where each depth bin sits on a person. Label depths as modeled and approximate.
- City counter: "new buildings in the modeled flood zone since 2016" for the chosen scenario.
- Ranked neighborhood list, also available as plain text. Suppressed neighborhoods show
  "not enough data."
- `features/validation/`: accuracy card with sample size and sampling method.
- `features/brief/`: the neighborhood brief, with a note on how it was checked.
- `features/limits/`: honesty panel and misuse notice from `/limits`, linked from every screen.
- Every data-driven component renders loading, error, and empty states, each with a test.
  Add a test where the selection changes quickly with a slow mocked response and the latest
  selection wins.
- Accessibility: keyboard use, readable contrast, and alt text for the map summary.

Acceptance: all screens work against the real API. `make check` passes.

GATE M6: walk the demo script and list anything that fails.

## M7. Briefs

- `api/services/briefs.py`: builds the input JSON (name, years, exposed counts for the chosen
  return period, growth, validation summary, caveats) and calls Gemini with the official SDK.
  Check current docs for model names.
- Prompt rules: plain language, 90 words or fewer, no numbers beyond those in the JSON, no
  blame language, mention uncertainty, and end with at most two pointers taken only from
  `config/resources.yaml`. HUMAN: fill that file with official preparedness links.
- `api/safety/number_check.py` and `banned_terms.py` check every output. On failure or API
  error, store a templated brief built from the same JSON with `source` set to `template`.
- `scripts/warm_briefs.py` fills the `briefs` table for every neighborhood before the demo.
- Tests: the number check catches an added number, the banned-term check catches a banned
  word, and the fallback path returns a valid brief.

## M8. Release

- Write the README: what it is, data sources, limits, ethics, how to run. State plainly what
  Tiger Data and Gemini are used for, and nothing more.
- Deploy the API and the static site. HUMAN: register a domain if wanted.
- Remove every `TODO(M..)`. Run the final health report and a cleanup pass.
- Run the demo script three times and fix whatever fails.

## Optional extensions (only after the definition of done)

Each is a full vertical slice: computation, API, UI, tests, and a dependency note.
- E1. Growth type view: horizontal versus vertical or combined growth, with the proxy note.
- E2. Rain strip with a time-series table and continuous aggregate. Handle API failure with a
  saved sample labeled "sample."
- E3. Brief translation, labeled machine translated and reviewed by a fluent speaker.

## Demo script (docs/DEMO.md)

1. Hook: "Cities are building into their floodplains. The people living there pay when the
   rains come."
2. Time-lapse: play 2016 to 2023 and read the city counter.
3. Scenario: switch to the 500-year flood. Show the depth overlay and the silhouette.
4. Neighborhood: click one and read the brief. Mention the number check.
5. Trust: show the accuracy card and the sampling note. Say what the tool cannot see.
6. Safeguards: neighborhoods only, suppressed small counts, and the misuse notice.

## Risks and fallbacks

| Risk | Fallback |
|---|---|
| Dataset access fails | Smaller box, or a different covered city |
| Year-to-year noise | Change threshold tuned on labels, stated on screen |
| Fewer labels than planned | Report the smaller sample honestly |
| Tiger Data setup stalls | Plain Postgres with the same schema |
| Gemini fails | Templated brief from the same JSON |
| Flood layer misses small drains | Say it on screen, it is river flooding only |
| Message misread as an enforcement tool | Neighborhood-only output and the misuse notice |
| A guardrail blocks progress | Fix the cause. Never weaken the rule. |

## Kickoff prompts for Claude Code

- "Read CLAUDE.md, CODE_RULES.md, and PLAN.md. Do M0 only. Stop at the gate with the
  scratch-violation proof."
- "Do M1. Stop at the gate and tell me which data access path worked."
- "Do M2, then show the gate output."
- "Do the Claude Code tasks in M3 and M4 together. Tell me when the labeling sheet is ready."
- "Do M5, then M6. Stop at each gate."
- "Do M7 and M8. Run the demo script and report any failures."
