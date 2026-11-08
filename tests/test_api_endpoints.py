from pathlib import Path
from typing import Any

import psycopg
from fastapi.testclient import TestClient

from tests.api_support import FOCUS_COUNTS, VALIDATION_PAYLOAD


def focus(client: TestClient, return_period: int = 100) -> dict[str, Any]:
    response = client.get("/focus", params={"return_period": return_period})
    assert response.status_code == 200
    body: dict[str, Any] = response.json()
    return body


def store_brief(conn: psycopg.Connection, text: str) -> None:
    conn.execute(
        "INSERT INTO briefs (neighborhood_id, return_period, text, source) VALUES ('n1', 100, %s, 'template')",
        (text,),
    )
    conn.commit()


def test_focus_returns_the_focus_neighborhood_and_its_yearly_counts(client: TestClient) -> None:
    body = focus(client)
    assert body["city"] == "Dhaka"
    assert body["return_periods"] == [10, 50, 100, 500]
    assert body["min_count_k"] == 20
    assert body["neighborhood"]["name"] == "One"
    series = body["series"]
    assert [row["buildings_in_zone"] for row in series] == FOCUS_COUNTS
    assert series[-1]["new_buildings_in_zone"] == 30
    assert series[-1]["growth_pct"] == 30.0


def test_signal_compares_the_change_with_the_noise_of_the_other_neighborhoods(client: TestClient) -> None:
    body = focus(client)
    assert body["noise"]["neighborhoods_used"] == 1
    assert body["signal"]["verdict"] == "clear_growth"
    assert body["signal"]["required_multiple"] == 2
    assert body["signal"]["times_typical_swing"] > 2


def test_balance_compares_the_focus_with_the_rest_of_the_city(client: TestClient) -> None:
    balance = focus(client)["balance"]
    assert balance["focus"] == {"cells_gaining": 30, "cells_losing": 5}
    assert balance["rest_of_city"] == {"cells_gaining": 11, "cells_losing": 11}
    assert balance["threshold_buildings"] == 5


def test_a_scenario_with_no_data_has_no_noise_and_not_enough_data(client: TestClient) -> None:
    body = focus(client, 10)
    assert body["noise"] is None
    assert body["signal"]["verdict"] == "not_enough_data"
    assert body["balance"] is None


def test_a_suppressed_focus_shows_null_counts_and_no_verdict(client: TestClient, conn: psycopg.Connection) -> None:
    conn.execute(
        "UPDATE neighborhood_year_exposure SET suppressed = true, buildings_in_zone = NULL,"
        " new_buildings_in_zone = NULL, growth_pct = NULL, change_available = false WHERE neighborhood_id = 'n1'"
    )
    conn.commit()
    body = focus(client)
    assert all(row["buildings_in_zone"] is None for row in body["series"])
    assert body["signal"]["verdict"] == "not_enough_data"


def test_unsupported_return_period_is_rejected(client: TestClient) -> None:
    assert client.get("/focus", params={"return_period": 25}).status_code == 422
    assert client.get("/focus", params={"return_period": "abc"}).status_code == 422


def test_a_missing_focus_neighborhood_is_not_found(client: TestClient, conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM neighborhood_change_balance")
    conn.execute("DELETE FROM neighborhood_year_exposure")
    conn.execute("DELETE FROM neighborhoods WHERE name = 'One'")
    conn.commit()
    assert client.get("/focus").status_code == 404


def test_validation_returns_the_stored_result(client: TestClient) -> None:
    body = client.get("/validation").json()
    for key in ("accuracy", "precision", "recall", "sampling_note", "label_sources"):
        assert body[key] == VALIDATION_PAYLOAD[key]


def test_validation_is_not_found_when_nothing_is_stored(client: TestClient, conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM validation_result")
    conn.commit()
    assert client.get("/validation").status_code == 404


def test_brief_is_served_from_storage(client: TestClient, conn: psycopg.Connection) -> None:
    store_brief(conn, "New buildings in the modeled flood zone grew by 30.")
    body = client.get("/brief", params={"return_period": 100}).json()
    assert body["source"] == "template"
    assert "30" in body["text"]


def test_missing_brief_is_not_found(client: TestClient) -> None:
    assert client.get("/brief", params={"return_period": 100}).status_code == 404


def test_overlay_info_and_image(client: TestClient) -> None:
    body = client.get("/hazard/overlay", params={"return_period": 100}).json()
    assert body["image_url"] == "/overlays/depth_rp100.png"
    assert len(body["bounds"]) == 4
    assert body["bins"][0]["min_depth_m"] == 0.1
    assert "Simulated" in body["label"]
    image = client.get(body["image_url"])
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"


def test_the_focus_outline_says_how_much_of_the_neighborhood_is_covered(client: TestClient) -> None:
    assert focus(client)["neighborhood"]["coverage"] == 0.9


def test_growth_is_served_as_images_with_no_cell_data(client: TestClient) -> None:
    body = client.get("/hazard/growth", params={"return_period": 100}).json()
    assert body["block_m"] == 500
    assert body["image_urls"]["2018"] == "/overlays/growth_rp100_2018.png"
    assert set(body) == {"return_period", "bounds", "block_m", "bins", "image_urls", "label"}
    assert client.get(body["image_urls"]["2018"]).headers["content-type"] == "image/png"


def test_growth_is_not_found_when_it_is_not_rendered(client: TestClient, tmp_path: Path) -> None:
    (tmp_path / "overlays" / "growth.json").unlink()
    assert client.get("/hazard/growth", params={"return_period": 100}).status_code == 404


def test_water_is_served_for_orientation_and_holds_no_buildings(client: TestClient) -> None:
    body = client.get("/hazard/water").json()
    assert body["geometry"]["type"] == "MultiPolygon"
    assert "buildings" not in str(body).lower()


def test_water_is_not_found_when_the_context_is_not_rendered(client: TestClient, tmp_path: Path) -> None:
    (tmp_path / "overlays" / "context.json").unlink()
    assert client.get("/hazard/water").status_code == 404


def test_overlay_for_a_missing_return_period_is_not_found(client: TestClient) -> None:
    assert client.get("/hazard/overlay", params={"return_period": 500}).status_code == 404


def test_only_manifest_images_are_served(client: TestClient) -> None:
    assert client.get("/overlays/overlays.json").status_code == 404
    assert client.get("/overlays/unknown.png").status_code == 404
