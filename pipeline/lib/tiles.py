"""Pure tile maths: which source tiles cover a box, and where they land on the output grid."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

BUCKET_HTTP = "https://storage.googleapis.com/open-buildings-temporal-data"
SOURCE_PIXEL_M = 0.5


@dataclass(frozen=True)
class Bounds:
    left: float
    bottom: float
    right: float
    top: float


@dataclass(frozen=True)
class TileRef:
    url: str
    bounds: Bounds


class Affine(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    scale_x: float = Field(alias="scaleX")
    translate_x: float = Field(alias="translateX")
    scale_y: float = Field(alias="scaleY")
    translate_y: float = Field(alias="translateY")


class Dimensions(BaseModel):
    width: int
    height: int


class TileSource(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    uris: list[str]
    affine: Affine = Field(alias="affineTransform")
    dimensions: Dimensions


class Tileset(BaseModel):
    sources: list[TileSource]


class Manifest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    uri_prefix: str = Field(alias="uriPrefix")
    tilesets: list[Tileset]


class GeoProperties(BaseModel):
    id: int
    name: str


class GeoPolygon(BaseModel):
    coordinates: list[list[list[float]]]


class GeoFeature(BaseModel):
    properties: GeoProperties
    geometry: GeoPolygon


class GeoCollection(BaseModel):
    features: list[GeoFeature]


@dataclass(frozen=True)
class FloodTile:
    tile_id: int
    name: str
    bounds: Bounds


def flood_tiles(collection: GeoCollection) -> list[FloodTile]:
    tiles: list[FloodTile] = []
    for feature in collection.features:
        ring = feature.geometry.coordinates[0]
        xs = [point[0] for point in ring]
        ys = [point[1] for point in ring]
        bounds = Bounds(min(xs), min(ys), max(xs), max(ys))
        tiles.append(FloodTile(feature.properties.id, feature.properties.name, bounds))
    return tiles


def utm_epsg(lon: float, lat: float) -> int:
    zone = int((lon + 180) // 6) + 1
    return (32600 if lat >= 0 else 32700) + zone


def manifest_matches(object_name: str, epsg: int, year: int) -> bool:
    return re.search(rf"_EPSG_{epsg}_{year}_06_30\.json$", object_name) is not None


def tile_url(uri_prefix: str, uri: str) -> str:
    gcs = uri_prefix + uri
    return gcs.replace("gs://open-buildings-temporal-data", BUCKET_HTTP)


def tile_bounds(source: TileSource) -> Bounds:
    a, d = source.affine, source.dimensions
    x1 = a.translate_x + d.width * a.scale_x
    y1 = a.translate_y + d.height * a.scale_y
    return Bounds(min(a.translate_x, x1), min(a.translate_y, y1), max(a.translate_x, x1), max(a.translate_y, y1))


def intersects(a: Bounds, b: Bounds) -> bool:
    return a.left < b.right and a.right > b.left and a.bottom < b.top and a.top > b.bottom


def tiles_in_bounds(manifest: Manifest, target: Bounds) -> list[TileRef]:
    found: list[TileRef] = []
    for tileset in manifest.tilesets:
        for source in tileset.sources:
            bounds = tile_bounds(source)
            if intersects(bounds, target):
                found.append(TileRef(tile_url(manifest.uri_prefix, source.uris[0]), bounds))
    return found


def snap_bounds(bounds: Bounds, step: float) -> Bounds:
    return Bounds(
        math.floor(bounds.left / step) * step,
        math.floor(bounds.bottom / step) * step,
        math.ceil(bounds.right / step) * step,
        math.ceil(bounds.top / step) * step,
    )


def overlap(a: Bounds, b: Bounds) -> Bounds:
    return Bounds(max(a.left, b.left), max(a.bottom, b.bottom), min(a.right, b.right), min(a.top, b.top))


def pixel_window(tile: Bounds, area: Bounds, pixel_m: float) -> tuple[int, int, int, int]:
    """Return (col_off, row_off, width, height) of `area` inside `tile`, in tile pixels."""
    col_off = round((area.left - tile.left) / pixel_m)
    row_off = round((tile.top - area.top) / pixel_m)
    width = round((area.right - area.left) / pixel_m)
    height = round((area.top - area.bottom) / pixel_m)
    return col_off, row_off, width, height


def flood_file_name(tile: FloodTile, kind: str) -> str:
    """kind is 'RP100_depth', 'permanent_water' or 'spurious_depth_areas'."""
    return f"ID{tile.tile_id}_{tile.name}_{kind}.tif"


def flood_tile_for_point(tiles: list[FloodTile], lon: float, lat: float) -> FloodTile:
    for tile in tiles:
        b = tile.bounds
        if b.left <= lon <= b.right and b.bottom <= lat <= b.top:
            return tile
    raise ValueError(f"No flood tile covers lon={lon}, lat={lat}")
