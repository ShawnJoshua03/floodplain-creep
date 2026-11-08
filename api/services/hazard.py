"""Modeled flood depth overlay: image location, bounds, and depth bins."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from api.core.errors import NotFoundError
from api.core.settings import Settings
from api.schemas.hazard import OverlayInfo, OverlayManifest
from api.services.choices import require_return_period

MANIFEST_NAME = "overlays.json"
OVERLAY_URL_PREFIX = "/overlays"
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
    if filename not in read_manifest(settings).images.values():
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
