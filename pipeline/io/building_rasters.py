"""Build one yearly building raster by streaming source tiles and summing to a coarser grid."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import rasterio

from pipeline.io.rasters import read_strip
from pipeline.lib.blocks import aggregate_blocks
from pipeline.lib.tiles import SOURCE_PIXEL_M, Bounds, TileRef, overlap, pixel_window

NODATA = -99.0
STRIP_ROWS = 512


def build_year_raster(tiles: list[TileRef], area: Bounds, factor: int) -> npt.NDArray[np.float32]:
    """Return (3, rows, cols) at pixel size SOURCE_PIXEL_M * factor covering `area`."""
    pixel_m = SOURCE_PIXEL_M * factor
    cols = round((area.right - area.left) / pixel_m)
    rows = round((area.top - area.bottom) / pixel_m)
    out = np.full((3, rows, cols), NODATA, dtype=np.float32)
    for tile in tiles:
        fill_from_tile(out, tile, area, factor)
    return out


def fill_from_tile(out: npt.NDArray[np.float32], tile: TileRef, area: Bounds, factor: int) -> None:
    pixel_m = SOURCE_PIXEL_M * factor
    shared = overlap(tile.bounds, area)
    col_off, row_off, width, height = pixel_window(tile.bounds, shared, SOURCE_PIXEL_M)
    out_col = round((shared.left - area.left) / pixel_m)
    out_row = round((area.top - shared.top) / pixel_m)
    with rasterio.open("/vsicurl/" + tile.url) as src:
        for start in range(0, height, STRIP_ROWS):
            rows = min(STRIP_ROWS, height - start)
            strip = read_strip(src, col_off, row_off + start, width, rows)
            small = aggregate_blocks(strip, factor, NODATA)
            r0 = out_row + start // factor
            out[:, r0 : r0 + small.shape[1], out_col : out_col + small.shape[2]] = small
