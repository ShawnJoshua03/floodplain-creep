"""Web Mercator tile maths for cutting a before/after view around one cell."""

from __future__ import annotations

import math
from dataclasses import dataclass

TILE_PX = 256
EARTH_CIRCUMFERENCE_M = 40075016.686


@dataclass(frozen=True)
class MosaicPlan:
    """A (2 * radius + 1) square block of tiles and where the cell centre falls in it."""

    zoom: int
    first_x: int
    first_y: int
    tiles_per_side: int
    centre_px: tuple[float, float]


def metres_per_pixel(lat: float, zoom: int) -> float:
    return EARTH_CIRCUMFERENCE_M * math.cos(math.radians(lat)) / (TILE_PX * (1 << zoom))


def lonlat_to_tile_fraction(lon: float, lat: float, zoom: int) -> tuple[float, float]:
    n = 1 << zoom
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


def plan_mosaic(lon: float, lat: float, zoom: int, radius: int) -> MosaicPlan:
    fx, fy = lonlat_to_tile_fraction(lon, lat, zoom)
    first_x = math.floor(fx) - radius
    first_y = math.floor(fy) - radius
    centre = ((fx - first_x) * TILE_PX, (fy - first_y) * TILE_PX)
    return MosaicPlan(zoom, first_x, first_y, 2 * radius + 1, centre)


def tile_coordinates(plan: MosaicPlan) -> list[tuple[int, int, int, int]]:
    """Return (tile_x, tile_y, column, row) for each tile of the mosaic."""
    return [
        (plan.first_x + col, plan.first_y + row, col, row)
        for row in range(plan.tiles_per_side)
        for col in range(plan.tiles_per_side)
    ]


def square_side_px(side_m: float, lat: float, zoom: int) -> float:
    return side_m / metres_per_pixel(lat, zoom)


def crop_box(centre_px: tuple[float, float], size_px: int) -> tuple[int, int, int, int]:
    left = round(centre_px[0] - size_px / 2)
    top = round(centre_px[1] - size_px / 2)
    return left, top, left + size_px, top + size_px
