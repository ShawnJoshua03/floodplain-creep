"""The limits text, misuse notice, and banned terms, as loaded from config/."""

from __future__ import annotations

from api.core.settings import Settings
from api.schemas.brief import Limits


def limits_text(settings: Settings) -> Limits:
    return Limits(limits=settings.limits, misuse_notice=settings.misuse_notice, banned_terms=settings.banned_terms)
