import psycopg
from fastapi.testclient import TestClient

from tests.api_support import VALIDATION_PAYLOAD


def features_by_id(client: TestClient, **params: int) -> dict[str, dict[str, object]]:
    response = client.get("/neighborhoods", params=params)
    assert response.status_code == 200
    return {f["properties"]["neighborhood_id"]: f["properties"] for f in response.json()["features"]}


def store_brief(conn: psycopg.Connection, text: str) -> None:
    conn.execute(
        "INSERT INTO briefs (neighborhood_id, return_period, text, source) VALUES ('n1', 100, %s, 'template')",
        (text,),
    )
    conn.commit()


def test_normal_neighborhood_returns_counts(client: TestClient) -> None:
    shown = features_by_id(client, return_period=100, year=2023)["n1"]
    assert shown["buildings_in_zone"] == 120
    assert shown["new_buildings_in_zone"] == 40
    assert shown["growth_pct"] == 50.0
    assert shown["suppressed"] is False
    assert shown["change_available"] is True


def test_suppressed_neighborhood_returns_null_counts(client: TestClient) -> None:
    hidden = features_by_id(client, return_period=100, year=2023)["n2"]
    assert hidden["suppressed"] is True
    assert hidden["buildings_in_zone"] is None
    assert hidden["new_buildings_in_zone"] is None
    assert hidden["growth_pct"] is None


def test_city_summary_counts_shown_and_suppressed(client: TestClient) -> None:
    body = client.get("/city/summary", params={"return_period": 100}).json()
    assert body["city"] == "Dhaka"
    assert body["return_periods"] == [10, 50, 100, 500]
    assert body["min_count_k"] == 20
    by_year = {row["year"]: row for row in body["years"]}
    assert by_year[2023]["buildings_in_zone"] == 120
    assert by_year[2023]["new_buildings_in_zone"] == 40
    assert by_year[2023]["neighborhoods_shown"] == 1
    assert by_year[2023]["neighborhoods_suppressed"] == 1


def test_unsupported_return_period_is_rejected(client: TestClient) -> None:
    assert client.get("/neighborhoods", params={"return_period": 25, "year": 2023}).status_code == 422
    assert client.get("/city/summary", params={"return_period": 25}).status_code == 422


def test_year_outside_the_data_years_is_rejected(client: TestClient) -> None:
    assert client.get("/neighborhoods", params={"return_period": 100, "year": 2017}).status_code == 422


def test_validation_returns_the_stored_result(client: TestClient) -> None:
    body = client.get("/validation").json()
    for key in ("accuracy", "precision", "recall", "sampling_note", "label_sources"):
        assert body[key] == VALIDATION_PAYLOAD[key]


def test_validation_is_not_found_when_nothing_is_stored(client: TestClient, conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM validation_result")
    conn.commit()
    assert client.get("/validation").status_code == 404


def test_brief_is_served_from_storage(client: TestClient, conn: psycopg.Connection) -> None:
    store_brief(conn, "New buildings in the modeled flood zone grew by 40.")
    body = client.get("/brief/n1", params={"return_period": 100}).json()
    assert body["source"] == "template"
    assert "40" in body["text"]


def test_missing_brief_and_unknown_neighborhood_are_not_found(client: TestClient) -> None:
    assert client.get("/brief/n1", params={"return_period": 100}).status_code == 404
    assert client.get("/brief/nope", params={"return_period": 100}).status_code == 404


def test_overlay_info_and_image(client: TestClient) -> None:
    body = client.get("/hazard/overlay", params={"return_period": 100}).json()
    assert body["image_url"] == "/overlays/depth_rp100.png"
    assert len(body["bounds"]) == 4
    assert body["bins"][0]["min_depth_m"] == 0.1
    assert "Simulated" in body["label"]
    image = client.get(body["image_url"])
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"


def test_overlay_for_a_missing_return_period_is_not_found(client: TestClient) -> None:
    assert client.get("/hazard/overlay", params={"return_period": 500}).status_code == 404


def test_only_manifest_images_are_served(client: TestClient) -> None:
    assert client.get("/overlays/overlays.json").status_code == 404
    assert client.get("/overlays/unknown.png").status_code == 404
