"""Unit tests for dp_hello.validation (FR-03, FR-04, FR-05, FR-06, FR-09)."""

from __future__ import annotations

import pytest

from dp_hello.options import OptionValue, ParsedArgs, UsageError
from dp_hello.validation import Config, validate, validate_count, validate_name


def count_error(text: str, spelled: str = "-c") -> str:
    with pytest.raises(UsageError) as caught:
        validate_count(OptionValue(text, spelled))
    return caught.value.message


def test_defaults() -> None:
    assert validate(ParsedArgs()) == Config(name="World", count=1)


def test_values_are_carried_into_the_config() -> None:
    parsed = ParsedArgs(name=OptionValue("Ada", "-n"), count=OptionValue("3", "--count"))
    assert validate(parsed) == Config(name="Ada", count=3)


@pytest.mark.parametrize(
    ("text", "value"),
    [("1", 1), ("2", 2), ("999", 999), ("1000", 1000), ("007", 7), ("0001000", 1000)],
)
def test_valid_counts(text: str, value: int) -> None:
    assert validate_count(OptionValue(text, "-c")) == value


@pytest.mark.parametrize(
    "text",
    [
        "0",
        "000",
        "1001",
        "99999999999999999999999999",
        "00001001",
        "",
        "abc",
        "-1",
        "+1",
        " 1",
        "1 ",
        "1.0",
        "1e3",
        "0x10",
        "1_000",
        "١٢",  # Arabic-Indic digits: int() accepts them, the SRS does not
        "²",
    ],
)
def test_invalid_counts_are_rejected_verbatim(text: str) -> None:
    assert count_error(text) == f"invalid argument '{text}' for '-c'"


def test_invalid_count_reports_the_long_spelling() -> None:
    assert count_error("0", "--count") == "invalid argument '0' for '--count'"


@pytest.mark.parametrize("name", ["A", "Ada Lovelace", "Zoë", "-x", " ", "x" * 10_000])
def test_any_non_empty_name_is_valid(name: str) -> None:
    assert validate_name(OptionValue(name, "-n")) == name


@pytest.mark.parametrize("spelled", ["-n", "--name"])
def test_empty_name_is_rejected(spelled: str) -> None:
    with pytest.raises(UsageError) as caught:
        validate_name(OptionValue("", spelled))
    assert caught.value.message == f"invalid argument '' for '{spelled}'"


def test_operand_is_reported_before_invalid_values() -> None:
    parsed = ParsedArgs(name=OptionValue("", "-n"), first_operand="extra")
    with pytest.raises(UsageError) as caught:
        validate(parsed)
    assert caught.value.message == "extra operand 'extra'"


def test_name_is_validated_before_count() -> None:
    parsed = ParsedArgs(name=OptionValue("", "--name"), count=OptionValue("0", "-c"))
    with pytest.raises(UsageError) as caught:
        validate(parsed)
    assert caught.value.message == "invalid argument '' for '--name'"
