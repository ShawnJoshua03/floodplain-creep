"""Esri World Imagery Wayback: dated imagery releases, tiles, and true capture dates."""

from __future__ import annotations

import datetime
import io
import re
from dataclasses import dataclass

import httpx
from PIL import Image

from pipeline.lib.webmerc import TILE_PX, MosaicPlan, tile_coordinates

CONFIG_URL = "https://s3-us-west-2.amazonaws.com/config.maptiles.arcgis.com/waybackconfig.json"
HEADERS = {"User-Agent": "floodplain-creep-research/0.1"}
TIMEOUT = httpx.Timeout(60.0)
METADATA_LAYERS = (3, 4, 5, 6, 7)


@dataclass(frozen=True)
class Release:
    release_date: str
    tile_url: str
    metadata_url: str


@dataclass(frozen=True)
class Capture:
    date: datetime.date
    source: str
    resolution_m: float


def load_releases() -> dict[str, Release]:
    response = httpx.get(CONFIG_URL, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    releases: dict[str, Release] = {}
    for entry in response.json().values():
        match = re.search(r"\d{4}-\d{2}-\d{2}", entry["itemTitle"])
        if match:
            releases[match.group(0)] = Release(match.group(0), entry["itemURL"], entry["metadataLayerUrl"])
    return releases


def fetch_tile(release: Release, zoom: int, tile_x: int, tile_y: int) -> Image.Image:
    url = release.tile_url.format(level=zoom, row=tile_y, col=tile_x)
    response = httpx.get(url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert("RGB")


def build_mosaic(release: Release, plan: MosaicPlan) -> Image.Image:
    side = plan.tiles_per_side * TILE_PX
    mosaic = Image.new("RGB", (side, side))
    for tile_x, tile_y, col, row in tile_coordinates(plan):
        mosaic.paste(fetch_tile(release, plan.zoom, tile_x, tile_y), (col * TILE_PX, row * TILE_PX))
    return mosaic


def capture_at(release: Release, lon: float, lat: float) -> Capture | None:
    """Capture date of the imagery this release shows at a point, from the metadata layers."""
    for layer in METADATA_LAYERS:
        params = {
            "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "SRC_DATE2,NICE_NAME,SRC_RES",
            "returnGeometry": "false",
            "f": "json",
        }
        response = httpx.get(f"{release.metadata_url}/{layer}/query", params=params, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        features = response.json().get("features", [])
        if features:
            attrs = features[0]["attributes"]
            day = datetime.datetime.fromtimestamp(attrs["SRC_DATE2"] / 1000, datetime.UTC).date()
            return Capture(day, str(attrs["NICE_NAME"]), float(attrs["SRC_RES"]))
    return None
