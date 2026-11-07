"""Load config/city.yaml and validate it at the boundary."""

from __future__ import annotations

from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, model_validator

from pipeline.lib.tiles import Bounds

ROOT = Path(__file__).resolve().parents[2]


class CityConfig(BaseModel):
    city: str
    min_count_k: int
    years: list[int]
    return_periods: list[int]
    grid_size_m: int
    presence_threshold: float
    min_depth_m: float
    min_coverage: float
    bbox: list[float]

    @model_validator(mode="after")
    def bbox_is_ordered(self) -> Self:
        if len(self.bbox) != 4:
            raise ValueError("bbox must have four values")
        west, south, east, north = self.bbox
        if west >= east or south >= north:
            raise ValueError("bbox must be [lon_min, lat_min, lon_max, lat_max]")
        return self

    @property
    def year_range(self) -> range:
        return range(self.years[0], self.years[1] + 1)

    @property
    def lonlat_bounds(self) -> Bounds:
        return Bounds(*self.bbox)


def load_city_config(path: Path = ROOT / "config" / "city.yaml") -> CityConfig:
    return CityConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
