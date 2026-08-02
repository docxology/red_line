#!/usr/bin/env python3
"""Thin orchestrator: print the current red-line canary statement + hash.

Follows the template ``scripts/`` convention — no business logic here; it
imports ``red_line`` for computation and only handles I/O. Prints the registry hash
to stdout so the value can be pinned in a public canary post. Deterministic:
two runs on an unchanged registry print an identical hash.

The successor guard is honored: unless ``--no-prior`` is given, the git-committed
prior canary (``tests/fixtures/canary_committed.json``) is loaded and passed as
``prev`` so a drifted registry cannot be silently re-attested. Omitting the prior
(``--no-prior``) bypasses the guard; the git-committed prior is the intended
anchor. When the registry has drifted, pass ``--rationale`` to emit a dated
successor statement.

Usage:
    python scripts/build_canary.py [ISO_DATE] [--json]
                                   [--prior PATH | --no-prior]
                                   [--rationale TEXT]

With no ISO_DATE, today's date is used (never a placeholder). An invalid ISO_DATE
prints usage to stderr and exits 2. ``--json`` prints the canary as JSON
byte-identical to the committed fixture serialization.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from red_line.canary import CanaryStatement, issue_canary
from red_line import PERSONAL_RED_LINES, SOURCE_URL

ROOT = Path(__file__).resolve().parent.parent

COMMITTED_PRIOR = ROOT / "tests" / "fixtures" / "canary_committed.json"


def _load_prior(path: Path) -> CanaryStatement:
    """Reconstruct a ``CanaryStatement`` from a committed canary JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return CanaryStatement(
        statement=data["statement"],
        issued_on=data["issued_on"],
        registry_digest=data["registry_digest"],
        line_ids=tuple(data["line_ids"]),
        line_digests=tuple(tuple(item) for item in data.get("line_digests", ())),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="build_canary.py",
        description="Print the current red-line canary statement + registry hash.",
    )
    parser.add_argument("date", nargs="?", help="ISO date (YYYY-MM-DD); defaults to today")
    parser.add_argument("--json", action="store_true", help="emit canary as JSON")
    parser.add_argument(
        "--prior",
        type=Path,
        default=None,
        help="path to a prior canary JSON (default: the committed fixture, if present)",
    )
    parser.add_argument(
        "--no-prior",
        action="store_true",
        help="bypass the successor guard (do not load any prior canary)",
    )
    parser.add_argument("--rationale", default=None, help="rationale for a successor statement")
    return parser


def main(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv[1:])

    if args.date is None:
        issued_on = date.today().isoformat()
    else:
        try:
            issued_on = date.fromisoformat(args.date).isoformat()
        except ValueError:
            print(f"error: invalid ISO date {args.date!r}", file=sys.stderr)
            parser.print_usage(sys.stderr)
            return 2

    prior: CanaryStatement | None = None
    if not args.no_prior:
        prior_path = args.prior if args.prior is not None else COMMITTED_PRIOR
        if args.prior is not None or prior_path.exists():
            prior = _load_prior(prior_path)

    canary = issue_canary(
        issued_on,
        PERSONAL_RED_LINES,
        prev=prior,
        rationale=args.rationale,
    )

    if args.json:
        payload = {
            "statement": canary.statement,
            "issued_on": canary.issued_on,
            "registry_digest": canary.registry_digest,
            "line_ids": list(canary.line_ids),
            "line_digests": [list(item) for item in canary.line_digests],
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return 0

    print("red_line — personal red-line canary")
    print(f"source framework: {SOURCE_URL}")
    print(f"issued_on: {canary.issued_on}")
    print(f"lines: {len(canary.line_ids)}")
    print(f"registry_sha256: {canary.registry_digest}")
    print(f"line_ids: {', '.join(canary.line_ids)}")
    print()
    print(canary.statement)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
