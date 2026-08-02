"""Tests for action evaluation behavior."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from red_line import AssessmentReasonCode, Classification, DeploymentTier, evaluate_action
from tests.helpers import action as make_action


def test_stopword_in_scope_does_not_exempt_block():
    """An incidental function word in scope must not silently exempt a red line."""
    action = make_action(
        description="Autonomous targeting; scope notes not final",
        scope=frozenset({"targeting", "autonomous_weapon", "not", "the"}),
    )
    result = evaluate_action(action)
    assert result.classification is Classification.NON_COMPLIANT
    assert any(rl.id == "s1-human-control-force" for rl in result.implicated)


def test_non_implicated_action_is_explicitly_outside_scope():
    action = make_action(description="Write docs", scope=frozenset({"documentation"}))
    result = evaluate_action(action)
    assert result.classification is Classification.OUTSIDE_SCOPE
    assert result.implicated == ()
    assert "no red line implicated" in " ".join(result.reasons)


def test_empty_scope_is_insufficient_information():
    result = evaluate_action(make_action("Undescribed work", frozenset()))
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert "scope declaration is empty" in " ".join(result.reasons)
    assert AssessmentReasonCode.EMPTY_SCOPE in result.reason_codes
    assert AssessmentReasonCode.INTAKE_BLOCKED in result.reason_codes


def test_unknown_scope_marker_is_insufficient_information():
    result = evaluate_action(make_action("Unresolved work", frozenset({"unknown"})))
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert "unknown scope marker" in " ".join(result.reasons)


def test_undeclared_context_unknown_is_distinct_from_unknown_scope_marker():
    base = make_action("Research", frozenset({"documentation"}))
    context = replace(base.context, unknowns=("purpose pending",))
    result = evaluate_action(replace(base, context=context))
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert AssessmentReasonCode.UNDECLARED_UNKNOWN in result.reason_codes
    assert AssessmentReasonCode.UNKNOWN_SCOPE not in result.reason_codes


def test_unicode_confusable_scope_is_insufficient_information():
    # Cyrillic "е" must not become a new token that evades surveillance scope.
    confusable = "surveillanc" + "\u0435"
    with pytest.raises(ValueError, match="ASCII"):
        make_action("mass surveillance", frozenset({confusable}))


def test_implicated_not_carved_out_is_non_compliant():
    action = make_action(
        description="Tune an autonomous targeting model",
        scope=frozenset({"targeting", "autonomous_weapon"}),
        tier=DeploymentTier.HOSTED,
    )
    result = evaluate_action(action)
    assert result.classification is Classification.NON_COMPLIANT
    assert any(rl.id == "s1-human-control-force" for rl in result.implicated)


def test_carve_out_only_is_compliant():
    action = make_action(
        description="Build a logistics optimizer",
        scope=frozenset({"targeting", "logistics"}),  # implicates S1 but matches carve-out
    )
    result = evaluate_action(action)
    # S1 is implicated by "targeting" but carved out by "logistics".
    assert result.classification is Classification.COMPLIANT
    assert any(rl.id == "s1-human-control-force" for rl in result.implicated)


def test_ambiguous_intake_blocks_before_policy_matching():
    action = make_action(
        description="Surveillance-adjacent research, scope unclear",
        scope=frozenset({"surveillance", "research"}),  # implicates S2 but carve-out matches
        ambiguous=True,
    )
    result = evaluate_action(action)
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert "ambiguous" in " ".join(result.reasons)


def test_assessment_reasons_are_populated_for_block():
    action = make_action(
        description="Covert influence campaign",
        scope=frozenset({"influence_ops", "manipulation"}),
    )
    result = evaluate_action(action)
    assert result.classification is Classification.NON_COMPLIANT
    assert len(result.reasons) >= 1
    assert AssessmentReasonCode.UNEXEMPTED_LINE in result.reason_codes


def test_plural_scope_nearmiss_still_implicates():
    # The reviewed explicit alias, not a suffix heuristic, maps this token.
    result = evaluate_action(
        make_action("weapon guidance module", frozenset({"weapon"}), tier=DeploymentTier.AIR_GAPPED)
    )
    assert result.classification is not Classification.COMPLIANT
    assert any(rl.id == "s1-human-control-force" for rl in result.implicated)


def test_explicit_adjacent_use_alias_does_not_widen_without_policy_match():
    # An exact adjacent-use trigger can narrow only the line it explicitly matches.
    result = evaluate_action(make_action("logistics optimizer", frozenset({"targeting", "logistics"})))
    assert result.classification is Classification.COMPLIANT


def test_ambiguous_no_match_is_insufficient_information():
    result = evaluate_action(make_action("write poetry", frozenset({"poetry"}), ambiguous=True))
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert any("ambiguous" in r for r in result.reasons)


def test_stale_duplicate_evidence_blocks_even_with_a_fresh_duplicate():
    from dataclasses import replace
    from red_line import EvidenceKind, EvidenceRecord, EvidenceStatus

    context = make_action("write docs", frozenset({"documentation"})).context
    stale = EvidenceRecord(
        EvidenceKind.PURPOSE,
        "test://evidence/old-purpose",
        "old purpose record",
        EvidenceStatus.VERIFIED,
        "2020-01-01",
    )
    context = replace(context, evidence=(*context.evidence, stale))
    result = evaluate_action(
        make_action("write docs", frozenset({"documentation"}), context=context),
        as_of=date.today().isoformat(),
    )
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert EvidenceKind.PURPOSE in result.stale_evidence
