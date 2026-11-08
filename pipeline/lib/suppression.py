"""The K rule. This is the only place a minimum count is applied.

A neighborhood-year with fewer than K buildings in the modeled flood zone is suppressed:
its counts are None. Change since the baseline year is shown only when the baseline count
also reaches K, so a hidden baseline cannot be worked out from a shown change.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from pipeline.lib.aggregation import ZoneTotal
from pipeline.lib.balance import RawBalance


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


@dataclass(frozen=True)
class BalanceRow:
    """Cell counts for one neighborhood, or for the whole study area when neighborhood_id is None."""

    neighborhood_id: str | None
    return_period: int
    cells_in_zone: int | None
    cells_gaining: int | None
    cells_losing: int | None
    suppressed: bool


def suppress_balance(raw: list[RawBalance], k: int) -> list[BalanceRow]:
    """A neighborhood with fewer than K flood-zone cells shows no cell counts. The whole study area always shows."""
    rows: list[BalanceRow] = []
    for item in raw:
        if item.neighborhood_id is not None and item.cells_in_zone < k:
            rows.append(BalanceRow(item.neighborhood_id, item.return_period, None, None, None, True))
        else:
            rows.append(
                BalanceRow(
                    item.neighborhood_id,
                    item.return_period,
                    item.cells_in_zone,
                    item.cells_gaining,
                    item.cells_losing,
                    False,
                )
            )
    return rows


def suppress_blocks(block_sums: npt.NDArray[np.float64], k: int) -> npt.NDArray[np.bool_]:
    """True where a map block may be drawn. A block with fewer than K buildings in the flood zone is hidden."""
    return np.round(block_sums) >= k
