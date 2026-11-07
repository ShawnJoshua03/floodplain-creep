"""Load neighborhood boundaries (geoBoundaries ADM3) and keep those mostly inside the study box."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box, mapping
from shapely.geometry.base import BaseGeometry

from pipeline.lib.tiles import Bounds

BOUNDARY_SOURCE = "geoBoundaries gbOpen BGD ADM3 (2020), CC BY 3.0 IGO"


@dataclass(frozen=True)
class Neighborhood:
    neighborhood_id: str
    name: str
    geometry: BaseGeometry
    coverage: float


@dataclass(frozen=True)
class BoundaryLoad:
    kept: list[Neighborhood]
    dropped: list[Neighborhood]


def load_neighborhoods(path: Path, lonlat: Bounds, crs: str, min_coverage: float) -> BoundaryLoad:
    """Read polygons touching the box. Coverage is the share of each polygon's area inside the box."""
    window = (lonlat.left, lonlat.bottom, lonlat.right, lonlat.top)
    frame = gpd.read_file(path, bbox=window).to_crs(crs)
    study_area = gpd.GeoSeries([box(*window)], crs="EPSG:4326").to_crs(crs).iloc[0]
    kept: list[Neighborhood] = []
    dropped: list[Neighborhood] = []
    for shape_id, name, geometry in zip(frame["shapeID"], frame["shapeName"], frame.geometry, strict=True):
        inside = geometry.intersection(study_area)
        coverage = float(inside.area / geometry.area)
        item = Neighborhood(str(shape_id), str(name), inside, coverage)
        (kept if coverage >= min_coverage else dropped).append(item)
    if not kept:
        raise RuntimeError(f"No neighborhood in {path} reaches {min_coverage:.0%} coverage of the box")
    return BoundaryLoad(sorted(kept, key=lambda n: n.neighborhood_id), dropped)


def write_neighborhood_geojson(path: Path, neighborhoods: list[Neighborhood], crs: str) -> None:
    """Write neighborhood polygons in WGS84. The smallest geometry ever published."""
    series = gpd.GeoSeries([n.geometry for n in neighborhoods], crs=crs).to_crs("EPSG:4326")
    features = [
        {
            "type": "Feature",
            "properties": {
                "neighborhood_id": n.neighborhood_id,
                "name": n.name,
                "coverage": round(n.coverage, 3),
                "boundary_source": BOUNDARY_SOURCE,
            },
            "geometry": mapping(geometry),
        }
        for n, geometry in zip(neighborhoods, series, strict=True)
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
