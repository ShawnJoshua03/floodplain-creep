"""Give each grid cell a neighborhood number."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import numpy.typing as npt
from rasterio.features import rasterize
from rasterio.transform import from_origin
from shapely.geometry.base import BaseGeometry

from pipeline.lib.grid import GridDef


def rasterize_neighborhoods(geometries: Sequence[BaseGeometry], grid: GridDef) -> npt.NDArray[np.int32]:
    """Cell value is 1 + index of the geometry containing the cell centre, 0 when none does."""
    if not geometries:
        return np.zeros((grid.rows, grid.cols), dtype=np.int32)
    shapes = [(geometry, index + 1) for index, geometry in enumerate(geometries)]
    transform = from_origin(grid.left, grid.top, grid.cell_m, grid.cell_m)
    labels = rasterize(shapes, out_shape=(grid.rows, grid.cols), transform=transform, fill=0, dtype="int32")
    return np.asarray(labels, dtype=np.int32)
