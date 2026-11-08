"""The focus view: one neighborhood, its yearly counts, and the evidence about noise."""

from __future__ import annotations

import psycopg

from api.core.errors import NotFoundError
from api.core.settings import Settings
from api.repositories.focus import BalanceRecord, fetch_balance, fetch_other_years, fetch_outline, fetch_series
from api.schemas.focus import Balance, CellCounts, FocusView, Outline
from api.services.choices import require_return_period
from api.services.signal import classify, typical_swing


def build_balance(records: list[BalanceRecord], threshold: float) -> Balance | None:
    """The rest of the city is the whole study area minus the focus neighborhood. No other neighborhood is named."""
    focus = next((item for item in records if item.neighborhood_id is not None), None)
    area = next((item for item in records if item.neighborhood_id is None), None)
    if focus is None or area is None:
        return None
    return Balance(
        threshold_buildings=threshold,
        focus=CellCounts(cells_gaining=focus.cells_gaining, cells_losing=focus.cells_losing),
        rest_of_city=CellCounts(
            cells_gaining=area.cells_gaining - focus.cells_gaining,
            cells_losing=area.cells_losing - focus.cells_losing,
        ),
    )


def focus_outline(conn: psycopg.Connection, settings: Settings) -> Outline:
    outline = fetch_outline(conn, settings.focus_neighborhood)
    if outline is None:
        raise NotFoundError(f"The focus neighborhood {settings.focus_neighborhood} is not in the database.")
    return outline


def focus_view(conn: psycopg.Connection, settings: Settings, return_period: int) -> FocusView:
    require_return_period(settings, return_period)
    outline = focus_outline(conn, settings)
    series = fetch_series(conn, outline.neighborhood_id, return_period)
    noise = typical_swing(fetch_other_years(conn, return_period, outline.neighborhood_id))
    balance = build_balance(
        fetch_balance(conn, return_period, outline.neighborhood_id), settings.balance_threshold_buildings
    )
    return FocusView(
        city=settings.city,
        return_period=return_period,
        return_periods=settings.return_periods,
        first_year=settings.first_year,
        last_year=settings.last_year,
        min_count_k=settings.min_count_k,
        neighborhood=outline,
        series=series,
        noise=noise,
        signal=classify(series, noise, settings.signal_noise_multiple),
        balance=balance,
    )
