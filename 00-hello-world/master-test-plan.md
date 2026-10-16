<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Master Test Plan (MTP) — Standard Terminal Hello World](#master-test-plan-mtp--standard-terminal-hello-world)
  - [1. Introduction and scope](#1-introduction-and-scope)
    - [1.1 Objectives](#11-objectives)
    - [1.2 In scope / out of scope](#12-in-scope--out-of-scope)
  - [2. Test items](#2-test-items)
  - [3. Test levels and approach](#3-test-levels-and-approach)
  - [4. Test design](#4-test-design)
    - [4.1 Equivalence partitions and boundaries](#41-equivalence-partitions-and-boundaries)
    - [4.2 Additional test cases (beyond the supplied suite)](#42-additional-test-cases-beyond-the-supplied-suite)
    - [4.3 Negative and robustness testing](#43-negative-and-robustness-testing)
    - [4.4 Performance and resource testing](#44-performance-and-resource-testing)
  - [5. Test environments](#5-test-environments)
  - [6. Entry and exit criteria](#6-entry-and-exit-criteria)
  - [7. Defect management](#7-defect-management)
  - [8. Schedule and deliverables](#8-schedule-and-deliverables)
  - [9. Risks and contingencies](#9-risks-and-contingencies)
  - [10. Test summary](#10-test-summary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Master Test Plan (MTP) — Standard Terminal Hello World

| Field                   | Value                                                  |
| :---------------------- | :----------------------------------------------------- |
| Project                 | `00-hello-world`                                       |
| Tools                   | dp-hello                                               |
| Implementation language | py (Python 3.14, uv)                                   |
| Author                  | Brandon Perkins                                        |
| Version / date          | 1.0 — 2026-10-13                                       |
| Standard                | Structure adapted from IEEE 829 / ISO/IEC/IEEE 29119-3 |

## 1. Introduction and scope

### 1.1 Objectives

"Tested enough" means: every SRS acceptance criterion (FR-01 … FR-11) is exercised by a unit
or black-box test; every CONV-13 diagnostic and every count boundary has a unit test; the 10
public and 10 hidden black-box tests pass on Linux, macOS, and Windows; and `make lint`
(ruff check, ruff format --check, mypy --strict) is clean.

### 1.2 In scope / out of scope

| In scope                                                                            | Out of scope                                                                            |
| :---------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------- |
| Every FR/NFR in the SRS and the applicable CONV rules, on Linux, macOS, and Windows | Terminal rendering of non-ASCII names (a console concern, user manual "Platform notes") |
| Build, install, and uninstall through the Makefile                                  | Python versions other than 3.14                                                         |

## 2. Test items

| Item                   | Version / location                                                             |
| :--------------------- | :----------------------------------------------------------------------------- |
| dp-hello               | `00-hello-world/src/dp_hello/` on branch `feat/00-hello-world`                 |
| Unit tests             | `00-hello-world/tests/` (pytest)                                               |
| Public black-box suite | `sdlc-curriculum/projects/00-hello-world/tests/public/` (10 tests)             |
| Hidden black-box suite | `sdlc-curriculum/projects/00-hello-world/tests/private/` (10 tests, run by CI) |

## 3. Test levels and approach

| Level              | Purpose                                                                             | Technique(s)                                                      | Tooling                             | Owner          |
| :----------------- | :---------------------------------------------------------------------------------- | :---------------------------------------------------------------- | :---------------------------------- | :------------- |
| Unit               | Parser, validator, greeting, and output units in isolation                          | Equivalence partitioning, boundary-value analysis, error guessing | pytest (`make test`)                | Developer      |
| Integration        | `cli.main` wiring the units, with real captured byte streams; one child-process run | Specification-based                                               | pytest `capsysbinary`, `subprocess` | Developer      |
| System (black-box) | Specified CLI behavior, byte-exact                                                  | Specification-based                                               | `make test` → `run-tests.py`        | Developer      |
| Acceptance         | Hidden suite on all OSes                                                            | —                                                                 | CI `make check` (`test-hidden`)     | CI             |
| Static analysis    | Style, lint, strict typing                                                          | —                                                                 | `make lint`                         | Developer / CI |

## 4. Test design

### 4.1 Equivalence partitions and boundaries

| Input               | Valid partitions                                          | Invalid partitions                                                             | Boundaries                                                              |
| :------------------ | :-------------------------------------------------------- | :----------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| NAME                | Any non-empty text: ASCII, spaces, non-ASCII, leading `-` | Empty string                                                                   | `""` (invalid), one character                                           |
| COUNT               | ASCII digits with value 1–1000, leading zeros allowed     | Empty, non-digits (signs, spaces, `.`, `_`, Unicode digits), value 0 or > 1000 | 0, 1, 1000, 1001, `007`, `0001000`, `00001001`, very long digit strings |
| Option syntax       | `-nX`, `-n X`, `--name=X`, `--name X`, repetitions        | Unknown short/long, abbreviations, missing values, `--help=`/`--version=`      | `--name=` (empty value), `-n` at end of argv                            |
| Operands            | none                                                      | Any operand, including after `--` and `-`                                      | `--` alone (valid)                                                      |
| Environment / stdin | Ignored                                                   | —                                                                              | Empty environment (runner)                                              |

### 4.2 Additional test cases (beyond the supplied suite)

| ID   | Requirement(s)   | Preconditions                               | Steps / command                                  | Expected result                             | Level       |
| :--- | :--------------- | :------------------------------------------ | :----------------------------------------------- | :------------------------------------------ | :---------- |
| T-01 | FR-04, FR-05     | —                                           | `validate_count` with 1, 1000, 0, 1001           | 1 and 1000 accepted; 0 and 1001 rejected    | unit        |
| T-02 | FR-04            | —                                           | `validate_count("007")`                          | 7                                           | unit        |
| T-03 | FR-05, CONV-06   | —                                           | counts `+1`, `1`, `1_000`, `١٢`, `²`             | `invalid argument` for each                 | unit        |
| T-04 | FR-03, CONV-15   | —                                           | `--name ''`, `-n ''`                             | `invalid argument '' for '--name'` / `'-n'` | unit        |
| T-05 | FR-02            | —                                           | `--name -x`, `-n-x`, `--name=-x`, `-n --help`    | name is the dash value, no help             | unit        |
| T-06 | FR-06            | —                                           | `-n A --name B --count=5 -c 7`                   | name B (`--name`), count 7 (`-c`)           | unit        |
| T-07 | FR-07, CONV-12   | —                                           | `--help extra -x`, `extra --help`, `-c 0 --help` | help, exit 0                                | unit        |
| T-08 | FR-10, CONV-12   | —                                           | `-x --help`, `--nme -x`                          | the first error in scan order               | unit        |
| T-09 | FR-09, CONV-09   | —                                           | `-- -n`, `-- --help`                             | `extra operand '-n'` / `'--help'`           | unit        |
| T-10 | FR-10, CONV-08   | —                                           | `--nam`, `--names=x`, `---`, `--=`               | `unrecognized option '<token>'`             | unit        |
| T-11 | CONV-05          | POSIX                                       | `-n` with bytes `Z\xffo`                         | bytes echoed unchanged                      | integration |
| T-12 | CONV-03, CONV-05 | child process                               | `python -m dp_hello -c2 --name 'Zoë Ådahl'`      | two UTF-8 lines, LF only (also on Windows)  | integration |
| T-13 | CONV-25, NFR-03  | stdout raises `BrokenPipeError` / is `None` | `main([])`                                       | exit 141, no stderr, no traceback           | unit        |
| T-14 | FR-04            | —                                           | `--count=1000`                                   | exactly 1000 lines                          | integration |

### 4.3 Negative and robustness testing

Every CONV-13 message is asserted by `test_syntax_errors_use_conv13_messages` and
`test_usage_errors_write_only_stderr_and_exit_2` (which also checks that stdout stays empty).
Broken pipes and closed stdout are simulated (T-13). Huge digit strings are rejected without
conversion (T-01 data). dp-hello reads no files or stdin, so missing files, permissions, and
binary input do not apply.

### 4.4 Performance and resource testing

NFR-02 (interpreted: < 300 ms, < 32 MiB): measured with `/usr/bin/time -v .venv/bin/dp-hello
-c 1000 > /dev/null` on Linux. Result on the development machine: about 40 ms wall clock and
about 13 MiB maximum RSS. The CI black-box runs act as a regression guard (runner timeout).

## 5. Test environments

| Environment       | OS / version                                           | Toolchain                                                       | How provisioned                |
| :---------------- | :----------------------------------------------------- | :-------------------------------------------------------------- | :----------------------------- |
| Local (container) | Fedora host, Debian trixie image                       | Python 3.14, uv 0.13                                            | `make check` (`Containerfile`) |
| Local (native)    | Fedora 44                                              | Python 3.14, uv                                                 | `DP_RUNTIME=local make test`   |
| CI                | ubuntu-latest, macos-latest, windows-latest (Git Bash) | Python 3.14 via `astral-sh/setup-uv` + `uv python install 3.14` | `.github/workflows/ci.yml`     |

## 6. Entry and exit criteria

- **Entry:** HLD/LLD written; `make all` succeeds; `make lint` is clean.
- **Exit:** all unit tests pass; the public and hidden black-box suites pass on all three OSes
  in CI; `make roundtrip` passes natively on all three OSes; the RTM shows every requirement
  as Verified; no open severity-1/2 defects.
- **Suspension / resumption:** suspend when the toolchain cannot be provisioned (for example a
  package index outage); resume by re-running CI.

## 7. Defect management

Defects are GitHub issues in this repository with a severity label. Every fix adds a unit test
that fails before the fix and passes after it, and CI re-runs every level on all OSes.

| Severity     | Definition                                                               |
| :----------- | :----------------------------------------------------------------------- |
| 1 — Critical | Crash, stack trace, or wrong output or exit status on a mainline path    |
| 2 — Major    | A wrong diagnostic, or a failure on one OS only                          |
| 3 — Minor    | Documentation, lint, or build-ergonomics issue with no behavioral effect |

## 8. Schedule and deliverables

| Milestone               | Deliverable                  | Target date |
| :---------------------- | :--------------------------- | :---------- |
| Design complete         | hld.md, lld.md               | 2026-10-13  |
| Implementation complete | src/, tests/, Makefile hooks | 2026-10-13  |
| Verification complete   | RTM all Verified, CI green   | 2026-10-13  |

## 9. Risks and contingencies

| Risk                                                        | Mitigation                                                              |
| :---------------------------------------------------------- | :---------------------------------------------------------------------- |
| Windows-only failure (argv decoding, CRLF, `.exe` launcher) | Native Windows CI from the first commit; T-12 runs a real child process |
| Lockfile drift between uv versions                          | `--locked` on every uv command; Dependabot (uv) updates the lockfile    |

## 10. Test summary

| Metric                                | Value                                                                                              |
| :------------------------------------ | :------------------------------------------------------------------------------------------------- |
| Unit tests (pass / total)             | 114 / 114 (45 test functions, parametrized)                                                        |
| Coverage (line / branch)              | Not measured (no coverage tool in the agreed tool set); every function and error branch has a test |
| Public black-box (pass / 10)          | 10 / 10 (container and native Linux; CI on 3 OSes)                                                 |
| Hidden black-box (pass / 10, from CI) | 10 / 10                                                                                            |
| Open defects by severity              | 0 / 0 / 0                                                                                          |
