"""Fetch JRC river flood hazard tiles covering the city box and summarise them.

Run: uv run python -m pipeline.steps.fetch_flood
"""

from __future__ import annotations

import json

from pipeline.io.city_config import ROOT, load_city_config
from pipeline.io.downloads import download_file
from pipeline.io.rasters import describe_raster
from pipeline.lib.summary import format_summary
from pipeline.lib.tiles import GeoCollection, flood_file_name, flood_tile_for_point, flood_tiles

BASE = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard"
OUT_DIR = ROOT / "data" / "raw" / "flood"


def main() -> None:
    config = load_city_config()
    box = config.lonlat_bounds
    extents = OUT_DIR / "tile_extents.geojson"
    download_file(f"{BASE}/tile_extents.geojson", extents)
    collection = GeoCollection.model_validate(json.loads(extents.read_text(encoding="utf-8")))
    centre = ((box.left + box.right) / 2, (box.bottom + box.top) / 2)
    tile = flood_tile_for_point(flood_tiles(collection), *centre)
    layers = [(f"RP{rp}", f"RP{rp}", f"RP{rp}_depth") for rp in config.return_periods]
    layers += [
        ("Permanent_WaterBodies", "permanent water", "permanent_water"),
        ("Spurious_Depths", "spurious depth", "spurious_depth_areas"),
    ]
    for folder, label, kind in layers:
        file_name = flood_file_name(tile, kind)
        path = OUT_DIR / file_name
        download_file(f"{BASE}/{folder}/{file_name}", path)
        print(format_summary(describe_raster(path, f"flood {label}", box)))


if __name__ == "__main__":
    main()
