"""Load processed neighborhood results into PostgreSQL with one command.

Run: uv run --env-file .env python -m pipeline.steps.load_database
Needs DATABASE_URL. Cell-level files (cells.npz, validation_design.csv) are never read here.
"""

from __future__ import annotations

import os

from pipeline.io.balance_csv import read_balance_csv
from pipeline.io.city_config import ROOT, load_city_config
from pipeline.io.database import (
    add_validation_result,
    apply_schema,
    connect,
    load_neighborhoods,
    replace_balance,
    replace_exposure,
)
from pipeline.io.exposure_csv import read_exposure_csv
from pipeline.io.validation_files import RESULT_PATH, read_json
from pipeline.lib.suppression import check_rows

PROCESSED = ROOT / "data" / "processed"


def main() -> None:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
    config = load_city_config()
    rows = read_exposure_csv(PROCESSED / "neighborhood_year_exposure.csv")
    check_rows(rows, config.min_count_k)
    with connect(url) as conn:
        apply_schema(conn)
        neighborhoods = load_neighborhoods(conn, PROCESSED / "neighborhoods.geojson")
        exposure = replace_exposure(conn, rows)
        balance = replace_balance(conn, read_balance_csv(PROCESSED / "neighborhood_change_balance.csv"))
        validated = RESULT_PATH.exists()
        if validated:
            add_validation_result(conn, read_json(RESULT_PATH))
        conn.commit()
    print(f"Loaded {neighborhoods} neighborhoods, {exposure} exposure rows and {balance} balance rows")
    print("Added a validation result" if validated else "No validation result yet, skipped")


if __name__ == "__main__":
    main()
