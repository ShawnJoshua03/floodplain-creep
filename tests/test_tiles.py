import pytest

from pipeline.lib.tiles import (
    Bounds,
    GeoCollection,
    Manifest,
    flood_file_name,
    flood_tile_for_point,
    flood_tiles,
    manifest_matches,
    overlap,
    pixel_window,
    snap_bounds,
    tile_url,
    tiles_in_bounds,
    utm_epsg,
)

MANIFEST = {
    "uriPrefix": "gs://open-buildings-temporal-data/v1/geotiffs/18",
    "tilesets": [
        {
            "sources": [
                {
                    "uris": ["aa_2016_06_30/tile_one.tif"],
                    "affineTransform": {"scaleX": 0.5, "translateX": 0.0, "scaleY": -0.5, "translateY": 100.0},
                    "dimensions": {"width": 100, "height": 100},
                },
                {
                    "uris": ["aa_2016_06_30/tile_two.tif"],
                    "affineTransform": {"scaleX": 0.5, "translateX": 500.0, "scaleY": -0.5, "translateY": 100.0},
                    "dimensions": {"width": 100, "height": 100},
                },
            ]
        }
    ],
}


def test_utm_zone_for_nairobi_is_37_south() -> None:
    assert utm_epsg(36.82, -1.29) == 32737
    assert utm_epsg(10.0, 50.0) == 32632


def test_manifest_name_match() -> None:
    assert manifest_matches("v1/manifests/19_EPSG_32737_2016_06_30.json", 32737, 2016)
    assert not manifest_matches("v1/manifests/19_EPSG_32737_2017_06_30.json", 32737, 2016)
    assert not manifest_matches("v1/manifests/19_EPSG_32637_2016_06_30.json", 32737, 2016)


def test_tile_url_maps_gcs_to_https() -> None:
    url = tile_url("gs://open-buildings-temporal-data/v1/geotiffs/18", "dcc_2016_06_30/tile_x.tif")
    assert url == "https://storage.googleapis.com/open-buildings-temporal-data/v1/geotiffs/18dcc_2016_06_30/tile_x.tif"


def test_tiles_in_bounds_selects_only_intersecting_tiles() -> None:
    manifest = Manifest.model_validate(MANIFEST)
    found = tiles_in_bounds(manifest, Bounds(10.0, 60.0, 20.0, 70.0))
    assert [t.url.rsplit("/", 1)[-1] for t in found] == ["tile_one.tif"]
    assert found[0].bounds == Bounds(0.0, 50.0, 50.0, 100.0)


def test_snap_bounds_expands_to_grid() -> None:
    assert snap_bounds(Bounds(1.0, 1.0, 9.0, 9.0), 4.0) == Bounds(0.0, 0.0, 12.0, 12.0)


def test_pixel_window_and_overlap() -> None:
    tile = Bounds(0.0, 0.0, 100.0, 100.0)
    shared = overlap(tile, Bounds(20.0, 40.0, 140.0, 80.0))
    assert shared == Bounds(20.0, 40.0, 100.0, 80.0)
    assert pixel_window(tile, shared, 0.5) == (40, 40, 160, 80)


def test_flood_tile_lookup_and_names() -> None:
    collection = GeoCollection.model_validate(
        {
            "features": [
                {
                    "properties": {"id": 151, "name": "N0_E30"},
                    "geometry": {"coordinates": [[[30, -10], [40, -10], [40, 0], [30, 0], [30, -10]]]},
                }
            ]
        }
    )
    tiles = flood_tiles(collection)
    tile = flood_tile_for_point(tiles, 36.8, -1.3)
    assert flood_file_name(tile, "RP100_depth") == "ID151_N0_E30_RP100_depth.tif"
    with pytest.raises(ValueError, match="No flood tile"):
        flood_tile_for_point(tiles, 0.0, 50.0)
