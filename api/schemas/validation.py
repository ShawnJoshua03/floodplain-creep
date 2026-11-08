"""Response shape for the stored validation result."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Interval(BaseModel):
    value: float | None
    low: float | None
    high: float | None
    n: int


class Confusion(BaseModel):
    tp: int
    fp: int
    fn: int
    tn: int


class LabelSources(BaseModel):
    human: int
    audit: int
    ai: int


class ValidationPayload(BaseModel):
    """The JSON written by pipeline/steps/evaluate_validation.py and stored as-is."""

    labeled_cells: int
    excluded_unclear: int
    tuning_cells: int
    test_cells: int
    change_threshold_buildings: float
    confusion: Confusion
    accuracy: Interval
    precision: Interval
    recall: Interval
    sampling_note: str
    label_sources: LabelSources
    ai_human_agreement: Interval
    imagery_source: str
    imagery_dates: str
    start_year: int
    end_year: int


class ValidationResult(ValidationPayload):
    created_at: datetime
