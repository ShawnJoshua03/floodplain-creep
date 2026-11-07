import csv
from pathlib import Path

from pipeline.io.validation_files import (
    SHEET_COLUMNS,
    CellPlace,
    read_changes,
    read_final_labels,
    read_label_map,
    write_audit_sheet,
    write_design,
    write_final_labels,
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


def test_label_map_reads_only_filled_labels(tmp_path: Path) -> None:
    path = write_sheet(tmp_path)
    assert read_label_map(path) == {}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    rows[1][-1] = "increase"
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    assert read_label_map(path) == {"r001c002": "increase"}
    assert read_label_map(tmp_path / "missing.csv") == {}


def test_audit_sheet_copies_chosen_rows_with_empty_labels(tmp_path: Path) -> None:
    sheet = write_sheet(tmp_path)
    audit = tmp_path / "audit.csv"
    write_audit_sheet(audit, ["r004c005"], sheet)
    with audit.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [r["cell_id"] for r in rows] == ["r004c005"]
    assert rows[0]["label"] == ""
    assert rows[0]["latitude"] == "23.760000"


def test_final_labels_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "final.csv"
    write_final_labels(path, [("a", "increase", "ai"), ("b", "decrease", "audit")])
    assert read_final_labels(path) == [("a", "increase"), ("b", "decrease")]


def test_design_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "design.csv"
    write_design(path, CELLS)
    assert read_changes(path) == {"r001c002": 3.5, "r004c005": 20.0}
