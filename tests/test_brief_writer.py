import shutil
from pathlib import Path

import psycopg
import pytest

from api.core.settings import CONFIG_DIR, load_settings
from api.repositories.briefs import store_brief
from api.safety.banned_terms import find_banned_terms
from api.safety.number_check import numbers_not_in_input
from api.schemas.brief_input import BriefInput, Resource
from api.services.brief_template import template_brief
from api.services.brief_writer import MAX_WORDS, ModelError, build_prompt, problems, write_brief
from pipeline.io.database import load_neighborhoods
from tests.api_support import write_neighborhoods

BANNED = ["illegal", "evict", "clear out"]
RESOURCE = Resource(title="Official guide", url="https://example.org/guide")


def make_input(**changes: object) -> BriefInput:
    base: dict[str, object] = {
        "neighborhood": "Badda",
        "city": "Dhaka",
        "return_period": 10,
        "first_year": 2018,
        "last_year": 2023,
        "buildings_first_year": 10014,
        "buildings_last_year": 14902,
        "change_since_first_year": 4888,
        "growth_pct": 48.8,
        "smoothed_change_pct": 31.8,
        "typical_swing_pct": 5.0,
        "times_typical_swing": 6.4,
        "required_multiple": 2.0,
        "verdict": "clear_growth",
        "areas_gaining": 427,
        "areas_losing": 40,
        "rest_areas_gaining": 733,
        "rest_areas_losing": 523,
        "accuracy_pct": 55.4,
        "labels_checked_by_person": False,
    }
    return BriefInput.model_validate({**base, **changes})


GOOD = (
    "Badda had 14,902 buildings in its modeled 10-year flood zone in 2023, 4,888 more than in 2018. "
    "The change is 6.4 times the usual yearly swing. Counts are estimates from satellite detections and the "
    "flood scenario is simulated."
)


def test_the_template_passes_its_own_checks_for_every_verdict() -> None:
    for verdict in ("clear_growth", "clear_decline", "within_noise", "not_enough_data"):
        data = make_input(verdict=verdict, times_typical_swing=None if verdict == "not_enough_data" else 1.5)
        text = template_brief(data)
        assert problems(text, data, BANNED) == [], (verdict, text)
        assert len(text.split()) <= MAX_WORDS


def test_the_template_for_a_suppressed_year_shows_no_count() -> None:
    data = make_input(buildings_last_year=None, change_since_first_year=None, growth_pct=None)
    text = template_brief(data)
    assert "too few buildings" in text
    assert numbers_not_in_input(text, data.model_dump()) == []


def test_the_template_says_it_is_modeled_and_uses_neutral_language() -> None:
    text = template_brief(make_input())
    assert "not a forecast or an official warning" in text
    assert find_banned_terms(text, BANNED) == []


def test_a_decrease_keeps_its_minus_sign() -> None:
    text = template_brief(make_input(change_since_first_year=-496, verdict="within_noise", times_typical_swing=1.0))
    assert "−496 since 2018" in text


def test_a_good_model_text_is_used_and_labeled_gemini() -> None:
    written = write_brief(make_input(), BANNED, [], lambda _prompt: GOOD)
    assert written.source == "gemini"
    assert written.text == GOOD


def test_an_added_number_falls_back_to_the_template() -> None:
    written = write_brief(make_input(), BANNED, [], lambda _prompt: GOOD + " That is about 15,000 buildings.")
    assert written.source == "template"
    assert "15,000" not in written.text


def test_a_banned_term_falls_back_to_the_template() -> None:
    written = write_brief(make_input(), BANNED, [], lambda _prompt: GOOD + " Some homes are illegal.")
    assert written.source == "template"


def test_a_text_over_the_word_limit_falls_back_to_the_template() -> None:
    long_text = " ".join(["word"] * (MAX_WORDS + 1))
    assert write_brief(make_input(), BANNED, [], lambda _prompt: long_text).source == "template"


def test_an_empty_answer_falls_back_to_the_template() -> None:
    assert write_brief(make_input(), BANNED, [], lambda _prompt: "   ").source == "template"


def test_a_model_error_falls_back_to_the_template() -> None:
    def failing(_prompt: str) -> str:
        raise ModelError("unreachable")

    written = write_brief(make_input(), BANNED, [], failing)
    assert written.source == "template"
    assert problems(written.text, make_input(), BANNED) == []


def test_other_errors_are_not_hidden() -> None:
    def broken(_prompt: str) -> str:
        raise RuntimeError("bug")

    with pytest.raises(RuntimeError):
        write_brief(make_input(), BANNED, [], broken)


def test_with_no_model_the_template_is_used() -> None:
    assert write_brief(make_input(), BANNED, [], None).source == "template"


def test_official_pointers_are_added_by_code_after_the_checks() -> None:
    written = write_brief(make_input(), BANNED, [RESOURCE], lambda _prompt: GOOD)
    assert written.text.startswith(GOOD)
    assert written.text.endswith("For preparedness help: Official guide: https://example.org/guide.")


def test_at_most_two_pointers_are_added() -> None:
    resources = [Resource(title=f"Guide {n}", url=f"https://example.org/{n}") for n in "abc"]
    text = write_brief(make_input(), BANNED, resources, None).text
    assert "Guide a" in text and "Guide b" in text and "Guide c" not in text


def test_the_prompt_holds_the_facts_and_forbids_links_and_blame() -> None:
    prompt = build_prompt(make_input())
    assert '"buildings_last_year": 14902' in prompt
    assert "Do not write links" in prompt
    assert "No blame" in prompt
    assert f"never exceed {MAX_WORDS}" in prompt


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (GOOD.replace(". ", ".\n"), "more than one paragraph"),
        (GOOD.replace("flood scenario", "flood_scenario"), "a field name leaked"),
        (GOOD[:-1], "does not end like a finished sentence"),
        (GOOD.replace("Badda", "The area"), "does not name the neighborhood"),
    ],
)
def test_unfinished_or_unreadable_text_is_caught(text: str, expected: str) -> None:
    assert any(expected in item for item in problems(text, make_input(), BANNED))


def test_a_cut_off_answer_from_the_model_falls_back_to_the_template() -> None:
    cut_off = "Badda had 14,902 buildings in its modeled 10-year flood zone in 20"
    assert write_brief(make_input(), BANNED, [], lambda _prompt: cut_off).source == "template"


def test_a_stored_brief_is_replaced_by_the_next_one(conn: psycopg.Connection, tmp_path: Path) -> None:
    write_neighborhoods(tmp_path / "n.geojson")
    load_neighborhoods(conn, tmp_path / "n.geojson")
    store_brief(conn, "n1", 10, "First text.", "template")
    store_brief(conn, "n1", 10, "Second text.", "gemini")
    conn.commit()
    rows = conn.execute("SELECT text, source FROM briefs WHERE neighborhood_id = 'n1'").fetchall()
    assert rows == [("Second text.", "gemini")]


def test_resources_are_read_from_config(tmp_path: Path) -> None:
    config = tmp_path / "config"
    shutil.copytree(CONFIG_DIR, config)
    (config / "resources.yaml").write_text(
        "resources:\n  - title: Official guide\n    url: https://example.org/guide\n", encoding="utf-8"
    )
    settings = load_settings("postgresql://x", config)
    assert settings.resources == [RESOURCE]


def test_empty_resources_mean_no_pointers(tmp_path: Path) -> None:
    config = tmp_path / "config"
    shutil.copytree(CONFIG_DIR, config)
    (config / "resources.yaml").write_text("resources: []\n", encoding="utf-8")
    assert load_settings("postgresql://x", config).resources == []
