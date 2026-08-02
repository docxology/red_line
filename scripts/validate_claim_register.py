#!/usr/bin/env python3
"""Validate the machine-readable publication claim contract and its prose map."""

from __future__ import annotations

import argparse
from pathlib import Path

from red_line.contracts import validate_claim_register

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. Takes no arguments; an unrecognized one exits 2.

    The parser exists so the script fails closed on a typo. Without it an
    unknown flag or a stray positional was accepted in silence and the script
    still printed a pass, which is the shape of a gate that cannot fail.
    """

    argparse.ArgumentParser(
        description="Validate the machine-readable publication claim contract and its prose map."
    ).parse_args(argv)
    errors = validate_claim_register(ROOT)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print("claim register: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
