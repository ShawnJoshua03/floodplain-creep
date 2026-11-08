"""Modeled flood depth overlay: image location, bounds, and depth bins."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from api.core.errors import NotFoundError
from api.core.settings import Settings
from api.schemas.hazard import GrowthInfo, GrowthManifest, OverlayInfo, OverlayManifest, WaterLayer
from api.services.choices import require_return_period

MANIFEST_NAME = "overlays.json"
CONTEXT_NAME = "context.json"
GROWTH_NAME = "growth.json"
OVERLAY_URL_PREFIX = "/overlays"
GROWTH_LABEL = "Buildings in the modeled flood zone, blended from blocks. Blocks with too few buildings are hidden."
OVERLAY_LABEL = "Modeled river flood depth. Simulated scenario, not a forecast."


def read_manifest(settings: Settings) -> OverlayManifest:
    path = settings.overlay_dir / MANIFEST_NAME
    if not path.exists():
        raise NotFoundError("Overlay images are not rendered yet. Run pipeline.steps.render_overlays.")
    try:
        return OverlayManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ValidationError) as error:
        raise NotFoundError(f"Overlay manifest is not readable: {error}") from error


def overlay_image_path(settings: Settings, filename: str) -> Path:
    """Only files named in the manifest are served, so a request cannot reach other files."""
    allowed = set(read_manifest(settings).images.values())
    growth = _read_growth(settings)
    if growth is not None:
        allowed.update(name for item in growth.return_periods.values() for name in item.images.values())
    if filename not in allowed:
        raise NotFoundError("Unknown overlay image.")
    return settings.overlay_dir / filename


def overlay_info(settings: Settings, return_period: int) -> OverlayInfo:
    require_return_period(settings, return_period)
    manifest = read_manifest(settings)
    filename = manifest.images.get(str(return_period))
    if filename is None:
        raise NotFoundError(f"No overlay image for return period {return_period}.")
    return OverlayInfo(
        return_period=return_period,
        image_url=f"{OVERLAY_URL_PREFIX}/{filename}",
        bounds=manifest.bounds,
        bins=manifest.bins,
        label=OVERLAY_LABEL,
    )


def water_layer(settings: Settings) -> WaterLayer:
    path = settings.overlay_dir / CONTEXT_NAME
    if not path.exists():
        raise NotFoundError("The map context is not rendered yet. Run pipeline.steps.render_overlays.")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        return WaterLayer(label=loaded["label"], geometry=loaded["water"])
    except (json.JSONDecodeError, KeyError, ValidationError) as error:
        raise NotFoundError(f"The map context is not readable: {error}") from error


def _read_growth(settings: Settings) -> GrowthManifest | None:
    path = settings.overlay_dir / GROWTH_NAME
    if not path.exists():
        return None
    try:
        return GrowthManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ValidationError) as error:
        raise NotFoundError(f"Growth manifest is not readable: {error}") from error


def growth_info(settings: Settings, return_period: int) -> GrowthInfo:
    require_return_period(settings, return_period)
    manifest = _read_growth(settings)
    item = manifest.return_periods.get(str(return_period)) if manifest else None
    if manifest is None or item is None:
        raise NotFoundError("Growth images are not rendered yet. Run pipeline.steps.render_growth.")
    return GrowthInfo(
        return_period=return_period,
        bounds=manifest.bounds,
        block_m=manifest.block_m,
        bins=item.bins,
        image_urls={year: f"{OVERLAY_URL_PREFIX}/{name}" for year, name in item.images.items()},
        label=GROWTH_LABEL,
    )
