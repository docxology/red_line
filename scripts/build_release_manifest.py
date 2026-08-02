#!/usr/bin/env python3
"""Build a hash-addressed release manifest for source, evidence, and artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from red_line.release import (
    build_manifest,
    decidable_failures,
    release_ready,
    undecided_before_render,
)

ROOT = Path(__file__).resolve().parent.parent

#: Surfaces written by the external render engine. Nothing in this repository
#: produces them, so before a render they are absent by construction — and the
#: analysis stage that runs this script runs *before* the render. Treating
#: their absence as failure made this script unconditionally red on a clean
#: tree, and green only when a previous render's ``output/`` happened to
#: survive: a manifest attesting to artifacts it did not describe.
RENDERED_SURFACES = (
    Path("output") / "web" / "index.html",
    Path("output") / "pdf" / "_combined_manuscript.md",
)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for writing the release manifest."""

    parser = argparse.ArgumentParser(description="Write a release manifest with source and artifact hashes.")
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "reports" / "release_manifest.json")
    parser.add_argument("--as-of", help="ISO date recorded for canary freshness validation")
    parser.add_argument(
        "--render-timestamp", help="UTC timestamp; pass explicitly for reproducible manifests"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail unless every required validation passes and both source and template checkouts are clean",
    )
    args = parser.parse_args(argv)
    manifest = build_manifest(ROOT, as_of=args.as_of, render_timestamp=args.render_timestamp)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)

    missing = [str(relative) for relative in RENDERED_SURFACES if not (ROOT / relative).exists()]
    if missing and not args.strict:
        undecided = undecided_before_render(manifest)
        failures = decidable_failures(manifest)
        print(f"pre-render manifest: rendered surfaces absent {missing}")
        print(f"publication gate deferred until after the render: {undecided or ['none']}")
        if failures:
            print(f"validations that do not depend on the render failed: {failures}")
            return 1
        return 0

    return 0 if release_ready(manifest, strict=args.strict) else 1


if __name__ == "__main__":
    raise SystemExit(main())
