from api.safety.number_check import allowed_numbers, normalize, numbers_in, numbers_not_in_input

PAYLOAD = {
    "neighborhood": "Badda",
    "return_period": 10,
    "first_year": 2018,
    "buildings_last_year": 14902,
    "change_since_first_year": 4888,
    "growth_pct": -6.8,
    "times_typical_swing": 6.38,
    "required_multiple": 2.0,
    "verdict": "clear_growth",
    "flag": True,
    "missing": None,
}


def test_commas_and_trailing_zeros_do_not_change_a_number() -> None:
    assert normalize("14,902") == "14902"
    assert normalize("2.0") == "2"
    assert normalize("not a number") is None


def test_numbers_are_found_in_plain_text() -> None:
    assert numbers_in("It had 14,902 buildings in 2023, up 6.8 percent.") == ["14902", "2023", "6.8"]


def test_a_sentence_end_after_a_number_is_not_part_of_it() -> None:
    assert numbers_in("The count was 14,902.") == ["14902"]


def test_text_that_uses_only_input_numbers_passes() -> None:
    text = "In 2018 the 10-year zone held 14,902 buildings, a change of 4,888, 2 times the swing."
    assert numbers_not_in_input(text, PAYLOAD) == []


def test_a_decrease_may_be_written_without_its_sign() -> None:
    assert numbers_not_in_input("Counts fell 6.8 percent.", PAYLOAD) == []


def test_a_float_may_be_rounded_to_one_decimal() -> None:
    assert numbers_not_in_input("That is 6.4 times the swing.", PAYLOAD) == []


def test_an_added_number_is_caught() -> None:
    assert numbers_not_in_input("About 15,000 buildings, up 33 percent.", PAYLOAD) == ["15000", "33"]


def test_a_rounded_guess_is_caught_because_it_is_not_in_the_input() -> None:
    assert numbers_not_in_input("Nearly 15 thousand buildings, 10 times the swing.", PAYLOAD) == ["15"]


def test_booleans_and_nulls_add_no_numbers() -> None:
    assert allowed_numbers({"flag": True, "missing": None}) == set()


def test_numbers_inside_lists_and_nested_objects_count() -> None:
    assert "7" in allowed_numbers({"series": [{"year": 7}]})
