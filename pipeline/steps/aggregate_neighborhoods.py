"""Roll cells up to neighborhoods, apply the K rule, and write the published table.

Run: uv run python -m pipeline.steps.aggregate_neighborhoods
Output: neighborhood_year_exposure.csv, neighborhood_change_balance.csv and neighborhoods.geojson in data/processed/.
"""

from __future__ import annotations

from pipeline.io.balance_csv import write_balance_csv
from pipeline.io.boundaries import write_neighborhood_geojson
from pipeline.io.cell_store import load_cells
from pipeline.io.city_config import ROOT, load_city_config
from pipeline.io.exposure_csv import write_exposure_csv
from pipeline.io.neighborhood_labels import load_labels
from pipeline.lib.aggregation import zone_totals
from pipeline.lib.balance import balance_counts
from pipeline.lib.suppression import apply_suppression, check_rows, suppress_balance

CELLS = ROOT / "data" / "processed" / "cells.npz"
OUT_DIR = ROOT / "data" / "processed"


def main() -> None:
    config = load_city_config()
    store = load_cells(CELLS)
    found = load_labels(config, store)
    for item in found.loaded.dropped:
        print(f"Dropped {item.name}: only {item.coverage:.0%} inside the box")
    kept = found.loaded.kept
    labels = found.labels
    totals = zone_totals(
        store.counts, store.flooded, labels, [n.neighborhood_id for n in kept], store.years, store.return_periods
    )
    rows = apply_suppression(totals, config.min_count_k, store.years[0])
    check_rows(rows, config.min_count_k)
    write_exposure_csv(OUT_DIR / "neighborhood_year_exposure.csv", rows)
    ids = [n.neighborhood_id for n in kept]
    raw = balance_counts(
        store.counts, store.flooded, labels, ids, store.return_periods, config.balance_threshold_buildings
    )
    write_balance_csv(OUT_DIR / "neighborhood_change_balance.csv", suppress_balance(raw, config.min_count_k))
    write_neighborhood_geojson(OUT_DIR / "neighborhoods.geojson", kept, store.grid.crs)
    shown = sum(1 for r in rows if not r.suppressed)
    print(f"{len(kept)} neighborhoods, {len(rows)} rows, {shown} shown, {len(rows) - shown} suppressed")


if __name__ == "__main__":
    main()
