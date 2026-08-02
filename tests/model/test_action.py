"""Tests for action-model properties."""

from __future__ import annotations

import pytest
from dataclasses import replace

from red_line import (
    Classification,
    EvidenceKind,
    EvidenceRecord,
    EvidenceStatus,
    ProposedAction,
    evaluate_action,
)
from tests.helpers import action as make_action


def test_outside_scope_is_not_compliance():
    action = make_action(
        description="Write ant-colony simulation tutorial",
        scope=frozenset({"education", "simulation"}),
    )
    result = evaluate_action(action)
    assert result.classification is Classification.OUTSIDE_SCOPE
    assert result.outside_scope is True


def test_outside_scope_false_when_verified_exemption_applies():
    action = make_action(
        description="Defensive red-team analysis of an influence operation",
        scope=frozenset({"influence_ops", "detection"}),
    )
    result = evaluate_action(action)
    assert result.classification is Classification.COMPLIANT
    assert result.outside_scope is False
    assert len(result.implicated) >= 1


@pytest.mark.parametrize(
    "reference",
    [
        "https://example.test/case?token=raw-secret",
        "mailto:person@example.com",
        "case://person/123-45-6789",
    ],
)
def test_evidence_reference_rejects_secret_or_raw_personal_identifier(reference: str):
    with pytest.raises(ValueError):
        EvidenceRecord(
            kind=EvidenceKind.PURPOSE,
            reference=reference,
            summary="reviewable purpose record",
            status=EvidenceStatus.VERIFIED,
            recorded_on="2026-07-17",
        )


def test_proposed_action_rejects_missing_or_untyped_context_and_scope():
    context = make_action("write docs", frozenset({"documentation"})).context
    with pytest.raises(TypeError, match="context"):
        ProposedAction("write docs", frozenset({"documentation"}), None)
    with pytest.raises(TypeError, match="tokens"):
        ProposedAction("write docs", frozenset({1}), context)


def test_evidence_record_rejects_malformed_fields():
    with pytest.raises(TypeError, match="kind and status"):
        EvidenceRecord("purpose", "test://purpose", "summary", EvidenceStatus.VERIFIED, "2026-07-15")
    with pytest.raises(TypeError, match="reference and summary"):
        EvidenceRecord(EvidenceKind.PURPOSE, "test://purpose", 1, EvidenceStatus.VERIFIED, "2026-07-15")
    with pytest.raises(TypeError, match="recorded_on"):
        EvidenceRecord(EvidenceKind.PURPOSE, "test://purpose", "summary", EvidenceStatus.VERIFIED, None)
    with pytest.raises(ValueError, match="required"):
        EvidenceRecord(EvidenceKind.PURPOSE, " ", "summary", EvidenceStatus.VERIFIED, "2026-07-15")
    with pytest.raises(ValueError, match="ISO date"):
        EvidenceRecord(
            EvidenceKind.PURPOSE, "test://purpose", "summary", EvidenceStatus.VERIFIED, "not-a-date"
        )


def test_action_context_rejects_untyped_values_and_reports_completeness():
    context = make_action("write docs", frozenset({"documentation"})).context
    assert context.complete() is True
    with pytest.raises(TypeError, match="fields"):
        replace(context, purpose=1)
    with pytest.raises(TypeError, match="EvidenceRecord"):
        replace(context, evidence=(object(),))
    with pytest.raises(TypeError, match="unknowns"):
        replace(context, unknowns=(1,))


def test_proposed_action_rejects_all_untyped_constructor_fields():
    context = make_action("write docs", frozenset({"documentation"})).context
    with pytest.raises(TypeError, match="description"):
        ProposedAction(1, frozenset({"documentation"}), context)
    with pytest.raises(TypeError, match="set-like"):
        ProposedAction("write docs", "documentation", context)
    with pytest.raises(TypeError, match="tier"):
        ProposedAction("write docs", frozenset({"documentation"}), context, tier="hosted")
    with pytest.raises(TypeError, match="ambiguous"):
        ProposedAction("write docs", frozenset({"documentation"}), context, ambiguous="no")
