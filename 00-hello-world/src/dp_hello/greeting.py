"""Pure greeting construction (FR-01, FR-02, FR-04, NFR-05)."""

from __future__ import annotations


def greeting_line(name: str) -> str:
    """Return one greeting line: ``Hello, <name>!`` followed by LF."""
    return f"Hello, {name}!\n"


def greeting_text(name: str, count: int) -> str:
    """Return ``count`` greeting lines for ``name`` (empty when ``count`` is 0 or less)."""
    return greeting_line(name) * max(count, 0)
