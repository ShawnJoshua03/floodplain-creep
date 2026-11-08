"""SQL for stored briefs."""

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


def store_brief(conn: psycopg.Connection, neighborhood_id: str, return_period: int, text: str, source: str) -> None:
    conn.execute(
        """
        INSERT INTO briefs (neighborhood_id, return_period, text, source)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (neighborhood_id, return_period)
        DO UPDATE SET text = EXCLUDED.text, source = EXCLUDED.source, created_at = now()
        """,
        (neighborhood_id, return_period, text, source),
    )
