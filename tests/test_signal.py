from api.repositories.focus import OtherYear
from api.schemas.focus import Noise, SeriesYear
from api.services.signal import classify, smoothed_change_pct, typical_swing


def other(key: str, counts: list[int | None]) -> list[OtherYear]:
    return [OtherYear(neighborhood_id=key, year=2018 + i, buildings_in_zone=c) for i, c in enumerate(counts)]


def series(counts: list[int | None]) -> list[SeriesYear]:
    return [
        SeriesYear(
            year=2018 + i,
            buildings_in_zone=c,
            new_buildings_in_zone=None,
            growth_pct=None,
            suppressed=c is None,
            change_available=False,
        )
        for i, c in enumerate(counts)
    ]


def test_typical_swing_is_the_median_yearly_change_in_percent() -> None:
    noise = typical_swing(other("a", [100, 110, 100, 110]) + other("b", [200, 200, 200, 200]))
    assert noise is not None
    assert noise.neighborhoods_used == 2
    assert 0.0 <= noise.typical_swing_pct <= 10.0


def test_a_neighborhood_missing_a_year_does_not_count_toward_noise() -> None:
    noise = typical_swing(other("a", [100, 110, 100, 110]) + other("b", [200, None, 200, 200]))
    assert noise is not None
    assert noise.neighborhoods_used == 1


def test_no_usable_neighborhood_gives_no_noise() -> None:
    assert typical_swing(other("a", [None, None, None])) is None
    assert typical_swing([]) is None


def test_smoothed_change_compares_two_year_averages() -> None:
    change = smoothed_change_pct(series([100, 100, 150, 150, 200, 200]))
    assert change == 100.0


def test_smoothed_change_needs_every_year() -> None:
    assert smoothed_change_pct(series([100, None, 150, 150, 200, 200])) is None
    assert smoothed_change_pct(series([100, 100, 100])) is None


def test_change_beyond_the_required_multiple_is_clear() -> None:
    noise = Noise(typical_swing_pct=5.0, neighborhoods_used=10)
    assert classify(series([100, 100, 100, 100, 120, 120]), noise, 2).verdict == "clear_growth"
    assert classify(series([100, 100, 100, 100, 80, 80]), noise, 2).verdict == "clear_decline"


def test_change_inside_the_multiple_is_within_noise() -> None:
    noise = Noise(typical_swing_pct=5.0, neighborhoods_used=10)
    signal = classify(series([100, 100, 100, 100, 105, 105]), noise, 2)
    assert signal.verdict == "within_noise"
    assert signal.times_typical_swing == 1.0


def test_missing_noise_or_counts_gives_not_enough_data() -> None:
    noise = Noise(typical_swing_pct=5.0, neighborhoods_used=10)
    assert classify(series([100, 100, 100, 100, 120, 120]), None, 2).verdict == "not_enough_data"
    assert classify(series([None] * 6), noise, 2).verdict == "not_enough_data"
