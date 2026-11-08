"""Response shapes for briefs and the limits text."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Brief(BaseModel):
    neighborhood_id: str
    return_period: int
    text: str
    source: Literal["gemini", "template"]


class Limits(BaseModel):
    limits: list[str]
    misuse_notice: str
    banned_terms: list[str]
