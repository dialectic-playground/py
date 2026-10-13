"""Unit tests for dp_hello.greeting, the pure greeting construction (FR-01, FR-02, FR-04)."""

from __future__ import annotations

import pytest

from dp_hello.greeting import greeting_line, greeting_text


def test_default_greeting_line() -> None:
    assert greeting_line("World") == "Hello, World!\n"


@pytest.mark.parametrize("name", ["Ada Lovelace", "Zoë", "-x", "Hi!", "a\tb", "日本"])
def test_name_is_used_verbatim(name: str) -> None:
    assert greeting_line(name) == f"Hello, {name}!\n"


@pytest.mark.parametrize("count", [1, 2, 1000])
def test_greeting_text_repeats_count_times(count: int) -> None:
    text = greeting_text("Ken", count)
    assert text == "Hello, Ken!\n" * count
    assert text.count("\n") == count
    assert "\r" not in text


def test_greeting_text_for_non_positive_count_is_empty() -> None:
    assert greeting_text("Ken", 0) == ""
    assert greeting_text("Ken", -1) == ""


def test_greeting_is_pure() -> None:
    assert greeting_text("Ada", 3) == greeting_text("Ada", 3)
