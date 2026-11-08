"""Building density for the map: 500 m block sums, bins, and colors. Blocks below K are hidden before drawing."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

GROWTH_ALPHA = 200
BIN_QUANTILES = (0.33, 0.66, 0.9)
GROWTH_COLORS: list[tuple[int, int, int]] = [(255, 214, 153), (255, 159, 64), (230, 92, 36), (176, 38, 24)]


@dataclass(frozen=True)
class GrowthBin:
    min_buildings: int
    max_buildings: int | None
    rgb: tuple[int, int, int]

    @property
    def hex(self) -> str:
        red, green, blue = self.rgb
        return f"#{red:02x}{green:02x}{blue:02x}"


def block_sums(counts: npt.NDArray[np.float64], flooded: npt.NDArray[np.bool_], block: int) -> npt.NDArray[np.float64]:
    """Sum building counts inside the flood zone into square blocks of block by block cells."""
    rows, cols = counts.shape
    padded = np.pad(np.where(flooded, counts, 0.0), ((0, -rows % block), (0, -cols % block)))
    height, width = padded.shape
    return padded.reshape(height // block, block, width // block, block).sum(axis=(1, 3))


def growth_bins(shown_sums: npt.NDArray[np.float64], k: int) -> list[GrowthBin]:
    """Four bins from the block sums of the last year. Edges are whole buildings and rise strictly."""
    edges = [k]
    if shown_sums.size:
        for quantile in BIN_QUANTILES:
            edges.append(max(int(np.quantile(shown_sums, quantile)), edges[-1] + 1))
    while len(edges) < len(GROWTH_COLORS):
        edges.append(edges[-1] + 1)
    upper: list[int | None] = [*edges[1:], None]
    return [GrowthBin(low, high, rgb) for low, high, rgb in zip(edges, upper, GROWTH_COLORS, strict=True)]


def colorize_growth(
    value: npt.NDArray[np.float32], shown: npt.NDArray[np.bool_], bins: list[GrowthBin]
) -> npt.NDArray[np.uint8]:
    """RGBA image. Pixels in hidden blocks are fully transparent."""
    image = np.zeros((*value.shape, 4), dtype=np.uint8)
    for spec in bins:
        in_bin = shown & (value >= spec.min_buildings)
        if spec.max_buildings is not None:
            in_bin &= value < spec.max_buildings
        image[in_bin] = (*spec.rgb, GROWTH_ALPHA)
    return image
