from __future__ import annotations

from dataclasses import replace

from red_line import PERSONAL_RED_LINES, RedLine

SHA_A = "0" * 64
SHA_B = "1" * 64
HOMOGLYPH_SURVEILLANCE = "surveillancе"  # Cyrillic 'е' — non-ASCII after NFKC


def _corrupt(record, **changes):
    """Plant an invalid state without bypassing normal constructor validation."""

    corrupted = replace(record)
    for name, value in changes.items():
        object.__setattr__(corrupted, name, value)
    return corrupted


def _line(line_id: str) -> RedLine:
    return next(rl for rl in PERSONAL_RED_LINES if rl.id == line_id)


def _swap(bad_line: RedLine) -> tuple[RedLine, ...]:
    return tuple(bad_line if rl.id == bad_line.id else rl for rl in PERSONAL_RED_LINES)
