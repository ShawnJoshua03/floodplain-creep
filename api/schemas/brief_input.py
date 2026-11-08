"""The only facts a brief may state. Every number in a brief must appear in this object."""

from __future__ import annotations

from pydantic import BaseModel


class Resource(BaseModel):
    """An official preparedness link from config/resources.yaml. Code adds these, the model never writes links."""

    title: str
    url: str


class BriefInput(BaseModel):
    neighborhood: str
    city: str
    return_period: int
    first_year: int
    last_year: int
    buildings_first_year: int | None
    buildings_last_year: int | None
    change_since_first_year: int | None
    growth_pct: float | None
    smoothed_change_pct: float | None
    typical_swing_pct: float | None
    times_typical_swing: float | None
    required_multiple: float
    verdict: str
    areas_gaining: int | None
    areas_losing: int | None
    rest_areas_gaining: int | None
    rest_areas_losing: int | None
    accuracy_pct: float | None
    labels_checked_by_person: bool


class WrittenBrief(BaseModel):
    text: str
    source: str
