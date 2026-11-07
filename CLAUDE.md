# Floodplain Creep

Hackathon project, solo builder. This file is the standing brief.
At the start of every session read, in this order: CLAUDE.md, CODE_RULES.md, PLAN.md.
`make check` must pass before every commit and at every gate.

## What we are building

A web app that shows, neighborhood by neighborhood, how many new buildings have appeared on
flood-prone ground in one city since 2016. It uses open satellite-derived building data and
free flood hazard maps.

Core features:
- A time-lapse of exposed buildings by neighborhood, 2016 to 2023.
- Flood scenarios by return period (10, 50, 100, 500 years) with a modeled depth overlay.
- A human-height silhouette next to the depth legend, so depth is easy to grasp.
- A plain-language brief per neighborhood, written by Gemini from computed numbers only.
- A measured accuracy card, computed from hand-labeled satellite samples.
- An honesty panel and a misuse notice that are always one click away.

Anything not listed here or in PLAN.md is out of scope. Ask before adding it.

## Framing (important)

This is a preparedness and accountability tool. It is never an enforcement tool.

Flood-zone maps have been used to justify demolitions that rights groups say targeted poor
residents while wealthier riparian buildings were left alone. A court later ordered
compensation for evicted residents. This app must not become a target list.

## Product hard rules (never break these)

1. Aggregate only. The database, API, and UI never hold or expose individual buildings or
   single grid cells. Cell-level data stays in local pipeline files and never enters the
   database. The smallest unit shown is a neighborhood polygon.
2. Minimum count. If a neighborhood has fewer than K = 20 buildings in the flood zone for a
   displayed year, store and show "not enough data" instead of a number. Suppressed rows
   store null counts. K lives in `config/city.yaml` and is applied in exactly one function,
   `pipeline/lib/suppression.py`. A test reads the database and checks every row.
3. Neutral language. Never use these words in UI copy, API text, or briefs: illegal,
   encroacher, squatter, slum, evict, demolish, clear out. Say "new buildings in the modeled
   flood zone." The word list and the misuse notice live in `config/banned_terms.txt` and
   `config/misuse_notice.txt`, and are loaded through settings.
4. Numbers come from code. Gemini receives a JSON of computed stats and may not add numbers.
   After every Gemini call, check that each number in the text appears in the input JSON.
   On failure or API error, store a templated brief and mark its `source` as `template`.
5. Report validation honestly. Accuracy, precision, and recall are read from the stored
   validation result. Never hardcode them. Show the sampling method next to them.
6. Show the limits on screen: data years 2016 to 2023, building detections can be unstable
   between years, the flood layer is river flooding only at about 90 m, this is not an
   official warning, and it is not for evictions or enforcement.
7. Growth type is a pattern, not a wealth label. Do not call any pattern "informal" or
   "wealthy" unless a sourced dataset supports it. Do not claim a growth-type comparison
   in the pitch unless extension E1 is complete.
8. No secrets in the repo. Use `.env` and keep `.env.example` current.
9. Public data only. No personal data of any kind.
10. Label scenarios and any sample data as simulated or sample.

## Code quality contract

CODE_RULES.md is binding. It exists to stop five problems: god files and mixed styles,
leftover AI text and dead code, silenced errors and type escapes, overlapping libraries,
and tangled state. Never weaken it. You may add checks to it and to
`scripts/check_repo_rules.py`, with a test for each new check.

The short version:
- One job per file, 300 lines or fewer. One style per language. One library per purpose.
- No conversational comments, no commented-out code, no unused imports, parameters, or files.
- No silent catch blocks and no type escapes. Fix causes, not symptoms.
- One data-fetching library and one shared state provider in the frontend.
- Search the repo and `docs/DEPENDENCIES.md` before writing a helper.
- Run `make check` before every commit and print the health report at every gate.

## Data sources (verify each before relying on it)

- Open Buildings 2.5D Temporal Dataset (Google Research). Annual building presence,
  fractional building counts, and heights, 2016 to 2023, about 4 m effective resolution.
  Earth Engine collection: `GOOGLE/Research/open-buildings-temporal/v1`.
  Docs and download info: https://sites.research.google/gr/open-buildings/temporal
  Notes from the docs: presence confidence is uncalibrated, so use it only for relative
  thresholds. Use height only where presence confidence is high. Detections are not always
  stable across years. Follow the dataset's example method for counting buildings.
- JRC Global River Flood Hazard Maps v2.1 (Copernicus). About 90 m. Depth for return periods
  10, 20, 50, 75, 100, 200, 500 years. Free and open. Includes a permanent water class and a
  spurious depth flag for small channels. Data store:
  https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/
  Read the README in that folder for tile naming.
- Neighborhood boundaries: an official or well-documented admin boundary source for the chosen
  city. Prefer a downloaded extract over live queries to public map servers.

Never invent URLs, band names, or API parameters. Read the official page and record it in
`docs/SOURCES.md` with the date you checked it.

## Stack (every item must also appear in docs/DEPENDENCIES.md)

- Python: rasterio, numpy, pandas, geopandas, shapely, pyproj, pydantic, fastapi, uvicorn,
  psycopg, httpx, the official Google GenAI SDK, pytest. Dev: ruff, mypy, vulture, deptry.
- Database: Tiger Data (PostgreSQL). Read its docs before writing SQL. Hypertables and
  continuous aggregates are used only if the documented setup works. App code is plain SQL
  and must run on any Postgres.
- Frontend: Vite, React, TypeScript, MapLibre GL, TanStack Query. Dev: ESLint, Vitest,
  Testing Library, knip.

## Repo layout

```
floodplain-creep/
  CLAUDE.md  CODE_RULES.md  PLAN.md  README.md  Makefile  .env.example
  config/     city.yaml  resources.yaml  banned_terms.txt  misuse_notice.txt
  db/         schema.sql
  data/       raw/  processed/            (gitignored)
  pipeline/   steps/  lib/  io/           (see CODE_RULES.md section 1)
  api/        routers/  services/  repositories/  schemas/  safety/  core/
  web/        src/api/  components/  features/  state/  lib/
  scripts/    check_repo_rules.py  warm_briefs.py  dump_openapi.py
  tests/
  docs/       DECISIONS.md  DEPENDENCIES.md  GLOSSARY.md  SOURCES.md  DEMO.md
```

## Working agreements

- Work one milestone at a time. Stop at each gate, print the health report, and wait.
- Do not hand-edit generated files. Run `make types`.
- If a step needs a human (accounts, license clicks, labeling, sponsor opt-ins), stop and say
  exactly what to do.
- A working fallback beats an unfinished feature. Every fallback is listed in
  `docs/DECISIONS.md` with the label users will see.
- Write UI copy and README text in short, plain sentences.
- Commit after each milestone with a clear message that explains root causes of any fixes.

## Definition of done

- The pipeline runs end to end on the chosen city from a clean checkout.
- `make check` passes with no suppressions beyond the limit.
- Every product hard rule has a passing test.
- The accuracy card reads real validation output.
- The demo script in `docs/DEMO.md` runs without errors.
