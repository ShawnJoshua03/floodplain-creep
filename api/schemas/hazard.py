"""Response shapes for the modeled flood depth overlay."""

from __future__ import annotations

from pydantic import BaseModel

from api.schemas.geometry import MultiPolygonGeometry, PolygonGeometry


class DepthBin(BaseModel):
    min_depth_m: float
    max_depth_m: float | None
    color: str


class OverlayManifest(BaseModel):
    """Written by pipeline/steps/render_overlays.py next to the images."""

    bounds: list[float]
    bins: list[DepthBin]
    images: dict[str, str]


class OverlayInfo(BaseModel):
    return_period: int
    image_url: str
    bounds: list[float]
    bins: list[DepthBin]
    label: str


class WaterLayer(BaseModel):
    """Permanent water, for orientation on the map. It holds no buildings."""

    label: str
    geometry: MultiPolygonGeometry | PolygonGeometry | None


class GrowthBin(BaseModel):
    min_buildings: int
    max_buildings: int | None
    color: str


class GrowthSet(BaseModel):
    bins: list[GrowthBin]
    images: dict[str, str]


class GrowthManifest(BaseModel):
    """Written by pipeline/steps/render_growth.py next to the images."""

    bounds: list[float]
    block_m: int
    return_periods: dict[str, GrowthSet]


class GrowthInfo(BaseModel):
    """Smoothed building density in the flood zone, one image per year. Blocks under the minimum count are hidden."""

    return_period: int
    bounds: list[float]
    block_m: int
    bins: list[GrowthBin]
    image_urls: dict[str, str]
    label: str
