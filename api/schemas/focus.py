"""Response shapes for the one neighborhood the app shows, and the evidence around it."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from api.schemas.geometry import MultiPolygonGeometry, PolygonGeometry

Verdict = Literal["clear_growth", "clear_decline", "within_noise", "not_enough_data"]


class SeriesYear(BaseModel):
    """Counts for the focus neighborhood in one year. A suppressed year holds null counts."""

    year: int
    buildings_in_zone: int | None
    new_buildings_in_zone: int | None
    growth_pct: float | None
    suppressed: bool
    change_available: bool


class Outline(BaseModel):
    neighborhood_id: str
    name: str
    boundary_source: str
    coverage: float
    geometry: PolygonGeometry | MultiPolygonGeometry


class Noise(BaseModel):
    """How much counts move from one year to the next in the other neighborhoods. No neighborhood is named."""

    typical_swing_pct: float
    neighborhoods_used: int


class Signal(BaseModel):
    """Whether the change from the first years to the last years stands out from the typical swing."""

    verdict: Verdict
    smoothed_change_pct: float | None
    times_typical_swing: float | None
    required_multiple: float


class CellCounts(BaseModel):
    cells_gaining: int
    cells_losing: int


class Balance(BaseModel):
    """Flood-zone areas of 100 m that gained buildings against areas that lost them, first year to last."""

    threshold_buildings: float
    focus: CellCounts
    rest_of_city: CellCounts


class FocusView(BaseModel):
    city: str
    return_period: int
    return_periods: list[int]
    first_year: int
    last_year: int
    min_count_k: int
    neighborhood: Outline
    series: list[SeriesYear]
    noise: Noise | None
    signal: Signal
    balance: Balance | None
