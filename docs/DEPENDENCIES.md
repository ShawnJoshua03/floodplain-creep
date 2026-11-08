# Dependencies

Every declared dependency has one line: `- `name`: reason`. A check compares this file with
`pyproject.toml` and `web/package.json`.

## Python
- `fastapi`: HTTP API framework.
- `pytest`: test runner.
- `ruff`: lint and format.
- `mypy`: strict type checking.
- `vulture`: dead code finder.
- `deptry`: unused and missing dependency finder.

## Frontend
Styling is plain CSS Modules plus `web/src/styles/tokens.css`. It adds no dependency. See DESIGN_RULES.md.

- `react`: UI components.
- `react-dom`: renders React in the browser.
- `vite`: dev server and build.
- `@vitejs/plugin-react`: React support for Vite.
- `typescript`: strict typing. Pinned to 5.9.x because typescript-eslint and openapi-typescript do not yet accept 7.
- `@types/react`: React types.
- `@types/react-dom`: React DOM types.
- `eslint`: lint.
- `@eslint/js`: ESLint base rules.
- `typescript-eslint`: TypeScript lint rules.
- `eslint-plugin-react-hooks`: hooks rules, exhaustive-deps is an error.
- `globals`: global names for ESLint environments.
- `vitest`: test runner.
- `jsdom`: browser-like test environment.
- `@testing-library/react`: component tests.
- `@testing-library/jest-dom`: DOM assertions.
- `knip`: unused file, export and dependency finder.
- `openapi-typescript`: generates API types from the OpenAPI schema.
- `rasterio`: read and write GeoTIFFs, reproject bounds.
- `numpy`: array maths for rasters.
- `httpx`: all Python HTTP downloads.
- `pydantic`: validate manifests, GeoJSON and config at the boundary.
- `pyyaml`: read `config/city.yaml`.
- `types-pyyaml`: type stubs for pyyaml.
- `geopandas`: read boundary polygons and reproject them.
- `shapely`: polygon geometry for neighborhoods.
- `types-shapely`: type stubs for shapely.
- `types-geopandas`: type stubs for geopandas.
- `pandas-stubs`: type stubs for pandas, which geopandas uses.
- `psycopg`: PostgreSQL client for the pipeline loader (API uses it in M5).
- `pgserver`: pip-installed local PostgreSQL so database tests run without Docker or an account.
- `pillow`: draw the before and after images used to review validation cells.
- `psycopg-pool`: connection pool the API opens once at startup.
- `uvicorn`: server that runs the API (`api/serve.py`).
- `@tanstack/react-query`: the one data-fetching library for server data in the frontend.
- `maplibre-gl`: the one map library, used only in `web/src/features/map/MapView.tsx`.
