import pytest

from pipeline.lib.label_merge import AI, AUDIT, HUMAN, ai_human_agreement, draw_audit, merge_labels

ORDER = ["a", "b", "c", "d"]
AI_LABELS = {"a": "increase", "b": "no_clear_change", "c": "increase", "d": "decrease"}


def test_precedence_is_human_then_audit_then_ai() -> None:
    final = merge_labels(ORDER, {"a": "decrease"}, {"a": "increase", "b": "unclear"}, AI_LABELS)
    assert [(f.cell_id, f.label, f.source) for f in final] == [
        ("a", "decrease", HUMAN),
        ("b", "unclear", AUDIT),
        ("c", "increase", AI),
        ("d", "decrease", AI),
    ]


def test_missing_label_is_rejected() -> None:
    with pytest.raises(ValueError, match="no label from any source"):
        merge_labels(ORDER, {}, {}, {"a": "increase"})


def test_unknown_label_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown labels"):
        merge_labels(["a"], {"a": "growth"}, {}, {"a": "increase"})


def test_agreement_counts_only_cells_with_both_labels() -> None:
    result = ai_human_agreement(AI_LABELS, {"a": "increase", "b": "increase", "x": "increase"})
    assert (result.compared, result.agreed) == (2, 1)
    assert result.estimate.value == 0.5


def test_agreement_without_overlap_has_no_estimate() -> None:
    result = ai_human_agreement(AI_LABELS, {})
    assert result.compared == 0
    assert result.estimate.value is None


def test_audit_draw_is_repeatable_and_keeps_sheet_order() -> None:
    order = [f"c{i}" for i in range(50)]
    first = draw_audit(order, 10, 7)
    assert first == draw_audit(order, 10, 7)
    assert first == sorted(first, key=order.index)
    assert len(set(first)) == 10


def test_audit_larger_than_sheet_is_rejected() -> None:
    with pytest.raises(ValueError, match="larger than"):
        draw_audit(["a"], 2, 1)
