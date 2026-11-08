import numpy as np

from pipeline.lib.density import block_sums, colorize_growth, growth_bins
from pipeline.lib.suppression import suppress_blocks


def test_block_sums_count_only_flooded_cells() -> None:
    counts = np.ones((4, 4))
    flooded = np.zeros((4, 4), dtype=bool)
    flooded[:2, :2] = True
    sums = block_sums(counts, flooded, 2)
    assert sums.tolist() == [[4.0, 0.0], [0.0, 0.0]]


def test_blocks_under_k_are_hidden() -> None:
    shown = suppress_blocks(np.array([[19.4, 19.6], [20.0, 80.0]]), 20)
    assert shown.tolist() == [[False, True], [True, True]]


def test_bins_rise_and_hidden_pixels_stay_transparent() -> None:
    bins = growth_bins(np.array([20.0, 25.0, 40.0, 90.0, 300.0]), 20)
    lows = [spec.min_buildings for spec in bins]
    assert lows == sorted(set(lows))
    value = np.array([[30.0, 500.0]], dtype=np.float32)
    image = colorize_growth(value, np.array([[False, True]]), bins)
    assert image[0, 0, 3] == 0
    assert image[0, 1, 3] > 0
