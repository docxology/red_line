"""Trust-boundary tests for evidence, canaries, and false certification."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace
from datetime import date
from pathlib import Path

import pytest

from red_line import (
    Classification,
    EvidenceKind,
    EvidenceRecord,
    EvidenceStatus,
    PERSONAL_RED_LINES,
    ReviewAuthorization,
    DeploymentTier,
    evaluate_action,
    review_engagement,
    transparency_report,
)
from red_line.canary import CanaryStatement, DEFAULT_MAX_AGE_DAYS, is_stale, issue_canary, verify_canary
from tests.helpers import action, complete_context


FIXTURE = Path(__file__).parent.parent / "fixtures" / "canary_committed.json"


def _committed() -> CanaryStatement:
    data = json.loads(FIXTURE.read_text())
    return CanaryStatement(
        statement=data["statement"],
        issued_on=data["issued_on"],
        registry_digest=data["registry_digest"],
        line_ids=tuple(data["line_ids"]),
        line_digests=tuple(tuple(item) for item in data.get("line_digests", ())),
    )


def test_committed_fixture_is_the_statement_the_live_registry_issues():
    """The on-disk prior copy must equal what the live registry attests.

    `_committed()` used to be dead code: this module claimed to pin the
    committed fixture while every test built its own statement in memory, so
    README and the amendment runbook credited a binding that did not exist.
    Reading the fixture here is what makes those sentences true.
    """
    committed = _committed()
    issued = issue_canary(committed.issued_on, PERSONAL_RED_LINES)

    assert committed.registry_digest == issued.registry_digest
    assert committed.line_ids == issued.line_ids
    assert committed.line_digests == issued.line_digests
    assert committed.line_digests, "an aggregate-only fixture cannot reach CANARY escalation"
    assert verify_canary(committed, PERSONAL_RED_LINES, as_of="2026-07-17").intact is True


def test_regeneration_attack_detected_against_committed_statement():
    committed = _committed()
    tampered = (replace(PERSONAL_RED_LINES[0], standard="I will look the other way."),) + PERSONAL_RED_LINES[
        1:
    ]
    regenerated = issue_canary("2026-07-16", tampered)
    assert regenerated.registry_digest != committed.registry_digest
    assert verify_canary(committed, tampered).intact is False


def test_regenerated_statement_verifies_clean_by_design():
    tampered = (replace(PERSONAL_RED_LINES[0], standard="I will look the other way."),) + PERSONAL_RED_LINES[
        1:
    ]
    regenerated = issue_canary("2026-07-16", tampered)
    assert verify_canary(regenerated, tampered, as_of="2026-07-17").intact is True


def test_scope_scrubbing_is_blocked_by_required_capability_evidence():
    scrubbed = action(
        "Tune a model that selects and engages targets",
        frozenset({"optimization", "simulation"}),
        context=complete_context(capability_scope="unknown"),
    )
    result = evaluate_action(scrubbed)
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert EvidenceKind.CAPABILITY_SCOPE in result.missing_evidence


def test_description_never_substitutes_for_scope():
    result = evaluate_action(action("Tune a model that selects targets", frozenset({"optimization"})))
    assert result.classification is Classification.OUTSIDE_SCOPE
    assert result.implicated == ()


def test_carve_out_keyword_without_verified_evidence_cannot_pass():
    context = complete_context(legal_basis="unknown")
    result = evaluate_action(
        action("Consent-based surveillance", frozenset({"surveillance", "opt_in_analytics"}), context=context)
    )
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert EvidenceKind.LEGAL_BASIS in result.missing_evidence


def test_self_asserted_required_evidence_blocks():
    evidence = tuple(
        replace(record, status=EvidenceStatus.SELF_ASSERTED)
        if record.kind is EvidenceKind.LEGAL_BASIS
        else record
        for record in complete_context().evidence
    )
    context = replace(complete_context(), evidence=evidence)
    result = evaluate_action(action("Write docs", frozenset({"documentation"}), context=context))
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert EvidenceKind.LEGAL_BASIS in result.missing_evidence


def test_unverified_required_evidence_blocks():
    evidence = tuple(
        replace(record, status=EvidenceStatus.UNVERIFIED)
        if record.kind is EvidenceKind.DOWNSTREAM_TRANSFER
        else record
        for record in complete_context().evidence
    )
    context = replace(complete_context(), evidence=evidence)
    result = evaluate_action(action("Write docs", frozenset({"documentation"}), context=context))
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert EvidenceKind.DOWNSTREAM_TRANSFER in result.missing_evidence


def test_stale_required_evidence_blocks_until_refreshed():
    evidence = tuple(
        replace(record, recorded_on="2025-01-01") if record.kind is EvidenceKind.DATA_PROVENANCE else record
        for record in complete_context().evidence
    )
    context = replace(complete_context(), evidence=evidence)
    result = evaluate_action(
        action("Write docs", frozenset({"documentation"}), context=context),
        as_of=date.today().isoformat(),
    )
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert EvidenceKind.DATA_PROVENANCE in result.stale_evidence


def test_contradicted_evidence_blocks_even_if_another_record_is_verified():
    evidence = list(complete_context().evidence)
    evidence.append(
        EvidenceRecord(
            EvidenceKind.END_USE,
            "test://contradiction/end-use",
            "A conflicting record",
            EvidenceStatus.CONTRADICTED,
            "2026-07-17",
        )
    )
    context = replace(complete_context(), evidence=tuple(evidence))
    result = evaluate_action(action("Write docs", frozenset({"documentation"}), context=context))
    assert result.classification is Classification.INSUFFICIENT_INFORMATION
    assert EvidenceKind.END_USE in result.unresolved_evidence


def test_carve_out_cannot_cover_multiple_prohibited_dimensions():
    result = evaluate_action(
        action(
            "Logistics optimizer that also selects and engages targets",
            frozenset({"targeting", "autonomous_weapon", "logistics"}),
        )
    )
    assert result.classification is Classification.REQUIRES_MODIFICATION
    assert any("multiple prohibited dimensions" in reason for reason in result.reasons)


def test_single_verified_adjacent_use_can_be_compliant():
    result = evaluate_action(action("Build a logistics optimizer", frozenset({"targeting", "logistics"})))
    assert result.classification is Classification.COMPLIANT


def test_hosted_model_release_is_not_falsely_blocked():
    hosted = evaluate_action(
        action(
            "Hosted dual-use modeling under retained oversight",
            frozenset({"dual_use", "capability"}),
            tier=DeploymentTier.HOSTED,
        )
    )
    assert hosted.classification is Classification.OUTSIDE_SCOPE
    releasing = evaluate_action(
        action(
            "Hand off model weights beyond recall",
            frozenset({"weights", "handoff"}),
            tier=DeploymentTier.AIR_GAPPED,
        )
    )
    assert releasing.classification is Classification.NON_COMPLIANT


def test_future_dated_canary_is_stale():
    assert is_stale(issue_canary("2027-01-01", PERSONAL_RED_LINES), as_of="2026-07-15") is True


def test_freshness_always_evaluated_by_default():
    ancient = issue_canary("2000-01-01", PERSONAL_RED_LINES)
    assert verify_canary(ancient, PERSONAL_RED_LINES).stale is True
    assert DEFAULT_MAX_AGE_DAYS < 9000


def test_authorization_documents_but_never_unblocks():
    blocked = review_engagement(
        action("Autonomous targeting", frozenset({"targeting", "autonomous_weapon"})),
        reviewed_on=date.today().isoformat(),
        authorization=ReviewAuthorization(
            "reviewer", "personal red-line review", "documented escalation", "2026-07-15"
        ),
    )
    assert blocked.classification is Classification.NON_COMPLIANT
    assert blocked.blocks is True
    assert transparency_report((blocked,)).authorizations == 1


def test_records_are_actually_immutable():
    red_line = PERSONAL_RED_LINES[0]
    with pytest.raises(FrozenInstanceError):
        red_line.id = "x"  # type: ignore[misc]
    proposed = action("a", frozenset({"documentation"}))
    with pytest.raises(FrozenInstanceError):
        proposed.description = "b"  # type: ignore[misc]
    canary = issue_canary("2026-07-15", PERSONAL_RED_LINES)
    with pytest.raises(FrozenInstanceError):
        canary.issued_on = "1999-01-01"  # type: ignore[misc]


def test_inconsistent_statement_never_intact():
    from red_line.canary import registry_hash

    forged = CanaryStatement(
        statement="hand-crafted",
        issued_on="2026-07-15",
        registry_digest=registry_hash(PERSONAL_RED_LINES),
        line_ids=("only-one-id",),
    )
    result = verify_canary(forged, PERSONAL_RED_LINES, as_of="2026-07-20")
    assert result.intact is False
    assert result.removed_ids == ("only-one-id",)


def test_inconsistent_line_metadata_never_intact():
    issued = issue_canary("2026-07-15")
    duplicated = replace(issued)
    object.__setattr__(duplicated, "line_digests", issued.line_digests + (issued.line_digests[0],))
    result = verify_canary(duplicated, PERSONAL_RED_LINES, as_of="2026-07-20")
    assert result.intact is False
    assert "metadata inconsistent" in result.detail


def test_handoff_requires_verified_downstream_context():
    bare = evaluate_action(action("hand off work", frozenset({"handoff"})))
    assert bare.classification is Classification.NON_COMPLIANT
    vetted = evaluate_action(
        action(
            "hand off to a vetted end user with flow-down commitment",
            frozenset({"handoff", "vetted", "flow_down"}),
        )
    )
    assert vetted.classification is Classification.COMPLIANT


def test_sensitive_evidence_reference_is_rejected():
    with pytest.raises(ValueError, match="secret"):
        EvidenceRecord(
            EvidenceKind.PURPOSE, "vault://token=raw-secret", "bad", EvidenceStatus.VERIFIED, "2026-07-17"
        )
