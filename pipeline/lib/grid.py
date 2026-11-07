"""Common analysis grid: align fine rasters to square cells and sum into them."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class GridDef:
    left: float
    top: float
    cell_m: float
    rows: int
    cols: int
    crs: str


def masked_counts(
    count: npt.NDArray[np.float32],
    presence: npt.NDArray[np.float32],
    nodata: float,
    presence_min: float,
) -> npt.NDArray[np.float32]:
    """Keep fractional counts only where presence confidence reaches the threshold."""
    keep = (count != nodata) & (presence != nodata) & (presence >= presence_min)
    return np.where(keep, count, 0.0).astype(np.float32)


@dataclass(frozen=True)
class RasterFrame:
    """Position and size of a raster: origin is the top-left corner."""

    left: float
    top: float
    rows: int
    cols: int
    pixel_m: float


def grid_for_raster(frame: RasterFrame, cell_m: float, crs: str) -> GridDef:
    """Smallest cell grid that covers the raster."""
    grid_left = math.floor(frame.left / cell_m) * cell_m
    grid_top = math.ceil(frame.top / cell_m) * cell_m
    width_m = frame.left - grid_left + frame.cols * frame.pixel_m
    height_m = grid_top - frame.top + frame.rows * frame.pixel_m
    return GridDef(grid_left, grid_top, cell_m, math.ceil(height_m / cell_m), math.ceil(width_m / cell_m), crs)


def sum_to_cells(values: npt.NDArray[np.float32], frame: RasterFrame, grid: GridDef) -> npt.NDArray[np.float64]:
    """Sum raster pixels into grid cells. The raster must align to the grid in whole pixels."""
    factor = round(grid.cell_m / frame.pixel_m)
    pad_left = round((frame.left - grid.left) / frame.pixel_m)
    pad_top = round((grid.top - frame.top) / frame.pixel_m)
    off_left = abs(pad_left * frame.pixel_m - (frame.left - grid.left))
    off_top = abs(pad_top * frame.pixel_m - (grid.top - frame.top))
    if off_left > 1e-6 or off_top > 1e-6:
        raise ValueError("Raster origin does not fall on a whole pixel of the grid")
    full = np.zeros((grid.rows * factor, grid.cols * factor), dtype=np.float64)
    full[pad_top : pad_top + frame.rows, pad_left : pad_left + frame.cols] = values
    return full.reshape(grid.rows, factor, grid.cols, factor).sum(axis=(1, 3))
