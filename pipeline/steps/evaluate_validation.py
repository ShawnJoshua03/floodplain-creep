"""Compute validation metrics from the labeled sheet.

Run: uv run python -m pipeline.steps.evaluate_validation
The first 60 percent of labels (sheet order) pick the change threshold. Metrics come from the rest.
"""

from __future__ import annotations

from pipeline.io.validation_files import (
    DESIGN_PATH,
    META_PATH,
    RESULT_PATH,
    SHEET_PATH,
    load_validation_config,
    read_changes,
    read_json,
    read_sheet_labels,
    write_json,
)
from pipeline.lib.validation_metrics import (
    UNCLEAR,
    Confusion,
    Estimate,
    LabeledCell,
    accuracy,
    confusion,
    precision,
    recall,
    split_labeled,
    tune_threshold,
)


def estimate_dict(value: Estimate) -> dict[str, object]:
    return {"value": value.value, "low": value.low, "high": value.high, "n": value.n}


def confusion_dict(value: Confusion) -> dict[str, int]:
    return {"tp": value.tp, "fp": value.fp, "fn": value.fn, "tn": value.tn}


def main() -> None:
    settings = load_validation_config()
    if not settings.imagery_source.strip() or not settings.imagery_dates.strip():
        raise ValueError("Fill imagery_source and imagery_dates in config/validation.yaml before evaluating")
    changes = read_changes(DESIGN_PATH)
    rows = read_sheet_labels(SHEET_PATH)
    usable = [LabeledCell(cell_id, label, changes[cell_id]) for cell_id, label in rows if label != UNCLEAR]
    excluded = len(rows) - len(usable)
    tune, test = split_labeled(usable)
    threshold = tune_threshold(tune)
    result = confusion(test, threshold)
    meta = read_json(META_PATH)
    write_json(
        RESULT_PATH,
        {
            "labeled_cells": len(rows),
            "excluded_unclear": excluded,
            "tuning_cells": len(tune),
            "test_cells": len(test),
            "change_threshold_buildings": threshold,
            "confusion": confusion_dict(result),
            "accuracy": estimate_dict(accuracy(result)),
            "precision": estimate_dict(precision(result)),
            "recall": estimate_dict(recall(result)),
            "sampling_note": meta["sampling_note"],
            "imagery_source": settings.imagery_source,
            "imagery_dates": settings.imagery_dates,
            "start_year": meta["start_year"],
            "end_year": meta["end_year"],
        },
    )
    print(f"Threshold {threshold:g} buildings (tuned on {len(tune)}), test on {len(test)}, unclear {excluded}")
    print(f"accuracy={accuracy(result).value} precision={precision(result).value} recall={recall(result).value}")


if __name__ == "__main__":
    main()
