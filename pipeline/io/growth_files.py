"""Render smoothed building density per year to Web Mercator PNG images and a manifest the API reads."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import numpy.typing as npt
from PIL import Image
from rasterio.transform import Affine, from_bounds
from rasterio.warp import Resampling, reproject, transform_bounds

from pipeline.io.cell_store import CellStore
from pipeline.io.overlay_files import PIXEL_M, WEB_MERCATOR
from pipeline.lib.density import GrowthBin, block_sums, colorize_growth, growth_bins
from pipeline.lib.suppression import suppress_blocks

SHOWN_LEVEL = 0.5


def _smooth(blocks: npt.NDArray[np.float64], block: int, rows: int, cols: int) -> npt.NDArray[np.float32]:
    """Blend block values bilinearly up to cell size so no single block can be read off the image."""
    size = (blocks.shape[1] * block, blocks.shape[0] * block)
    big = Image.fromarray(blocks.astype(np.float32), mode="F").resize(size, Image.Resampling.BILINEAR)
    return np.asarray(big, dtype=np.float32)[:rows, :cols]


def _to_mercator(layer: npt.NDArray[np.float32], store: CellStore, lonlat_bbox: list[float]) -> npt.NDArray[np.float32]:
    left, bottom, right, top = transform_bounds("EPSG:4326", WEB_MERCATOR, *lonlat_bbox)
    width = round((right - left) / PIXEL_M)
    height = round((top - bottom) / PIXEL_M)
    out = np.zeros((height, width), dtype=np.float32)
    grid = store.grid
    reproject(
        source=layer,
        destination=out,
        src_transform=Affine(grid.cell_m, 0, grid.left, 0, -grid.cell_m, grid.top),
        src_crs=grid.crs,
        dst_transform=from_bounds(left, bottom, right, top, width, height),
        dst_crs=WEB_MERCATOR,
        resampling=Resampling.bilinear,
    )
    return out


def render_growth(
    store: CellStore, return_period: int, lonlat_bbox: list[float], block: int, k: int, out_dir: Path
) -> tuple[list[GrowthBin], dict[int, str]]:
    """Write one image per year for a return period. Returns the bins and the file name by year."""
    flooded = store.flooded[store.return_periods.index(return_period)]
    sums = [block_sums(store.counts[i], flooded, block) for i in range(len(store.years))]
    last = sums[-1]
    bins = growth_bins(last[suppress_blocks(last, k)], k)
    rows, cols = flooded.shape
    names: dict[int, str] = {}
    for year, year_sums in zip(store.years, sums, strict=True):
        shown = suppress_blocks(year_sums, k).astype(np.float32)
        weighted = _to_mercator(_smooth(year_sums * shown, block, rows, cols), store, lonlat_bbox)
        weight = _to_mercator(_smooth(shown.astype(np.float64), block, rows, cols), store, lonlat_bbox)
        visible = weight >= SHOWN_LEVEL
        value = np.divide(weighted, weight, out=np.zeros_like(weighted), where=visible)
        name = f"growth_rp{return_period}_{year}.png"
        Image.fromarray(colorize_growth(value, visible, bins), mode="RGBA").save(out_dir / name)
        names[year] = name
    return bins, names


def write_growth_manifest(
    out_dir: Path, lonlat_bbox: list[float], block_m: int, entries: dict[int, tuple[list[GrowthBin], dict[int, str]]]
) -> None:
    manifest = {
        "bounds": lonlat_bbox,
        "block_m": block_m,
        "return_periods": {
            str(return_period): {
                "bins": [
                    {"min_buildings": b.min_buildings, "max_buildings": b.max_buildings, "color": b.hex} for b in bins
                ],
                "images": {str(year): name for year, name in names.items()},
            }
            for return_period, (bins, names) in entries.items()
        },
    }
    (out_dir / "growth.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
