"""Neighborhoods kept for the grid, and the cell-to-neighborhood label raster."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from pipeline.io.boundaries import BoundaryLoad, load_neighborhoods
from pipeline.io.cell_store import CellStore
from pipeline.io.city_config import ROOT, CityConfig
from pipeline.lib.labels import rasterize_neighborhoods

BOUNDARIES = ROOT / "data" / "raw" / "boundaries" / "adm3.geojson"


@dataclass(frozen=True)
class NeighborhoodLabels:
    loaded: BoundaryLoad
    labels: npt.NDArray[np.int32]


def load_labels(config: CityConfig, store: CellStore) -> NeighborhoodLabels:
    loaded = load_neighborhoods(BOUNDARIES, config.lonlat_bounds, store.grid.crs, config.min_coverage)
    labels = rasterize_neighborhoods([n.geometry for n in loaded.kept], store.grid)
    return NeighborhoodLabels(loaded, labels)
