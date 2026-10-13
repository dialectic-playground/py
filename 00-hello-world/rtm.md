# Requirements Traceability Matrix (RTM) — Standard Terminal Hello World

| Field | Value |
| :-- | :-- |
| Project | `00-hello-world` |
| Tools | dp-hello |
| Author | Brandon Perkins |
| Version / date | 1.0 — 2026-10-13 |

Code paths are relative to `src/dp_hello/`; unit tests are in `tests/` (`file::test`).
Public black-box tests are `P01` … `P10` (`tests/public` of the curriculum). The hidden suite
runs in CI on Linux, macOS, and Windows and is not cited.

## 1. User requirements to system requirements

| User requirement (URD) | Derived system requirements (SRS) |
| :-- | :-- |
| UR-01 | FR-01 |
| UR-02 | FR-02 |
| UR-03 | FR-04 |
| UR-04 | FR-07 |
| UR-05 | FR-08 |
| UR-06 | FR-03, FR-05, FR-09, FR-10, FR-11 |
| UR-07 | FR-01, SRS §3.7 |
| UR-08 | NFR-01, CONV-03 |
| UR-09 | FR-02, CONV-05 |
| UR-10 | FR-06, FR-10, CONV-07 … CONV-15 |
| UR-11 | NFR-02 |
| UR-12 | NFR-06 |

## 2. Forward traceability

| Req. ID | Summary | Design (HLD/LLD) | Code (file::function) | Verification (unit / black-box) | Status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| UR-01 … UR-12 | User needs | HLD §2 | via the FR/NFR rows below | via the FR/NFR rows below; P01–P10 | Verified |
| FR-01 | Default greeting | HLD §3.3, LLD §3.3 | `greeting.py::greeting_line`, `validation.py::validate` | `test_greeting.py::test_default_greeting_line`, `test_validation.py::test_defaults`, `test_cli.py::test_default_greeting`, P01 | Verified |
| FR-02 | Named greeting, verbatim, UTF-8 | HLD §5, LLD §3.1, §3.4 | `options.py::parse_args`, `greeting.py::greeting_line`, `output.py::encode` | `test_options.py::test_name_spellings_are_equivalent`, `test_name_may_begin_with_a_dash`, `test_non_ascii_values_are_kept_verbatim`, `test_greeting.py::test_name_is_used_verbatim`, `test_cli.py::test_non_ascii_name_is_written_as_utf8`, P02, P03, P04 | Verified |
| FR-03 | Empty name rejected | LLD §3.2 | `validation.py::validate_name` | `test_validation.py::test_empty_name_is_rejected`, `test_cli.py::test_usage_errors_write_only_stderr_and_exit_2` | Verified |
| FR-04 | Repetition 1–1000, leading zeros | LLD §3.2, §3.3 | `validation.py::validate_count`, `greeting.py::greeting_text` | `test_validation.py::test_valid_counts`, `test_greeting.py::test_greeting_text_repeats_count_times`, `test_cli.py::test_maximum_count`, P05, P06 | Verified |
| FR-05 | Invalid count rejected | LLD §3.2 | `validation.py::validate_count` | `test_validation.py::test_invalid_counts_are_rejected_verbatim`, `test_invalid_count_reports_the_long_spelling` | Verified |
| FR-06 | Last occurrence wins | LLD §3.1 | `options.py::parse_args` | `test_options.py::test_last_occurrence_wins_and_keeps_its_spelling`, `test_values_are_not_validated_by_the_parser` | Verified |
| FR-07 | Help, scan order | HLD D2, LLD §3.1, §3.5 | `options.py::_parse_long`, `cli.py::main`, `cli.py::HELP_TEXT` | `test_options.py::test_help_and_version_stop_the_scan`, `test_cli.py::test_help_is_byte_exact`, P07 | Verified |
| FR-08 | Version | LLD §3.5 | `cli.py::main`, `cli.py::VERSION_TEXT` | `test_cli.py::test_version`, P08 | Verified |
| FR-09 | Operands rejected | LLD §3.1, §3.2 | `options.py::parse_args`, `validation.py::validate` | `test_options.py::test_double_dash_ends_options`, `test_double_dash_hides_help`, `test_validation.py::test_operand_is_reported_before_invalid_values`, P10 | Verified |
| FR-10 | Unknown / malformed options | LLD §2.3, §3.1 | `options.py::_parse_long`, `options.py::_parse_short_bundle` | `test_options.py::test_syntax_errors_use_conv13_messages`, `test_first_error_in_scan_order_wins`, P09 | Verified |
| FR-11 | No stdout on error | HLD §3.3, D3 | `cli.py::main` | `test_cli.py::test_usage_errors_write_only_stderr_and_exit_2`, P09, P10 | Verified |
| NFR-01 | Byte-identical, LF only | HLD §5, LLD §5 | `output.py::write_stdout`, `output.py::encode` | `test_cli.py::test_process_output_is_utf8_and_lf_only`, `test_help_is_byte_exact`, P01–P10 on 3 OSes (CI) | Verified |
| NFR-02 | < 300 ms, < 32 MiB | HLD §7 | whole package (stdlib only) | MTP §4.4 measurement | Verified |
| NFR-03 | No crash / stack trace | HLD §6 | `cli.py::main`, `output.py::_write` | `test_cli.py::test_broken_pipe_is_silent`, `test_closed_stdout_does_not_crash`, `test_validation.py::test_invalid_counts_are_rejected_verbatim` | Verified |
| NFR-04 | Separate units | HLD §3.2 | `options.py`, `validation.py`, `greeting.py`, `output.py` | Design review (LLD §8); one test file per unit | Verified |
| NFR-05 | Pure, unit-tested greeting | LLD §3.3 | `greeting.py::greeting_text` | `test_greeting.py` (all) | Verified |
| NFR-06 | Every Makefile target | HLD D6 | `Makefile` (DP_* hooks) | CI: `make check` (container, 3 native OSes) and `make roundtrip` | Verified |
| NFR-07 | No files / env / subprocesses | HLD §7 | whole package | Inspection (only `sys`, `os.fsencode`, `os.open(os.devnull)` after a failed write) | Verified |
| CONV-01 | Canonical name | LLD §3.4 | `output.py::TOOL`, `cli.py::HELP_TEXT` | `test_cli.py::test_diagnostic_format`, P07–P10 | Verified |
| CONV-02 | Version line | LLD §3.5 | `cli.py::VERSION_TEXT` | `test_cli.py::test_version`, P08 | Verified |
| CONV-03 | LF output, binary mode | HLD §5 | `output.py::_write` | `test_cli.py::test_process_output_is_utf8_and_lf_only`, P01–P10 | Verified |
| CONV-05 | UTF-8 arguments | HLD §5, LLD §5 | `output.py::encode` | `test_cli.py::test_non_ascii_name_is_written_as_utf8`, `test_undecodable_argument_bytes_round_trip`, `test_process_output_is_utf8_and_lf_only` | Verified |
| CONV-06 | Locale-independent | HLD D5 | `output.py::encode`, `validation.py::validate_count` | `test_validation.py::test_invalid_counts_are_rejected_verbatim` (non-ASCII digits), P01–P10 (empty environment) | Verified |
| CONV-07 | Short options | LLD §3.1 | `options.py::_parse_short_bundle` | `test_options.py::test_bundled_short_options_take_the_rest_of_the_token`, `test_bundled_value_may_contain_option_letters`, P06 | Verified |
| CONV-08 | Long options, no abbreviation | LLD §3.1 | `options.py::_parse_long` | `test_options.py::test_name_spellings_are_equivalent`, `test_syntax_errors_use_conv13_messages`, P04 | Verified |
| CONV-09 | `--` terminator | LLD §3.1 | `options.py::parse_args` | `test_options.py::test_double_dash_ends_options`, `test_lone_double_dash_is_harmless` | Verified |
| CONV-10 | Operands, interleaving | LLD §3.1 | `options.py::parse_args` | `test_options.py::test_single_dash_is_an_operand`, `test_operands_and_options_may_interleave`, P10 | Verified |
| CONV-11 | Repetition | LLD §3.1 | `options.py::parse_args` | `test_options.py::test_last_occurrence_wins_and_keeps_its_spelling` | Verified |
| CONV-12 | Scan order | HLD D2 | `options.py::parse_args`, `cli.py::main` | `test_options.py::test_help_and_version_stop_the_scan`, `test_first_error_in_scan_order_wins`, `test_cli.py::test_help_is_byte_exact` | Verified |
| CONV-13 | Exact usage messages | LLD §2.3 | `options.py`, `validation.py` | `test_options.py::test_syntax_errors_use_conv13_messages`, `test_cli.py::test_usage_errors_write_only_stderr_and_exit_2`, P09, P10 | Verified |
| CONV-14 | "Try" line, exit 2 | HLD §6 | `output.py::usage_diagnostic`, `cli.py::main` | `test_cli.py::test_diagnostic_format`, P09, P10 | Verified |
| CONV-15 | Values verbatim, `''` | LLD §3.2 | `validation.py::_invalid` | `test_validation.py::test_empty_name_is_rejected`, `test_invalid_counts_are_rejected_verbatim` | Verified |
| CONV-18 | Exit statuses | HLD §6 | `cli.py::main` | `test_cli.py` (all status assertions), P01–P10 | Verified |
| CONV-22 | `--help`/`--version` take no argument | LLD §3.1 | `options.py::_parse_long` | `test_options.py::test_syntax_errors_use_conv13_messages` | Verified |
| CONV-23 | Help byte-for-byte | LLD §3.5 | `cli.py::HELP_TEXT` | `test_cli.py::test_help_is_byte_exact`, P07 | Verified |
| CONV-24 | No crash | HLD §6 | `cli.py::main`, `output.py::_write` | `test_cli.py::test_broken_pipe_is_silent`, `test_closed_stdout_does_not_crash` | Verified |
| CONV-25 | EPIPE: quiet exit | LLD §3.4 | `output.py::_write`, `output.py::_silence` | `test_cli.py::test_broken_pipe_is_silent` | Verified |
| CONV-26 | stdin not read | HLD §3.1 | whole package | Inspection; P01–P10 (stdin is the null device) | Verified |
| CONV-27 … CONV-30 | Harness conditions | HLD D6 | `Makefile` (`BIN_DIR`) | P01–P10 via `run-tests.py` on 3 OSes | Verified |

## 3. Backward traceability (test → requirement)

| Test | Type | Requirement(s) verified |
| :-- | :-- | :-- |
| P01 | black-box, public | FR-01, NFR-01, CONV-03 |
| P02, P03, P04 | black-box, public | FR-02, CONV-08 (P04) |
| P05 | black-box, public | FR-04 |
| P06 | black-box, public | FR-04, CONV-07 |
| P07 | black-box, public | FR-07, CONV-23 |
| P08 | black-box, public | FR-08, CONV-02 |
| P09 | black-box, public | FR-10, FR-11, CONV-13, CONV-14 |
| P10 | black-box, public | FR-09, FR-11, CONV-10, CONV-13, CONV-14 |
| `tests/test_options.py` (19 tests) | unit | FR-02, FR-06, FR-07, FR-09, FR-10, CONV-07 … CONV-13, CONV-22 |
| `tests/test_validation.py` (9 tests) | unit | FR-01, FR-03, FR-04, FR-05, FR-09, CONV-06, CONV-15 |
| `tests/test_greeting.py` (5 tests) | unit | FR-01, FR-02, FR-04, NFR-05 |
| `tests/test_cli.py` (12 tests) | unit / integration | FR-01 … FR-11, NFR-01, NFR-03, CONV-01 … CONV-05, CONV-14, CONV-18, CONV-23 … CONV-25 |

## 4. Coverage summary

| Category | Total | Designed | Implemented | Verified |
| :-- | :-- | :-- | :-- | :-- |
| User requirements (UR) | 12 | 12 | 12 | 12 |
| Functional (FR) | 11 | 11 | 11 | 11 |
| Non-functional (NFR) | 7 | 7 | 7 | 7 |
| Conventions (CONV) | 24 applicable | 24 | 24 | 24 |

## 5. Gaps and justifications

No applicable requirement is unverified. Not applicable to `dp-hello`, which copies no input
and touches no files or paths: CONV-04 (byte pass-through), CONV-16 and CONV-17 (file errors),
CONV-19 … CONV-21 (paths and traversal). NFR-02 and NFR-07 are verified by measurement and
inspection, as SRS §7 prescribes.
