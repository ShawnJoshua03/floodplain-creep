"""Does a change stand out from noise? Pure functions over counts, no database."""

from __future__ import annotations

import statistics
from collections import defaultdict

from api.repositories.focus import OtherYear
from api.schemas.focus import Noise, SeriesYear, Signal, Verdict


def typical_swing(others: list[OtherYear]) -> Noise | None:
    """Median year-to-year change, as a percent, over neighborhoods that are shown in every year."""
    by_neighborhood: dict[str, list[OtherYear]] = defaultdict(list)
    for item in others:
        by_neighborhood[item.neighborhood_id].append(item)
    swings: list[float] = []
    used = 0
    for years in by_neighborhood.values():
        counts = [item.buildings_in_zone for item in sorted(years, key=lambda item: item.year)]
        if len(counts) < 2 or any(count is None or count == 0 for count in counts):
            continue
        used += 1
        pairs = zip(counts, counts[1:], strict=False)
        swings.extend(abs(100.0 * (after - before) / before) for before, after in pairs if before and after is not None)
    if not swings:
        return None
    return Noise(typical_swing_pct=statistics.median(swings), neighborhoods_used=used)


def smoothed_change_pct(series: list[SeriesYear]) -> float | None:
    """Change from the average of the first two years to the average of the last two, which damps one bad year."""
    ordered = sorted(series, key=lambda item: item.year)
    counts = [item.buildings_in_zone for item in ordered]
    if len(counts) < 4 or any(count is None for count in counts):
        return None
    shown = [count for count in counts if count is not None]
    start = (shown[0] + shown[1]) / 2
    end = (shown[-2] + shown[-1]) / 2
    return 100.0 * (end - start) / start if start else None


def classify(series: list[SeriesYear], noise: Noise | None, required_multiple: float) -> Signal:
    change = smoothed_change_pct(series)
    if change is None or noise is None or noise.typical_swing_pct == 0:
        return Signal(
            verdict="not_enough_data",
            smoothed_change_pct=change,
            times_typical_swing=None,
            required_multiple=required_multiple,
        )
    times = abs(change) / noise.typical_swing_pct
    verdict: Verdict
    if times < required_multiple:
        verdict = "within_noise"
    else:
        verdict = "clear_growth" if change > 0 else "clear_decline"
    return Signal(
        verdict=verdict,
        smoothed_change_pct=change,
        times_typical_swing=times,
        required_multiple=required_multiple,
    )
