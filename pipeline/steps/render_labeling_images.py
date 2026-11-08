"""Render before and after images for the cells in the labeling sheet.

Run: uv run python -m pipeline.steps.render_labeling_images [cell_id ...]
With no ids, every cell in the sheet is rendered. Existing images are kept, so a failed run can be
repeated. Output goes to data/processed/labeling_images/.
Imagery: Esri World Imagery Wayback. The header of each image shows the true capture date.
"""

from __future__ import annotations

import csv
import sys
from concurrent.futures import ThreadPoolExecutor

from pipeline.io.city_config import ROOT
from pipeline.io.labeling_images import capture_pair, render_cell
from pipeline.io.validation_files import SHEET_PATH, load_validation_config, write_capture_rows
from pipeline.io.wayback import load_releases

IMAGES = ROOT / "data" / "processed" / "labeling_images"
WORKERS = 4


def main() -> None:
    settings = load_validation_config()
    releases = load_releases()
    start = releases[settings.wayback_start_release]
    end = releases[settings.wayback_end_release]
    with SHEET_PATH.open(newline="", encoding="utf-8") as handle:
        cells = [(r["cell_id"], float(r["longitude"]), float(r["latitude"])) for r in csv.DictReader(handle)]
    wanted = set(sys.argv[1:])
    if wanted:
        cells = [c for c in cells if c[0] in wanted]

    def work(cell: tuple[str, float, float]) -> list[str]:
        cell_id, lon, lat = cell
        image = IMAGES / f"{cell_id}.png"
        if image.exists():
            found = capture_pair(start, end, lon, lat)
        else:
            found = render_cell(start, end, lon, lat, settings.wayback_zoom, image)
        row = [cell_id]
        for capture in (found.start, found.end):
            row += (
                ["", "", ""]
                if capture is None
                else [capture.date.isoformat(), capture.source, f"{capture.resolution_m:g}"]
            )
        return row

    with ThreadPoolExecutor(WORKERS) as pool:
        rows = list(pool.map(work, cells))
    write_capture_rows(rows)
    print(f"Rendered {len(rows)} images in {IMAGES.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
