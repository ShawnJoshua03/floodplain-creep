"""Side-by-side before and after images of one 100 m cell, for reviewing labels."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from pipeline.io.wayback import Capture, Release, build_mosaic, capture_at
from pipeline.lib.webmerc import crop_box, plan_mosaic, square_side_px

PANEL_PX = 320
HEADER_PX = 20
CELL_SIDE_M = 100.0
OUTLINE = (255, 255, 0)
TEXT = (255, 255, 255)
BAND = (0, 0, 0)


@dataclass(frozen=True)
class CellCaptures:
    start: Capture | None
    end: Capture | None


def describe(capture: Capture | None, release: Release) -> str:
    if capture is None:
        return f"release {release.release_date}, capture date unknown"
    return f"{capture.date.isoformat()} {capture.source} {capture.resolution_m:g} m"


def render_panel(release: Release, lon: float, lat: float, zoom: int) -> Image.Image:
    plan = plan_mosaic(lon, lat, zoom, radius=1)
    mosaic = build_mosaic(release, plan)
    panel = mosaic.crop(crop_box(plan.centre_px, PANEL_PX))
    half = square_side_px(CELL_SIDE_M, lat, zoom) / 2
    centre = PANEL_PX / 2
    ImageDraw.Draw(panel).rectangle((centre - half, centre - half, centre + half, centre + half), outline=OUTLINE)
    return panel


def capture_pair(start: Release, end: Release, lon: float, lat: float) -> CellCaptures:
    return CellCaptures(capture_at(start, lon, lat), capture_at(end, lon, lat))


def render_cell(start: Release, end: Release, lon: float, lat: float, zoom: int, destination: Path) -> CellCaptures:
    captures = capture_pair(start, end, lon, lat)
    canvas = Image.new("RGB", (2 * PANEL_PX, PANEL_PX + HEADER_PX), BAND)
    canvas.paste(render_panel(start, lon, lat, zoom), (0, HEADER_PX))
    canvas.paste(render_panel(end, lon, lat, zoom), (PANEL_PX, HEADER_PX))
    draw = ImageDraw.Draw(canvas)
    draw.text((4, 4), describe(captures.start, start), fill=TEXT)
    draw.text((PANEL_PX + 4, 4), describe(captures.end, end), fill=TEXT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)
    return captures
