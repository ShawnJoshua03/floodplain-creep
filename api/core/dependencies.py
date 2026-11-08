"""FastAPI dependencies: settings and one pooled connection per request."""

from __future__ import annotations

from collections.abc import Iterator

import psycopg
from fastapi import Request

from api.core.settings import Settings


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def get_connection(request: Request) -> Iterator[psycopg.Connection]:
    with request.app.state.pool.connection() as conn:
        yield conn
