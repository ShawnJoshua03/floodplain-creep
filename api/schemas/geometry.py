"""Polygon shapes. The smallest geometry anywhere in the API is a neighborhood outline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class PolygonGeometry(BaseModel):
    type: Literal["Polygon"]
    coordinates: list[list[list[float]]]


class MultiPolygonGeometry(BaseModel):
    type: Literal["MultiPolygon"]
    coordinates: list[list[list[list[float]]]]
