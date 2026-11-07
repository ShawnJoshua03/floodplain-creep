"""Draw the validation sample and write the labeling sheet.

Run: uv run python -m pipeline.steps.make_validation_sample
The sheet (data/processed/labeling_sheet.csv) holds cell id, place and links. It does not hold the
algorithm's answer or the sample type. A human fills the `label` column.
"""

from __future__ import annotations

from pipeline.io.cell_store import load_cells
from pipeline.io.city_config import ROOT, load_city_config
from pipeline.io.neighborhood_labels import load_labels
from pipeline.io.rasters import cell_centres_lonlat
from pipeline.io.validation_files import (
    DESIGN_PATH,
    META_PATH,
    SHEET_PATH,
    CellPlace,
    load_validation_config,
    write_design,
    write_json,
    write_labeling_sheet,
)
from pipeline.lib.sampling import SampleDesign, draw_sample, flagged_pool_size, sampling_note

CELLS = ROOT / "data" / "processed" / "cells.npz"


def main() -> None:
    config = load_city_config()
    settings = load_validation_config()
    store = load_cells(CELLS)
    if SHEET_PATH.exists():
        raise FileExistsError(f"{SHEET_PATH} exists. Delete it deliberately to redraw: labels would be lost.")
    labels = load_labels(config, store).labels
    zone = store.flooded[store.return_periods.index(settings.return_period)]
    eligible = zone & (labels > 0)
    change = store.counts[-1] - store.counts[0]
    design = SampleDesign(settings.n_random, settings.n_flagged, settings.flag_threshold, settings.seed)
    cells = draw_sample(eligible, change, design)
    coordinates = cell_centres_lonlat(store.grid, [(c.row, c.col) for c in cells])
    places = [CellPlace(lat, lon) for lon, lat in coordinates]
    write_design(DESIGN_PATH, cells)
    write_labeling_sheet(SHEET_PATH, cells, places)
    note = sampling_note(design, int(eligible.sum()), flagged_pool_size(eligible, change, design.flag_threshold))
    write_json(
        META_PATH,
        {
            "return_period": settings.return_period,
            "eligible_cells": int(eligible.sum()),
            "n_random": design.n_random,
            "n_flagged": design.n_flagged,
            "flag_threshold": design.flag_threshold,
            "seed": design.seed,
            "start_year": store.years[0],
            "end_year": store.years[-1],
            "sampling_note": note,
        },
    )
    print(f"Wrote {len(cells)} cells to {SHEET_PATH.relative_to(ROOT).as_posix()}")
    print(note)


if __name__ == "__main__":
    main()
