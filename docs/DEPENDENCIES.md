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
