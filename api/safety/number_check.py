"""Every number in a brief must come from the computed input. The model may not add one.

Only digits are checked. A number written as a word is not a number the model can add, because the prompt
asks for digits and a text with a number word still has to pass the other checks.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

NUMBER_PATTERN = re.compile(r"\d[\d,]*(?:\.\d+)?")


def normalize(text: str) -> str | None:
    """'5,434' and '5434.0' both become '5434'. Returns None for anything that is not a number."""
    try:
        value = Decimal(text.replace(",", ""))
    except InvalidOperation:
        return None
    return format(value.normalize(), "f")


def numbers_in(text: str) -> list[str]:
    found = (normalize(match.group(0).rstrip(",")) for match in NUMBER_PATTERN.finditer(text))
    return [number for number in found if number is not None]


def allowed_numbers(node: object) -> set[str]:
    """Every number in the input, in the ways a plain-language brief would write it. Signs are dropped."""
    allowed: set[str] = set()
    if isinstance(node, bool):
        return allowed
    if isinstance(node, int):
        allowed.add(str(abs(node)))
    elif isinstance(node, float):
        for form in (f"{abs(node)}", f"{abs(node):.1f}", f"{abs(node):.0f}"):
            normalized = normalize(form)
            if normalized is not None:
                allowed.add(normalized)
    elif isinstance(node, dict):
        for value in node.values():
            allowed |= allowed_numbers(value)
    elif isinstance(node, list):
        for value in node:
            allowed |= allowed_numbers(value)
    return allowed


def numbers_not_in_input(text: str, payload: object) -> list[str]:
    """The numbers in the text that the input does not hold. An empty list means the text passes."""
    allowed = allowed_numbers(payload)
    return [number for number in numbers_in(text) if number not in allowed]
