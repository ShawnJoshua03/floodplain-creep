"""Check that a requested return period or year is one this city supports."""

from __future__ import annotations

from api.core.errors import InvalidChoiceError
from api.core.settings import Settings


def require_return_period(settings: Settings, return_period: int) -> int:
    if return_period not in settings.return_periods:
        raise InvalidChoiceError(f"return_period must be one of {settings.return_periods}")
    return return_period


def require_year(settings: Settings, year: int) -> int:
    if not settings.first_year <= year <= settings.last_year:
        raise InvalidChoiceError(f"year must be between {settings.first_year} and {settings.last_year}")
    return year
