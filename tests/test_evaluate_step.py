import csv
import json
from pathlib import Path

import pytest

from pipeline.io.validation_files import ValidationConfig
from pipeline.steps import evaluate_validation

CONFIG = ValidationConfig(
    return_period=100,
    n_random=10,
    n_flagged=5,
    flag_threshold=10.0,
    seed=1,
    imagery_source="test imagery",
    imagery_dates="start 2016, end 2023",
)


def label_for(change: float) -> str:
    return "increase" if change >= 10 else "no_clear_change"


def build_files(tmp_path: Path) -> None:
    changes = [float(v) for v in range(-5, 25)]
    with (tmp_path / "design.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["cell_id", "row", "col", "sample_type", "change"])
        writer.writerows([f"c{i}", i, i, "random", v] for i, v in enumerate(changes))
    with (tmp_path / "sheet.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["cell_id", "latitude", "longitude", "earth_link", "satellite_link", "label"])
        for i, v in enumerate(changes):
            label = "unclear" if i in (3, 17) else label_for(v)
            writer.writerow([f"c{i}", 0, 0, "", "", label])
    (tmp_path / "meta.json").write_text(
        json.dumps({"sampling_note": "note", "start_year": 2016, "end_year": 2023}), encoding="utf-8"
    )


def point_step_at(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, config: ValidationConfig) -> None:
    monkeypatch.setattr(evaluate_validation, "DESIGN_PATH", tmp_path / "design.csv")
    monkeypatch.setattr(evaluate_validation, "SHEET_PATH", tmp_path / "sheet.csv")
    monkeypatch.setattr(evaluate_validation, "META_PATH", tmp_path / "meta.json")
    monkeypatch.setattr(evaluate_validation, "RESULT_PATH", tmp_path / "result.json")
    monkeypatch.setattr(evaluate_validation, "load_validation_config", lambda: config)


def test_result_file_has_all_metrics_and_notes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_files(tmp_path)
    point_step_at(tmp_path, monkeypatch, CONFIG)
    evaluate_validation.main()
    result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert result["labeled_cells"] == 30
    assert result["excluded_unclear"] == 2
    assert result["tuning_cells"] + result["test_cells"] == 28
    assert result["change_threshold_buildings"] == 10.0
    for name in ("accuracy", "precision", "recall"):
        assert set(result[name]) == {"value", "low", "high", "n"}
    assert result["accuracy"]["value"] == 1.0
    assert result["sampling_note"] == "note"
    assert result["imagery_source"] == "test imagery"


def test_blank_imagery_source_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_files(tmp_path)
    point_step_at(tmp_path, monkeypatch, CONFIG.model_copy(update={"imagery_source": " "}))
    with pytest.raises(ValueError, match="imagery_source"):
        evaluate_validation.main()
