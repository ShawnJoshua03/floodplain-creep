import re

from pipeline.io.city_config import ROOT
from pipeline.lib.density import GROWTH_COLORS

TOKENS = ROOT / "web" / "src" / "styles" / "tokens.css"


def test_growth_colors_match_the_growth_ramp_tokens() -> None:
    css = TOKENS.read_text(encoding="utf-8")
    ramp = [match.lower() for match in re.findall(r"--ramp-growth-\d:\s*(#[0-9a-fA-F]{6})", css)]
    assert ramp == [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in GROWTH_COLORS]
