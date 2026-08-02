#!/usr/bin/env python3
"""Build the manuscript's deterministic, source-driven explanatory figures."""

from __future__ import annotations

import argparse
from pathlib import Path

from red_line.figures import build_figures

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. Takes no arguments; an unrecognized one exits 2.

    The parser exists so the script fails closed on a typo. Without it an
    unknown flag or a stray positional was accepted in silence and the build
    still reported success, so a mistyped invocation inside a gate script read
    as a pass. ``tests/test_script_clis.py`` pins the non-zero exit.
    """

    argparse.ArgumentParser(
        description="Build the deterministic manuscript figures under output/figures."
    ).parse_args(argv)
    paths = build_figures(ROOT)
    print(f"generated {len(paths)} figures under output/figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
