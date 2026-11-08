"""The stored brief for the focus neighborhood. Generation arrives in M7."""

from __future__ import annotations

import logging

import psycopg

from api.core.errors import NotFoundError
from api.core.settings import Settings
from api.repositories.briefs import fetch_brief
from api.safety.banned_terms import find_banned_terms
from api.schemas.brief import Brief
from api.services.choices import require_return_period
from api.services.focus import focus_outline

logger = logging.getLogger(__name__)


def stored_brief(conn: psycopg.Connection, settings: Settings, return_period: int) -> Brief:
    require_return_period(settings, return_period)
    outline = focus_outline(conn, settings)
    brief = fetch_brief(conn, outline.neighborhood_id, return_period)
    if brief is None:
        raise NotFoundError("No brief is stored for this scenario.")
    found = find_banned_terms(brief.text, settings.banned_terms)
    if found:
        logger.error("Stored brief for %s holds banned terms %s and was not served", outline.neighborhood_id, found)
        raise NotFoundError("No brief is available for this scenario.")
    return brief
