import json
from pathlib import Path

import numpy as np

from pipeline.io.overlay_files import write_manifest
from pipeline.lib.overlay import DEPTH_BINS, OVERLAY_ALPHA, colorize


def test_colorize_picks_a_bin_by_depth() -> None:
    depth = np.array([[0.2, 0.7, 1.5, 3.0]], dtype=np.float32)
    image = colorize(depth, np.ones_like(depth, dtype=np.bool_))
    for index, spec in enumerate(DEPTH_BINS):
        assert tuple(image[0, index]) == (*spec.rgb, OVERLAY_ALPHA)


def test_colorize_leaves_pixels_outside_the_zone_transparent() -> None:
    depth = np.array([[0.2, 3.0]], dtype=np.float32)
    zone = np.array([[True, False]])
    image = colorize(depth, zone)
    assert image[0, 1, 3] == 0


def test_bins_do_not_overlap_or_leave_gaps() -> None:
    for lower, upper in zip(DEPTH_BINS, DEPTH_BINS[1:], strict=False):
        assert lower.max_depth_m == upper.min_depth_m
    assert DEPTH_BINS[-1].max_depth_m is None


def test_manifest_lists_bins_and_images(tmp_path: Path) -> None:
    write_manifest(tmp_path, [1.0, 2.0, 3.0, 4.0], {100: "depth_rp100.png"})
    manifest = json.loads((tmp_path / "overlays.json").read_text(encoding="utf-8"))
    assert manifest["images"] == {"100": "depth_rp100.png"}
    assert manifest["bins"][0]["color"] == DEPTH_BINS[0].hex
