import json
import re
from pathlib import Path

import psycopg
import pytest

from pipeline.io.city_config import load_city_config
from pipeline.io.database import (
    add_validation_result,
    load_neighborhoods,
    replace_exposure,
)
from pipeline.io.exposure_csv import read_exposure_csv, write_exposure_csv
from pipeline.lib.aggregation import ZoneTotal
from pipeline.lib.suppression import ExposureRow, apply_suppression

CELL_LEVEL_WORDS = {"cell", "row", "col", "lat", "lon", "latitude", "longitude", "x", "y"}


def write_geojson(path: Path) -> None:
    feature = {
        "type": "Feature",
        "properties": {"neighborhood_id": "n1", "name": "One", "coverage": 0.9, "boundary_source": "test"},
        "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
    }
    second = json.loads(json.dumps(feature))
    second["properties"].update({"neighborhood_id": "n2", "name": "Two"})
    path.write_text(json.dumps({"type": "FeatureCollection", "features": [feature, second]}), encoding="utf-8")


def sample_rows(k: int) -> list[ExposureRow]:
    totals = [
        ZoneTotal("n1", 2016, 100, 80.0),
        ZoneTotal("n1", 2017, 100, 120.0),
        ZoneTotal("n2", 2016, 100, 4.0),
        ZoneTotal("n2", 2017, 100, 60.0),
    ]
    return apply_suppression(totals, k, 2016)


def fill(conn: psycopg.Connection, tmp_path: Path, rows: list[ExposureRow]) -> None:
    write_geojson(tmp_path / "n.geojson")
    load_neighborhoods(conn, tmp_path / "n.geojson")
    replace_exposure(conn, rows)
    conn.commit()


def test_every_stored_row_follows_the_k_rule(conn: psycopg.Connection, tmp_path: Path) -> None:
    k = load_city_config().min_count_k
    fill(conn, tmp_path, sample_rows(k))
    stored = conn.execute(
        "SELECT buildings_in_zone, new_buildings_in_zone, growth_pct, suppressed FROM neighborhood_year_exposure"
    ).fetchall()
    assert len(stored) == 4
    for stock, new, growth, suppressed in stored:
        if suppressed:
            assert stock is None and new is None and growth is None
        else:
            assert stock is not None and stock >= k


def test_database_rejects_a_suppressed_row_with_counts(conn: psycopg.Connection, tmp_path: Path) -> None:
    write_geojson(tmp_path / "n.geojson")
    load_neighborhoods(conn, tmp_path / "n.geojson")
    bad = ExposureRow("n1", 2020, 100, 5, None, None, True, False)
    with pytest.raises(psycopg.errors.CheckViolation):
        replace_exposure(conn, [bad])


def test_database_rejects_change_without_baseline(conn: psycopg.Connection, tmp_path: Path) -> None:
    write_geojson(tmp_path / "n.geojson")
    load_neighborhoods(conn, tmp_path / "n.geojson")
    bad = ExposureRow("n1", 2020, 100, 50, 10, 5.0, False, False)
    with pytest.raises(psycopg.errors.CheckViolation):
        replace_exposure(conn, [bad])


def test_reload_replaces_rows(conn: psycopg.Connection, tmp_path: Path) -> None:
    k = load_city_config().min_count_k
    fill(conn, tmp_path, sample_rows(k))
    fill(conn, tmp_path, sample_rows(k))
    count = conn.execute("SELECT count(*) FROM neighborhood_year_exposure").fetchone()
    assert count == (4,)
    neighborhoods = conn.execute("SELECT count(*) FROM neighborhoods").fetchone()
    assert neighborhoods == (2,)


def test_csv_round_trip_into_database(conn: psycopg.Connection, tmp_path: Path) -> None:
    k = load_city_config().min_count_k
    path = tmp_path / "rows.csv"
    write_exposure_csv(path, sample_rows(k))
    rows = read_exposure_csv(path)
    assert rows == [
        ExposureRow(
            r.neighborhood_id,
            r.year,
            r.return_period,
            r.buildings_in_zone,
            r.new_buildings_in_zone,
            None if r.growth_pct is None else round(r.growth_pct, 1),
            r.suppressed,
            r.change_available,
        )
        for r in sample_rows(k)
    ]
    fill(conn, tmp_path, rows)


def test_validation_result_is_stored(conn: psycopg.Connection) -> None:
    add_validation_result(conn, {"accuracy": {"value": 0.8}})
    conn.commit()
    stored = conn.execute("SELECT payload ->> 'accuracy' FROM validation_result").fetchone()
    assert stored is not None and "0.8" in stored[0]


def test_no_table_holds_cell_level_columns(conn: psycopg.Connection) -> None:
    schema = conn.execute("SELECT current_schema()").fetchone()
    assert schema is not None
    found = conn.execute(
        "SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = %s", (schema[0],)
    ).fetchall()
    assert {t for t, _ in found} == {"neighborhoods", "neighborhood_year_exposure", "validation_result", "briefs"}
    for table, column in found:
        assert not CELL_LEVEL_WORDS.intersection(re.split(r"_", column)), (table, column)
