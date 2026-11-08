"""Recompute the sampled cells' change after the baseline year moved.

Run: uv run python -m pipeline.steps.rebase_validation_sample
The cells and their sample types stay as drawn. The change column becomes last year minus first
year of the current cells.npz, and the sampling note says how the flagged cells were chosen.
"""

from __future__ import annotations

from pipeline.io.cell_store import load_cells
from pipeline.io.city_config import ROOT
from pipeline.io.validation_files import META_PATH, read_design_cells, read_json, rewrite_design_changes, write_json

CELLS = ROOT / "data" / "processed" / "cells.npz"
REBASE_NOTE = (
    " The 40 extra cells were chosen with the change between {old_start} and {end}, before the baseline "
    "moved to {start}. Change is now measured between {start} and {end}, so the extra cells are not "
    "guaranteed to show an increase under the new baseline."
)


def main() -> None:
    store = load_cells(CELLS)
    start, end = store.years[0], store.years[-1]
    meta = read_json(META_PATH)
    if meta["start_year"] == start:
        print(f"Sample already uses {start} as the baseline. Nothing to do.")
        return
    change = store.counts[-1] - store.counts[0]
    cells = read_design_cells()
    rewrite_design_changes({cell_id: float(change[row, col]) for cell_id, row, col, _ in cells})
    note = str(meta["sampling_note"]) + REBASE_NOTE.format(old_start=meta["start_year"], start=start, end=end)
    write_json(META_PATH, {**meta, "start_year": start, "end_year": end, "sampling_note": note})
    print(f"Rebased {len(cells)} cells to {start} to {end}")


if __name__ == "__main__":
    main()
