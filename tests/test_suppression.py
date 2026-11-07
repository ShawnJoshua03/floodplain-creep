import numpy as np
import pytest

from pipeline.lib.aggregation import ZoneTotal, zone_totals
from pipeline.lib.suppression import ExposureRow, apply_suppression, check_rows

K = 20


def total(year: int, value: float, name: str = "a", return_period: int = 100) -> ZoneTotal:
    return ZoneTotal(name, year, return_period, value)


def test_small_count_is_suppressed_with_null_counts() -> None:
    rows = apply_suppression([total(2016, 30), total(2017, 19.4)], K, 2016)
    small = rows[1]
    assert small.suppressed
    assert small.buildings_in_zone is None
    assert small.new_buildings_in_zone is None
    assert small.growth_pct is None
    assert not small.change_available


def test_count_at_k_is_shown() -> None:
    rows = apply_suppression([total(2016, 20), total(2017, 20)], K, 2016)
    assert [r.suppressed for r in rows] == [False, False]
    assert rows[1].buildings_in_zone == 20


def test_change_uses_baseline_when_baseline_is_large_enough() -> None:
    rows = apply_suppression([total(2016, 100), total(2023, 150)], K, 2016)
    last = rows[1]
    assert last.new_buildings_in_zone == 50
    assert last.growth_pct == 50.0
    assert last.change_available


def test_change_is_hidden_when_baseline_is_below_k() -> None:
    rows = apply_suppression([total(2016, 5), total(2023, 90)], K, 2016)
    assert rows[0].suppressed
    last = rows[1]
    assert not last.suppressed
    assert last.buildings_in_zone == 90
    assert last.new_buildings_in_zone is None
    assert last.growth_pct is None
    assert not last.change_available


def test_check_rows_accepts_output_of_apply_suppression() -> None:
    totals = [total(2016, 5), total(2023, 90), total(2016, 50, "b"), total(2023, 60, "b")]
    check_rows(apply_suppression(totals, K, 2016), K)


def test_check_rows_rejects_suppressed_row_with_counts() -> None:
    bad = ExposureRow("a", 2020, 100, 3, None, None, True, False)
    with pytest.raises(ValueError, match="Suppressed row has counts"):
        check_rows([bad], K)


def test_check_rows_rejects_shown_row_below_k() -> None:
    bad = ExposureRow("a", 2020, 100, 3, None, None, False, False)
    with pytest.raises(ValueError, match="below K"):
        check_rows([bad], K)


def test_check_rows_rejects_change_without_baseline() -> None:
    bad = ExposureRow("a", 2020, 100, 30, 10, 5.0, False, False)
    with pytest.raises(ValueError, match="without a usable baseline"):
        check_rows([bad], K)


def test_zone_totals_sum_only_flooded_cells_per_neighborhood() -> None:
    counts = np.array([[[1.0, 2.0], [3.0, 4.0]], [[2.0, 2.0], [3.0, 8.0]]])
    flooded = np.array([[[True, False], [True, True]]])
    labels = np.array([[1, 1], [2, 0]], dtype=np.int32)
    result = zone_totals(counts, flooded, labels, ["a", "b"], [2016, 2017], [100])
    by_key = {(t.neighborhood_id, t.year): t.buildings_in_zone for t in result}
    assert by_key == {("a", 2016): 1.0, ("b", 2016): 3.0, ("a", 2017): 2.0, ("b", 2017): 3.0}
