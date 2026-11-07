"""Combine human, audit and AI labels, and measure how often the AI reviewer agrees with people."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pipeline.lib.validation_metrics import LABELS, Estimate, estimate

HUMAN = "human"
AUDIT = "audit"
AI = "ai"


@dataclass(frozen=True)
class FinalLabel:
    cell_id: str
    label: str
    source: str


@dataclass(frozen=True)
class Agreement:
    compared: int
    agreed: int
    estimate: Estimate


def merge_labels(
    order: list[str], sheet: dict[str, str], audit: dict[str, str], ai: dict[str, str]
) -> list[FinalLabel]:
    """Pick one label per cell. A person's label beats an audit label, which beats the AI label."""
    merged: list[FinalLabel] = []
    for cell_id in order:
        for source, labels in ((HUMAN, sheet), (AUDIT, audit), (AI, ai)):
            if cell_id in labels:
                merged.append(FinalLabel(cell_id, labels[cell_id], source))
                break
    missing = [cell_id for cell_id in order if cell_id not in {m.cell_id for m in merged}]
    if missing:
        raise ValueError(f"{len(missing)} cells have no label from any source, first: {missing[0]}")
    unknown = sorted({m.label for m in merged} - LABELS)
    if unknown:
        raise ValueError(f"Unknown labels {unknown}. Allowed: {sorted(LABELS)}")
    return merged


def ai_human_agreement(ai: dict[str, str], human: dict[str, str]) -> Agreement:
    """Share of cells where the AI label equals the person's label, over cells that have both."""
    both = [cell_id for cell_id in human if cell_id in ai]
    agreed = sum(1 for cell_id in both if ai[cell_id] == human[cell_id])
    return Agreement(len(both), agreed, estimate(agreed, len(both)))


def draw_audit(order: list[str], size: int, seed: int) -> list[str]:
    """Pick cells for a person to label without seeing the AI label. Order follows the sheet."""
    if size > len(order):
        raise ValueError(f"Audit size {size} is larger than the {len(order)} cells")
    rng = np.random.default_rng(seed)
    picked = set(rng.choice(len(order), size=size, replace=False).tolist())
    return [cell_id for index, cell_id in enumerate(order) if index in picked]
