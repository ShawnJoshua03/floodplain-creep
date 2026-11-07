import numpy as np
import pytest
from shapely.geometry import box

from pipeline.lib.exposure import flood_zone
from pipeline.lib.grid import GridDef, RasterFrame, grid_for_raster, masked_counts, sum_to_cells
from pipeline.lib.labels import rasterize_neighborhoods

NODATA = -99.0


def test_grid_covers_raster_and_sums_to_cells() -> None:
    frame = RasterFrame(left=104.0, top=196.0, rows=50, cols=50, pixel_m=4.0)
    grid = grid_for_raster(frame, 100.0, "EPSG:32646")
    assert (grid.left, grid.top) == (100.0, 200.0)
    assert (grid.rows, grid.cols) == (3, 3)
    values = np.ones((50, 50), dtype=np.float32)
    cells = sum_to_cells(values, frame, grid)
    assert cells.shape == (3, 3)
    assert cells.sum() == 2500
    assert cells[0, 0] == 24 * 24


def test_misaligned_origin_is_rejected() -> None:
    grid = GridDef(0.0, 200.0, 100.0, 2, 2, "EPSG:32646")
    frame = RasterFrame(left=1.0, top=200.0, rows=10, cols=10, pixel_m=4.0)
    with pytest.raises(ValueError, match="whole pixel"):
        sum_to_cells(np.ones((10, 10), dtype=np.float32), frame, grid)


def test_masked_counts_drop_low_presence_and_nodata() -> None:
    count = np.array([[1.0, 1.0, NODATA, 1.0]], dtype=np.float32)
    presence = np.array([[0.9, 0.2, 0.9, NODATA]], dtype=np.float32)
    assert masked_counts(count, presence, NODATA, 0.45).tolist() == [[1.0, 0.0, 0.0, 0.0]]


def test_flood_zone_excludes_permanent_water_and_spurious_depth() -> None:
    depth = np.array([[0.05, 0.2, 0.5, 0.6, -9999.0]], dtype=np.float32)
    water = np.array([[255, 255, 1, 255, 255]], dtype=np.uint8)
    spurious = np.array([[255, 255, 255, 1, 255]], dtype=np.uint8)
    zone = flood_zone(depth, water, spurious, -9999.0, 255, 0.1)
    assert zone.tolist() == [[False, True, False, False, False]]


def test_rasterize_labels_use_cell_centres() -> None:
    grid = GridDef(0.0, 200.0, 100.0, 2, 2, "EPSG:32646")
    left_half = box(0, 0, 100, 200)
    labels = rasterize_neighborhoods([left_half], grid)
    assert labels.tolist() == [[1, 0], [1, 0]]
