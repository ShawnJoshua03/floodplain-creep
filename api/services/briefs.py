"""Stored neighborhood briefs. Generation arrives in M7."""

from __future__ import annotations

import logging

import psycopg

from api.core.errors import NotFoundError
from api.core.settings import Settings
from api.repositories.briefs import fetch_brief, neighborhood_exists
from api.safety.banned_terms import find_banned_terms
from api.schemas.brief import Brief
from api.services.choices import require_return_period

logger = logging.getLogger(__name__)


def stored_brief(conn: psycopg.Connection, settings: Settings, neighborhood_id: str, return_period: int) -> Brief:
    require_return_period(settings, return_period)
    if not neighborhood_exists(conn, neighborhood_id):
        raise NotFoundError(f"Unknown neighborhood: {neighborhood_id}")
    brief = fetch_brief(conn, neighborhood_id, return_period)
    if brief is None:
        raise NotFoundError("No brief is stored for this neighborhood and return period.")
    found = find_banned_terms(brief.text, settings.banned_terms)
    if found:
        logger.error("Stored brief for %s holds banned terms %s and was not served", neighborhood_id, found)
        raise NotFoundError("No brief is available for this neighborhood and return period.")
    return brief
