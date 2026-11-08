"""Build the facts a brief may state, from numbers the API already computed."""

from __future__ import annotations

from api.schemas.brief_input import BriefInput
from api.schemas.focus import FocusView
from api.schemas.validation import ValidationResult


def build_brief_input(view: FocusView, validation: ValidationResult | None) -> BriefInput:
    first = next((row for row in view.series if row.year == view.first_year), None)
    last = next((row for row in view.series if row.year == view.last_year), None)
    accuracy = validation.accuracy.value if validation else None
    checked = bool(validation and (validation.label_sources.human + validation.label_sources.audit) > 0)
    balance = view.balance
    return BriefInput(
        neighborhood=view.neighborhood.name,
        city=view.city,
        return_period=view.return_period,
        first_year=view.first_year,
        last_year=view.last_year,
        buildings_first_year=first.buildings_in_zone if first else None,
        buildings_last_year=last.buildings_in_zone if last else None,
        change_since_first_year=last.new_buildings_in_zone if last else None,
        growth_pct=last.growth_pct if last else None,
        smoothed_change_pct=view.signal.smoothed_change_pct,
        typical_swing_pct=view.noise.typical_swing_pct if view.noise else None,
        times_typical_swing=view.signal.times_typical_swing,
        required_multiple=view.signal.required_multiple,
        verdict=view.signal.verdict,
        areas_gaining=balance.focus.cells_gaining if balance else None,
        areas_losing=balance.focus.cells_losing if balance else None,
        rest_areas_gaining=balance.rest_of_city.cells_gaining if balance else None,
        rest_areas_losing=balance.rest_of_city.cells_losing if balance else None,
        accuracy_pct=round(accuracy * 100, 1) if accuracy is not None else None,
        labels_checked_by_person=checked,
    )
