"""Tests for the RedLine model and lexical helpers."""

from __future__ import annotations

import pytest

from red_line import PERSONAL_RED_LINES, EvidenceStatus
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
def test_review_alias_table_rejects_ambiguous_keys_and_cycles():
    from red_line.model.red_line import validated_aliases

    for table in ({"a-b": "one", "a_b": "two"}, {"a": "b", "b": "a"}, {"---": "a"}):
        with pytest.raises(ValueError):
            validated_aliases(table)
    assert validated_aliases({"a-b": "a_b", "a_b": "a_b"}) == {"a_b": "a_b"}


@pytest.mark.parametrize("status", list(EvidenceStatus))
@pytest.mark.parametrize("recorded_on", ["2026-10-20", "2020-01-01", "2027-01-01"])
def test_review_dated_applicability_preserves_duplicates(status, recorded_on):
    from dataclasses import replace
    from datetime import date
    from red_line import EvidenceStatus
    from red_line.analysis.outcome_coverage import _verified_context

    context = _verified_context("2026-10-20")
    duplicate = replace(context.evidence[0], status=status, recorded_on=recorded_on)
    context = replace(context, evidence=context.evidence + (duplicate,))
    line = PERSONAL_RED_LINES[0]
    scope = line.exemptions[0].trigger_scope
    ready = recorded_on == "2026-10-20" and status is not EvidenceStatus.CONTRADICTED
    assert context.complete(date(2026, 10, 20)) == ready
    assert bool(line.applicable_exemptions(scope, context, date(2026, 10, 20))) == ready
    with pytest.raises(TypeError):
        line.exemptions[0].applicable(scope, context, None)


def test_context_predicates_require_action_level_intake_validation():
    from red_line import Classification, DeploymentTier, evaluate_action
    from tests.helpers import action
    from datetime import date

    line = next(line for line in PERSONAL_RED_LINES if line.id == "cogsec-integrity")
    for scope, tier, ambiguous in (
        ({"cogsec", "education", "unknown"}, DeploymentTier.HOSTED, False),
        ({"cogsec", "education", "connected"}, DeploymentTier.HOSTED, False),
        ({"cogsec", "education"}, DeploymentTier.HOSTED, True),
    ):
        candidate = action("synthetic", frozenset(scope), tier=tier, ambiguous=ambiguous)
        assert line.applicable_exemptions(candidate.scope, candidate.context, date.today())
        result = evaluate_action(candidate, as_of=date.today())
        assert result.classification is Classification.INSUFFICIENT_INFORMATION
        assert not result.decision_trace
