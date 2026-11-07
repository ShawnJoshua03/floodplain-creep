"""Plain-text description of a raster for step output."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BandRange:
    name: str
    minimum: float
    maximum: float
    valid_pixels: int


@dataclass(frozen=True)
class RasterSummary:
    label: str
    shape: tuple[int, int]
    crs: str
    resolution: tuple[float, float]
    nodata: float | None
    bands: list[BandRange]


def format_summary(summary: RasterSummary) -> str:
    head = (
        f"{summary.label}: shape={summary.shape[0]}x{summary.shape[1]} crs={summary.crs} "
        f"res={summary.resolution[0]:g}x{summary.resolution[1]:g} nodata={summary.nodata}"
    )
    lines = [head]
    for band in summary.bands:
        lines.append(f"    {band.name}: min={band.minimum:.4g} max={band.maximum:.4g} valid_pixels={band.valid_pixels}")
    return "\n".join(lines)
