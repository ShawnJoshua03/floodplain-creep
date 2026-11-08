"""Shared setup for API tests: a seeded schema, settings, and overlay files.

Neighborhood n1 is the focus and grows. n2 stays too small to show. n3 is a steady neighborhood that sets the noise.
"""

from __future__ import annotations

import json
from pathlib import Path

import psycopg
from psycopg.conninfo import make_conninfo

from api.core.settings import Settings, load_settings
from pipeline.io.database import add_validation_result, load_neighborhoods, replace_balance, replace_exposure
from pipeline.lib.aggregation import ZoneTotal
from pipeline.lib.balance import RawBalance
from pipeline.lib.suppression import apply_suppression, suppress_balance

YEARS = [2018, 2019, 2020, 2021, 2022, 2023]
FOCUS_COUNTS = [100, 102, 110, 108, 115, 130]
STEADY_COUNTS = [200, 204, 198, 202, 206, 200]
SMALL_COUNTS = [4, 5, 4, 6, 5, 6]

VALIDATION_PAYLOAD: dict[str, object] = {
    "labeled_cells": 140,
    "excluded_unclear": 0,
    "tuning_cells": 84,
    "test_cells": 56,
    "change_threshold_buildings": 1.8,
    "confusion": {"tp": 9, "fp": 21, "fn": 4, "tn": 22},
    "accuracy": {"value": 0.55, "low": 0.42, "high": 0.68, "n": 56},
    "precision": {"value": 0.3, "low": 0.17, "high": 0.48, "n": 30},
    "recall": {"value": 0.69, "low": 0.42, "high": 0.87, "n": 13},
    "sampling_note": "Test sampling note.",
    "label_sources": {"human": 0, "audit": 0, "ai": 140},
    "ai_human_agreement": {"value": None, "low": None, "high": None, "n": 0},
    "imagery_source": "Test imagery",
    "imagery_dates": "Test dates",
    "start_year": 2018,
    "end_year": 2023,
}


def write_neighborhoods(path: Path) -> None:
    ring = [[[0, 0], [1, 0], [1, 1], [0, 0]]]
    features = [
        {
            "type": "Feature",
            "properties": {"neighborhood_id": key, "name": name, "coverage": 0.9, "boundary_source": "test"},
            "geometry": {"type": "Polygon", "coordinates": ring},
        }
        for key, name in [("n1", "One"), ("n2", "Two"), ("n3", "Three")]
    ]
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")


def totals(key: str, counts: list[int]) -> list[ZoneTotal]:
    return [ZoneTotal(key, year, 100, float(count)) for year, count in zip(YEARS, counts, strict=True)]


def seed_database(conn: psycopg.Connection, tmp_path: Path, k: int) -> None:
    write_neighborhoods(tmp_path / "n.geojson")
    load_neighborhoods(conn, tmp_path / "n.geojson")
    all_totals = totals("n1", FOCUS_COUNTS) + totals("n2", SMALL_COUNTS) + totals("n3", STEADY_COUNTS)
    replace_exposure(conn, apply_suppression(all_totals, k, YEARS[0]))
    balance = [
        RawBalance("n1", 100, 50, 30, 5),
        RawBalance("n2", 100, 4, 1, 1),
        RawBalance("n3", 100, 60, 10, 10),
        RawBalance(None, 100, 114, 41, 16),
    ]
    replace_balance(conn, suppress_balance(balance, k))
    add_validation_result(conn, VALIDATION_PAYLOAD)
    conn.commit()


def write_overlay_files(overlay_dir: Path) -> None:
    overlay_dir.mkdir(parents=True, exist_ok=True)
    (overlay_dir / "depth_rp100.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    manifest = {
        "bounds": [90.34, 23.69, 90.47, 23.82],
        "bins": [{"min_depth_m": 0.1, "max_depth_m": 0.5, "color": "#1e4f86"}],
        "images": {"100": "depth_rp100.png"},
    }
    (overlay_dir / "overlays.json").write_text(json.dumps(manifest), encoding="utf-8")
    water = {"type": "MultiPolygon", "coordinates": [[[[90.4, 23.7], [90.41, 23.7], [90.41, 23.71], [90.4, 23.7]]]]}
    (overlay_dir / "context.json").write_text(json.dumps({"label": "Test water", "water": water}), encoding="utf-8")


def api_settings(database_url: str, schema_name: str, overlay_dir: Path) -> Settings:
    scoped_url = make_conninfo(database_url, options=f"-c search_path={schema_name}")
    return load_settings(scoped_url).model_copy(update={"overlay_dir": overlay_dir, "focus_neighborhood": "One"})
