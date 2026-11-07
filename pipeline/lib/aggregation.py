"""Roll cells up to neighborhoods. Output holds neighborhood totals only, never cell values."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class ZoneTotal:
    """Buildings inside the modeled flood zone, before any suppression."""

    neighborhood_id: str
    year: int
    return_period: int
    buildings_in_zone: float


def zone_totals(
    counts: npt.NDArray[np.float64],
    flooded: npt.NDArray[np.bool_],
    labels: npt.NDArray[np.int32],
    neighborhood_ids: list[str],
    years: list[int],
    return_periods: list[int],
) -> list[ZoneTotal]:
    """counts is (years, rows, cols), flooded is (return periods, rows, cols).

    Label n (1-based) is neighborhood_ids[n - 1]. Label 0 is outside every neighborhood.
    """
    size = len(neighborhood_ids) + 1
    totals: list[ZoneTotal] = []
    for p_index, return_period in enumerate(return_periods):
        in_zone = flooded[p_index]
        zone_labels = labels[in_zone]
        for y_index, year in enumerate(years):
            sums = np.bincount(zone_labels, weights=counts[y_index][in_zone], minlength=size)
            totals.extend(
                ZoneTotal(neighborhood_ids[n - 1], year, return_period, float(sums[n])) for n in range(1, size)
            )
    return totals
