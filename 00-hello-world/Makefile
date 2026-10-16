# 00-hello-world: Standard Terminal Hello World, in Python.
#
# Extends the universal build contract in shared/templates/BASE-MAKEFILE:
#
#   make all | install | uninstall | test | check | lint | format | clean | distclean
#   make test-hidden | grade | help
#
# Toolchain: uv (Python 3.14). pyproject.toml and uv.lock in this directory define the
# dp-hello package (sources in src/dp_hello/, unit tests in tests/) and the dev group
# (pytest, ruff, mypy).
#
# Build: `uv sync --locked` creates the project virtual environment .venv/ in this directory
# and installs dp-hello into it (editable). That generates the console script
# .venv/bin/dp-hello, a `#!` script naming the venv's interpreter (Windows:
# .venv/Scripts/dp-hello.exe), so BIN_DIR is the venv's script directory. The container
# mounts the repository at the same path as on the host, so the same .venv path works in
# both; if .venv was created by the other environment, uv sees that its interpreter is
# missing or different and recreates it.
#
# Install: a separate virtual environment holding a non-editable dp-hello goes to
# $(LIBDIR)/py/00-hello-world/venv, and a `#!/bin/sh` launcher that execs its console script
# (absolute path baked in) goes to $(BINDIR)/dp-hello. Uninstall removes both.
#
# Container-first: goals run in the toolchain container built from the repository's
# Containerfile (podman, then docker, then local; override with DP_RUNTIME).

PROJECT := 00-hello-world
TOOLS   := dp-hello

# Path to the sdlc-curriculum checkout (the specs, test suites, and runner live there).
CURRICULUM_ROOT ?= ../sdlc-curriculum

UV ?= uv
# The project environment is always ./.venv, whatever the caller's environment says.
unexport UV_PROJECT_ENVIRONMENT VIRTUAL_ENV

ifeq ($(OS),Windows_NT)
VENV_SCRIPTS := Scripts
else
VENV_SCRIPTS := bin
endif

# Directory that contains the built executables after `make all`.
BIN_DIR := .venv/$(VENV_SCRIPTS)

# Where `make install` puts the payload (see the header).
INSTALL_DIR = $(LIBDIR)/py/$(PROJECT)

DP_BUILD = $(UV) sync --locked

DP_UNIT_TEST = $(UV) run --locked pytest

define DP_LINT
$(UV) run --locked ruff check .
$(UV) run --locked ruff format --check .
$(UV) run --locked mypy
endef

DP_FORMAT = $(UV) run --locked ruff format .

define DP_INSTALL
rm -rf "$(INSTALL_DIR)"
$(UV) venv --quiet --python 3.14 "$(INSTALL_DIR)/venv"
$(UV) pip install --quiet --python "$(INSTALL_DIR)/venv" --no-deps .
mkdir -p "$(BINDIR)"
printf '#!/bin/sh\nexec %s "$$@"\n' "'$(INSTALL_DIR)/venv/$(VENV_SCRIPTS)/dp-hello$(EXE)'" \
	> "$(BINDIR)/dp-hello"
chmod +x "$(BINDIR)/dp-hello"
"$(BINDIR)/dp-hello" --version
endef

define DP_UNINSTALL
rm -f "$(BINDIR)/dp-hello"
rm -rf "$(INSTALL_DIR)"
rmdir "$(LIBDIR)/py" "$(LIBDIR)" 2>/dev/null || true
endef

define DP_CLEAN
rm -rf build dist .pytest_cache .mypy_cache .ruff_cache
find src tests -name __pycache__ -type d -prune -exec rm -rf {} +
endef

DP_DISTCLEAN = rm -rf .venv

include $(CURRICULUM_ROOT)/shared/templates/BASE-MAKEFILE
