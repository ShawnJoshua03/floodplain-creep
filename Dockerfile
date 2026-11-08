FROM node:22-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY api/ api/
COPY pipeline/ pipeline/
COPY config/ config/
COPY deploy/overlays/ deploy/overlays/
COPY --from=web /web/dist web/dist
ENV WEB_DIST=/app/web/dist OVERLAY_DIR=/app/deploy/overlays
CMD ["sh", "-c", "uv run --no-dev uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
