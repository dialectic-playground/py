"""Command-line parsing for dp-hello (CONV-07 ... CONV-13, SRS section 3.2).

The parser is hand-written (no argparse, whose diagnostics differ from CONV-13). It only
recognizes the syntax; checking option *values* is the job of :mod:`dp_hello.validation`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class UsageError(Exception):
    """A CONV-13 usage error. ``message`` is the diagnostic without the ``dp-hello: `` prefix."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class Action(Enum):
    """What the invocation asks for."""

    GREET = "greet"
    HELP = "help"
    VERSION = "version"


@dataclass(frozen=True)
class OptionValue:
    """A raw option value together with the option as the user spelled it (``-n``/``--name``)."""

    value: str
    spelled: str


@dataclass(frozen=True)
class ParsedArgs:
    """The syntactic result of a parse. Values are unvalidated; the last occurrence wins."""

    action: Action = Action.GREET
    name: OptionValue | None = None
    count: OptionValue | None = None
    first_operand: str | None = None


# Options that take a value: short letter and long name -> the ParsedArgs field they set.
_SHORT_VALUED = {"n": "name", "c": "count"}
_LONG_VALUED = {"name": "name", "count": "count"}
_LONG_FLAGS = {"help": Action.HELP, "version": Action.VERSION}


def parse_args(args: list[str]) -> ParsedArgs:
    """Parse the arguments (without the program name) from left to right.

    Returns as soon as ``--help`` or ``--version`` is reached (CONV-12). Raises
    :class:`UsageError` for the first syntactic error met before that point.
    """
    values: dict[str, OptionValue] = {}
    operands: list[str] = []
    index = 0
    while index < len(args):
        token = args[index]
        index += 1
        if token == "--":
            operands.extend(args[index:])
            break
        if token.startswith("--"):
            action, index = _parse_long(token, args, index, values)
            if action is not None:
                return ParsedArgs(action=action)
        elif token.startswith("-") and token != "-":
            index = _parse_short_bundle(token, args, index, values)
        else:
            operands.append(token)
    return ParsedArgs(
        name=values.get("name"),
        count=values.get("count"),
        first_operand=operands[0] if operands else None,
    )


def _parse_long(
    token: str, args: list[str], index: int, values: dict[str, OptionValue]
) -> tuple[Action | None, int]:
    """Handle one ``--long[=value]`` token (CONV-08); returns (action, next index)."""
    name, has_value, inline = token[2:].partition("=")
    if name in _LONG_FLAGS:
        if has_value:
            raise UsageError(f"option '--{name}' doesn't allow an argument")
        return _LONG_FLAGS[name], index
    if name not in _LONG_VALUED:
        raise UsageError(f"unrecognized option '{token}'")
    if has_value:
        value = inline
    elif index < len(args):
        value = args[index]
        index += 1
    else:
        raise UsageError(f"option '--{name}' requires an argument")
    values[_LONG_VALUED[name]] = OptionValue(value, f"--{name}")
    return None, index


def _parse_short_bundle(
    token: str, args: list[str], index: int, values: dict[str, OptionValue]
) -> int:
    """Handle one ``-x...`` token (CONV-07); returns the next index."""
    letter = token[1]
    if letter not in _SHORT_VALUED:
        raise UsageError(f"invalid option -- '{letter}'")
    # Both short options take a value, which consumes the rest of the token or the next one.
    attached = token[2:]
    if attached:
        value = attached
    elif index < len(args):
        value = args[index]
        index += 1
    else:
        raise UsageError(f"option requires an argument -- '{letter}'")
    values[_SHORT_VALUED[letter]] = OptionValue(value, f"-{letter}")
    return index
