"""Build the 100 m cell file: yearly building counts and flood zone per return period.

Run: uv run python -m pipeline.steps.build_grid
Needs the outputs of fetch_buildings and fetch_flood. Cell data stays in data/processed/.
"""

from __future__ import annotations

import numpy as np

from pipeline.io.cell_store import CellStore, save_cells
from pipeline.io.city_config import ROOT, load_city_config
from pipeline.io.flood_grid import DEPTH_NODATA, MASK_NODATA, depth_on_grid, mask_on_grid
from pipeline.io.rasters import read_building_year
from pipeline.lib.exposure import flood_zone
from pipeline.lib.grid import grid_for_raster, masked_counts, sum_to_cells

BUILDINGS = ROOT / "data" / "raw" / "buildings"
FLOOD = ROOT / "data" / "raw" / "flood"
OUTPUT = ROOT / "data" / "processed" / "cells.npz"


def find_flood_file(suffix: str) -> str:
    matches = sorted(FLOOD.glob(f"ID*_{suffix}.tif"))
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one flood file ending _{suffix}.tif in {FLOOD}, found {len(matches)}")
    return matches[0].name


def main() -> None:
    config = load_city_config()
    years = list(config.year_range)
    first = read_building_year(BUILDINGS / f"buildings_{years[0]}.tif")
    grid = grid_for_raster(first.frame, config.grid_size_m, first.crs)
    counts = np.zeros((len(years), grid.rows, grid.cols), dtype=np.float64)
    for index, year in enumerate(years):
        layer = read_building_year(BUILDINGS / f"buildings_{year}.tif")
        if layer.frame != first.frame:
            raise ValueError(f"Building raster for {year} does not match the {years[0]} grid")
        kept = masked_counts(layer.count, layer.presence, layer.nodata, config.presence_threshold)
        counts[index] = sum_to_cells(kept, layer.frame, grid)
        print(f"{year}: {counts[index].sum():.0f} buildings in {grid.rows}x{grid.cols} cells")
    water = mask_on_grid(FLOOD / find_flood_file("permanent_water"), grid)
    spurious = mask_on_grid(FLOOD / find_flood_file("spurious_depth_areas"), grid)
    flooded = np.zeros((len(config.return_periods), grid.rows, grid.cols), dtype=np.bool_)
    for index, return_period in enumerate(config.return_periods):
        depth = depth_on_grid(FLOOD / find_flood_file(f"RP{return_period}_depth"), grid)
        flooded[index] = flood_zone(depth, water, spurious, DEPTH_NODATA, MASK_NODATA, config.min_depth_m)
        print(f"RP{return_period}: {int(flooded[index].sum())} flood-zone cells")
    save_cells(OUTPUT, CellStore(grid, years, config.return_periods, counts, flooded))
    print(f"Wrote {OUTPUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
