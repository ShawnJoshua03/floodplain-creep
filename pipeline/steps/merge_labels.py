"""Merge human, audit and AI labels into final_labels.csv and record how well they agree.

Run: uv run python -m pipeline.steps.merge_labels
Precedence per cell: a label typed in labeling_sheet.csv, then audit_sheet.csv, then ai_labels.csv.
"""

from __future__ import annotations

from pipeline.io.validation_files import (
    AI_LABELS_PATH,
    AUDIT_PATH,
    FINAL_LABELS_PATH,
    LABEL_META_PATH,
    SHEET_PATH,
    read_label_map,
    read_sheet_order,
    write_final_labels,
    write_json,
)
from pipeline.lib.label_merge import ai_human_agreement, merge_labels


def main() -> None:
    sheet = read_label_map(SHEET_PATH)
    audit = read_label_map(AUDIT_PATH)
    ai = read_label_map(AI_LABELS_PATH)
    final = merge_labels(read_sheet_order(), sheet, audit, ai)
    write_final_labels(FINAL_LABELS_PATH, [(f.cell_id, f.label, f.source) for f in final])
    agreement = ai_human_agreement(ai, {**audit, **sheet})
    sources = {name: sum(1 for f in final if f.source == name) for name in ("human", "audit", "ai")}
    est = agreement.estimate
    write_json(
        LABEL_META_PATH,
        {
            "label_sources": sources,
            "ai_human_compared": agreement.compared,
            "ai_human_agreed": agreement.agreed,
            "ai_human_agreement": {"value": est.value, "low": est.low, "high": est.high, "n": est.n},
        },
    )
    print(f"Sources: {sources}")
    print(f"AI agreed with people on {agreement.agreed} of {agreement.compared} compared cells")


if __name__ == "__main__":
    main()
