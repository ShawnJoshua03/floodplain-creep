import math
from pathlib import Path

from pipeline.io.validation_files import CAPTURE_COLUMNS, write_capture_rows
from pipeline.lib.webmerc import (
    crop_box,
    lonlat_to_tile_fraction,
    metres_per_pixel,
    plan_mosaic,
    square_side_px,
    tile_coordinates,
)


def test_known_tile_for_dhaka_at_zoom_18() -> None:
    x, y = lonlat_to_tile_fraction(90.462947, 23.724677, 18)
    assert (math.floor(x), math.floor(y)) == (196945, 113280)


def test_metres_per_pixel_shrinks_with_latitude_and_zoom() -> None:
    assert metres_per_pixel(0.0, 0) > metres_per_pixel(60.0, 0)
    assert metres_per_pixel(23.7, 18) == metres_per_pixel(23.7, 17) / 2
    assert round(metres_per_pixel(23.7, 18), 2) == 0.55


def test_mosaic_plan_centres_the_point() -> None:
    plan = plan_mosaic(90.462947, 23.724677, 18, radius=1)
    assert plan.tiles_per_side == 3
    assert (plan.first_x, plan.first_y) == (196944, 113279)
    assert 256 <= plan.centre_px[0] < 512
    assert 256 <= plan.centre_px[1] < 512
    coords = tile_coordinates(plan)
    assert len(coords) == 9
    assert coords[0] == (196944, 113279, 0, 0)
    assert coords[-1] == (196946, 113281, 2, 2)


def test_cell_side_and_crop_box() -> None:
    assert round(square_side_px(100.0, 23.7, 18)) == 183
    assert crop_box((384.0, 384.0), 320) == (224, 224, 544, 544)


def test_capture_rows_keep_other_cells(tmp_path: Path) -> None:
    path = tmp_path / "captures.csv"
    write_capture_rows([["b", "2017-02-25", "Metro", "0.31", "2023-11-10", "Vivid", "0.5"]], path)
    write_capture_rows([["a", "", "", "", "", "", ""], ["b", "2018-01-01", "X", "0.3", "2023-11-10", "V", "0.5"]], path)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0].split(",") == CAPTURE_COLUMNS
    assert [line.split(",")[0] for line in lines[1:]] == ["a", "b"]
    assert "2018-01-01" in lines[2]
