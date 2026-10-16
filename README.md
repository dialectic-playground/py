<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [py](#py)
  - [Python at a glance](#python-at-a-glance)
  - [Toolchain](#toolchain)
  - [Layout](#layout)
  - [Development](#development)
  - [Implementing a project](#implementing-a-project)
  - [Contributing](#contributing)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dialectic-playground/.github/main/assets/py/dist/logo-dark.svg">
    <img alt="dialectic playground / py" src="https://raw.githubusercontent.com/dialectic-playground/.github/main/assets/py/dist/logo.svg" height="96">
  </picture>
</p>

# py

Python implementation of the Dialectic Playground SDLC curriculum.

📖 **Documentation:** <https://dialectic-playground.github.io/docs/reference/languages/py/>

This repository implements the fifty-three projects of the
[SDLC curriculum](https://github.com/dialectic-playground/sdlc-curriculum) in Python. Each project is
specified to the byte by the curriculum and verified by its black-box tests on Linux, macOS,
and Windows.

**Status:** Implemented projects: 00-hello-world.

## Python at a glance

| Aspect                  | Python                                            |
| :---------------------- | :------------------------------------------------ |
| File extension          | `.py`                                             |
| CLI classification      | Included                                          |
| Image category          | First-Class                                       |
| Access to OS primitives | High (via sys/os/subprocess)                      |
| Entry-point mechanism   | Interpreter maps args to high-level sys.argv list |

## Toolchain

|                      |                                                                                       |
| :------------------- | :------------------------------------------------------------------------------------ |
| Release line         | Python 3.14                                                                           |
| Build / package tool | uv                                                                                    |
| Container image      | `python:3.14-slim-trixie (+ uv)`, pinned by digest ([`Containerfile`](Containerfile)) |
| Native CI            | astral-sh/setup-uv, then uv python install 3.14                                       |

`make toolchain` verifies that the container and native toolchains are on this release line.

Each project is a uv project: `pyproject.toml` and the committed `uv.lock` live in the project
directory, sources in `src/<package>/`, and unit tests in `tests/`. The dev dependency group
provides the project tools, which uv installs into the project's `.venv/` on `make all`:

| Purpose    | Tool                                                 | Make target   |
| :--------- | :--------------------------------------------------- | :------------ |
| Unit tests | pytest                                               | `make test`   |
| Lint       | `ruff check`, `ruff format --check`, `mypy --strict` | `make lint`   |
| Format     | `ruff format`                                        | `make format` |

`make all` runs `uv sync --locked`, which installs the tool as a console script into the
project's `.venv` (`BIN_DIR` is `.venv/bin`, or `.venv/Scripts` on Windows). The container
mounts the repository at the same path as the host, so the same `.venv` serves both; uv
recreates it when it was made by the other environment. `make install` puts a virtual
environment under `$(LIBDIR)/py/<project>/` and a `#!/bin/sh` launcher in `$(BINDIR)`.
Dependabot (uv) keeps each project's lockfile current.

**Windows:** run the installed tools from Git Bash or MSYS2, which honor `#!` lines. (The
build itself produces native `dp-*.exe` console-script launchers in `.venv/Scripts`.)

## Layout

| Path                                 | Contents                                                                                                          |
| :----------------------------------- | :---------------------------------------------------------------------------------------------------------------- |
| `00-hello-world/` … `52-spacecraft/` | One workspace per curriculum project: `Makefile` (with `DP_*` hooks), HLD, LLD, RTM, master test plan, and `src/` |
| `sdlc-curriculum/`                   | The curriculum, as a git submodule pinned to a release tag                                                        |
| `Makefile`                           | `make check` (repository, toolchain, implemented projects), `toolchain`, `projects`, `roundtrip`                  |
| `Containerfile`, `.devcontainer/`    | The toolchain image and the matching dev container                                                                |
| `tools/dp-run`, `tools/container.mk` | Shared container tooling (copies of the canonical files in `dialectic-playground/.github`)                        |
| `.github/workflows/ci.yml`           | CI: container and native (Linux, macOS, Windows) `make` targets, shared-tooling check, DCO                        |

## Development

Container-first: `make` targets and `tools/dp-run <command>` run in the toolchain container
via Podman, then Docker, then the local system. `DP_RUNTIME=podman|docker|local` overrides
the choice.

```sh
git clone --recurse-submodules https://github.com/dialectic-playground/py.git
cd py
make check                    # repository, toolchain, and every implemented project
DP_RUNTIME=local make check   # the same with your native toolchain
make -C 00-hello-world help   # a project's configuration and hooks
```

## Implementing a project

1. Complete the project's `hld.md` and `lld.md` before writing code.
2. Write the implementation and its unit tests under the project's `src/`, add the
   repository's uv configuration, and fill in `BIN_DIR` and the `DP_*` hooks in
   the project's `Makefile`.
3. Pass `make -C <project> test` (container) and `DP_RUNTIME=local make -C <project> test`.
4. Add the project directory to `IMPLEMENTED` in the root `Makefile`. CI then builds, lints,
   and tests it in the container and natively on all three operating systems.
5. Keep `rtm.md` and `master-test-plan.md` current.

Specifications: [curriculum reference](https://dialectic-playground.github.io/docs/reference/curriculum/). Language setup:
[Set up a language repository](https://dialectic-playground.github.io/docs/how-to/set-up-a-language-repository/).

## Contributing

See the [organization contributing guide](https://github.com/dialectic-playground/.github/blob/main/CONTRIBUTING.md).
Pull requests are squash-merged, titles follow Conventional Commits, and every commit needs a
DCO sign-off.

## License

[MIT](LICENSE)
