"""Write and read the published change-balance table. Columns hold cell counts per neighborhood only."""

from __future__ import annotations

import csv
from pathlib import Path

from pipeline.lib.suppression import BalanceRow

COLUMNS = ["neighborhood_id", "return_period", "cells_in_zone", "cells_gaining", "cells_losing", "suppressed"]


def blank_if_none(value: object) -> object:
    return "" if value is None else value


def optional_int(text: str) -> int | None:
    return int(text) if text else None


def write_balance_csv(path: Path, rows: list[BalanceRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow(
                [
                    blank_if_none(row.neighborhood_id),
                    row.return_period,
                    blank_if_none(row.cells_in_zone),
                    blank_if_none(row.cells_gaining),
                    blank_if_none(row.cells_losing),
                    str(row.suppressed).lower(),
                ]
            )


def read_balance_csv(path: Path) -> list[BalanceRow]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            raise ValueError(f"Unexpected columns in {path}: {reader.fieldnames}")
        return [
            BalanceRow(
                neighborhood_id=r["neighborhood_id"] or None,
                return_period=int(r["return_period"]),
                cells_in_zone=optional_int(r["cells_in_zone"]),
                cells_gaining=optional_int(r["cells_gaining"]),
                cells_losing=optional_int(r["cells_losing"]),
                suppressed=r["suppressed"] == "true",
            )
            for r in reader
        ]
