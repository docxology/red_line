"""Rasterizer discovery for deterministic SVG figures."""

from __future__ import annotations

import shutil

RASTERIZER = "rsvg-convert"


def resolve_rasterizer() -> str:
    """Return the ``rsvg-convert`` executable found on ``PATH``, or fail closed.

    Resolution is ``PATH``-only. No machine-specific install location is
    consulted, so a missing tool is reported on every machine rather than
    silently satisfied on the one where it happens to be installed.
    """

    path = shutil.which(RASTERIZER)
    if path is None:
        raise RuntimeError(
            f"{RASTERIZER} is required to rasterize the deterministic SVG figures; "
            "it was not found on PATH (macOS: brew install librsvg; "
            "Debian/Ubuntu: apt-get install librsvg2-bin)"
        )
    return path
