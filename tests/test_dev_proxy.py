import re

from api.main import app
from pipeline.io.city_config import ROOT

VITE_CONFIG = ROOT / "web" / "vite.config.ts"


def proxied_paths() -> set[str]:
    text = VITE_CONFIG.read_text(encoding="utf-8")
    listed = re.search(r"const API_PATHS = \[(.*?)\];", text, flags=re.DOTALL)
    assert listed is not None, "vite.config.ts must define API_PATHS"
    return set(re.findall(r'"(/[^"]*)"', listed.group(1)))


def test_every_api_route_is_proxied_by_the_dev_server() -> None:
    """A route missing here answers with the web page's HTML, and the app reports that it cannot reach its data."""
    first_segments = {"/" + path.strip("/").split("/")[0] for path in app.openapi()["paths"]}
    assert first_segments <= proxied_paths(), first_segments - proxied_paths()


def test_the_dev_server_proxies_no_route_the_api_does_not_have() -> None:
    first_segments = {"/" + path.strip("/").split("/")[0] for path in app.openapi()["paths"]}
    assert proxied_paths() <= first_segments, proxied_paths() - first_segments
