"""Resample JRC flood rasters (WGS84, ~90 m) onto the 100 m analysis grid."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import numpy.typing as npt
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject

from pipeline.lib.grid import GridDef

DEPTH_NODATA = -9999.0
MASK_NODATA = 255


def reproject_to_grid(
    path: Path, grid: GridDef, dtype: str, nodata: float
) -> npt.NDArray[np.float32] | npt.NDArray[np.uint8]:
    """Take the maximum of source pixels falling in each cell, so thin flooded strips are kept."""
    destination = np.full((grid.rows, grid.cols), nodata, dtype=dtype)
    transform = from_origin(grid.left, grid.top, grid.cell_m, grid.cell_m)
    with rasterio.open(path) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            dst_transform=transform,
            dst_crs=grid.crs,
            dst_nodata=nodata,
            src_nodata=src.nodata,
            resampling=Resampling.max,
        )
    return destination


def depth_on_grid(path: Path, grid: GridDef) -> npt.NDArray[np.float32]:
    return np.asarray(reproject_to_grid(path, grid, "float32", DEPTH_NODATA), dtype=np.float32)


def mask_on_grid(path: Path, grid: GridDef) -> npt.NDArray[np.uint8]:
    return np.asarray(reproject_to_grid(path, grid, "uint8", MASK_NODATA), dtype=np.uint8)
