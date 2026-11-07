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
from pipeline.lib.validation_metrics import LABELS

CONFIG_PATH = ROOT / "config" / "validation.yaml"
PROCESSED = ROOT / "data" / "processed"
DESIGN_PATH = PROCESSED / "validation_design.csv"
META_PATH = PROCESSED / "validation_sample_meta.json"
SHEET_PATH = PROCESSED / "labeling_sheet.csv"
RESULT_PATH = PROCESSED / "validation_result.json"
SHEET_COLUMNS = ["cell_id", "latitude", "longitude", "earth_link", "satellite_link", "label"]


class ValidationConfig(BaseModel):
    return_period: int
    n_random: int
    n_flagged: int
    flag_threshold: float
    seed: int
    imagery_source: str
    imagery_dates: str


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


def read_sheet_labels(path: Path) -> list[tuple[str, str]]:
    """Return (cell_id, label) in sheet order. Raise when a label is blank or not allowed."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [(r["cell_id"], r["label"].strip()) for r in csv.DictReader(handle)]
    blank = [cell_id for cell_id, label in rows if not label]
    if blank:
        raise ValueError(f"{len(blank)} cells have no label yet, first: {blank[0]}")
    bad = sorted({label for _, label in rows if label not in LABELS})
    if bad:
        raise ValueError(f"Unknown labels {bad}. Allowed: {sorted(LABELS)}")
    return rows


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    loaded: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
    return loaded
