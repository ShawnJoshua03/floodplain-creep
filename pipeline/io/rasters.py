"""Read, write and describe rasters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds
from rasterio.windows import Window

from pipeline.lib.grid import RasterFrame
from pipeline.lib.summary import BandRange, RasterSummary
from pipeline.lib.tiles import Bounds


def to_crs_bounds(bounds: Bounds, source_crs: str, target_crs: str) -> Bounds:
    return Bounds(*transform_bounds(source_crs, target_crs, *astuple(bounds)))


def astuple(bounds: Bounds) -> tuple[float, float, float, float]:
    return bounds.left, bounds.bottom, bounds.right, bounds.top


def read_strip(
    src: rasterio.DatasetReader, col_off: int, row_off: int, width: int, height: int
) -> npt.NDArray[np.float32]:
    window = Window(col_off, row_off, width, height)
    return np.asarray(src.read(window=window), dtype=np.float32)


@dataclass(frozen=True)
class GridSpec:
    origin: tuple[float, float]
    pixel_m: float
    crs: str
    nodata: float


def write_raster(path: Path, pixels: npt.NDArray[np.float32], grid: GridSpec, band_names: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bands, rows, cols = pixels.shape
    transform = from_origin(grid.origin[0], grid.origin[1], grid.pixel_m, grid.pixel_m)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=rows,
        width=cols,
        count=bands,
        dtype="float32",
        crs=grid.crs,
        transform=transform,
        nodata=grid.nodata,
        compress="deflate",
        tiled=True,
        blockxsize=256,
        blockysize=256,
    ) as dst:
        dst.write(pixels)
        dst.descriptions = tuple(band_names)


def describe_raster(path: Path, label: str, lonlat: Bounds | None = None) -> RasterSummary:
    """Summarise a raster, optionally only inside a lon/lat box."""
    with rasterio.open(path) as src:
        window = None
        if lonlat is not None:
            box = to_crs_bounds(lonlat, "EPSG:4326", str(src.crs))
            window = src.window(*astuple(box)).round_offsets().round_lengths()
        data = src.read(window=window, masked=True)
        names = src.descriptions
        bands = [band_range(data[i], names[i] or f"band{i + 1}") for i in range(src.count)]
        return RasterSummary(
            label=label,
            shape=(data.shape[1], data.shape[2]),
            crs=str(src.crs),
            resolution=(src.res[0], src.res[1]),
            nodata=src.nodata,
            bands=bands,
        )


def band_range(band: np.ma.MaskedArray[tuple[int, int], np.dtype[np.float32]], name: str) -> BandRange:
    valid = int(band.count())
    if valid == 0:
        return BandRange(name, float("nan"), float("nan"), 0)
    return BandRange(name, float(band.min()), float(band.max()), valid)


@dataclass(frozen=True)
class BuildingYear:
    count: npt.NDArray[np.float32]
    presence: npt.NDArray[np.float32]
    frame: RasterFrame
    nodata: float
    crs: str


def read_building_year(path: Path) -> BuildingYear:
    """Read the yearly 4 m building raster written by fetch_buildings."""
    with rasterio.open(path) as src:
        count = np.asarray(src.read(1), dtype=np.float32)
        presence = np.asarray(src.read(3), dtype=np.float32)
        frame = RasterFrame(src.transform.c, src.transform.f, src.height, src.width, src.res[0])
        return BuildingYear(count, presence, frame, float(src.nodata), str(src.crs))
