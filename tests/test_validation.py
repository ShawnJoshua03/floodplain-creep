import numpy as np
import pytest

from pipeline.lib.sampling import FLAGGED, RANDOM, SampleDesign, draw_sample, flagged_pool_size
from pipeline.lib.validation_metrics import (
    Confusion,
    LabeledCell,
    accuracy,
    confusion,
    precision,
    recall,
    split_labeled,
    tune_threshold,
    wilson,
)


def cell(index: int, label: str, change: float) -> LabeledCell:
    return LabeledCell(f"c{index}", label, change)


def test_wilson_matches_known_value() -> None:
    low, high = wilson(8, 10)
    assert low == pytest.approx(0.4902, abs=1e-3)
    assert high == pytest.approx(0.9433, abs=1e-3)


def test_wilson_needs_observations() -> None:
    with pytest.raises(ValueError, match="at least one"):
        wilson(0, 0)


def test_confusion_and_metrics() -> None:
    cells = [
        cell(1, "increase", 10.0),
        cell(2, "increase", 1.0),
        cell(3, "no_clear_change", 9.0),
        cell(4, "decrease", -3.0),
        cell(5, "no_clear_change", 0.0),
    ]
    c = confusion(cells, 5.0)
    assert c == Confusion(tp=1, fp=1, fn=1, tn=2)
    assert accuracy(c).value == pytest.approx(0.6)
    assert precision(c).value == pytest.approx(0.5)
    assert recall(c).value == pytest.approx(0.5)


def test_precision_is_none_when_nothing_is_predicted() -> None:
    c = Confusion(tp=0, fp=0, fn=3, tn=2)
    assert precision(c).value is None
    assert precision(c).n == 0


def test_tune_threshold_separates_classes() -> None:
    cells = [cell(i, "increase", 10.0 + i) for i in range(5)] + [
        cell(9 + i, "no_clear_change", float(i)) for i in range(5)
    ]
    assert tune_threshold(cells) == 10.0


def test_tune_threshold_needs_positives() -> None:
    with pytest.raises(ValueError, match="no increases"):
        tune_threshold([cell(1, "no_clear_change", 1.0)])


def test_split_is_sixty_forty_in_order() -> None:
    cells = [cell(i, "increase", 1.0) for i in range(10)]
    tune, test = split_labeled(cells)
    assert [c.cell_id for c in tune] == [f"c{i}" for i in range(6)]
    assert len(test) == 4


def sample_inputs() -> tuple[np.ndarray, np.ndarray]:
    eligible = np.ones((20, 20), dtype=np.bool_)
    change = np.arange(400, dtype=np.float64).reshape(20, 20)
    return eligible, change


def test_sample_has_expected_counts_and_no_duplicates() -> None:
    eligible, change = sample_inputs()
    design = SampleDesign(n_random=30, n_flagged=10, flag_threshold=300.0, seed=1)
    cells = draw_sample(eligible, change, design)
    assert len(cells) == 40
    assert len({c.cell_id for c in cells}) == 40
    assert sum(c.sample_type == RANDOM for c in cells) == 30
    flagged = [c for c in cells if c.sample_type == FLAGGED]
    assert len(flagged) == 10
    assert all(c.change >= 300.0 for c in flagged)


def test_sample_is_repeatable_and_shuffled() -> None:
    eligible, change = sample_inputs()
    design = SampleDesign(30, 10, 300.0, 7)
    first = draw_sample(eligible, change, design)
    assert first == draw_sample(eligible, change, design)
    types = [c.sample_type for c in first]
    assert types != sorted(types)


def test_sample_only_uses_eligible_cells() -> None:
    eligible, change = sample_inputs()
    eligible[:, 10:] = False
    cells = draw_sample(eligible, change, SampleDesign(20, 5, 100.0, 3))
    assert all(c.col < 10 for c in cells)


def test_sample_fails_when_pool_too_small() -> None:
    eligible, change = sample_inputs()
    with pytest.raises(ValueError, match="flagged cells left"):
        draw_sample(eligible, change, SampleDesign(10, 50, 395.0, 1))
    assert flagged_pool_size(eligible, change, 395.0) == 5
