"""SQL for stored briefs and neighborhood lookups."""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from api.schemas.brief import Brief


def fetch_brief(conn: psycopg.Connection, neighborhood_id: str, return_period: int) -> Brief | None:
    with conn.cursor(row_factory=class_row(Brief)) as cur:
        return cur.execute(
            "SELECT neighborhood_id, return_period, text, source FROM briefs"
            " WHERE neighborhood_id = %s AND return_period = %s",
            (neighborhood_id, return_period),
        ).fetchone()


def neighborhood_exists(conn: psycopg.Connection, neighborhood_id: str) -> bool:
    row = conn.execute("SELECT 1 FROM neighborhoods WHERE neighborhood_id = %s", (neighborhood_id,)).fetchone()
    return row is not None
