"""Write neighborhood-level results to PostgreSQL. Plain SQL, no extensions required."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

from pipeline.io.city_config import ROOT
from pipeline.lib.suppression import BalanceRow, ExposureRow

SCHEMA_PATH = ROOT / "db" / "schema.sql"


def connect(url: str, schema: str | None = None) -> psycopg.Connection:
    """Open a connection. With `schema`, create it and use it first on the search path."""
    conn = psycopg.connect(url)
    if schema is not None:
        conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
        conn.execute(f'SET search_path TO "{schema}"')
        conn.commit()
    return conn


def apply_schema(conn: psycopg.Connection, schema_path: Path = SCHEMA_PATH) -> None:
    conn.execute(schema_path.read_text(encoding="utf-8"))
    conn.commit()


def load_neighborhoods(conn: psycopg.Connection, geojson_path: Path) -> int:
    collection = json.loads(geojson_path.read_text(encoding="utf-8"))
    rows = [
        (
            f["properties"]["neighborhood_id"],
            f["properties"]["name"],
            f["properties"]["boundary_source"],
            f["properties"]["coverage"],
            Jsonb(f["geometry"]),
        )
        for f in collection["features"]
    ]
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO neighborhoods (neighborhood_id, name, boundary_source, coverage, geometry)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (neighborhood_id) DO UPDATE SET
                name = EXCLUDED.name,
                boundary_source = EXCLUDED.boundary_source,
                coverage = EXCLUDED.coverage,
                geometry = EXCLUDED.geometry
            """,
            rows,
        )
    return len(rows)


def replace_exposure(conn: psycopg.Connection, rows: list[ExposureRow]) -> int:
    values = [
        (
            r.neighborhood_id,
            date(r.year, 1, 1),
            r.return_period,
            r.buildings_in_zone,
            r.new_buildings_in_zone,
            r.growth_pct,
            r.suppressed,
            r.change_available,
        )
        for r in rows
    ]
    with conn.cursor() as cur:
        cur.execute("DELETE FROM neighborhood_year_exposure")
        cur.executemany(
            """
            INSERT INTO neighborhood_year_exposure
                (neighborhood_id, year_start, return_period, buildings_in_zone,
                 new_buildings_in_zone, growth_pct, suppressed, change_available)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            values,
        )
    return len(values)


def add_validation_result(conn: psycopg.Connection, payload: dict[str, object]) -> None:
    conn.execute("INSERT INTO validation_result (payload) VALUES (%s)", (Jsonb(payload),))


def replace_balance(conn: psycopg.Connection, rows: list[BalanceRow]) -> int:
    values = [
        (r.neighborhood_id, r.return_period, r.cells_in_zone, r.cells_gaining, r.cells_losing, r.suppressed)
        for r in rows
    ]
    with conn.cursor() as cur:
        cur.execute("DELETE FROM neighborhood_change_balance")
        cur.executemany(
            """
            INSERT INTO neighborhood_change_balance
                (neighborhood_id, return_period, cells_in_zone, cells_gaining, cells_losing, suppressed)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            values,
        )
    return len(values)
