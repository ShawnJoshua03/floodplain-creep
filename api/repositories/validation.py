"""SQL for the stored validation result."""

from __future__ import annotations

from datetime import datetime

import psycopg
from psycopg.rows import class_row
from pydantic import BaseModel

from api.schemas.validation import ValidationPayload


class ValidationRecord(BaseModel):
    payload: ValidationPayload
    created_at: datetime


def fetch_latest_validation(conn: psycopg.Connection) -> ValidationRecord | None:
    with conn.cursor(row_factory=class_row(ValidationRecord)) as cur:
        return cur.execute("SELECT payload, created_at FROM validation_result ORDER BY id DESC LIMIT 1").fetchone()
