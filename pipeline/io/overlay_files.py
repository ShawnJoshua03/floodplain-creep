"""Render modeled flood depth to Web Mercator PNG images and a manifest the API reads."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import numpy.typing as npt
import rasterio
from PIL import Image
from pyproj import Transformer
from rasterio.features import shapes
from rasterio.transform import from_bounds
from rasterio.warp import Resampling, reproject, transform_bounds
from shapely.geometry import box, mapping, shape
from shapely.ops import transform, unary_union

from pipeline.io.flood_grid import DEPTH_NODATA, MASK_NODATA
from pipeline.lib.exposure import flood_zone
from pipeline.lib.overlay import DEPTH_BINS, colorize

WEB_MERCATOR = "EPSG:3857"
PIXEL_M = 100.0
WATER_SIMPLIFY_M = 40.0
WATER_SOURCE = "JRC permanent water, about 90 m. A river or lake that is water all year."


def warp_to_mercator(
    path: Path, lonlat_bbox: list[float], dtype: str, nodata: float
) -> npt.NDArray[np.float32] | npt.NDArray[np.uint8]:
    """Nearest-neighbour copy of a raster onto a Web Mercator grid covering the box."""
    left, bottom, right, top = transform_bounds("EPSG:4326", WEB_MERCATOR, *lonlat_bbox)
    width = round((right - left) / PIXEL_M)
    height = round((top - bottom) / PIXEL_M)
    destination = np.full((height, width), nodata, dtype=dtype)
    with rasterio.open(path) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            dst_transform=from_bounds(left, bottom, right, top, width, height),
            dst_crs=WEB_MERCATOR,
            dst_nodata=nodata,
            src_nodata=src.nodata,
            resampling=Resampling.nearest,
        )
    return destination


def render_depth_png(
    depth_path: Path, water_path: Path, spurious_path: Path, lonlat_bbox: list[float], min_depth_m: float, out: Path
) -> None:
    depth = np.asarray(warp_to_mercator(depth_path, lonlat_bbox, "float32", DEPTH_NODATA), dtype=np.float32)
    water = np.asarray(warp_to_mercator(water_path, lonlat_bbox, "uint8", MASK_NODATA), dtype=np.uint8)
    spurious = np.asarray(warp_to_mercator(spurious_path, lonlat_bbox, "uint8", MASK_NODATA), dtype=np.uint8)
    zone = flood_zone(depth, water, spurious, DEPTH_NODATA, MASK_NODATA, min_depth_m)
    Image.fromarray(colorize(depth, zone), mode="RGBA").save(out)


def write_manifest(out_dir: Path, lonlat_bbox: list[float], images: dict[int, str]) -> None:
    manifest = {
        "bounds": lonlat_bbox,
        "bins": [
            {"min_depth_m": spec.min_depth_m, "max_depth_m": spec.max_depth_m, "color": spec.hex} for spec in DEPTH_BINS
        ],
        "images": {str(return_period): name for return_period, name in images.items()},
    }
    (out_dir / "overlays.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def water_geometry(water_path: Path, lonlat_bbox: list[float]) -> dict[str, object] | None:
    """Permanent water as one polygon in lon/lat, for orientation on the map. No buildings, no cells exposed."""
    left, bottom, right, top = transform_bounds("EPSG:4326", WEB_MERCATOR, *lonlat_bbox)
    mask = np.asarray(warp_to_mercator(water_path, lonlat_bbox, "uint8", MASK_NODATA), dtype=np.uint8) != MASK_NODATA
    if not mask.any():
        return None
    height, width = mask.shape
    frame = from_bounds(left, bottom, right, top, width, height)
    pieces = [shape(geometry) for geometry, value in shapes(mask.astype(np.uint8), mask=mask, transform=frame) if value]
    merged = unary_union(pieces).simplify(WATER_SIMPLIFY_M).intersection(box(left, bottom, right, top))
    to_lonlat = Transformer.from_crs(WEB_MERCATOR, "EPSG:4326", always_xy=True).transform
    geometry = mapping(transform(to_lonlat, merged))
    return {"type": geometry["type"], "coordinates": json.loads(json.dumps(geometry["coordinates"]))}


def write_context(out_dir: Path, water: dict[str, object] | None) -> None:
    context = {"label": WATER_SOURCE, "water": water}
    (out_dir / "context.json").write_text(json.dumps(context) + "\n", encoding="utf-8")
