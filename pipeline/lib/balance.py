"""Change balance: how many flood-zone cells gained buildings against how many lost them.

Building counts per cell are noisy, and noise pushes cells up and down about equally. A neighborhood where
far more cells gain than lose is harder to explain by noise alone. Output holds counts of cells only.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class RawBalance:
    """Cell counts before any suppression. neighborhood_id is None for the whole study area."""

    neighborhood_id: str | None
    return_period: int
    cells_in_zone: int
    cells_gaining: int
    cells_losing: int


def balance_counts(
    counts: npt.NDArray[np.float64],
    flooded: npt.NDArray[np.bool_],
    labels: npt.NDArray[np.int32],
    neighborhood_ids: list[str],
    return_periods: list[int],
    threshold: float,
) -> list[RawBalance]:
    """Compare the last year with the first. counts is (years, rows, cols). Label 0 is outside every neighborhood."""
    change = counts[-1] - counts[0]
    size = len(neighborhood_ids) + 1
    result: list[RawBalance] = []
    for p_index, return_period in enumerate(return_periods):
        in_zone = flooded[p_index] & (labels > 0)
        zone_labels = labels[in_zone]
        zone_change = change[in_zone]
        total = np.bincount(zone_labels, minlength=size)
        gaining = np.bincount(zone_labels[zone_change >= threshold], minlength=size)
        losing = np.bincount(zone_labels[zone_change <= -threshold], minlength=size)
        result.extend(
            RawBalance(neighborhood_ids[n - 1], return_period, int(total[n]), int(gaining[n]), int(losing[n]))
            for n in range(1, size)
        )
        result.append(
            RawBalance(None, return_period, int(total.sum()), int(gaining.sum()), int(losing.sum())),
        )
    return result
