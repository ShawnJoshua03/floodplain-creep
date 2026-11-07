"""Confusion matrix, accuracy, precision, recall, Wilson intervals and threshold tuning."""

from __future__ import annotations

import math
from dataclasses import dataclass

POSITIVE = "increase"
NEGATIVES = frozenset({"no_clear_change", "decrease"})
UNCLEAR = "unclear"
LABELS = frozenset({POSITIVE, UNCLEAR}) | NEGATIVES
TUNE_SHARE = 0.6
Z_95 = 1.96


@dataclass(frozen=True)
class LabeledCell:
    cell_id: str
    label: str
    change: float


@dataclass(frozen=True)
class Confusion:
    tp: int
    fp: int
    fn: int
    tn: int


@dataclass(frozen=True)
class Estimate:
    value: float | None
    low: float | None
    high: float | None
    n: int


def wilson(successes: int, n: int) -> tuple[float, float]:
    """Wilson 95 percent interval for a proportion."""
    if n == 0:
        raise ValueError("Wilson interval needs at least one observation")
    p = successes / n
    denom = 1 + Z_95**2 / n
    centre = (p + Z_95**2 / (2 * n)) / denom
    half = Z_95 * math.sqrt(p * (1 - p) / n + Z_95**2 / (4 * n**2)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def estimate(successes: int, n: int) -> Estimate:
    if n == 0:
        return Estimate(None, None, None, 0)
    low, high = wilson(successes, n)
    return Estimate(successes / n, low, high, n)


def split_labeled(cells: list[LabeledCell]) -> tuple[list[LabeledCell], list[LabeledCell]]:
    """First 60 percent in sheet order tunes the threshold, the rest is the test set."""
    cut = int(len(cells) * TUNE_SHARE)
    return cells[:cut], cells[cut:]


def is_positive(cell: LabeledCell) -> bool:
    return cell.label == POSITIVE


def confusion(cells: list[LabeledCell], threshold: float) -> Confusion:
    tp = fp = fn = tn = 0
    for cell in cells:
        predicted = cell.change >= threshold
        truth = is_positive(cell)
        tp += predicted and truth
        fp += predicted and not truth
        fn += (not predicted) and truth
        tn += (not predicted) and not truth
    return Confusion(tp, fp, fn, tn)


def f1(c: Confusion) -> float:
    denom = 2 * c.tp + c.fp + c.fn
    return 0.0 if denom == 0 else 2 * c.tp / denom


def tune_threshold(cells: list[LabeledCell]) -> float:
    """Pick the change threshold with the best F1 on the tuning cells. Ties go to the lower threshold."""
    if not any(is_positive(c) for c in cells):
        raise ValueError("Tuning cells contain no increases, so a threshold cannot be chosen")
    candidates = sorted({c.change for c in cells})
    return max(candidates, key=lambda t: (f1(confusion(cells, t)), -t))


def accuracy(c: Confusion) -> Estimate:
    return estimate(c.tp + c.tn, c.tp + c.fp + c.fn + c.tn)


def precision(c: Confusion) -> Estimate:
    return estimate(c.tp, c.tp + c.fp)


def recall(c: Confusion) -> Estimate:
    return estimate(c.tp, c.tp + c.fn)
