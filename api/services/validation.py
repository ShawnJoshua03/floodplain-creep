"""The stored validation result. Numbers are never computed or hardcoded here."""

from __future__ import annotations

import psycopg

from api.core.errors import NotFoundError
from api.repositories.validation import fetch_latest_validation
from api.schemas.validation import ValidationResult


def latest_validation(conn: psycopg.Connection) -> ValidationResult:
    record = fetch_latest_validation(conn)
    if record is None:
        raise NotFoundError("No validation result is stored yet.")
    return ValidationResult(**record.payload.model_dump(), created_at=record.created_at)
