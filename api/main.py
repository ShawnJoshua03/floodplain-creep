"""FastAPI app. The connection pool and settings are created once at startup."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from psycopg_pool import ConnectionPool

from api.core.errors import register_error_handlers
from api.core.settings import Settings, load_settings
from api.routers import focus, reference


def create_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        active = settings or load_settings()

        pool = ConnectionPool(active.database_url, min_size=1, max_size=5, open=True)
        app.state.settings = active
        app.state.pool = pool
        try:
            yield
        finally:
            pool.close()

    app = FastAPI(title="Floodplain Creep", lifespan=lifespan)
    register_error_handlers(app)
    app.include_router(focus.router)
    app.include_router(reference.router)
    return app


app = create_app()
