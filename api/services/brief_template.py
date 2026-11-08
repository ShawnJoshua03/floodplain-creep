"""The templated brief. It is what people see when the model is unavailable or its text fails a check."""

from __future__ import annotations

from api.schemas.brief_input import BriefInput

COUNT = "{:,}"


def signed(value: int) -> str:
    return f"+{COUNT.format(value)}" if value > 0 else COUNT.format(value).replace("-", "−")


def verdict_sentence(data: BriefInput) -> str:
    if data.verdict == "not_enough_data" or data.times_typical_swing is None:
        return "There is not enough data to say whether this change stands out from normal year-to-year noise."
    times = f"{data.times_typical_swing:.1f}"
    if data.verdict == "within_noise":
        needed = f"{data.required_multiple:g}"
        return f"The change is {times} times the usual yearly swing, below the {needed} times needed to call it clear."
    direction = "growth" if data.verdict == "clear_growth" else "decline"
    return f"The {direction} is {times} times the usual yearly swing, so it is unlikely to be noise alone."


def template_brief(data: BriefInput) -> str:
    """A plain paragraph of 90 words or fewer, built only from the input."""
    if data.buildings_last_year is None:
        return (
            f"There are too few buildings in the modeled {data.return_period}-year flood zone in {data.neighborhood} "
            f"in {data.last_year} to show a number. This is a modeled scenario, not a forecast or an official warning."
        )
    change = ""
    if data.change_since_first_year is not None:
        change = f", {signed(data.change_since_first_year)} since {data.first_year}"
    return (
        f"{data.neighborhood} had {COUNT.format(data.buildings_last_year)} buildings in its modeled "
        f"{data.return_period}-year flood zone in {data.last_year}{change}. {verdict_sentence(data)} "
        "Counts come from satellite detections and can shift between years without real change, so treat them as "
        "estimates. This is a modeled scenario, not a forecast or an official warning."
    )
