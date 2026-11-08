"""Product hard rules as seen through the API."""

import json
import re
from typing import Any

import psycopg
import pytest
from fastapi.testclient import TestClient

from api.core.settings import CONFIG_DIR, load_settings
from api.main import app
from api.safety.banned_terms import find_banned_terms
from pipeline.io.city_config import load_city_config

CELL_LEVEL_WORDS = {"cell", "row", "col", "lat", "lon", "latitude", "longitude", "x", "y", "building"}
ALLOWED_PATHS = {
    "/focus",
    "/hazard/overlay",
    "/hazard/growth",
    "/hazard/water",
    "/overlays/{filename}",
    "/validation",
    "/brief",
    "/limits",
}
ENDPOINTS = [
    "/focus?return_period=100",
    "/hazard/overlay?return_period=100",
    "/hazard/growth?return_period=100",
    "/hazard/water",
    "/validation",
    "/limits",
]


def all_keys(node: object) -> set[str]:
    if isinstance(node, dict):
        return set(node) | {key for value in node.values() for key in all_keys(value)}
    if isinstance(node, list):
        return {key for value in node for key in all_keys(value)}
    return set()


def test_no_response_holds_cell_level_keys(client: TestClient) -> None:
    for url in ENDPOINTS:
        for key in all_keys(client.get(url).json()):
            assert not CELL_LEVEL_WORDS.intersection(re.split(r"_", key)), (url, key)


def test_the_api_exposes_no_route_that_lists_neighborhoods() -> None:
    assert set(app.openapi()["paths"]) == ALLOWED_PATHS


def test_only_the_focus_neighborhood_is_ever_returned(client: TestClient, conn: psycopg.Connection) -> None:
    assert client.get("/neighborhoods").status_code == 404
    assert client.get("/city/summary").status_code == 404
    body = client.get("/focus", params={"return_period": 100}).json()
    stored = conn.execute("SELECT geometry FROM neighborhoods WHERE name = 'One'").fetchone()
    assert stored is not None
    assert body["neighborhood"]["geometry"] == stored[0]
    text = json.dumps(body)
    assert "Two" not in text and "Three" not in text and "n2" not in text and "n3" not in text


def test_every_shown_count_reaches_k(client: TestClient) -> None:
    k = load_city_config().min_count_k
    for return_period in (10, 50, 100, 500):
        body: dict[str, Any] = client.get("/focus", params={"return_period": return_period}).json()
        for row in body["series"]:
            if row["suppressed"]:
                assert row["buildings_in_zone"] is None
            elif row["buildings_in_zone"] is not None:
                assert row["buildings_in_zone"] >= k


def test_limits_come_from_config_and_state_the_data_years(client: TestClient) -> None:
    body = client.get("/limits").json()
    assert body["misuse_notice"] == (CONFIG_DIR / "misuse_notice.txt").read_text(encoding="utf-8").strip()
    assert body["banned_terms"] == [
        line.strip() for line in (CONFIG_DIR / "banned_terms.txt").read_text(encoding="utf-8").splitlines() if line
    ]
    joined = " ".join(body["limits"])
    assert "2018 to 2023" in joined
    assert "2016 and 2017 are not used" in joined
    assert "not an official warning" in joined
    assert "river flooding only" in joined


def test_limits_text_and_overlay_label_use_neutral_language(client: TestClient) -> None:
    terms = client.get("/limits").json()["banned_terms"]
    texts = client.get("/limits").json()["limits"] + [client.get("/hazard/overlay").json()["label"]]
    for text in texts:
        assert find_banned_terms(text, terms) == [], text


def test_brief_with_a_banned_term_is_not_served(client: TestClient, conn: psycopg.Connection) -> None:
    conn.execute(
        "INSERT INTO briefs (neighborhood_id, return_period, text, source)"
        " VALUES ('n1', 100, 'Residents were evicted.', 'template')"
    )
    conn.commit()
    assert client.get("/brief", params={"return_period": 100}).status_code == 404


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("New buildings in the modeled flood zone.", []),
        ("An Illegal build.", ["illegal"]),
        ("They were evicted.", ["evict", "evicted"]),
        ("Plans to clear out the area.", ["clear out"]),
    ],
)
def test_find_banned_terms(text: str, expected: list[str]) -> None:
    terms = ["illegal", "evict", "evicted", "clear out"]
    assert find_banned_terms(text, terms) == expected


def test_settings_need_a_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        load_settings()
