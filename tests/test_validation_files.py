import csv
from pathlib import Path

import pytest

from pipeline.io.validation_files import (
    SHEET_COLUMNS,
    CellPlace,
    read_changes,
    read_sheet_labels,
    write_design,
    write_labeling_sheet,
)
from pipeline.lib.sampling import FLAGGED, RANDOM, SampledCell

CELLS = [SampledCell("r001c002", 1, 2, RANDOM, 3.5), SampledCell("r004c005", 4, 5, FLAGGED, 20.0)]
PLACES = [CellPlace(23.75, 90.4), CellPlace(23.76, 90.41)]


def write_sheet(tmp_path: Path) -> Path:
    path = tmp_path / "sheet.csv"
    write_labeling_sheet(path, CELLS, PLACES)
    return path


def test_sheet_hides_prediction_and_sample_type(tmp_path: Path) -> None:
    path = write_sheet(tmp_path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert reader.fieldnames == SHEET_COLUMNS
    text = path.read_text(encoding="utf-8")
    assert "flagged" not in text and "random" not in text
    assert "3.5" not in text and "20.0" not in text
    assert rows[0]["label"] == ""
    assert rows[0]["earth_link"].startswith("https://earth.google.com/web/@23.750000,90.400000")


def test_unlabeled_sheet_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no label yet"):
        read_sheet_labels(write_sheet(tmp_path))


def test_labeled_sheet_is_read_in_order(tmp_path: Path) -> None:
    path = write_sheet(tmp_path)
    path.write_text(path.read_text(encoding="utf-8").replace(",\r\n", ",increase\r\n", 1), encoding="utf-8", newline="")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    rows[1][-1] = "increase"
    rows[2][-1] = "unclear"
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    assert read_sheet_labels(path) == [("r001c002", "increase"), ("r004c005", "unclear")]


def test_unknown_label_is_rejected(tmp_path: Path) -> None:
    path = write_sheet(tmp_path)
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    rows[1][-1] = "growth"
    rows[2][-1] = "increase"
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    with pytest.raises(ValueError, match="Unknown labels"):
        read_sheet_labels(path)


def test_design_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "design.csv"
    write_design(path, CELLS)
    assert read_changes(path) == {"r001c002": 3.5, "r004c005": 20.0}
