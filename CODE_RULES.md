# CODE_RULES.md

Read this before writing or editing any code. These rules exist to prevent five known
problems in AI-assisted projects. Each rule says how it is enforced. If a rule and a
shortcut disagree, the rule wins.

`make check` must pass before every commit and at every gate in PLAN.md.

## 0. How these rules are enforced

- Linters and type checkers with strict settings (configured in milestone M0).
- `scripts/check_repo_rules.py` for rules the linters do not cover.
- A health report at every gate (see the end of this file).
- Type escapes always fail the check: `any`, `as any`, `as unknown as X`, `@ts-ignore`,
  `@ts-expect-error`, `@ts-nocheck`. Fix the data shape instead.
- Suppression comments (`# noqa`, `# type: ignore`, `# pyright: ignore`, `eslint-disable`)
  are allowed only with the reason written in docs/DECISIONS.md. The repo-wide limit is 3.

When a check fails, find the root cause and fix it. Never silence a check to make it pass.

## 1. Architecture: one structure, one style

### No god files
- Maximum 300 lines per source file. Maximum about 40 lines per function.
- Split by responsibility. One file does one job.
- Before adding code to a file, ask: does this belong here? If not, make or find the right file.

### Layers and allowed imports

Python pipeline:
```
pipeline/steps/   one script per job, thin, calls lib and io
pipeline/lib/     pure functions (grid, exposure, aggregation, validation math). No file or network access.
pipeline/io/      reading and writing rasters, files, and the database
```
Python API:
```
api/routers/        thin HTTP handlers. Parse input, call a service, return a schema.
api/services/       business logic (exposure queries, brief generation)
api/repositories/   all SQL lives here and nowhere else
api/schemas/        pydantic models, the single source of truth for response shapes
api/safety/         K rule, number check, banned-word check
api/core/           settings, logging, error types
```
Frontend:
```
web/src/api/          fetch client, query hooks, generated types
web/src/components/   presentational components, no data fetching
web/src/features/     map, timelapse, scenario, brief, validation (each a folder)
web/src/state/        the one shared UI state provider
web/src/lib/          small pure helpers
```
Rules: routers never run SQL. Components never fetch. `lib/` never does I/O. Business logic
never lives in a component or a router.

### One paradigm
- Python: functions plus pydantic models and dataclasses. No classes beyond those.
- Python API handlers are plain `def` (synchronous), with a synchronous database client and a
  synchronous HTTP client. Do not mix sync and async in the API.
- TypeScript only. No `.js` or `.jsx` files in `web/src`.
- React: function components and hooks only. No class components.
- Async: `async/await` only. No `.then()` chains anywhere in `web/src`.
- DOM: no `document.getElementById` or `document.querySelector`. The map library's imperative
  API is confined to `web/src/features/map/MapView.tsx` and uses refs.

### Naming
- Python: `snake_case` functions and variables, `PascalCase` classes, `UPPER_SNAKE` constants.
- TypeScript: `camelCase` variables and functions, `PascalCase` components and types,
  `UPPER_SNAKE` constants. Component files are `PascalCase.tsx`. Other files are `camelCase.ts`.
- Names describe the domain. Use the terms in docs/GLOSSARY.md (cell, neighborhood, exposure,
  return period, suppressed, growth type) and nothing vaguer.
- Banned generic names for functions and modules: `process`, `process_item`, `handle_data`,
  `do_stuff`, `helper`, `helpers`, `util`, `utils`, `misc`, `data2`, `tmp`, `final`, `new_`.
- Enforced by ruff naming rules, the TypeScript naming-convention lint rule, and review.

## 2. No AI artifacts or ghost code

- No conversational comments. Never write "Sure, here is...", "Note: ensure you have
  installed...", "updated function", or similar. Comments explain why, not what.
- No commented-out code. Delete it. Git remembers.
- No orphaned parameters. When a function changes, update every call site and remove inputs it
  no longer uses in the same change. Enforced by unused-argument lint rules and
  `noUnusedParameters`.
- No dead code. No unused imports, variables, files, exports, or functions. Enforced by ruff,
  vulture, `tsc`, and knip. Delete, do not leave "for later."
- No re-implementations. Before writing a utility, search the repo and the approved libraries
  in docs/DEPENDENCIES.md. Use the standard library or an approved library first.
- No pasted chat text in source files. The check script scans for common filler phrases and
  stray code fences.
- `TODO` comments must name a milestone, like `TODO(M6): ...`, and are removed by M8.

## 3. Error handling: fix causes, not symptoms

- No bare `except:` and no `except Exception:` followed by `pass`, a print, or a silent
  `continue`. Catch specific exceptions only.
- Catch errors only at boundaries: HTTP handlers, calls to external services, file reads.
  There, log with context and return a typed error or a documented fallback.
- Allowed fallbacks are listed in docs/DECISIONS.md with the label users will see.
  Examples: templated brief when Gemini fails, saved sample rain data labeled "sample."
- Pipeline scripts fail loudly. Raise errors with clear messages and exit non-zero.
- `console.log` is not error handling. Surface errors in the UI with an error state.
- TypeScript is strict: `strict: true`, `noUncheckedIndexedAccess`, `noUnusedLocals`,
  `noUnusedParameters`.
- Banned: `any`, `as any`, `as unknown as X`, `@ts-ignore`, `@ts-expect-error`,
  `@ts-nocheck`, and non-null assertions (`!`). Fix the data shape instead.
- One source of truth for data shapes: pydantic models in `api/schemas`. Generate the
  TypeScript types from the API's OpenAPI schema. Never hand-copy interfaces.
- Validate external data at the boundary (API responses, files, config) before using it.

## 4. Dependencies: one tool per job

- Every dependency is listed in docs/DEPENDENCIES.md with a one-line reason. Adding one
  requires adding that line in the same commit.
- One library per purpose:

| Purpose | Choice |
|---|---|
| HTTP, Python | `httpx` only (no `requests`, no `aiohttp`) |
| HTTP, frontend | native `fetch`, wrapped once in `web/src/api/client.ts` |
| Server data in React | one data-fetching library (TanStack Query) |
| Shared UI state | one React context provider (see section 5) |
| Map | MapLibre GL only (no Leaflet) |
| Dates | standard library and `Intl`. No `moment`. |
| Utilities | native language features. No `lodash`. |

- Banned packages: `axios`, `node-fetch`, `request`, `requests`, `aiohttp`, `lodash`,
  `moment`, `redux`, `@reduxjs/toolkit`, `zustand`, `mobx`, `leaflet`, `react-leaflet`.
- Prefer the standard library and modern native features before adding a package.
- Unused or missing dependencies fail the check (deptry for Python, knip for the frontend).

## 5. State and data flow

- Server data: fetched only through the data-fetching library's hooks in `web/src/api/`.
  No raw `useEffect` fetching. This handles loading, errors, caching, and canceling stale
  requests.
- Shared UI state: one `SelectionProvider` in `web/src/state/` holding `year`,
  `returnPeriod`, `neighborhoodId`, `overlayOn`. Nothing else is global. Read it with
  `useSelection()`.
- Local component state: `useState` only for state that no other component needs.
- Props: no prop drilling beyond two levels. If a value is needed deeper, it belongs in the
  provider or a hook.
- Every data-driven component renders three explicit states: loading, error, and empty. A
  test covers each.
- Effects: the `react-hooks/exhaustive-deps` lint rule is an error. Effects clean up after
  themselves. Rapid slider changes must never show stale data. A test changes the selection
  quickly with a slow mocked response and asserts the latest selection wins.
- Backend: create the database pool once at startup. No mutable module-level state. Read
  configuration through one settings object.

## 6. Process rules for Claude Code

- Search before you create. Check for an existing function, type, or dependency first.
- Make small, single-purpose commits. Run `make check` first.
- Never "make the red go away." Explain the root cause of each fixed failure in the commit
  message.
- Do not edit generated files by hand. Regenerate them.
- Do not add a feature that PLAN.md does not list. Ask first.

## 7. Health report at every gate

At each GATE in PLAN.md, print and review:
1. The five largest files and their line counts.
2. Suppression count (limit 3) and where each one is.
3. Dependencies added since the last gate, each with its reason.
4. Output of the unused-code and unused-dependency tools.
5. Anything deleted in the cleanup pass.

Then do a short cleanup pass: remove dead code, fix names, update docs. Commit only after
`make check` passes.
