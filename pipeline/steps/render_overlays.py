"""Render the modeled flood depth overlay images, one per return period.

Run: uv run python -m pipeline.steps.render_overlays
Needs the outputs of fetch_flood. The images show modeled depth only, with no buildings.
"""

from __future__ import annotations

from pipeline.io.city_config import ROOT, load_city_config
from pipeline.io.overlay_files import render_depth_png, write_manifest
from pipeline.steps.build_grid import FLOOD, find_flood_file

OUTPUT = ROOT / "data" / "processed" / "overlays"


def main() -> None:
    config = load_city_config()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    water = FLOOD / find_flood_file("permanent_water")
    spurious = FLOOD / find_flood_file("spurious_depth_areas")
    images: dict[int, str] = {}
    for return_period in config.return_periods:
        name = f"depth_rp{return_period}.png"
        depth = FLOOD / find_flood_file(f"RP{return_period}_depth")
        render_depth_png(depth, water, spurious, config.bbox, config.min_depth_m, OUTPUT / name)
        images[return_period] = name
        print(f"Wrote {name}")
    write_manifest(OUTPUT, config.bbox, images)
    print(f"Wrote overlays.json in {OUTPUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
