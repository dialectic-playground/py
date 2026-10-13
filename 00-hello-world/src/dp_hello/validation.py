"""Validation of parsed arguments into a :class:`Config` (FR-03, FR-05, FR-06, FR-09)."""

from __future__ import annotations

from dataclasses import dataclass

from dp_hello.options import OptionValue, ParsedArgs, UsageError

DEFAULT_NAME = "World"
DEFAULT_COUNT = 1
MIN_COUNT = 1
MAX_COUNT = 1000
_DIGITS = frozenset("0123456789")


@dataclass(frozen=True)
class Config:
    """A validated greeting request: ``name`` is non-empty and ``1 <= count <= 1000``."""

    name: str = DEFAULT_NAME
    count: int = DEFAULT_COUNT


def validate(parsed: ParsedArgs) -> Config:
    """Turn a GREET parse result into a :class:`Config`, or raise :class:`UsageError`.

    Operands are rejected first, then the winning ``--name`` and ``--count`` values.
    """
    if parsed.first_operand is not None:
        raise UsageError(f"extra operand '{parsed.first_operand}'")
    name = DEFAULT_NAME if parsed.name is None else validate_name(parsed.name)
    count = DEFAULT_COUNT if parsed.count is None else validate_count(parsed.count)
    return Config(name=name, count=count)


def validate_name(option: OptionValue) -> str:
    """Return the name, which may be anything except the empty string (FR-03)."""
    if option.value == "":
        raise _invalid(option)
    return option.value


def validate_count(option: OptionValue) -> int:
    """Return the count: ASCII digits only (leading zeros allowed), value 1-1000 (FR-05)."""
    text = option.value
    if not text or not _DIGITS.issuperset(text):
        raise _invalid(option)
    # Strip leading zeros first so that a huge all-digit string is never converted to an int.
    significant = text.lstrip("0")
    if len(significant) > len(str(MAX_COUNT)):
        raise _invalid(option)
    value = int(significant or "0")
    if not MIN_COUNT <= value <= MAX_COUNT:
        raise _invalid(option)
    return value


def _invalid(option: OptionValue) -> UsageError:
    return UsageError(f"invalid argument '{option.value}' for '{option.spelled}'")
