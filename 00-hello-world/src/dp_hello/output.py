"""Byte-exact output for dp-hello (CONV-03, CONV-05, CONV-13, CONV-14, CONV-25).

Text is encoded here and written to the binary buffers beneath ``sys.stdout`` and
``sys.stderr``, so Python never translates LF into CRLF (Windows) and never applies the
locale's encoding (CONV-06).
"""

from __future__ import annotations

import os
import sys
from typing import BinaryIO

TOOL = "dp-hello"


def encode(text: str) -> bytes:
    """Encode text that may contain command-line arguments as the user's exact UTF-8 bytes.

    On Windows, Python decodes the UTF-16 command line into ``sys.argv``, so UTF-8 is its
    exact encoding (``surrogatepass`` keeps even unpaired surrogates). On POSIX,
    ``os.fsencode`` inverts the decoding Python applied to the argument bytes
    (``surrogateescape``), so the original bytes come back unchanged (CONV-05).
    """
    if os.name == "nt":
        return text.encode("utf-8", "surrogatepass")
    return os.fsencode(text)


def usage_diagnostic(message: str) -> bytes:
    """Return the two CONV-13/CONV-14 lines for a usage error ``message``."""
    return encode(f"{TOOL}: {message}\nTry '{TOOL} --help' for more information.\n")


def write_stdout(data: bytes) -> bool:
    """Write ``data`` to standard output; return False if the reader went away (CONV-25)."""
    return _write(sys.stdout, data)


def write_stderr(data: bytes) -> bool:
    """Write ``data`` to standard error; return False if it cannot be written."""
    return _write(sys.stderr, data)


def _write(stream: object, data: bytes) -> bool:
    buffer: BinaryIO | None = getattr(stream, "buffer", None)
    if buffer is None:  # the stream is closed or not a text stream (e.g. fd not open)
        return False
    try:
        buffer.write(data)
        buffer.flush()
    except OSError:  # BrokenPipeError (EPIPE), or EINVAL from a closed pipe on Windows
        _silence(buffer)
        return False
    return True


def _silence(buffer: BinaryIO) -> None:
    """Point the stream's descriptor at the null device so the exit-time flush stays quiet."""
    try:
        null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(null, buffer.fileno())
        os.close(null)
    except OSError, ValueError:
        pass
