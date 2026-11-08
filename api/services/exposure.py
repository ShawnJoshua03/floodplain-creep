"""Exposure answers for the whole city and for each neighborhood."""

from __future__ import annotations

import psycopg

from api.core.settings import Settings
from api.repositories.exposure import fetch_city_years, fetch_neighborhoods
from api.schemas.exposure import CitySummary, NeighborhoodCollection, NeighborhoodFeature, NeighborhoodProperties
from api.services.choices import require_return_period, require_year


def city_summary(conn: psycopg.Connection, settings: Settings, return_period: int) -> CitySummary:
    require_return_period(settings, return_period)
    return CitySummary(
        city=settings.city,
        return_period=return_period,
        first_year=settings.first_year,
        last_year=settings.last_year,
        years=fetch_city_years(conn, return_period),
    )


def neighborhood_collection(
    conn: psycopg.Connection, settings: Settings, return_period: int, year: int
) -> NeighborhoodCollection:
    require_return_period(settings, return_period)
    require_year(settings, year)
    features = [
        NeighborhoodFeature(
            properties=NeighborhoodProperties(
                neighborhood_id=record.neighborhood_id,
                name=record.name,
                boundary_source=record.boundary_source,
                year=year,
                return_period=return_period,
                buildings_in_zone=record.buildings_in_zone,
                new_buildings_in_zone=record.new_buildings_in_zone,
                growth_pct=record.growth_pct,
                suppressed=record.suppressed,
                change_available=record.change_available,
            ),
            geometry=record.geometry,
        )
        for record in fetch_neighborhoods(conn, return_period, year)
    ]
    return NeighborhoodCollection(year=year, return_period=return_period, features=features)
