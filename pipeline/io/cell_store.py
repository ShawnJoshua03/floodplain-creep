"""Cell-level working file. It lives in data/processed/ only and never goes to the database."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt

from pipeline.lib.grid import GridDef


@dataclass(frozen=True)
class CellStore:
    grid: GridDef
    years: list[int]
    return_periods: list[int]
    counts: npt.NDArray[np.float64]
    flooded: npt.NDArray[np.bool_]


def save_cells(path: Path, store: CellStore) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    grid = store.grid
    np.savez_compressed(
        path,
        counts=store.counts,
        flooded=store.flooded,
        years=np.array(store.years),
        return_periods=np.array(store.return_periods),
        geometry=np.array([grid.left, grid.top, grid.cell_m, grid.rows, grid.cols]),
        crs=np.array(grid.crs),
    )


def load_cells(path: Path) -> CellStore:
    with np.load(path) as data:
        left, top, cell_m, rows, cols = (float(v) for v in data["geometry"])
        grid = GridDef(left, top, cell_m, int(rows), int(cols), str(data["crs"]))
        return CellStore(
            grid=grid,
            years=[int(y) for y in data["years"]],
            return_periods=[int(r) for r in data["return_periods"]],
            counts=np.asarray(data["counts"], dtype=np.float64),
            flooded=np.asarray(data["flooded"], dtype=np.bool_),
        )
