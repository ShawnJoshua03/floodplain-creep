"""Route for the one neighborhood the app shows."""

from __future__ import annotations

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends

from api.core.dependencies import get_connection, get_settings
from api.core.settings import Settings
from api.schemas.focus import FocusView
from api.services import focus

router = APIRouter()

Connection = Annotated[psycopg.Connection, Depends(get_connection)]
AppSettings = Annotated[Settings, Depends(get_settings)]


@router.get("/focus", response_model=FocusView)
def get_focus(conn: Connection, settings: AppSettings, return_period: int = 100) -> FocusView:
    return focus.focus_view(conn, settings, return_period)
