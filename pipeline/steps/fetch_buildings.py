"""Fetch Open Buildings 2.5D Temporal rasters for the city box, one file per year.

Run: uv run python -m pipeline.steps.fetch_buildings [year ...]
With no years, every year in config/city.yaml is fetched.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pipeline.io.building_rasters import NODATA, build_year_raster
from pipeline.io.city_config import ROOT, load_city_config
from pipeline.io.downloads import fetch_text, list_bucket_names
from pipeline.io.rasters import GridSpec, describe_raster, to_crs_bounds, write_raster
from pipeline.lib.summary import format_summary
from pipeline.lib.tiles import (
    BUCKET_HTTP,
    SOURCE_PIXEL_M,
    Manifest,
    TileRef,
    manifest_matches,
    snap_bounds,
    tiles_in_bounds,
    utm_epsg,
)

OUT_DIR = ROOT / "data" / "raw" / "buildings"
FACTOR = 8
BANDS = ["building_fractional_count", "building_height", "building_presence"]


def load_manifest(name: str) -> Manifest:
    cache = OUT_DIR / "manifests" / Path(name).name
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(fetch_text(f"{BUCKET_HTTP}/{name}"), encoding="utf-8")
    return Manifest.model_validate(json.loads(cache.read_text(encoding="utf-8")))


def main() -> None:
    config = load_city_config()
    box = config.lonlat_bounds
    epsg = utm_epsg((box.left + box.right) / 2, (box.bottom + box.top) / 2)
    crs = f"EPSG:{epsg}"
    area = snap_bounds(to_crs_bounds(box, "EPSG:4326", crs), SOURCE_PIXEL_M * FACTOR)
    names = list_bucket_names("v1/manifests/")
    years = [int(arg) for arg in sys.argv[1:]] or list(config.year_range)
    for year in years:
        target = OUT_DIR / f"buildings_{year}.tif"
        if not target.exists():
            matched = [n for n in names if manifest_matches(n, epsg, year)]
            if not matched:
                raise RuntimeError(f"No manifest found for EPSG:{epsg} year {year}")
            tiles: dict[str, TileRef] = {}
            for name in matched:
                for tile in tiles_in_bounds(load_manifest(name), area):
                    tiles[tile.url] = tile
            if not tiles:
                raise RuntimeError(f"No tiles cover the box for {year}")
            pixels = build_year_raster(list(tiles.values()), area, FACTOR)
            grid = GridSpec((area.left, area.top), SOURCE_PIXEL_M * FACTOR, crs, NODATA)
            write_raster(target, pixels, grid, BANDS)
        print(format_summary(describe_raster(target, f"buildings {year}")))


if __name__ == "__main__":
    main()
