# Toolchain image for dialectic-playground/py: Python (container-first; see tools/dp-run).
#
# Python 3.14; build and package tool: uv.
# Official base image pinned by multi-architecture index digest, plus make and python3 (for the
# curriculum's black-box runner). Dependabot (docker) refreshes the digest; moving to a new
# release line is a deliberate change (keep `make toolchain` and the native CI in step).
FROM docker.io/library/python:3.14-slim-trixie@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170

COPY --from=ghcr.io/astral-sh/uv:0.13.0@sha256:cdc6093146eb3ff6a40107b38f008b789e050e77ad87865e381d9917da55a168 /uv /uvx /usr/local/bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    DP_IN_CONTAINER=1
