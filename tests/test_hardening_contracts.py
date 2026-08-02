"""Adversarial coverage for public record and release-boundary contracts."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from red_line import (
    ActionAssessment,
    AssessmentReasonCode,
    Classification,
    EvidenceKind,
    EvidenceStatus,
    ExemptionMatchMode,
    PERSONAL_RED_LINES,
    evaluate_action,
)
from red_line.canary import CanaryStatement, issue_canary, is_stale, verify_canary
from red_line.model import EvidenceRecord, Exemption, RedLine
from red_line.oversight import TransparencyReport, transparency_report
from tests.helpers import action, complete_context


def _red_line(**changes) -> RedLine:
    source = PERSONAL_RED_LINES[0]
    values = {
        "id": source.id,
        "title": source.title,
        "standard": source.standard,
        "rationale": source.rationale,
        "scope": source.scope,
        "carve_outs": source.carve_outs,
        "max_tier": source.max_tier,
        "severity": source.severity,
        "stated_by": source.stated_by,
        "stated_on": source.stated_on,
        "exemptions": source.exemptions,
    }
    values.update(changes)
    return RedLine(**values)


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("id", 1, TypeError),
        ("id", "not a slug", ValueError),
        ("title", " ", ValueError),
        ("standard", "The author refuses this.", ValueError),
        ("stated_on", "not-a-date", ValueError),
        ("scope", "targeting", TypeError),
        ("carve_outs", "clause", TypeError),
        ("exemptions", "exemption", TypeError),
        ("scope", (1,), ValueError),
        ("carve_outs", (1,), ValueError),
        ("exemptions", ("not-an-exemption",), TypeError),
        ("max_tier", "hosted", TypeError),
    ],
)
def test_red_line_constructor_rejects_malformed_records(field, value, error):
    with pytest.raises(error):
        _red_line(**{field: value})


@pytest.mark.parametrize(
    ("args", "error"),
    [
        (("", "description", frozenset({"support"}), frozenset({EvidenceKind.PURPOSE})), ValueError),
        (("id", "", frozenset({"support"}), frozenset({EvidenceKind.PURPOSE})), ValueError),
        (("id", "description", "support", frozenset({EvidenceKind.PURPOSE})), TypeError),
        (("id", "description", frozenset({1}), frozenset({EvidenceKind.PURPOSE})), TypeError),
        (("id", "description", frozenset({"support"}), {"purpose"}), TypeError),
        (("id", "description", frozenset({"support"}), frozenset({EvidenceKind.PURPOSE}), "all"), TypeError),
        (("id", "description", frozenset({"---"}), frozenset({EvidenceKind.PURPOSE})), ValueError),
    ],
)
def test_exemption_constructor_rejects_malformed_records(args, error):
    with pytest.raises(error):
        Exemption(*args)


def test_exemption_match_modes_are_explicit_and_deeply_immutable():
    any_match = Exemption(
        "any",
        "any trigger",
        {"defensive_alerting", "human_in_loop"},
        {EvidenceKind.HUMAN_CONTROL},
    )
    all_match = Exemption(
        "all",
        "all triggers",
        {"defensive_alerting", "human_in_loop"},
        {EvidenceKind.HUMAN_CONTROL},
        ExemptionMatchMode.ALL,
    )
    assert any_match.matches(frozenset({"defensive_alerting"}))
    assert all_match.matches(frozenset({"defensive_alerting"})) is False
    assert all_match.matches(frozenset({"defensive_alerting", "human_in_loop"}))
    assert isinstance(any_match.trigger_scope, frozenset)
    assert isinstance(any_match.required_evidence, frozenset)


def test_action_context_canonicalizes_nested_collections_and_default_complete_is_freshness_aware():
    old_record = EvidenceRecord(
        EvidenceKind.PURPOSE,
        "test://old",
        "old evidence",
        EvidenceStatus.VERIFIED,
        "2020-01-01",
    )
    context = replace(complete_context(), evidence=[old_record], unknowns=["review later"])
    assert isinstance(context.evidence, tuple)
    assert isinstance(context.unknowns, tuple)
    assert context.complete(date(2020, 1, 1)) is False
    assert context.complete() is False
    with pytest.raises(TypeError):
        context.has_verified_evidence("purpose")
    with pytest.raises(ValueError):
        old_record.is_stale(date.today(), -1)


def test_action_scope_alias_is_stored_canonically_and_assessment_is_immutable():
    proposed = action("handoff", frozenset({"vetted", "flow-down"}))
    assert proposed.scope == frozenset({"vetted_end_user", "flow_down"})
    assessment = evaluate_action(proposed)
    assert isinstance(assessment.normalized_scope, tuple)
    with pytest.raises(TypeError):
        ActionAssessment(proposed, "compliant", ())
    with pytest.raises(TypeError):
        ActionAssessment(proposed, Classification.COMPLIANT, (), reasons={"mutable"})
    with pytest.raises(TypeError, match="reason_codes"):
        ActionAssessment(proposed, Classification.COMPLIANT, (), reason_codes=("not-a-code",))
    with pytest.raises(ValueError, match="unique"):
        ActionAssessment(
            proposed,
            Classification.COMPLIANT,
            (),
            reason_codes=(AssessmentReasonCode.OUTSIDE_SCOPE, AssessmentReasonCode.OUTSIDE_SCOPE),
        )


def _forged_canary(**changes) -> CanaryStatement:
    source = issue_canary("2026-07-15")
    forged = object.__new__(CanaryStatement)
    for field in ("statement", "issued_on", "registry_digest", "line_ids", "line_digests"):
        object.__setattr__(forged, field, getattr(source, field))
    for field, value in changes.items():
        object.__setattr__(forged, field, value)
    return forged


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"statement": ""}, "statement"),
        ({"issued_on": 1}, "issued_on"),
        ({"issued_on": "bad"}, "ISO date"),
        ({"registry_digest": "bad"}, "SHA-256"),
        ({"line_ids": ["x", "x"]}, "unique"),
        ({"line_ids": [1]}, "non-empty"),
        ({"line_digests": ["bad"]}, "triples"),
        ({"line_digests": [("x", "unknown", "0" * 64)]}, "severity"),
        ({"line_digests": [("x", "strong", "bad")]}, "digest"),
    ],
)
def test_canary_statement_rejects_malformed_metadata(changes, message):
    with pytest.raises((TypeError, ValueError), match=message):
        CanaryStatement(
            **{
                field: changes.get(field, getattr(issue_canary("2026-07-15"), field))
                for field in ("statement", "issued_on", "registry_digest", "line_ids", "line_digests")
            }
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"statement": ""},
        {"issued_on": 1},
        {"registry_digest": "bad"},
        {"line_ids": 1},
        {"line_ids": ["duplicate", "duplicate"]},
        {"line_digests": 1},
        {"line_digests": [("x", "strong")]},
        {"line_digests": [("", "strong", "0" * 64)]},
        {"line_digests": [("x", "unknown", "0" * 64)]},
        {"line_digests": [("x", "strong", "bad")]},
    ],
)
def test_verify_canary_returns_structured_failure_for_forged_metadata(changes):
    result = verify_canary(_forged_canary(**changes), as_of="2026-07-17")
    assert result.intact is False
    assert result.stale is True
    assert "metadata invalid" in result.detail


def test_canary_missing_and_invalid_freshness_parameters_fail_closed():
    missing = verify_canary(None)
    assert missing.intact is False and missing.stale is True
    assert is_stale(None) is True
    with pytest.raises(ValueError):
        is_stale(issue_canary("2026-07-15"), max_age_days=-1)
    with pytest.raises(TypeError):
        issue_canary(None)
    with pytest.raises(ValueError):
        issue_canary("2026-07-15", statement=" ")


def test_transparency_report_freezes_mapping_and_rejects_bad_shapes():
    report = transparency_report([], period="2026")
    assert report.by_classification[Classification.COMPLIANT.value] == 0
    with pytest.raises(TypeError):
        report.by_classification["new"] = 1
    with pytest.raises(TypeError):
        transparency_report("not-findings")
    with pytest.raises(TypeError):
        TransparencyReport("2026", 0, [], 0, 0)
    with pytest.raises(ValueError):
        TransparencyReport("", 0, {}, 0, 0)
