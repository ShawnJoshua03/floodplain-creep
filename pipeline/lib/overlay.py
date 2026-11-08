"""Depth bins and colors for the modeled flood overlay. Built from depth values only, never from buildings."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

OVERLAY_ALPHA = 190


@dataclass(frozen=True)
class DepthBinSpec:
    min_depth_m: float
    max_depth_m: float | None
    rgb: tuple[int, int, int]

    @property
    def hex(self) -> str:
        red, green, blue = self.rgb
        return f"#{red:02x}{green:02x}{blue:02x}"


DEPTH_BINS = [
    DepthBinSpec(0.1, 0.5, (158, 202, 225)),
    DepthBinSpec(0.5, 1.0, (107, 174, 214)),
    DepthBinSpec(1.0, 2.0, (49, 130, 189)),
    DepthBinSpec(2.0, None, (8, 69, 148)),
]


def colorize(depth: npt.NDArray[np.float32], zone: npt.NDArray[np.bool_]) -> npt.NDArray[np.uint8]:
    """RGBA image. Pixels outside the flood zone are fully transparent."""
    image = np.zeros((*depth.shape, 4), dtype=np.uint8)
    for spec in DEPTH_BINS:
        in_bin = zone & (depth >= spec.min_depth_m)
        if spec.max_depth_m is not None:
            in_bin &= depth < spec.max_depth_m
        image[in_bin] = (*spec.rgb, OVERLAY_ALPHA)
    return image
