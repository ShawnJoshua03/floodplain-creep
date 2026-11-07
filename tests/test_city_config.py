from pathlib import Path

import pytest
from pydantic import ValidationError

from pipeline.io.city_config import load_city_config

BASE = """\
city: X
min_count_k: 20
years: [2016, 2018]
return_periods: [100]
grid_size_m: 100
presence_threshold: 0.45
min_depth_m: 0.1
min_coverage: 0.5
"""


def write(tmp_path: Path, bbox: str) -> Path:
    path = tmp_path / "city.yaml"
    path.write_text(BASE + f"bbox: {bbox}\n", encoding="utf-8")
    return path


def test_valid_config_loads(tmp_path: Path) -> None:
    config = load_city_config(write(tmp_path, "[1.0, 2.0, 3.0, 4.0]"))
    assert list(config.year_range) == [2016, 2017, 2018]
    assert config.lonlat_bounds.right == 3.0


@pytest.mark.parametrize("bbox", ["[1.0, 2.0, 3.0]", "[3.0, 2.0, 1.0, 4.0]", "[1.0, 4.0, 3.0, 2.0]"])
def test_bad_bbox_is_rejected(tmp_path: Path, bbox: str) -> None:
    with pytest.raises(ValidationError):
        load_city_config(write(tmp_path, bbox))


def test_repo_config_loads() -> None:
    assert load_city_config().min_count_k == 20
