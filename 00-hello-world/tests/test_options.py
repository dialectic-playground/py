"""Unit tests for dp_hello.options (CONV-07 ... CONV-13, FR-06, FR-07, FR-10)."""

from __future__ import annotations

import pytest

from dp_hello.options import Action, OptionValue, ParsedArgs, UsageError, parse_args


def error_of(args: list[str]) -> str:
    with pytest.raises(UsageError) as caught:
        parse_args(args)
    return caught.value.message


def test_no_arguments_is_a_default_greeting() -> None:
    assert parse_args([]) == ParsedArgs()


@pytest.mark.parametrize(
    ("args", "spelled"),
    [
        (["-n", "Ada"], "-n"),
        (["-nAda"], "-n"),
        (["--name", "Ada"], "--name"),
        (["--name=Ada"], "--name"),
    ],
)
def test_name_spellings_are_equivalent(args: list[str], spelled: str) -> None:
    assert parse_args(args).name == OptionValue("Ada", spelled)


def test_bundled_short_options_take_the_rest_of_the_token() -> None:
    parsed = parse_args(["-c2", "-nKen"])
    assert parsed.count == OptionValue("2", "-c")
    assert parsed.name == OptionValue("Ken", "-n")


def test_bundled_value_may_contain_option_letters() -> None:
    assert parse_args(["-cn"]).count == OptionValue("n", "-c")


def test_count_long_option_with_separate_value() -> None:
    assert parse_args(["--count", "3"]).count == OptionValue("3", "--count")


def test_long_option_value_may_be_empty_or_contain_equals() -> None:
    assert parse_args(["--name="]).name == OptionValue("", "--name")
    assert parse_args(["--name=a=b"]).name == OptionValue("a=b", "--name")


@pytest.mark.parametrize("args", [["--name", "-x"], ["--name=-x"], ["-n-x"], ["-n", "--help"]])
def test_name_may_begin_with_a_dash(args: list[str]) -> None:
    parsed = parse_args(args)
    assert parsed.action is Action.GREET
    assert parsed.name is not None
    assert parsed.name.value == args[-1].removeprefix("--name=").removeprefix("-n")


def test_last_occurrence_wins_and_keeps_its_spelling() -> None:
    parsed = parse_args(["-n", "A", "--name", "B", "--count=5", "-c", "7"])
    assert parsed.name == OptionValue("B", "--name")
    assert parsed.count == OptionValue("7", "-c")


def test_values_are_not_validated_by_the_parser() -> None:
    parsed = parse_args(["--count", "abc", "-n", ""])
    assert parsed.count == OptionValue("abc", "--count")
    assert parsed.name == OptionValue("", "-n")


def test_non_ascii_values_are_kept_verbatim() -> None:
    assert parse_args(["-n", "Zoë 😀"]).name == OptionValue("Zoë 😀", "-n")


def test_operands_are_collected_and_the_first_is_kept() -> None:
    assert parse_args(["extra", "more"]).first_operand == "extra"


def test_single_dash_is_an_operand() -> None:
    assert parse_args(["-"]).first_operand == "-"


def test_double_dash_ends_options() -> None:
    parsed = parse_args(["-n", "A", "--", "-n", "B"])
    assert parsed.name == OptionValue("A", "-n")
    assert parsed.first_operand == "-n"


def test_lone_double_dash_is_harmless() -> None:
    assert parse_args(["--"]) == ParsedArgs()


def test_operands_and_options_may_interleave() -> None:
    parsed = parse_args(["extra", "-n", "A"])
    assert parsed.first_operand == "extra"
    assert parsed.name == OptionValue("A", "-n")


@pytest.mark.parametrize(
    ("args", "action"),
    [
        (["--help"], Action.HELP),
        (["--version"], Action.VERSION),
        (["--help", "extra", "-x"], Action.HELP),
        (["--version", "--help"], Action.VERSION),
        (["extra", "--help"], Action.HELP),
        (["-c", "0", "--help"], Action.HELP),
        (["--help", "--bogus"], Action.HELP),
    ],
)
def test_help_and_version_stop_the_scan(args: list[str], action: Action) -> None:
    assert parse_args(args).action is action


def test_double_dash_hides_help() -> None:
    parsed = parse_args(["--", "--help"])
    assert parsed.action is Action.GREET
    assert parsed.first_operand == "--help"


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["-x"], "invalid option -- 'x'"),
        (["-x", "--help"], "invalid option -- 'x'"),
        (["-h"], "invalid option -- 'h'"),
        (["-é"], "invalid option -- 'é'"),
        (["--nme", "Ada"], "unrecognized option '--nme'"),
        (["--nam"], "unrecognized option '--nam'"),
        (["--names=x"], "unrecognized option '--names=x'"),
        (["--bogus=1", "--help"], "unrecognized option '--bogus=1'"),
        (["---"], "unrecognized option '---'"),
        (["--="], "unrecognized option '--='"),
        (["-n"], "option requires an argument -- 'n'"),
        (["-c"], "option requires an argument -- 'c'"),
        (["--name"], "option '--name' requires an argument"),
        (["--count"], "option '--count' requires an argument"),
        (["--help=1"], "option '--help' doesn't allow an argument"),
        (["--version="], "option '--version' doesn't allow an argument"),
    ],
)
def test_syntax_errors_use_conv13_messages(args: list[str], message: str) -> None:
    assert error_of(args) == message


def test_first_error_in_scan_order_wins() -> None:
    assert error_of(["--nme", "-x"]) == "unrecognized option '--nme'"
