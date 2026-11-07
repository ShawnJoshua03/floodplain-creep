"""The K rule. This is the only place a minimum count is applied.

A neighborhood-year with fewer than K buildings in the modeled flood zone is suppressed:
its counts are None. Change since the baseline year is shown only when the baseline count
also reaches K, so a hidden baseline cannot be worked out from a shown change.
"""

from __future__ import annotations

from dataclasses import dataclass

from pipeline.lib.aggregation import ZoneTotal


@dataclass(frozen=True)
class ExposureRow:
    neighborhood_id: str
    year: int
    return_period: int
    buildings_in_zone: int | None
    new_buildings_in_zone: int | None
    growth_pct: float | None
    suppressed: bool
    change_available: bool


def apply_suppression(totals: list[ZoneTotal], k: int, baseline_year: int) -> list[ExposureRow]:
    baseline = {
        (t.neighborhood_id, t.return_period): round(t.buildings_in_zone) for t in totals if t.year == baseline_year
    }
    rows: list[ExposureRow] = []
    for total in totals:
        key = (total.neighborhood_id, total.year, total.return_period)
        stock = round(total.buildings_in_zone)
        if stock < k:
            rows.append(ExposureRow(*key, None, None, None, True, False))
            continue
        base = baseline.get((total.neighborhood_id, total.return_period))
        if base is None or base < k:
            rows.append(ExposureRow(*key, stock, None, None, False, False))
            continue
        growth = 100.0 * (stock - base) / base
        rows.append(ExposureRow(*key, stock, stock - base, growth, False, True))
    return rows


def check_rows(rows: list[ExposureRow], k: int) -> None:
    """Raise if any row breaks the K rule. Steps call this before writing output."""
    for row in rows:
        where = f"{row.neighborhood_id} {row.year} RP{row.return_period}"
        has_counts = (
            row.buildings_in_zone is not None or row.new_buildings_in_zone is not None or row.growth_pct is not None
        )
        if row.suppressed and has_counts:
            raise ValueError(f"Suppressed row has counts: {where}")
        if not row.suppressed and (row.buildings_in_zone is None or row.buildings_in_zone < k):
            raise ValueError(f"Shown row is below K={k}: {where}")
        if not row.change_available and (row.new_buildings_in_zone is not None or row.growth_pct is not None):
            raise ValueError(f"Change shown without a usable baseline: {where}")
