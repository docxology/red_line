#!/usr/bin/env python3
"""Compare two canonical PDF/HTML render passes for deterministic artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from red_line.release import (
    TemplateRootUnavailable,
    compare_artifacts,
    template_render_passes,
)

ROOT = Path(__file__).resolve().parent.parent

REPORT = ROOT / "output" / "reports" / "render_determinism.json"


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for running the render comparison and writing its report."""

    parser = argparse.ArgumentParser(description="Compare two canonical PDF/HTML render passes.")
    parser.add_argument("--output", type=Path, default=REPORT)
    parser.add_argument(
        "--hash-only",
        action="store_true",
        help="compare the current artifact tree twice without invoking the template renderer",
    )
    args = parser.parse_args(argv)
    if args.hash_only:
        render = None
    else:
        try:
            render = template_render_passes(ROOT)
        except TemplateRootUnavailable as unavailable:
            # A missing external dependency is a stated condition, not a crash.
            # Say what is missing and what to do instead of a traceback.
            print(f"render comparison: {unavailable}")
            print("to compare an already-built artifact tree instead, pass --hash-only")
            return 1
    result = compare_artifacts(ROOT, render=render)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"render comparison: {'identical' if result['identical'] else 'different'}")
    return 0 if result["identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
