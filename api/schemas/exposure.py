"""Response shapes for exposure counts. The smallest geometry is a neighborhood polygon."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ExposureCounts(BaseModel):
    """Counts for one neighborhood and year. Suppressed rows hold null counts."""

    buildings_in_zone: int | None
    new_buildings_in_zone: int | None
    growth_pct: float | None
    suppressed: bool
    change_available: bool


class NeighborhoodProperties(ExposureCounts):
    neighborhood_id: str
    name: str
    year: int
    return_period: int
    boundary_source: str


class PolygonGeometry(BaseModel):
    type: Literal["Polygon"]
    coordinates: list[list[list[float]]]


class MultiPolygonGeometry(BaseModel):
    type: Literal["MultiPolygon"]
    coordinates: list[list[list[list[float]]]]


class NeighborhoodFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    properties: NeighborhoodProperties
    geometry: PolygonGeometry | MultiPolygonGeometry


class NeighborhoodCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    year: int
    return_period: int
    features: list[NeighborhoodFeature]


class CityYear(BaseModel):
    """Totals over the neighborhoods that are shown. Suppressed neighborhoods are counted, not summed."""

    year: int
    buildings_in_zone: int
    new_buildings_in_zone: int | None
    neighborhoods_shown: int
    neighborhoods_suppressed: int


class CitySummary(BaseModel):
    city: str
    return_period: int
    first_year: int
    last_year: int
    years: list[CityYear]
