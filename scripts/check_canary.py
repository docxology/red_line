#!/usr/bin/env python3
"""Thin orchestrator: verify the committed canary against the live registry.

Loads the git-committed prior canary and re-derives the current registry state,
printing the verification detail and exiting 0 iff the canary is intact (hash
unchanged AND attestation fresh), else 1. Freshness is evaluated against today —
a canary that stops being re-issued eventually trips this check, which is the
point of the instrument.

Usage:
    python scripts/check_canary.py [--prior PATH] [--as-of ISO_DATE]

``argv`` is threaded straight into ``parse_args``, so ``main(None)`` reads the
real process arguments. It previously parsed a hard-coded empty list whenever
``argv`` was ``None`` — the ``__main__`` path — which silently discarded every
flag the command line carried: ``--as-of`` never reached the freshness check and
an unknown flag exited 0. ``tests/test_script_clis.py`` now pins the live
behaviour of both flags through this entrypoint.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from red_line.canary import CanaryStatement, verify_canary
from red_line import PERSONAL_RED_LINES

ROOT = Path(__file__).resolve().parent.parent
COMMITTED = ROOT / "tests" / "fixtures" / "canary_committed.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the committed red-line canary.")
    parser.add_argument("--prior", type=Path, default=COMMITTED, help="prior canary JSON")
    parser.add_argument("--as-of", dest="as_of", help="ISO date for deterministic freshness checks")
    args = parser.parse_args(argv)
    if args.as_of is not None:
        try:
            args.as_of = date.fromisoformat(args.as_of).isoformat()
        except ValueError:
            parser.error(f"invalid ISO date {args.as_of!r}")
    try:
        data = json.loads(args.prior.read_text(encoding="utf-8"))
        prev = CanaryStatement(
            statement=data["statement"],
            issued_on=data["issued_on"],
            registry_digest=data["registry_digest"],
            line_ids=tuple(data["line_ids"]),
            line_digests=tuple(tuple(item) for item in data.get("line_digests", ())),
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"canary metadata invalid — {exc}")
        return 1
    result = verify_canary(prev, PERSONAL_RED_LINES, as_of=args.as_of)
    print(result.detail)
    return 0 if result.intact else 1


if __name__ == "__main__":
    raise SystemExit(main())
