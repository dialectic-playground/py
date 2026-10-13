# Low-Level Design (LLD) — Standard Terminal Hello World

| Field | Value |
| :-- | :-- |
| Project | `00-hello-world` |
| Tools | dp-hello |
| Implementation language | py (Python 3.14, uv) |
| Author | Brandon Perkins |
| Version / date | 1.0 — 2026-10-13 |
| Status | In review |
| Inputs | `hld.md`, `specs/SRS.md`, `shared/CLI-CONVENTIONS.md` |

## 1. Source layout

```text
00-hello-world/
├── Makefile               # BASE-MAKEFILE hooks (uv)
├── pyproject.toml         # package dp-hello, console script, dev group, ruff/mypy/pytest config
├── uv.lock                # locked dependencies
├── .python-version        # 3.14
├── src/dp_hello/
│   ├── __init__.py        # package docstring (module map)
│   ├── __main__.py        # `python -m dp_hello`
│   ├── cli.py             # main(), run(), HELP_TEXT, VERSION_TEXT, exit statuses
│   ├── options.py         # parse_args(), ParsedArgs, OptionValue, Action, UsageError
│   ├── validation.py      # validate(), validate_name(), validate_count(), Config
│   ├── greeting.py        # greeting_line(), greeting_text() (pure)
│   └── output.py          # encode(), usage_diagnostic(), write_stdout(), write_stderr()
└── tests/                 # pytest: test_options.py, test_validation.py, test_greeting.py, test_cli.py
```

## 2. Data types

### 2.1 `options.ParsedArgs` (frozen dataclass)
| Field | Type | Default | Constraint / invariant | SRS |
| :-- | :-- | :-- | :-- | :-- |
| `action` | `Action` (`GREET`, `HELP`, `VERSION`) | `GREET` | For `HELP`/`VERSION` all other fields are unset | FR-07, FR-08 |
| `name` | `OptionValue \| None` | `None` | Last `-n`/`--name` occurrence, unvalidated | FR-02, FR-06 |
| `count` | `OptionValue \| None` | `None` | Last `-c`/`--count` occurrence, unvalidated | FR-04, FR-06 |
| `first_operand` | `str \| None` | `None` | First operand, including tokens after `--` | FR-09 |

`OptionValue(value: str, spelled: str)` keeps a raw value and the option spelling (`-n`,
`--name`, `-c`, `--count`) for CONV-13 messages.

### 2.2 `validation.Config` (frozen dataclass)
| Field | Type | Default | Constraint / invariant | SRS |
| :-- | :-- | :-- | :-- | :-- |
| `name` | `str` | `"World"` | Non-empty | FR-01 … FR-03 |
| `count` | `int` | `1` | `1 <= count <= 1000` | FR-04, FR-05 |

### 2.3 Error type
`options.UsageError(message)`; `message` is the text after `dp-hello: `. `cli.main` writes it
followed by `Try 'dp-hello --help' for more information.` and returns 2.

| Variant (message) | Raised by | Exit status |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | `_parse_short_bundle` | 2 |
| `unrecognized option '<token>'` | `_parse_long` | 2 |
| `option requires an argument -- 'n'` / `'c'` | `_parse_short_bundle` | 2 |
| `option '--name' requires an argument` / `'--count'` | `_parse_long` | 2 |
| `option '--help' doesn't allow an argument` / `'--version'` | `_parse_long` | 2 |
| `invalid argument '<V>' for '<spelling>'` | `validate_name`, `validate_count` | 2 |
| `extra operand '<X>'` | `validate` | 2 |

## 3. Module and function specifications

### 3.1 `options.parse_args`
- **Signature:** `parse_args(args: list[str]) -> ParsedArgs`
- **Responsibility:** syntactic left-to-right scan of the arguments.
- **Preconditions:** `args` excludes the program name.
- **Postconditions:** returns `ParsedArgs(action=HELP|VERSION)` at the first `--help`/`--version`;
  otherwise the last value of each option and the first operand.
- **Errors:** the first syntax error met in the scan (table §2.3, except the last two rows).
- **Algorithm:** for each token: `--` → all remaining tokens are operands, stop; `--*` →
  `_parse_long`; `-` followed by anything → `_parse_short_bundle`; else operand.
  `_parse_long` splits at the first `=`; `help`/`version` reject an inline value; `name`/`count`
  take the inline value or the next token (even if it starts with `-`); anything else is
  unrecognized (no abbreviations). `_parse_short_bundle` checks the first letter; since both
  short options take a value, the rest of the token (if non-empty) or the next token is the
  value.
- **Complexity:** O(total argument length) time and memory.
- **Satisfies:** FR-02, FR-06, FR-07, FR-08, FR-10, CONV-07 … CONV-13, CONV-22.
- **Unit tests:** all of `tests/test_options.py`.

### 3.2 `validation.validate`, `validate_name`, `validate_count`
- **Signatures:** `validate(parsed: ParsedArgs) -> Config`;
  `validate_name(option: OptionValue) -> str`; `validate_count(option: OptionValue) -> int`
- **Responsibility:** reject operands and invalid values, apply defaults.
- **Order:** operand first, then name, then count.
- **Algorithm (count):** reject unless non-empty and every character is in `0123456789` (so
  Unicode digits, signs, spaces, `_` are rejected although `int()` would accept them); strip
  leading zeros; reject more than four significant digits (never converts huge strings); convert;
  reject outside 1–1000.
- **Errors:** `invalid argument '<value>' for '<spelling>'`, `extra operand '<X>'`.
- **Complexity:** O(length of the values).
- **Satisfies:** FR-03, FR-04, FR-05, FR-06, FR-09, CONV-15.
- **Unit tests:** all of `tests/test_validation.py`.

### 3.3 `greeting.greeting_line`, `greeting_text`
- **Signatures:** `greeting_line(name: str) -> str`; `greeting_text(name: str, count: int) -> str`
- **Responsibility:** pure construction of `Hello, <name>!\n`, repeated `count` times (empty for
  `count <= 0`).
- **Complexity:** O(count × len(name)).
- **Satisfies:** FR-01, FR-02, FR-04, NFR-05.
- **Unit tests:** all of `tests/test_greeting.py`.

### 3.4 `output.encode`, `usage_diagnostic`, `write_stdout`, `write_stderr`
- **Signatures:** `encode(text: str) -> bytes`; `usage_diagnostic(message: str) -> bytes`;
  `write_stdout(data: bytes) -> bool`; `write_stderr(data: bytes) -> bool`
- **Responsibility:** exact bytes and binary writes.
- **Algorithm:** `encode` uses `text.encode("utf-8", "surrogatepass")` on Windows and
  `os.fsencode(text)` on POSIX (§5). Writes go to `sys.stdout.buffer`/`sys.stderr.buffer`
  followed by `flush()`. A missing buffer (closed descriptor) or `OSError` returns `False`;
  after an error the descriptor is pointed at the null device so the interpreter's exit-time
  flush cannot print a traceback.
- **Satisfies:** CONV-03, CONV-05, CONV-13, CONV-14, CONV-25, FR-11.
- **Unit tests:** `test_cli.py::test_diagnostic_format`, `test_broken_pipe_is_silent`,
  `test_closed_stdout_does_not_crash`, `test_undecodable_argument_bytes_round_trip`,
  `test_process_output_is_utf8_and_lf_only`.

### 3.5 `cli.main`, `cli.run`
- **Signatures:** `main(args: list[str]) -> int`; `run() -> None` (console-script entry point,
  `sys.exit(main(sys.argv[1:]))`)
- **Algorithm:** parse → help/version text, or validate + `greeting_text`; on `UsageError` write
  the diagnostic to stderr and return 2; otherwise write the text and return 0 (141 if stdout
  could not be written).
- **Satisfies:** FR-01 … FR-11, CONV-02, CONV-12, CONV-14, CONV-18, CONV-23, CONV-24.
- **Unit tests:** `tests/test_cli.py`.

## 4. Algorithms
The only algorithms are the scanner (§3.1) and the count check (§3.2). The scanner is a single
pass with one index, which makes scan order (CONV-12) and "first error wins" fall out of the
control flow. Counting with an explicit ASCII digit set, rather than `str.isdigit()` or `int()`,
is required because both accept non-ASCII digits and `int()` also accepts `+`, `-`, `_`, and
surrounding whitespace.

## 5. Platform-specific details

| Concern | Linux | macOS | Windows | Abstraction |
| :-- | :-- | :-- | :-- | :-- |
| argv decoding | bytes → str (UTF-8 or locale, `surrogateescape`) | same | UTF-16 command line → str | `output.encode` inverts it |
| Line endings | binary buffer | binary buffer | binary buffer (no CRLF) | `output._write` |
| EPIPE | `BrokenPipeError` | `BrokenPipeError` | `OSError` (`EINVAL`/`EPIPE`) | `output._write` catches `OSError` |
| Executable in `BIN_DIR` | `.venv/bin/dp-hello` (`#!` script) | same | `.venv/Scripts/dp-hello.exe` | Makefile `VENV_SCRIPTS` |
| Installed launcher | `#!/bin/sh` script execing the installed console script | same | same (run from Git Bash / MSYS2) | `DP_INSTALL` |

## 6. Resource management
No files, sockets, or child processes are used at run time. The only buffer is the output
string: at most 1000 × (9 + len(NAME)) bytes. `output._silence` opens and closes the null device
only after a failed write.

## 7. Sequence of one invocation
P06, `dp-hello -c2 -n Ken`: `run` → `main(["-c2", "-n", "Ken"])` → `parse_args`:
`_parse_short_bundle("-c2")` stores `OptionValue("2", "-c")`; `_parse_short_bundle("-n")` takes
the next token, `OptionValue("Ken", "-n")` → `ParsedArgs(GREET, name, count)` → `validate` →
`Config("Ken", 2)` → `greeting_text("Ken", 2)` → `encode` → `write_stdout(b"Hello, Ken!\nHello, Ken!\n")`
→ `main` returns 0 → `sys.exit(0)`.

## 8. Design-to-code checklist

| HLD component | LLD section | Source file(s) | Unit-test file(s) |
| :-- | :-- | :-- | :-- |
| options | §3.1 | `src/dp_hello/options.py` | `tests/test_options.py` |
| validation | §3.2 | `src/dp_hello/validation.py` | `tests/test_validation.py` |
| greeting | §3.3 | `src/dp_hello/greeting.py` | `tests/test_greeting.py` |
| output | §3.4 | `src/dp_hello/output.py` | `tests/test_cli.py` |
| cli | §3.5 | `src/dp_hello/cli.py`, `src/dp_hello/__main__.py` | `tests/test_cli.py` |
