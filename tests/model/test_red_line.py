"""Tests for the RedLine model and lexical helpers."""

from __future__ import annotations

import pytest

from red_line import PERSONAL_RED_LINES
from red_line.model import EvidenceKind, RedLine, Severity, normalize_scope, normalize_token


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


def test_covers_and_carved_out_helpers():
    line = next(rl for rl in PERSONAL_RED_LINES if rl.id == "s1-human-control-force")
    assert line.covers(frozenset({"targeting"}))
    assert not line.covers(frozenset({"unrelated"}))
    assert line.matching_exemptions(frozenset({"logistics"}))
    assert not line.carved_out(frozenset({"logistics"}))


def test_tokens_filters_short_tokens():
    line = next(rl for rl in PERSONAL_RED_LINES if rl.id == "s2-untargeted-profiling")
    # "of", "an" etc are dropped; a real carve-out keyword survives.
    assert line.matching_exemptions(frozenset({"research"}))


def test_carve_out_ignores_boilerplate_stopwords():
    """Function words from 'Does not restrict …' boilerplate are not carve-out keys."""
    s1 = next(rl for rl in PERSONAL_RED_LINES if rl.id == "s1-human-control-force")
    for noise in ("not", "the", "does", "restrict", "with"):
        assert not s1.matching_exemptions(frozenset({noise})), noise
    # A genuine domain carve-out keyword still matches.
    assert s1.matching_exemptions(frozenset({"logistics"}))


def test_scope_aliases_are_explicit_not_heuristic():
    assert normalize_scope(frozenset({"weapon", "autonomous-weapons"})) == frozenset(
        {"weapons", "autonomous_weapon"}
    )


def test_scope_normalization_rejects_non_strings_and_empty_tokens():
    with pytest.raises(TypeError, match="strings"):
        normalize_token(1)
    assert normalize_scope(frozenset({"---"})) == frozenset()
    assert normalize_scope(frozenset({"A---B"})) == frozenset({"a_b"})


def test_exemptions_have_typed_evidence_requirements():
    assert all(
        exemption.required_evidence and exemption.required_evidence.issubset(set(EvidenceKind))
        for line in PERSONAL_RED_LINES
        for exemption in line.exemptions
    )
