#!/usr/bin/env python3
"""Build deterministic release-input data for the rendered artifact tree."""

from __future__ import annotations

import argparse
from pathlib import Path

from red_line.release import write_snapshot

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for writing the release-input snapshot."""

    parser = argparse.ArgumentParser(
        description="Write the deterministic release-input snapshot for the render boundary."
    )
    parser.parse_args(argv)
    path = write_snapshot(ROOT)
    print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
