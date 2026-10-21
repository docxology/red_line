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
def test_review_tier_tokens_cannot_supply_oversight():
    from red_line import AssessmentReasonCode, Classification, DeploymentTier, evaluate_action
    from tests.helpers import action

    for token in ("hosted", "HOSTED", "connected", "Connected", "air-gapped", "air gapped"):
        tier = DeploymentTier.HOSTED if "air" in token else DeploymentTier.AIR_GAPPED
        result = evaluate_action(action("release", frozenset({"model_release", token}), tier=tier))
        assert result.classification is Classification.INSUFFICIENT_INFORMATION
        assert "tier_scope_conflict" in {code.value for code in result.reason_codes}
        assert AssessmentReasonCode.INTAKE_BLOCKED in result.reason_codes


def test_review_correct_tier_redundancy_and_resolved_hard_block():
    from red_line import Classification, DeploymentTier, evaluate_action
    from tests.helpers import action

    for tier in DeploymentTier:
        bare = evaluate_action(action("release", frozenset({"model_release"}), tier=tier))
        redundant = evaluate_action(action("release", frozenset({"model_release", tier.value}), tier=tier))
        assert (bare.classification, bare.implicated, bare.reason_codes) == (
            redundant.classification, redundant.implicated, redundant.reason_codes
        )
        assert bare.classification is (
            Classification.NON_COMPLIANT if tier is DeploymentTier.AIR_GAPPED else Classification.COMPLIANT
        )
    blocked = evaluate_action(action("release", frozenset({"model_release", "targeting"})))
    assert blocked.classification is Classification.NON_COMPLIANT


def test_review_aliases_preserve_end_to_end_policy():
    from red_line.model.red_line import SCOPE_ALIASES, normalize_token
    from red_line import evaluate_action
    from tests.helpers import action

    for alias, target in SCOPE_ALIASES.items():
        assert normalize_token(alias) == normalize_token(target), alias
        assert normalize_token(normalize_token(alias)) == normalize_token(alias)
        for anchor in (frozenset(), frozenset({"targeting"})):
            left = evaluate_action(action("alias", anchor | {alias}))
            right = evaluate_action(action("alias", anchor | {target}))
            assert (left.classification, left.implicated) == (right.classification, right.implicated), alias
    for token in ("hand_office", "researcher_and_development", "targets"):
        assert normalize_token(token) == token


def test_review_hard_block_retains_tier_reason_code():
    from red_line import AssessmentReasonCode, DeploymentTier, evaluate_action, review_engagement
    from tests.helpers import action

    for tier in DeploymentTier:
        candidate = action("targeting", frozenset({"targeting"}), tier=tier)
        result = evaluate_action(candidate)
        assert result.reason_codes.count(AssessmentReasonCode.UNEXEMPTED_LINE) == 1
        assert result.reason_codes.count(AssessmentReasonCode.BELOW_TIER_FLOOR) == (
            int(tier is not DeploymentTier.HOSTED)
        )
        assert review_engagement(candidate).reason_codes == tuple(code.value for code in result.reason_codes)


def test_generic_intake_is_not_exemption_specific_proof():
    from dataclasses import replace
    from red_line import Classification, EvidenceStatus, evaluate_action, canonical_intake
    from tests.helpers import action

    for scope, first, second in (
        ({"surveillance", "research"}, "aggregate-only output", "individualized output retained"),
        ({"model_release", "task_specific"}, "dangerous capability ablated", "dangerous capability retained"),
    ):
        candidate = action("synthetic", frozenset(scope))
        narrowed = replace(candidate, context=replace(candidate.context, capability_scope=first))
        misleading = replace(candidate, context=replace(candidate.context, capability_scope=second))
        assert canonical_intake(narrowed) != canonical_intake(misleading)
        assert evaluate_action(narrowed).classification is Classification.COMPLIANT
        assert evaluate_action(misleading).classification is Classification.COMPLIANT
        evidence = misleading.context.evidence
        contradiction = replace(evidence[-1], status=EvidenceStatus.CONTRADICTED)
        stopped = replace(misleading, context=replace(misleading.context, evidence=evidence + (contradiction,)))
        assert evaluate_action(stopped).classification is Classification.INSUFFICIENT_INFORMATION
