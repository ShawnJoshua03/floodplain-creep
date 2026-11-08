"""Shared setup for API tests: a seeded schema, settings, and overlay files."""

from __future__ import annotations

import json
from pathlib import Path

import psycopg
from psycopg.conninfo import make_conninfo

from api.core.settings import Settings, load_settings
from pipeline.io.database import add_validation_result, load_neighborhoods, replace_exposure
from pipeline.lib.aggregation import ZoneTotal
from pipeline.lib.suppression import apply_suppression
from tests.test_database import write_geojson

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


def seed_database(conn: psycopg.Connection, tmp_path: Path, k: int) -> None:
    """Neighborhood n1 stays above K in both years. Neighborhood n2 stays below K."""
    totals = [
        ZoneTotal("n1", 2018, 100, 80.0),
        ZoneTotal("n1", 2023, 100, 120.0),
        ZoneTotal("n2", 2018, 100, 4.0),
        ZoneTotal("n2", 2023, 100, 6.0),
    ]
    write_geojson(tmp_path / "n.geojson")
    load_neighborhoods(conn, tmp_path / "n.geojson")
    replace_exposure(conn, apply_suppression(totals, k, 2018))
    add_validation_result(conn, VALIDATION_PAYLOAD)
    conn.commit()


def write_overlay_files(overlay_dir: Path) -> None:
    overlay_dir.mkdir(parents=True, exist_ok=True)
    (overlay_dir / "depth_rp100.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    manifest = {
        "bounds": [90.34, 23.69, 90.47, 23.82],
        "bins": [{"min_depth_m": 0.1, "max_depth_m": 0.5, "color": "#9ecae1"}],
        "images": {"100": "depth_rp100.png"},
    }
    (overlay_dir / "overlays.json").write_text(json.dumps(manifest), encoding="utf-8")


def api_settings(database_url: str, schema_name: str, overlay_dir: Path) -> Settings:
    scoped_url = make_conninfo(database_url, options=f"-c search_path={schema_name}")
    return load_settings(scoped_url).model_copy(update={"overlay_dir": overlay_dir})
