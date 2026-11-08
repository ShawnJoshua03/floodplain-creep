"""Routes for the hazard overlay, validation result, briefs, and limits text."""

from __future__ import annotations

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from api.core.dependencies import get_connection, get_settings
from api.core.settings import Settings
from api.schemas.brief import Brief, Limits
from api.schemas.hazard import OverlayInfo
from api.schemas.validation import ValidationResult
from api.services import briefs, hazard, limits, validation

router = APIRouter()

Connection = Annotated[psycopg.Connection, Depends(get_connection)]
AppSettings = Annotated[Settings, Depends(get_settings)]


@router.get("/hazard/overlay", response_model=OverlayInfo)
def get_overlay(settings: AppSettings, return_period: int = 100) -> OverlayInfo:
    return hazard.overlay_info(settings, return_period)


@router.get("/overlays/{filename}", response_class=FileResponse)
def get_overlay_image(filename: str, settings: AppSettings) -> FileResponse:
    return FileResponse(hazard.overlay_image_path(settings, filename), media_type="image/png")


@router.get("/validation", response_model=ValidationResult)
def get_validation(conn: Connection) -> ValidationResult:
    return validation.latest_validation(conn)


@router.get("/brief", response_model=Brief)
def get_brief(conn: Connection, settings: AppSettings, return_period: int = 100) -> Brief:
    return briefs.stored_brief(conn, settings, return_period)


@router.get("/limits", response_model=Limits)
def get_limits(settings: AppSettings) -> Limits:
    return limits.limits_text(settings)
