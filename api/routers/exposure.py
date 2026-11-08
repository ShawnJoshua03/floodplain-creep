"""Routes for city totals and neighborhood counts."""

from __future__ import annotations

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends

from api.core.dependencies import get_connection, get_settings
from api.core.settings import Settings
from api.schemas.exposure import CitySummary, NeighborhoodCollection
from api.services import exposure

router = APIRouter()

Connection = Annotated[psycopg.Connection, Depends(get_connection)]
AppSettings = Annotated[Settings, Depends(get_settings)]


@router.get("/city/summary", response_model=CitySummary)
def get_city_summary(conn: Connection, settings: AppSettings, return_period: int = 100) -> CitySummary:
    return exposure.city_summary(conn, settings, return_period)


@router.get("/neighborhoods", response_model=NeighborhoodCollection)
def get_neighborhoods(
    conn: Connection, settings: AppSettings, return_period: int = 100, year: int = 2023
) -> NeighborhoodCollection:
    return exposure.neighborhood_collection(conn, settings, return_period, year)
