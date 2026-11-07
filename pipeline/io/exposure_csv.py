"""Write the published neighborhood table. Columns hold neighborhood totals only."""

from __future__ import annotations

import csv
from pathlib import Path

from pipeline.lib.suppression import ExposureRow

COLUMNS = [
    "neighborhood_id",
    "year",
    "return_period",
    "buildings_in_zone",
    "new_buildings_in_zone",
    "growth_pct",
    "suppressed",
    "change_available",
]


def blank_if_none(value: object) -> object:
    return "" if value is None else value


def write_exposure_csv(path: Path, rows: list[ExposureRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for row in rows:
            growth = None if row.growth_pct is None else round(row.growth_pct, 1)
            writer.writerow(
                [
                    row.neighborhood_id,
                    row.year,
                    row.return_period,
                    blank_if_none(row.buildings_in_zone),
                    blank_if_none(row.new_buildings_in_zone),
                    blank_if_none(growth),
                    str(row.suppressed).lower(),
                    str(row.change_available).lower(),
                ]
            )


def optional_int(text: str) -> int | None:
    return int(text) if text else None


def read_exposure_csv(path: Path) -> list[ExposureRow]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            raise ValueError(f"Unexpected columns in {path}: {reader.fieldnames}")
        return [
            ExposureRow(
                neighborhood_id=r["neighborhood_id"],
                year=int(r["year"]),
                return_period=int(r["return_period"]),
                buildings_in_zone=optional_int(r["buildings_in_zone"]),
                new_buildings_in_zone=optional_int(r["new_buildings_in_zone"]),
                growth_pct=float(r["growth_pct"]) if r["growth_pct"] else None,
                suppressed=r["suppressed"] == "true",
                change_available=r["change_available"] == "true",
            )
            for r in reader
        ]
