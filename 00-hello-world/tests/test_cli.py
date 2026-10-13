"""Unit/integration tests for dp_hello.cli and dp_hello.output (FR-01 ... FR-11, CONV-03)."""

from __future__ import annotations

import io
import os
import subprocess
import sys

import pytest

from dp_hello import output
from dp_hello.cli import EXIT_BROKEN_PIPE, HELP_TEXT, main

TRY = b"Try 'dp-hello --help' for more information.\n"


Capture = pytest.CaptureFixture[bytes]


def run(capture: Capture, *args: str) -> tuple[int, bytes, bytes]:
    """Run main() with the real sys.stdout/sys.stderr captured as bytes by pytest."""
    status = main(list(args))
    out, err = capture.readouterr()
    return status, out, err


def test_default_greeting(capsysbinary: Capture) -> None:
    assert run(capsysbinary) == (0, b"Hello, World!\n", b"")


def test_named_repeated_greeting(capsysbinary: Capture) -> None:
    assert run(capsysbinary, "-c2", "-n", "Ken") == (0, b"Hello, Ken!\nHello, Ken!\n", b"")


def test_non_ascii_name_is_written_as_utf8(capsysbinary: Capture) -> None:
    assert run(capsysbinary, "--name", "Zoë") == (0, "Hello, Zoë!\n".encode(), b"")


def test_maximum_count(capsysbinary: Capture) -> None:
    status, out, err = run(capsysbinary, "--count=1000")
    assert (status, err) == (0, b"")
    assert out == b"Hello, World!\n" * 1000


def test_help_is_byte_exact(capsysbinary: Capture) -> None:
    status, out, err = run(capsysbinary, "--help", "extra", "-x")
    assert (status, err) == (0, b"")
    assert out == HELP_TEXT.encode("ascii")
    assert out.endswith(b"exit\n")
    assert b"\r" not in out


def test_version(capsysbinary: Capture) -> None:
    assert run(capsysbinary, "--version") == (0, b"dp-hello (dialectic-playground) 1.0.0\n", b"")


@pytest.mark.parametrize(
    ("args", "first_line"),
    [
        (["-x"], b"dp-hello: invalid option -- 'x'\n"),
        (["--nme", "Ada"], b"dp-hello: unrecognized option '--nme'\n"),
        (["--name"], b"dp-hello: option '--name' requires an argument\n"),
        (["--version=1"], b"dp-hello: option '--version' doesn't allow an argument\n"),
        (["--name", ""], b"dp-hello: invalid argument '' for '--name'\n"),
        (["-c", "1001"], b"dp-hello: invalid argument '1001' for '-c'\n"),
        (["extra"], b"dp-hello: extra operand 'extra'\n"),
        (["--", "-n"], b"dp-hello: extra operand '-n'\n"),
        (["Zoë"], "dp-hello: extra operand 'Zoë'\n".encode()),
    ],
)
def test_usage_errors_write_only_stderr_and_exit_2(
    capsysbinary: Capture, args: list[str], first_line: bytes
) -> None:
    assert run(capsysbinary, *args) == (2, b"", first_line + TRY)


@pytest.mark.skipif(os.name == "nt", reason="POSIX argument bytes")
def test_undecodable_argument_bytes_round_trip(capsysbinary: Capture) -> None:
    raw = b"Z\xffo"
    status, out, _ = run(capsysbinary, "-n", os.fsdecode(raw))
    assert (status, out) == (0, b"Hello, " + raw + b"!\n")


def test_broken_pipe_is_silent(monkeypatch: pytest.MonkeyPatch, capsysbinary: Capture) -> None:
    class BrokenBuffer(io.BytesIO):
        def write(self, data: object) -> int:
            raise BrokenPipeError

    class BrokenStream:
        buffer = BrokenBuffer()

    monkeypatch.setattr(sys, "stdout", BrokenStream())
    monkeypatch.setattr(output, "_silence", lambda buffer: None)
    assert main([]) == EXIT_BROKEN_PIPE
    assert capsysbinary.readouterr().err == b""


def test_closed_stdout_does_not_crash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdout", None)
    assert main([]) == EXIT_BROKEN_PIPE


def test_process_output_is_utf8_and_lf_only() -> None:
    """End to end in a child interpreter: real argv decoding and binary stdout (CONV-03/05).

    On Windows this exercises the UTF-16 command line and the absence of CRLF translation.
    """
    completed = subprocess.run(
        [sys.executable, "-m", "dp_hello", "-c2", "--name", "Zoë Ådahl"],
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0
    assert completed.stdout == "Hello, Zoë Ådahl!\n".encode() * 2
    assert completed.stderr == b""


def test_diagnostic_format() -> None:
    assert output.usage_diagnostic("extra operand 'x'") == b"dp-hello: extra operand 'x'\n" + TRY
