# High-Level Design (HLD) — Standard Terminal Hello World

| Field | Value |
| :-- | :-- |
| Project | `00-hello-world` |
| Tools | dp-hello |
| Implementation language | py (Python 3.14, uv) |
| Author | Brandon Perkins |
| Version / date | 1.0 — 2026-10-13 |
| Status | In review |
| Inputs | `specs/URD.md`, `specs/SRS.md`, `specs/user-manual.md`, `shared/CLI-CONVENTIONS.md` |

## 1. Introduction

### 1.1 Scope
`dp-hello` writes `Hello, NAME!` + LF to standard output COUNT times (NAME defaults to `World`,
COUNT to 1, range 1–1000), prints help and version text, and rejects every usage error with
an exact CONV-13 diagnostic and exit status 2. It reads no input, files, or environment
variables, takes no operands, and runs no subprocesses (SRS §1.2, §3, NFR-07).

### 1.2 Definitions and acronyms
| Term | Meaning |
| :-- | :-- |
| Token | One element of `sys.argv[1:]` |
| Spelling | The option as the user wrote it (`-n` or `--name`), used in diagnostics |
| Console script | The launcher uv generates for `[project.scripts]` (`dp-hello`, `dp-hello.exe`) |
| venv | A Python virtual environment |

### 1.3 References
- SRS §3.2 (options), §4 (FR-01 … FR-11), §5 (NFR-01 … NFR-07), §6 (diagnostics)
- CLI-CONV §2 (CONV-03, CONV-05), §3 (CONV-07 … CONV-12), §4.1 (CONV-13 … CONV-15), §8

## 2. Requirements summary

| Area | SRS requirements | Architectural impact |
| :-- | :-- | :-- |
| Option parsing | FR-02, FR-06, FR-07, FR-08, FR-10, CONV-07 … CONV-12 | A hand-written, purely syntactic parser (`options`) that stops at `--help`/`--version` |
| Validation | FR-03, FR-04, FR-05, FR-09 | A separate `validation` unit turns raw values into a `Config` |
| Greeting | FR-01, FR-02, FR-04, NFR-05 | A pure function with no I/O (`greeting`) |
| Output and diagnostics | FR-11, NFR-01, CONV-03, CONV-05, CONV-13, CONV-14, CONV-25 | One `output` unit encodes text and writes bytes; all output happens after all checks |
| Robustness | NFR-03, CONV-24 | Errors are values (`UsageError`) caught in one place; I/O failures are handled, never propagated |
| Build / install | NFR-06, UR-12 | uv project; console script in the venv; installed venv + `#!/bin/sh` launcher |

## 3. Architectural overview

### 3.1 Context diagram

```text
   argv (UTF-8 bytes / UTF-16 on Windows) ──▶ ┌──────────┐ ──▶ stdout (greeting, help, version)
                                              │ dp-hello │ ──▶ stderr (usage diagnostics)
                                              └──────────┘ ──▶ exit status 0 / 2
   (stdin, files, environment, network: not used)
```

### 3.2 Component (module) decomposition

| Component | Responsibility | Depends on |
| :-- | :-- | :-- |
| `dp_hello.options` | Turn argv into a `ParsedArgs` (action, raw values with spellings, first operand) or raise `UsageError` for syntax errors | — |
| `dp_hello.validation` | Turn a `ParsedArgs` into a validated `Config` or raise `UsageError` | `options` (types) |
| `dp_hello.greeting` | Build the greeting text from a name and count (pure) | — |
| `dp_hello.output` | Encode text to exact bytes; write stdout/stderr in binary; format diagnostics; handle EPIPE | — |
| `dp_hello.cli` | Entry point: orchestrate the units, own the help/version texts and exit statuses | all of the above |

### 3.3 Data flow
`cli.run` passes `sys.argv[1:]` to `cli.main`. `options.parse_args` scans left to right; on
`--help`/`--version` it returns immediately. Otherwise `validation.validate` rejects operands
and invalid values and yields a `Config`, and `greeting.greeting_text` builds the whole output
as one string. Only then does `output.write_stdout` encode and write it in one call, and `main`
returns 0. Any `UsageError` raised on the way is turned by `main` into the two-line diagnostic
on stderr and status 2, so nothing reaches stdout (FR-11).

## 4. Key design decisions

| # | Decision | Alternatives considered | Rationale |
| :-- | :-- | :-- | :-- |
| D1 | Hand-written parser | `argparse`, `getopt` | argparse's messages, abbreviations, and exit codes differ from CONV-08/CONV-13; getopt cannot report the spelling of the winning option; third-party parsers are excluded |
| D2 | Parse (syntax) and validate (values) separately | Validate while parsing | FR-06/CONV-12: only the winning value is validated, and `--help` after an invalid value still wins |
| D3 | Build the complete output, then write once | Stream line by line | At most 1000 short lines; guarantees "no stdout on error" and a single write |
| D4 | One exception type, mapped to diagnostics in `cli.main` only | Status codes returned through every function | A single mapping point for messages and exit statuses (§6) |
| D5 | Write bytes to `sys.stdout.buffer` / `sys.stderr.buffer` | Text streams | No CRLF translation on Windows and no locale encoding (CONV-03, CONV-06) |
| D6 | uv project with a console script; `BIN_DIR` is the venv's script directory | A hand-written `#!` launcher in `build/` | uv generates a `#!` script on POSIX and a native `.exe` on Windows, so the black-box runner works on every OS without extra code |

## 5. Cross-platform strategy
All platform differences are isolated in `dp_hello.output`. Output is encoded to bytes and
written to the binary buffers, so LF is never translated to CRLF on Windows (CONV-03, NFR-01).
For arguments, CPython on Windows builds `sys.argv` from the UTF-16 command line, so
`output.encode` encodes the text as UTF-8 (`surrogatepass`); on POSIX it uses `os.fsencode`,
the exact inverse of how CPython decoded the argument bytes, so names are echoed byte-for-byte
whatever the locale (CONV-05, CONV-06). `dp-hello` handles no paths, so CONV-19 … CONV-21 do
not apply. The build is identical on every OS; only the venv script directory differs (`bin`
or `Scripts`, chosen in the Makefile).

## 6. Error handling and diagnostics
Syntax and value errors raise `options.UsageError(message)`, where `message` is the CONV-13
text without the tool prefix. `cli.main` is the only place that catches it: it writes
`output.usage_diagnostic(message)` (`dp-hello: <message>` + LF + the CONV-14 line) to stderr
and returns 2. Write failures (EPIPE, a closed stream) are reported by `output` as `False`;
`main` then returns 141 without a diagnostic (CONV-25). No other exception escapes for any
argument list.

## 7. Non-functional design

| Quality attribute | SRS reference | How the design achieves it |
| :-- | :-- | :-- |
| Performance / memory | NFR-02 | Standard library only and five small modules; about 40 ms per run, well under 32 MiB |
| Portability | NFR-01 | Binary-mode output and explicit encoding in `output` (§5) |
| Robustness | NFR-03 | Total parser and validator (every token ends in a value or a `UsageError`); guarded writes |
| Security / input validation | NFR-07 | No file, environment, or subprocess access in the code; COUNT checked as ASCII digits before conversion |
| Maintainability | NFR-04, NFR-05 | One module per responsibility; pure greeting construction; `mypy --strict` and ruff |

## 8. Risks and open issues

| Risk / issue | Likelihood | Impact | Mitigation |
| :-- | :-- | :-- | :-- |
| Windows console-script launcher or argv decoding differs from POSIX | M | H | Native Windows CI runs both black-box suites and `test_process_output_is_utf8_and_lf_only` |
| A `.venv` created in the container is reused on the host (or the reverse) | M | L | uv detects the foreign interpreter and recreates the venv |
| Python start-up time on slow CI runners | L | M | No third-party imports at run time; measured far below the 300 ms budget |

## 9. Approval

| Role | Name | Date | Decision |
| :-- | :-- | :-- | :-- |
| Author | Brandon Perkins | 2026-10-13 | Submitted |
| Reviewer | Pull-request reviewer | — | Pending |
