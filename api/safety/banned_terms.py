"""Neutral-language check. The word list is config/banned_terms.txt, loaded through settings."""

from __future__ import annotations

import re


def find_banned_terms(text: str, terms: list[str]) -> list[str]:
    """Return the banned terms found in the text. A term also matches longer forms that start with it."""
    found = []
    for term in terms:
        if re.search(rf"\b{re.escape(term)}", text, flags=re.IGNORECASE):
            found.append(term)
    return found
