"""Files for the validation work: design, labeling sheet, labeled sheet, result. Local only."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel

from pipeline.io.city_config import ROOT
from pipeline.lib.sampling import SampledCell

CONFIG_PATH = ROOT / "config" / "validation.yaml"
PROCESSED = ROOT / "data" / "processed"
DESIGN_PATH = PROCESSED / "validation_design.csv"
META_PATH = PROCESSED / "validation_sample_meta.json"
SHEET_PATH = PROCESSED / "labeling_sheet.csv"
RESULT_PATH = PROCESSED / "validation_result.json"
CAPTURES_PATH = PROCESSED / "labeling_captures.csv"
AI_LABELS_PATH = PROCESSED / "ai_labels.csv"
AUDIT_PATH = PROCESSED / "audit_sheet.csv"
FINAL_LABELS_PATH = PROCESSED / "final_labels.csv"
LABEL_META_PATH = PROCESSED / "label_meta.json"
CAPTURE_COLUMNS = [
    "cell_id",
    "start_date",
    "start_source",
    "start_res_m",
    "end_date",
    "end_source",
    "end_res_m",
]
SHEET_COLUMNS = ["cell_id", "latitude", "longitude", "earth_link", "satellite_link", "label"]


class ValidationConfig(BaseModel):
    return_period: int
    n_random: int
    n_flagged: int
    flag_threshold: float
    seed: int
    imagery_source: str
    imagery_dates: str
    wayback_start_release: str = "2017-11-16"
    wayback_end_release: str = "2024-12-12"
    wayback_zoom: int = 18
    audit_size: int = 30


@dataclass(frozen=True)
class CellPlace:
    latitude: float
    longitude: float


def load_validation_config(path: Path = CONFIG_PATH) -> ValidationConfig:
    return ValidationConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def write_design(path: Path, cells: list[SampledCell]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["cell_id", "row", "col", "sample_type", "change"])
        writer.writerows([c.cell_id, c.row, c.col, c.sample_type, c.change] for c in cells)


def read_changes(path: Path) -> dict[str, float]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {r["cell_id"]: float(r["change"]) for r in csv.DictReader(handle)}


def write_labeling_sheet(path: Path, cells: list[SampledCell], places: list[CellPlace]) -> None:
    """The sheet has no algorithm output and no sample type. Row order is the shuffled sample order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(SHEET_COLUMNS)
        for cell, place in zip(cells, places, strict=True):
            lat, lon = place.latitude, place.longitude
            earth = f"https://earth.google.com/web/@{lat:.6f},{lon:.6f},0a,400d,35y,0h,0t,0r"
            satellite = f"https://www.google.com/maps/@{lat:.6f},{lon:.6f},19z/data=!3m1!1e3"
            writer.writerow([cell.cell_id, f"{lat:.6f}", f"{lon:.6f}", earth, satellite, ""])


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    loaded: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def write_capture_rows(rows: list[list[str]], path: Path = CAPTURES_PATH) -> None:
    """Save capture dates by cell id. Rows already in the file for other cells are kept."""
    merged: dict[str, list[str]] = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as handle:
            merged = {r[0]: r for r in list(csv.reader(handle))[1:]}
    merged.update({r[0]: r for r in rows})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(CAPTURE_COLUMNS)
        writer.writerows(merged[key] for key in sorted(merged))


def read_label_map(path: Path) -> dict[str, str]:
    """Return {cell_id: label} for rows that have a label. A missing file gives an empty map."""
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {r["cell_id"]: r["label"].strip() for r in csv.DictReader(handle) if r["label"].strip()}


def read_sheet_order(path: Path = SHEET_PATH) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [r["cell_id"] for r in csv.DictReader(handle)]


def write_audit_sheet(path: Path, ids: list[str], sheet_path: Path = SHEET_PATH) -> None:
    """Copy the chosen rows of the labeling sheet with an empty label column."""
    wanted = set(ids)
    with sheet_path.open(newline="", encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle) if r["cell_id"] in wanted]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(SHEET_COLUMNS)
        writer.writerows([r[c] if c != "label" else "" for c in SHEET_COLUMNS] for r in rows)


def write_final_labels(path: Path, labels: list[tuple[str, str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["cell_id", "label", "source"])
        writer.writerows(labels)


def read_final_labels(path: Path = FINAL_LABELS_PATH) -> list[tuple[str, str]]:
    """Return (cell_id, label) in sheet order."""
    with path.open(newline="", encoding="utf-8") as handle:
        return [(r["cell_id"], r["label"]) for r in csv.DictReader(handle)]
