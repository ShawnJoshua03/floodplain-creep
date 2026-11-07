import numpy as np

from pipeline.lib.blocks import aggregate_blocks

NODATA = -99.0


def test_count_is_summed_and_height_is_max() -> None:
    pixels = np.zeros((3, 4, 4), dtype=np.float32)
    pixels[0, 0, 0] = 0.5
    pixels[0, 1, 1] = 0.25
    pixels[1, 0, 1] = 7.0
    pixels[2, 1, 0] = 0.9
    out = aggregate_blocks(pixels, 2, NODATA)
    assert out.shape == (3, 2, 2)
    assert out[0, 0, 0] == 0.75
    assert out[1, 0, 0] == 7.0
    assert np.isclose(out[2, 0, 0], 0.9)


def test_total_count_is_preserved() -> None:
    rng = np.random.default_rng(1)
    pixels = rng.random((3, 16, 16), dtype=np.float32)
    out = aggregate_blocks(pixels, 4, NODATA)
    assert np.isclose(out[0].sum(), pixels[0].sum(), rtol=1e-5)


def test_nodata_pixels_are_ignored_and_all_nodata_block_stays_nodata() -> None:
    pixels = np.full((3, 4, 4), NODATA, dtype=np.float32)
    pixels[:, 0, 0] = [1.0, 3.0, 0.5]
    out = aggregate_blocks(pixels, 2, NODATA)
    assert out[0, 0, 0] == 1.0
    assert out[1, 0, 0] == 3.0
    assert out[0, 1, 1] == NODATA
    assert out[2, 1, 1] == NODATA


def test_shape_must_divide_by_factor() -> None:
    try:
        aggregate_blocks(np.zeros((3, 5, 4), dtype=np.float32), 2, NODATA)
    except ValueError as error:
        assert "multiple of factor" in str(error)
    else:
        raise AssertionError("expected ValueError")
