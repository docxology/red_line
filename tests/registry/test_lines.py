"""Tests for registry structure and content counts."""

from __future__ import annotations

from red_line import PERSONAL_RED_LINES, Severity
from red_line.model import RedLine


def test_registry_nonempty_and_typed():
    assert len(PERSONAL_RED_LINES) >= 6
    assert all(isinstance(rl, RedLine) for rl in PERSONAL_RED_LINES)


def test_unique_ids():
    ids = [rl.id for rl in PERSONAL_RED_LINES]
    assert len(ids) == len(set(ids))


def test_every_line_has_carve_out():
    assert all(len(rl.carve_outs) >= 1 for rl in PERSONAL_RED_LINES)


def test_has_standard_one_and_two_analogs():
    ids = {rl.id for rl in PERSONAL_RED_LINES}
    assert "s1-human-control-force" in ids
    assert "s2-untargeted-profiling" in ids
    canary = [rl for rl in PERSONAL_RED_LINES if rl.severity is Severity.CANARY]
    assert len(canary) >= 2
