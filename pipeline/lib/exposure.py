"""Which cells count as flood zone for a return period."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt


def flood_zone(
    depth: npt.NDArray[np.float32],
    permanent_water: npt.NDArray[np.uint8],
    spurious_depth: npt.NDArray[np.uint8],
    depth_nodata: float,
    mask_nodata: int,
    min_depth_m: float,
) -> npt.NDArray[np.bool_]:
    """True where modeled depth reaches the minimum, away from permanent water and spurious depth."""
    wet = (depth != depth_nodata) & (depth >= min_depth_m)
    water = permanent_water != mask_nodata
    spurious = spurious_depth != mask_nodata
    return np.asarray(wet & ~water & ~spurious, dtype=np.bool_)
