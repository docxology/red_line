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
def test_review_stale_duplicate_blocks_completeness():
    from dataclasses import replace
    from datetime import date
    from red_line.analysis.outcome_coverage import _verified_context

    context = _verified_context("2026-10-20")
    for old_date in ("2020-01-01", "2027-01-01"):
        duplicate = replace(context.evidence[0], recorded_on=old_date)
        assert not replace(context, evidence=context.evidence + (duplicate,)).complete(date(2026, 10, 20))


def test_decision_trace_is_typed_and_immutable():
    from red_line.model.action import LineDecision

    entry = LineDecision("line", ["scope"], [], [], False)
    assert entry.coverage_hits == ("scope",)
    for changes, error in (({"line_id": ""}, ValueError), ({"below_tier_floor": "yes"}, TypeError),
                           ({"coverage_hits": "scope"}, TypeError), ({"coverage_hits": ("",)}, ValueError),
                           ({"coverage_hits": ("a", "a")}, ValueError)):
        with pytest.raises(error):
            replace(entry, **changes)
    from red_line import ActionAssessment, review_engagement

    candidate = make_action("synthetic", frozenset({"targeting"}))
    with pytest.raises(TypeError, match="LineDecision"):
        ActionAssessment(candidate, Classification.NON_COMPLIANT, (), decision_trace=("bad",))
    with pytest.raises(TypeError, match="LineDecision"):
        replace(review_engagement(candidate), decision_trace=("bad",))


@pytest.mark.parametrize("text", ["\ud800", "\udfff", "\ud83d\ude00"])
def test_native_custody_rejects_non_scalar_text_before_serialization(text):
    from red_line import PERSONAL_RED_LINES, ReviewAuthorization, review_engagement

    candidate = make_action("synthetic", frozenset({"targeting"}))
    with pytest.raises(ValueError):
        replace(candidate, description=text)
    for kind in EvidenceKind:
        with pytest.raises(ValueError):
            replace(candidate.context, **{kind.value: text})
    with pytest.raises(ValueError):
        replace(candidate.context, unknowns=(text,))
    for name in ("reference", "summary"):
        with pytest.raises(ValueError):
            replace(candidate.context.evidence[0], **{name: text})
    line = PERSONAL_RED_LINES[0]
    for name in ("title", "standard", "rationale", "stated_by"):
        with pytest.raises(ValueError):
            replace(line, **{name: "I " + text})
    with pytest.raises(ValueError):
        replace(line, carve_outs=(text,))
    with pytest.raises(ValueError):
        replace(line.exemptions[0], description=text)
    with pytest.raises(ValueError):
        ReviewAuthorization(text, "authority", "rationale", "2026-11-10")
    finding = review_engagement(candidate)
    for name in ("engagement", "finding", "evaluator_id"):
        with pytest.raises(ValueError):
            replace(finding, **{name: text})


@pytest.mark.parametrize("text", ["\ud800", "\udfff", "\ud83d\ude00"])
def test_snapshot_reader_rejects_raw_non_scalar_text(text):
    import json
    from red_line import action_from_snapshot, canonical_intake

    payload = json.loads(canonical_intake(make_action("synthetic", frozenset({"targeting"}))))
    payload["description"] = text
    snapshot = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    with pytest.raises(ValueError):
        action_from_snapshot(snapshot)


def test_scalar_unicode_intake_preserves_identity_bytes_and_replay():
    import json
    from red_line import (
        action_from_snapshot,
        canonical_intake,
        intake_digest,
        registry_hash,
        PERSONAL_RED_LINES,
    )

    text = "résumé / 研究 / \U0001f600"
    candidate = make_action(text, frozenset({"targeting"}))
    record = replace(candidate.context.evidence[0], reference="record://" + text, summary=text)
    candidate = replace(
        candidate,
        context=replace(
            candidate.context,
            purpose=text,
            evidence=(record,) + candidate.context.evidence[1:],
            unknowns=[text],
        ),
    )
    snapshot = canonical_intake(candidate)
    restored = action_from_snapshot(snapshot)
    assert restored == candidate
    assert json.loads(snapshot)["description"] == text
    assert canonical_intake(restored) == snapshot
    assert intake_digest(canonical_intake(restored)) == intake_digest(snapshot)
    alternate = replace(candidate, description=text + "\U0001f601")
    assert intake_digest(canonical_intake(alternate)) != intake_digest(snapshot)
    line = replace(PERSONAL_RED_LINES[0], title=text)
    assert line.title == text
    assert registry_hash((line,)) != registry_hash((PERSONAL_RED_LINES[0],))


def test_evidence_date_policy_keeps_supported_basic_and_week_spellings():
    from datetime import date

    record = make_action("synthetic", frozenset({"targeting"})).context.evidence[0]
    for value in ("20261110", "2026-W46-2"):
        admitted = replace(record, recorded_on=value)
        assert admitted.recorded_on == value
        assert not admitted.is_stale(date(2026, 11, 10))
