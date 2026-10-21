"""Tests for evidence-gated review findings."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta

import pytest

from red_line import Classification, DeploymentTier, EvidenceKind, EvidenceRecord, EvidenceStatus, PERSONAL_RED_LINES
from red_line.oversight import ReviewAuthorization, ReviewFinding, review_engagement, transparency_report
from red_line.oversight.findings import _render_finding
from red_line import ActionAssessment
from tests.helpers import action


def _outside_action():
    return action("Open-source docs", frozenset({"documentation"}))


def _blocking_action():
    return action("Autonomous targeting", frozenset({"targeting", "autonomous_weapon"}))


def _ambiguous_action():
    return action("Unclear surveillance research", frozenset({"surveillance", "research"}), ambiguous=True)


def test_review_engagement_outside_scope_is_not_compliance():
    finding = review_engagement(_outside_action(), reviewed_on=date.today().isoformat())
    assert finding.classification is Classification.OUTSIDE_SCOPE
    assert finding.blocks is False
    assert "OUTSIDE SCOPE" in finding.finding


def test_review_engagement_non_compliant_blocks():
    finding = review_engagement(_blocking_action(), reviewed_on=date.today().isoformat())
    assert finding.classification is Classification.NON_COMPLIANT
    assert finding.blocks is True
    assert "s1-human-control-force" in finding.implicated_ids
    assert "unexempted_line" in finding.reason_codes
    assert finding.normalized_scope


def test_authorization_records_but_does_not_unblock():
    finding = review_engagement(
        _blocking_action(),
        reviewed_on=date.today().isoformat(),
        authorization=ReviewAuthorization("reviewer", "red-line review", "record escalation", "2026-07-15"),
    )
    assert finding.classification is Classification.NON_COMPLIANT
    assert finding.blocks is True
    assert transparency_report((finding,)).authorizations == 1


def test_review_engagement_defaults_date():
    finding = review_engagement(_outside_action())
    assert len(finding.reviewed_on) == 10 and finding.reviewed_on.count("-") == 2


def test_insufficient_information_finding_text():
    finding = review_engagement(_ambiguous_action(), reviewed_on=date.today().isoformat())
    assert finding.classification is Classification.INSUFFICIENT_INFORMATION
    assert "INSUFFICIENT INFORMATION" in finding.finding
    assert finding.blocks is True
    assert "intake_blocked" in finding.reason_codes
    assert "Reason codes:" in finding.finding


def test_insufficient_information_is_counted_as_blocked():
    finding = review_engagement(_ambiguous_action(), reviewed_on=date.today().isoformat())
    report = transparency_report((finding,))
    assert report.blocked == 1


def test_review_finding_is_frozen_record():
    finding = ReviewFinding(
        engagement="x",
        classification=Classification.OUTSIDE_SCOPE,
        implicated_ids=(),
        finding="ok",
        reviewed_on=date.today().isoformat(),
    )
    assert finding.blocks is False
    assert finding.authorization is None


def test_review_authorization_rejects_malformed_records():
    with pytest.raises(TypeError, match="fields"):
        ReviewAuthorization(1, "authority", "rationale", "2026-07-15")
    with pytest.raises(TypeError, match="recorded_on"):
        ReviewAuthorization("reviewer", "authority", "rationale", None)
    with pytest.raises(ValueError, match="requires"):
        ReviewAuthorization(" ", "authority", "rationale", "2026-07-15")
    with pytest.raises(ValueError, match="ISO date"):
        ReviewAuthorization("reviewer", "authority", "rationale", "not-a-date")


def test_review_finding_rejects_malformed_records():
    kwargs = dict(
        engagement="engagement",
        classification=Classification.OUTSIDE_SCOPE,
        implicated_ids=(),
        finding="finding",
        reviewed_on=date.today().isoformat(),
    )
    with pytest.raises(TypeError, match="text fields"):
        ReviewFinding(**{**kwargs, "engagement": 1})
    with pytest.raises(TypeError, match="reviewed_on"):
        ReviewFinding(**{**kwargs, "reviewed_on": None})
    with pytest.raises(ValueError, match="require"):
        ReviewFinding(**{**kwargs, "finding": " "})
    with pytest.raises(TypeError, match="classification"):
        ReviewFinding(**{**kwargs, "classification": "outside_scope"})
    with pytest.raises(ValueError, match="ISO date"):
        ReviewFinding(**{**kwargs, "reviewed_on": "not-a-date"})
    with pytest.raises(TypeError, match="reason_codes"):
        ReviewFinding(**{**kwargs, "reason_codes": "intake_blocked"})
    with pytest.raises(ValueError, match="non-empty"):
        ReviewFinding(**{**kwargs, "reason_codes": (" ",)})
    with pytest.raises(ValueError, match="duplicates"):
        ReviewFinding(**{**kwargs, "reason_codes": ("intake_blocked", "intake_blocked")})
    with pytest.raises(ValueError, match="blocking findings"):
        ReviewFinding(
            **kwargs,
            authorization=ReviewAuthorization("reviewer", "authority", "rationale", "2026-07-15"),
        )


def test_finding_renderer_preserves_prose_when_no_reason_codes_exist():
    assessment = ActionAssessment(
        action=_outside_action(),
        classification=Classification.OUTSIDE_SCOPE,
        implicated=(),
        reasons=("No registered boundary matched.",),
    )
    rendered = _render_finding(assessment)
    assert "Reason codes:" not in rendered
    assert "No registered boundary matched." in rendered


def test_review_engagement_rejects_invalid_review_date():
    with pytest.raises(ValueError, match="reviewed_on"):
        review_engagement(_outside_action(), reviewed_on="not-a-date")


def test_review_engagement_captures_provenance_fields():
    reviewed = action(
        "Open-source docs",
        frozenset({"documentation", "release"}),
        tier=DeploymentTier.CONNECTED,
        ambiguous=True,
    )
    finding = review_engagement(reviewed, reviewed_on=date.today().isoformat())
    assert finding.declared_scope == ("documentation", "release")
    assert finding.tier == "connected"
    assert finding.ambiguous is True


def test_review_date_controls_evidence_freshness():
    context = _outside_action().context
    future_for_review = EvidenceRecord(
        kind=EvidenceKind.PURPOSE,
        reference="test://evidence/future-for-review",
        summary="recorded after the stated review date",
        status=EvidenceStatus.VERIFIED,
        recorded_on=date.today().isoformat(),
    )
    context = replace(
        context,
        evidence=tuple(
            future_for_review if record.kind is EvidenceKind.PURPOSE else record
            for record in context.evidence
        ),
    )
    finding = review_engagement(
        action("Open-source docs", frozenset({"documentation"}), context=context),
        reviewed_on=(date.today() - timedelta(days=1)).isoformat(),
    )
    assert finding.classification is Classification.INSUFFICIENT_INFORMATION
    assert "future-dated" in finding.finding


def test_undeclared_scope_hint_flags_scrubbed_scope_without_certifying_it():
    finding = review_engagement(
        action("Autonomous targeting of individuals", frozenset({"documentation"})),
        reviewed_on=date.today().isoformat(),
    )
    assert finding.classification is Classification.OUTSIDE_SCOPE
    assert "undeclared-scope hint" in finding.finding
    assert "'targeting'" in finding.finding


def test_undeclared_scope_hint_absent_for_honest_declaration():
    finding = review_engagement(
        action("Autonomous targeting of individuals", frozenset({"targeting"})),
        reviewed_on=date.today().isoformat(),
    )
    assert "undeclared-scope hint" not in finding.finding
    assert finding.classification is Classification.NON_COMPLIANT


def test_undeclared_scope_hint_absent_when_description_is_benign():
    finding = review_engagement(_outside_action(), reviewed_on=date.today().isoformat())
    assert "undeclared-scope hint" not in finding.finding
def test_review_snapshot_binds_every_context_and_evidence_field_and_replays():
    from dataclasses import replace
    from red_line import canonical_intake, intake_digest, replay_finding, report_digest
    from red_line.analysis.outcome_coverage import _verified_context
    from red_line import ProposedAction, DeploymentTier, EvidenceStatus, review_engagement

    candidate = ProposedAction("synthetic", frozenset({"cogsec", "education"}), _verified_context("2026-10-20"))
    finding = review_engagement(candidate, "2026-10-20")
    snapshot = canonical_intake(candidate)
    assert not replay_finding(finding, snapshot)
    assert finding.decision_trace[0].coverage_hits == ("cogsec",)
    assert finding.decision_trace[0].matched_exemption_ids
    assert finding.decision_trace[0].matched_exemption_ids == finding.decision_trace[0].supported_exemption_ids
    assert "intake snapshot unavailable" in replay_finding(finding, None)
    for field in candidate.context.values():
        changed = replace(candidate, context=replace(candidate.context, **{field.value: "different"}))
        assert intake_digest(canonical_intake(changed)) != finding.intake_digest
    for changes in ({"reference": "restricted://different"}, {"summary": "different"},
                    {"status": EvidenceStatus.CONTRADICTED}, {"recorded_on": "2026-10-19"}):
        evidence = (replace(candidate.context.evidence[0], **changes),) + candidate.context.evidence[1:]
        changed = replace(candidate, context=replace(candidate.context, evidence=evidence))
        assert intake_digest(canonical_intake(changed)) != finding.intake_digest
        assert report_digest(review_engagement(changed, "2026-10-20")) != report_digest(finding)
    for changed in (replace(candidate, description="other"), replace(candidate, scope={"targeting"}),
                    replace(candidate, tier=DeploymentTier.AIR_GAPPED), replace(candidate, ambiguous=True),
                    replace(candidate, context=replace(candidate.context, unknowns=("unresolved",)))):
        assert intake_digest(canonical_intake(changed)) != finding.intake_digest
    assert replay_finding(finding, canonical_intake(replace(candidate, description="different")))
    assert replay_finding(finding, snapshot, ()) == ("registry digest disagreement",)
    assert replay_finding(replace(finding, evaluator_version="old"), snapshot)
    assert replay_finding(replace(finding, finding="modified"), snapshot) == ("replayed finding disagreement",)
    assert not replay_finding(finding, snapshot, tuple(reversed(PERSONAL_RED_LINES)))


def test_review_snapshot_parser_and_provenance_validation_fail_closed():
    from dataclasses import replace
    import json
    from red_line import action_from_snapshot, canonical_intake, review_engagement
    from tests.helpers import action

    candidate = action("synthetic", frozenset({"targeting"}))
    snapshot = canonical_intake(candidate)
    assert action_from_snapshot(snapshot) == candidate
    with pytest.raises(ValueError, match="schema"):
        action_from_snapshot(snapshot.replace("red-line.intake/1.0", "unsupported"))
    with pytest.raises(ValueError, match="canonical"):
        action_from_snapshot(json.dumps(json.loads(snapshot), indent=2))
    finding = review_engagement(candidate)
    with pytest.raises(ValueError, match="all present"):
        replace(finding, registry_digest="")
    with pytest.raises(ValueError, match="SHA-256"):
        replace(finding, intake_digest="bad")
    with pytest.raises(TypeError, match="bindings"):
        replace(finding, evaluator_id=None)


def test_canonical_registry_permutations_preserve_report_and_replay():
    from red_line import canonical_intake, canonical_report, registry_hash, replay_finding

    candidate = action("cogsec influence_ops manipulation", frozenset({"cogsec", "education", "detection"}))
    finding = review_engagement(candidate)
    permuted = tuple(replace(line, scope=tuple(reversed(line.scope)),
                             exemptions=tuple(reversed(line.exemptions)))
                     for line in reversed(PERSONAL_RED_LINES))
    assert registry_hash(permuted) == finding.registry_digest
    assert canonical_report(review_engagement(candidate, lines=permuted)) == canonical_report(finding)
    assert replay_finding(finding, canonical_intake(candidate), permuted) == ()
