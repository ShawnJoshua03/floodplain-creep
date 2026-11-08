"""SQL for exposure counts. All counts come from neighborhood-level rows, never from cells."""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row
from pydantic import BaseModel

from api.schemas.exposure import CityYear, MultiPolygonGeometry, PolygonGeometry


class NeighborhoodRecord(BaseModel):
    neighborhood_id: str
    name: str
    boundary_source: str
    geometry: PolygonGeometry | MultiPolygonGeometry
    buildings_in_zone: int | None
    new_buildings_in_zone: int | None
    growth_pct: float | None
    suppressed: bool
    change_available: bool


NEIGHBORHOODS_SQL = """
    SELECT n.neighborhood_id, n.name, n.boundary_source, n.geometry,
           e.buildings_in_zone, e.new_buildings_in_zone, e.growth_pct::float8 AS growth_pct,
           e.suppressed, e.change_available
    FROM neighborhoods n
    JOIN neighborhood_year_exposure e ON e.neighborhood_id = n.neighborhood_id
    WHERE e.return_period = %s AND e.year_start = make_date(%s, 1, 1)
    ORDER BY n.name, n.neighborhood_id
"""

CITY_YEARS_SQL = """
    SELECT EXTRACT(YEAR FROM year_start)::int AS year,
           COALESCE(SUM(buildings_in_zone) FILTER (WHERE NOT suppressed), 0)::int AS buildings_in_zone,
           SUM(new_buildings_in_zone) FILTER (WHERE change_available AND NOT suppressed)::int
               AS new_buildings_in_zone,
           COUNT(*) FILTER (WHERE NOT suppressed)::int AS neighborhoods_shown,
           COUNT(*) FILTER (WHERE suppressed)::int AS neighborhoods_suppressed
    FROM neighborhood_year_exposure
    WHERE return_period = %s
    GROUP BY year_start
    ORDER BY year_start
"""


def fetch_neighborhoods(conn: psycopg.Connection, return_period: int, year: int) -> list[NeighborhoodRecord]:
    with conn.cursor(row_factory=class_row(NeighborhoodRecord)) as cur:
        return cur.execute(NEIGHBORHOODS_SQL, (return_period, year)).fetchall()


def fetch_city_years(conn: psycopg.Connection, return_period: int) -> list[CityYear]:
    with conn.cursor(row_factory=class_row(CityYear)) as cur:
        return cur.execute(CITY_YEARS_SQL, (return_period,)).fetchall()
