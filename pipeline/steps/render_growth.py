"""Render smoothed building density in the modeled flood zone, one image per return period and year.

Run: uv run python -m pipeline.steps.render_growth
Needs data/processed/cells.npz from build_grid. Images are blended from 500 m blocks. Blocks with fewer
than K buildings are hidden. No cell values leave the pipeline.
"""

from __future__ import annotations

from pipeline.io.cell_store import load_cells
from pipeline.io.city_config import ROOT, load_city_config
from pipeline.io.growth_files import render_growth, write_growth_manifest

OUTPUT = ROOT / "data" / "processed" / "overlays"
CELLS = ROOT / "data" / "processed" / "cells.npz"
BLOCK_CELLS = 5


def main() -> None:
    config = load_city_config()
    store = load_cells(CELLS)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    entries = {}
    for return_period in config.return_periods:
        entries[return_period] = render_growth(
            store, return_period, config.bbox, BLOCK_CELLS, config.min_count_k, OUTPUT
        )
        print(f"Wrote growth images for RP{return_period}")
    write_growth_manifest(OUTPUT, config.bbox, BLOCK_CELLS * config.grid_size_m, entries)
    print("Wrote growth.json")


if __name__ == "__main__":
    main()
