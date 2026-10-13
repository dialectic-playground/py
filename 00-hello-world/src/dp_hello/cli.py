"""Entry point of dp-hello: parse, validate, build, and write (SRS sections 3 and 4)."""

from __future__ import annotations

import sys

from dp_hello.greeting import greeting_text
from dp_hello.options import Action, UsageError, parse_args
from dp_hello.output import encode, usage_diagnostic, write_stderr, write_stdout
from dp_hello.validation import validate

EXIT_SUCCESS = 0
EXIT_USAGE = 2
# CONV-25 leaves the status after a broken pipe unspecified; use the shell's SIGPIPE status.
EXIT_BROKEN_PIPE = 141

VERSION_TEXT = "dp-hello (dialectic-playground) 1.0.0\n"
HELP_TEXT = """\
Usage: dp-hello [OPTION]...
Print a greeting to standard output.

Options:
  -n, --name=NAME     greet NAME instead of World
  -c, --count=COUNT   print the greeting COUNT times (1-1000, default 1)
      --help          display this help and exit
      --version       output version information and exit
"""


def main(args: list[str]) -> int:
    """Run dp-hello with ``args`` (without the program name); return the exit status."""
    try:
        parsed = parse_args(args)
        if parsed.action is Action.HELP:
            text = HELP_TEXT
        elif parsed.action is Action.VERSION:
            text = VERSION_TEXT
        else:
            config = validate(parsed)
            text = greeting_text(config.name, config.count)
    except UsageError as error:
        write_stderr(usage_diagnostic(error.message))
        return EXIT_USAGE
    return EXIT_SUCCESS if write_stdout(encode(text)) else EXIT_BROKEN_PIPE


def run() -> None:
    """Console-script entry point: exit with :func:`main`'s status for ``sys.argv``."""
    sys.exit(main(sys.argv[1:]))
