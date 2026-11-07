from pathlib import Path

import numpy as np

from pipeline.io.rasters import GridSpec, describe_raster, write_raster
from pipeline.lib.summary import format_summary


def test_write_then_describe_round_trip(tmp_path: Path) -> None:
    pixels = np.full((3, 4, 5), -99.0, dtype=np.float32)
    pixels[0, 1, 1] = 2.5
    pixels[1, 1, 1] = 9.0
    pixels[2, 1, 1] = 0.8
    path = tmp_path / "grid.tif"
    grid = GridSpec((500000.0, 9860000.0), 4.0, "EPSG:32737", -99.0)
    write_raster(path, pixels, grid, ["count", "height", "presence"])
    summary = describe_raster(path, "test")
    assert summary.shape == (4, 5)
    assert summary.crs == "EPSG:32737"
    assert summary.resolution == (4.0, 4.0)
    assert [b.name for b in summary.bands] == ["count", "height", "presence"]
    assert summary.bands[0].minimum == 2.5
    assert summary.bands[1].maximum == 9.0
    assert summary.bands[0].valid_pixels == 1
    assert "shape=4x5" in format_summary(summary)
