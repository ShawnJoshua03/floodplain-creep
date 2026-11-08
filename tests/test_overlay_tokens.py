import re

from pipeline.io.city_config import ROOT
from pipeline.lib.overlay import DEPTH_BINS

TOKENS = ROOT / "web" / "src" / "styles" / "tokens.css"


def test_overlay_colors_match_the_depth_ramp_tokens() -> None:
    """The overlay image is drawn in Python and the legend in CSS. One ramp, written in tokens.css."""
    css = TOKENS.read_text(encoding="utf-8")
    ramp = [match.lower() for match in re.findall(r"--ramp-depth-\d:\s*(#[0-9a-fA-F]{6})", css)]
    assert ramp == [spec.hex for spec in DEPTH_BINS]
