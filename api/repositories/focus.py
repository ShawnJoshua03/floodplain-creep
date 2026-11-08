"""SQL for the focus neighborhood and the evidence around it. Every row is a neighborhood-level count."""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row
from pydantic import BaseModel

from api.schemas.focus import Outline, SeriesYear

OUTLINE_SQL = """
    SELECT neighborhood_id, name, boundary_source, coverage::float8 AS coverage, geometry
    FROM neighborhoods
    WHERE name = %s
"""

SERIES_SQL = """
    SELECT EXTRACT(YEAR FROM year_start)::int AS year,
           buildings_in_zone, new_buildings_in_zone, growth_pct::float8 AS growth_pct,
           suppressed, change_available
    FROM neighborhood_year_exposure
    WHERE neighborhood_id = %s AND return_period = %s
    ORDER BY year_start
"""

OTHERS_SQL = """
    SELECT neighborhood_id, EXTRACT(YEAR FROM year_start)::int AS year, buildings_in_zone
    FROM neighborhood_year_exposure
    WHERE return_period = %s AND neighborhood_id <> %s
    ORDER BY neighborhood_id, year_start
"""

BALANCE_SQL = """
    SELECT neighborhood_id, cells_gaining, cells_losing
    FROM neighborhood_change_balance
    WHERE return_period = %s AND NOT suppressed AND (neighborhood_id = %s OR neighborhood_id IS NULL)
"""


class OtherYear(BaseModel):
    """One neighborhood-year of the other neighborhoods. buildings_in_zone is null when suppressed."""

    neighborhood_id: str
    year: int
    buildings_in_zone: int | None


class BalanceRecord(BaseModel):
    """neighborhood_id is None for the whole study area."""

    neighborhood_id: str | None
    cells_gaining: int
    cells_losing: int


def fetch_outline(conn: psycopg.Connection, name: str) -> Outline | None:
    with conn.cursor(row_factory=class_row(Outline)) as cur:
        return cur.execute(OUTLINE_SQL, (name,)).fetchone()


def fetch_series(conn: psycopg.Connection, neighborhood_id: str, return_period: int) -> list[SeriesYear]:
    with conn.cursor(row_factory=class_row(SeriesYear)) as cur:
        return cur.execute(SERIES_SQL, (neighborhood_id, return_period)).fetchall()


def fetch_other_years(conn: psycopg.Connection, return_period: int, focus_id: str) -> list[OtherYear]:
    with conn.cursor(row_factory=class_row(OtherYear)) as cur:
        return cur.execute(OTHERS_SQL, (return_period, focus_id)).fetchall()


def fetch_balance(conn: psycopg.Connection, return_period: int, focus_id: str) -> list[BalanceRecord]:
    with conn.cursor(row_factory=class_row(BalanceRecord)) as cur:
        return cur.execute(BALANCE_SQL, (return_period, focus_id)).fetchall()
