"""Sum fine pixels into coarser blocks without losing building counts."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

BAND_COUNT, BAND_HEIGHT, BAND_PRESENCE = 0, 1, 2


def aggregate_blocks(pixels: npt.NDArray[np.float32], factor: int, nodata: float) -> npt.NDArray[np.float32]:
    """Reduce (3, h, w) pixels by `factor`.

    Fractional count is summed so totals are kept. Height and presence use the maximum.
    A block with only nodata pixels stays nodata.
    """
    bands, rows, cols = pixels.shape
    if rows % factor or cols % factor:
        raise ValueError(f"Shape {rows}x{cols} is not a multiple of factor {factor}")
    blocks = pixels.reshape(bands, rows // factor, factor, cols // factor, factor)
    valid = blocks != nodata
    summed = np.where(valid, blocks, 0.0).sum(axis=(2, 4), dtype=np.float64)
    largest = np.where(valid, blocks, -np.inf).max(axis=(2, 4))
    any_valid = valid.any(axis=(2, 4))
    out = np.where(any_valid, largest, nodata)
    out[BAND_COUNT] = np.where(any_valid[BAND_COUNT], summed[BAND_COUNT], nodata)
    return out.astype(np.float32)
