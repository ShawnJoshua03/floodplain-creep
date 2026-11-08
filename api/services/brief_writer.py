"""Write a brief with a model, check it, and fall back to the template when anything fails."""

from __future__ import annotations

import logging
from collections.abc import Callable

from api.safety.banned_terms import find_banned_terms
from api.safety.number_check import numbers_not_in_input
from api.schemas.brief_input import BriefInput, Resource, WrittenBrief
from api.services.brief_template import template_brief

logger = logging.getLogger(__name__)

MAX_WORDS = 90

PROMPT = """Write a plain-language brief about flood exposure for residents and local planners.
Rules:
- Aim for 60 to 75 words and never exceed {max_words}.
- One paragraph of whole sentences, starting with the neighborhood name.
- Use only the facts in the JSON. Write numbers as digits, with commas for thousands. Add no other number.
- Never write a field name from the JSON. Never use an underscore.
- Say the counts are estimates from satellite detections and the flood scenario is simulated.
- Say whether the change stands out from normal yearly noise, in plain words.
- No blame, no guesses about who lives there or why buildings were built.
- Do not write links or names of organizations.
What the fields mean:
- buildings_first_year and buildings_last_year: buildings in the modeled flood zone in those years.
- change_since_first_year and growth_pct: the change between those years, in buildings and in percent.
- smoothed_change_pct: the same change after averaging two years at each end, which damps one bad year.
- typical_swing_pct: how much counts usually move from one year to the next elsewhere in the city.
- times_typical_swing: the smoothed change divided by that usual swing.
  required_multiple is the bar for calling a change clear.
- verdict: clear_growth or clear_decline means the change stands out from noise. within_noise means it does not.
  not_enough_data means no judgment is possible.
- areas_gaining and areas_losing: 100 meter patches of flood-zone ground here that gained or lost 5 or more buildings.
  rest_areas_gaining and rest_areas_losing: the same for the rest of the city.
- accuracy_pct: how often the building-change check matched satellite imagery in a sample. labels_checked_by_person
  says whether a person reviewed that sample.
Facts:
{facts}
"""

ModelCall = Callable[[str], str]


class ModelError(Exception):
    """The model could not be reached or gave no usable answer."""


def build_prompt(data: BriefInput) -> str:
    return PROMPT.format(max_words=MAX_WORDS, facts=data.model_dump_json(indent=2))


def problems(text: str, data: BriefInput, banned_terms: list[str]) -> list[str]:
    found: list[str] = []
    if not text.strip():
        found.append("empty text")
    if "\n" in text.strip():
        found.append("more than one paragraph")
    if "_" in text:
        found.append("a field name leaked into the text")
    if not text.strip().endswith((".", "!", "?")):
        found.append("the text does not end like a finished sentence")
    if data.neighborhood not in text:
        found.append("the text does not name the neighborhood")
    if len(text.split()) > MAX_WORDS:
        found.append(f"more than {MAX_WORDS} words")
    extra = numbers_not_in_input(text, data.model_dump())
    if extra:
        found.append(f"numbers not in the input: {extra}")
    banned = find_banned_terms(text, banned_terms)
    if banned:
        found.append(f"banned terms: {banned}")
    return found


def with_pointers(text: str, resources: list[Resource]) -> str:
    """Official links are added by code, from config, after the checks. At most two."""
    if not resources:
        return text
    pointers = "; ".join(f"{item.title}: {item.url}" for item in resources[:2])
    return f"{text} For preparedness help: {pointers}."


def write_brief(
    data: BriefInput, banned_terms: list[str], resources: list[Resource], call_model: ModelCall | None
) -> WrittenBrief:
    """The model text is used only when every check passes. Otherwise the template is stored and labeled as one."""
    if call_model is not None:
        try:
            text = call_model(build_prompt(data)).strip()
        except ModelError as error:
            logger.warning("Model call failed for %s: %s", data.neighborhood, error)
        else:
            found = problems(text, data, banned_terms)
            if not found:
                return WrittenBrief(text=with_pointers(text, resources), source="gemini")
            logger.warning("Model text for %s failed checks: %s", data.neighborhood, found)
    return WrittenBrief(text=with_pointers(template_brief(data), resources), source="template")
