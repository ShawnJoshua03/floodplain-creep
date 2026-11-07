"""Roll cells up to neighborhoods, apply the K rule, and write the published table.

Run: uv run python -m pipeline.steps.aggregate_neighborhoods
Output: data/processed/neighborhood_year_exposure.csv and neighborhoods.geojson.
"""

from __future__ import annotations

from pipeline.io.boundaries import load_neighborhoods, write_neighborhood_geojson
from pipeline.io.cell_store import load_cells
from pipeline.io.city_config import ROOT, load_city_config
from pipeline.io.exposure_csv import write_exposure_csv
from pipeline.lib.aggregation import zone_totals
from pipeline.lib.labels import rasterize_neighborhoods
from pipeline.lib.suppression import apply_suppression, check_rows

BOUNDARIES = ROOT / "data" / "raw" / "boundaries" / "adm3.geojson"
CELLS = ROOT / "data" / "processed" / "cells.npz"
OUT_DIR = ROOT / "data" / "processed"


def main() -> None:
    config = load_city_config()
    store = load_cells(CELLS)
    loaded = load_neighborhoods(BOUNDARIES, config.lonlat_bounds, store.grid.crs, config.min_coverage)
    for item in loaded.dropped:
        print(f"Dropped {item.name}: only {item.coverage:.0%} inside the box")
    kept = loaded.kept
    labels = rasterize_neighborhoods([n.geometry for n in kept], store.grid)
    totals = zone_totals(
        store.counts, store.flooded, labels, [n.neighborhood_id for n in kept], store.years, store.return_periods
    )
    rows = apply_suppression(totals, config.min_count_k, store.years[0])
    check_rows(rows, config.min_count_k)
    write_exposure_csv(OUT_DIR / "neighborhood_year_exposure.csv", rows)
    write_neighborhood_geojson(OUT_DIR / "neighborhoods.geojson", kept, store.grid.crs)
    shown = sum(1 for r in rows if not r.suppressed)
    print(f"{len(kept)} neighborhoods, {len(rows)} rows, {shown} shown, {len(rows) - shown} suppressed")


if __name__ == "__main__":
    main()
