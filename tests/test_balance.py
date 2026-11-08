from pathlib import Path

import numpy as np
import psycopg
import pytest

from pipeline.io.balance_csv import read_balance_csv, write_balance_csv
from pipeline.io.database import load_neighborhoods, replace_balance
from pipeline.lib.balance import RawBalance, balance_counts
from pipeline.lib.suppression import BalanceRow, suppress_balance
from tests.test_database import write_geojson

K = 20


def small_grid() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Two neighborhoods side by side on a 1 by 6 grid, one scenario, two years."""
    labels = np.array([[1, 1, 1, 2, 2, 0]], dtype=np.int32)
    counts = np.zeros((2, 1, 6))
    counts[1] = [[6.0, -7.0, 1.0, 5.0, 0.0, 99.0]]
    flooded = np.ones((1, 1, 6), dtype=np.bool_)
    return counts, flooded, labels


def test_cells_are_counted_as_gaining_or_losing_by_the_threshold() -> None:
    counts, flooded, labels = small_grid()
    result = balance_counts(counts, flooded, labels, ["a", "b"], [100], threshold=5)
    by_id = {item.neighborhood_id: item for item in result}
    assert (by_id["a"].cells_in_zone, by_id["a"].cells_gaining, by_id["a"].cells_losing) == (3, 1, 1)
    assert (by_id["b"].cells_in_zone, by_id["b"].cells_gaining, by_id["b"].cells_losing) == (2, 1, 0)


def test_study_area_row_leaves_out_cells_outside_every_neighborhood() -> None:
    counts, flooded, labels = small_grid()
    study_area = [r for r in balance_counts(counts, flooded, labels, ["a", "b"], [100], 5) if r.neighborhood_id is None]
    assert study_area == [RawBalance(None, 100, 5, 2, 1)]


def test_cells_outside_the_flood_zone_are_not_counted() -> None:
    counts, _, labels = small_grid()
    dry = np.zeros((1, 1, 6), dtype=np.bool_)
    result = balance_counts(counts, dry, labels, ["a", "b"], [100], 5)
    assert all(item.cells_in_zone == 0 for item in result)


def test_small_neighborhood_shows_no_cell_counts() -> None:
    raw = [RawBalance("a", 100, K - 1, 5, 2), RawBalance("b", 100, K, 5, 2), RawBalance(None, 100, 3, 1, 1)]
    a, b, area = suppress_balance(raw, K)
    assert a.suppressed and a.cells_in_zone is None and a.cells_gaining is None and a.cells_losing is None
    assert not b.suppressed and b.cells_in_zone == K
    assert not area.suppressed and area.cells_in_zone == 3


def test_csv_round_trip(tmp_path: Path) -> None:
    rows = [
        BalanceRow("a", 100, 30, 10, 5, False),
        BalanceRow("b", 100, None, None, None, True),
        BalanceRow(None, 100, 60, 20, 10, False),
    ]
    write_balance_csv(tmp_path / "balance.csv", rows)
    assert read_balance_csv(tmp_path / "balance.csv") == rows


def test_every_stored_balance_row_follows_the_k_rule(conn: psycopg.Connection, tmp_path: Path) -> None:
    write_geojson(tmp_path / "n.geojson")
    load_neighborhoods(conn, tmp_path / "n.geojson")
    raw = [RawBalance("n1", 100, 50, 20, 5), RawBalance("n2", 100, 4, 2, 1), RawBalance(None, 100, 54, 22, 6)]
    replace_balance(conn, suppress_balance(raw, K))
    conn.commit()
    stored = conn.execute(
        "SELECT neighborhood_id, cells_in_zone, cells_gaining, cells_losing, suppressed"
        " FROM neighborhood_change_balance"
    ).fetchall()
    assert len(stored) == 3
    for area, cells, gaining, losing, suppressed in stored:
        if suppressed:
            assert cells is None and gaining is None and losing is None
        elif area is not None:
            assert cells is not None and cells >= K


def test_database_rejects_a_suppressed_balance_row_with_counts(conn: psycopg.Connection, tmp_path: Path) -> None:
    write_geojson(tmp_path / "n.geojson")
    load_neighborhoods(conn, tmp_path / "n.geojson")
    with pytest.raises(psycopg.errors.CheckViolation):
        replace_balance(conn, [BalanceRow("n1", 100, 5, 1, 1, True)])


def test_database_rejects_a_suppressed_study_area_row(conn: psycopg.Connection) -> None:
    with pytest.raises(psycopg.errors.CheckViolation):
        replace_balance(conn, [BalanceRow(None, 100, None, None, None, True)])
