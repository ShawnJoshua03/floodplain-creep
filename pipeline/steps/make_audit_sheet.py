"""Draw a random audit sample for a person to label blind.

Run: uv run python -m pipeline.steps.make_audit_sheet
Output: data/processed/audit_sheet.csv, same columns as the labeling sheet and an empty label.
The person labels these cells without seeing the AI labels. Never overwrites an existing audit sheet.
"""

from __future__ import annotations

from pipeline.io.validation_files import (
    AUDIT_PATH,
    load_validation_config,
    read_sheet_order,
    write_audit_sheet,
)
from pipeline.lib.label_merge import draw_audit


def main() -> None:
    settings = load_validation_config()
    if AUDIT_PATH.exists():
        raise FileExistsError(f"{AUDIT_PATH} exists. Delete it deliberately to redraw: labels would be lost.")
    ids = draw_audit(read_sheet_order(), settings.audit_size, settings.seed + 1)
    write_audit_sheet(AUDIT_PATH, ids)
    print(f"Wrote {len(ids)} audit cells to {AUDIT_PATH.name}")


if __name__ == "__main__":
    main()
