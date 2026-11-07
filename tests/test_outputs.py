import csv
from pathlib import Path

import numpy as np

from pipeline.io.cell_store import CellStore, load_cells, save_cells
from pipeline.io.exposure_csv import COLUMNS, write_exposure_csv
from pipeline.lib.aggregation import ZoneTotal
from pipeline.lib.grid import GridDef
from pipeline.lib.suppression import apply_suppression, check_rows

K = 20
CELL_LEVEL_WORDS = ("cell", "row", "col", "lat", "lon", "x", "y", "geometry")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_csv_has_only_neighborhood_level_columns(tmp_path: Path) -> None:
    for column in COLUMNS:
        assert not any(word in column.split("_") for word in CELL_LEVEL_WORDS), column
    totals = [ZoneTotal("n1", 2016, 100, 50.0), ZoneTotal("n1", 2017, 100, 10.0)]
    path = tmp_path / "out.csv"
    write_exposure_csv(path, apply_suppression(totals, K, 2016))
    assert list(read_rows(path)[0]) == COLUMNS


def test_suppressed_rows_have_empty_counts_in_csv(tmp_path: Path) -> None:
    totals = [
        ZoneTotal("n1", 2016, 100, 50.0),
        ZoneTotal("n1", 2017, 100, 10.0),
        ZoneTotal("n2", 2016, 100, 3.0),
        ZoneTotal("n2", 2017, 100, 80.0),
    ]
    rows = apply_suppression(totals, K, 2016)
    check_rows(rows, K)
    path = tmp_path / "out.csv"
    write_exposure_csv(path, rows)
    for record in read_rows(path):
        if record["suppressed"] == "true":
            assert record["buildings_in_zone"] == ""
            assert record["new_buildings_in_zone"] == ""
            assert record["growth_pct"] == ""
        else:
            assert int(record["buildings_in_zone"]) >= K
    by_key = {(r["neighborhood_id"], r["year"]): r for r in read_rows(path)}
    assert by_key[("n2", "2017")]["new_buildings_in_zone"] == ""
    assert by_key[("n1", "2017")]["suppressed"] == "true"


def test_cell_store_round_trip(tmp_path: Path) -> None:
    grid = GridDef(100.0, 300.0, 100.0, 2, 3, "EPSG:32646")
    counts = np.arange(2 * 2 * 3, dtype=np.float64).reshape(2, 2, 3)
    flooded = np.zeros((1, 2, 3), dtype=np.bool_)
    flooded[0, 1, 2] = True
    path = tmp_path / "cells.npz"
    save_cells(path, CellStore(grid, [2016, 2017], [100], counts, flooded))
    loaded = load_cells(path)
    assert loaded.grid == grid
    assert loaded.years == [2016, 2017]
    assert loaded.return_periods == [100]
    assert np.array_equal(loaded.counts, counts)
    assert np.array_equal(loaded.flooded, flooded)
