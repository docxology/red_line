"""Strict-constructor rejection of malformed model and oversight objects."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from red_line import (
    ActionContext,
    Classification,
    EvidenceKind,
    PERSONAL_RED_LINES,
    ProposedAction,
)
from red_line.model import ActionAssessment, Exemption, ExemptionMatchMode
from red_line.oversight import (
    ReviewAuthorization,
    ReviewFinding,
    TransparencyReport,
    review_engagement,
    transparency_report,
)

from ..helpers import action, complete_context


class TestExemptionConstructorRejections:
    def _kwargs(self, **overrides):
        base = dict(
            id="valid-exemption",
            description="a valid exemption",
            trigger_scope=frozenset({"support"}),
            required_evidence=frozenset({EvidenceKind.PURPOSE}),
        )
        base.update(overrides)
        return base

    @pytest.mark.parametrize(
        ("overrides", "exc"),
        [
            ({"id": "   "}, ValueError),
            ({"description": "   "}, ValueError),
            ({"trigger_scope": "support"}, TypeError),
            ({"required_evidence": "purpose"}, TypeError),
            ({"trigger_scope": frozenset({42})}, TypeError),
            ({"required_evidence": frozenset({"purpose"})}, TypeError),
            ({"match_mode": "any"}, TypeError),
            ({"trigger_scope": frozenset({"__"})}, ValueError),
            ({"trigger_scope": frozenset()}, ValueError),
        ],
    )
    def test_rejected(self, overrides, exc):
        with pytest.raises(exc):
            Exemption(**self._kwargs(**overrides))

    def test_all_match_mode_covers_only_supersets(self):
        exemption = Exemption(
            **self._kwargs(
                trigger_scope=frozenset({"support", "research"}),
                match_mode=ExemptionMatchMode.ALL,
            )
        )
        assert exemption.matches(frozenset({"support"})) is False
        assert exemption.matches(frozenset({"support", "research", "extra"})) is True


class TestRedLineConstructorRejections:
    @pytest.mark.parametrize(
        ("overrides", "exc"),
        [
            ({"id": 5}, TypeError),
            ({"id": "Bad_ID"}, ValueError),
            ({"title": "   "}, ValueError),
            ({"standard": "Never do the thing"}, ValueError),  # not first-person
            ({"stated_on": "not-a-date"}, ValueError),
            ({"scope": "targeting"}, TypeError),
            ({"carve_outs": "does not restrict x"}, TypeError),
            ({"exemptions": "none"}, TypeError),
            ({"scope": ("__",)}, ValueError),
            ({"scope": (42,)}, ValueError),
            ({"carve_outs": ("   ",)}, ValueError),
            ({"exemptions": ("not-an-exemption",)}, TypeError),
            ({"max_tier": "hosted"}, TypeError),
            ({"severity": "canary"}, TypeError),
        ],
    )
    def test_rejected(self, overrides, exc):
        with pytest.raises(exc):
            replace(PERSONAL_RED_LINES[0], **overrides)


class TestActionModelRejections:
    def test_blank_description_rejected(self):
        with pytest.raises(ValueError):
            ProposedAction(description="   ", scope=frozenset({"teaching"}), context=complete_context())

    def test_blank_scope_token_rejected(self):
        with pytest.raises(ValueError):
            ProposedAction(description="x", scope=frozenset({"  "}), context=complete_context())

    @pytest.mark.parametrize(
        ("overrides", "exc"),
        [
            ({"evidence": "records"}, TypeError),
            ({"unknowns": "unknown"}, TypeError),
        ],
    )
    def test_context_collection_types_enforced(self, overrides, exc):
        base = complete_context()
        values = dict(
            purpose=base.purpose,
            end_use=base.end_use,
            affected_parties=base.affected_parties,
            data_provenance=base.data_provenance,
            legal_basis=base.legal_basis,
            human_control=base.human_control,
            deployment=base.deployment,
            downstream_transfer=base.downstream_transfer,
            capability_scope=base.capability_scope,
        )
        values.update(overrides)
        with pytest.raises(exc):
            ActionContext(**values)

    def test_evidence_queries_reject_bad_arguments(self):
        context = complete_context()
        with pytest.raises(TypeError):
            context.has_verified_evidence("purpose")
        with pytest.raises(TypeError):
            context.has_verified_evidence(EvidenceKind.PURPOSE, as_of="2026-07-16")
        with pytest.raises(TypeError):
            context.missing_fields(as_of="2026-07-16")
        with pytest.raises(TypeError):
            context.stale_evidence(as_of="2026-07-16")

    def test_assessment_rejects_malformed_fields(self):
        act = action("teaching materials", frozenset({"teaching"}))
        good = dict(action=act, classification=Classification.OUTSIDE_SCOPE, implicated=())
        with pytest.raises(TypeError):
            ActionAssessment(**{**good, "action": "not-an-action"})
        with pytest.raises(TypeError):
            ActionAssessment(**{**good, "classification": "outside_scope"})
        with pytest.raises(TypeError):
            ActionAssessment(**{**good, "implicated": ("not-a-line",)})
        with pytest.raises(TypeError):
            ActionAssessment(**{**good, "reasons": 42})
        with pytest.raises(TypeError):
            ActionAssessment(**{**good, "reasons": (1,)})
        with pytest.raises(TypeError):
            ActionAssessment(**{**good, "missing_evidence": ("purpose",)})


class TestOversightRejections:
    def _finding_kwargs(self, **overrides):
        base = dict(
            engagement="an engagement",
            classification=Classification.OUTSIDE_SCOPE,
            implicated_ids=(),
            finding="a finding",
            reviewed_on="2026-07-15",
        )
        base.update(overrides)
        return base

    @pytest.mark.parametrize(
        ("overrides", "exc"),
        [
            ({"implicated_ids": "s1"}, TypeError),
            ({"implicated_ids": ("  ",)}, ValueError),
            ({"implicated_ids": ("a", "a")}, ValueError),
            ({"authorization": "approved"}, TypeError),
            ({"declared_scope": 42}, TypeError),
            ({"declared_scope": (1,)}, TypeError),
            ({"tier": 3}, TypeError),
            ({"tier": "orbital"}, ValueError),
            ({"ambiguous": "yes"}, TypeError),
        ],
    )
    def test_review_finding_rejects(self, overrides, exc):
        with pytest.raises(exc):
            ReviewFinding(**self._finding_kwargs(**overrides))

    def test_authorization_never_unblocks(self):
        authorization = ReviewAuthorization(
            authorized_by="the author",
            authority="self-review escalation",
            rationale="documented escalation, not a bypass",
            recorded_on="2026-07-15",
        )
        act = action("bulk-to-individual inference", frozenset({"surveillance"}))
        finding = review_engagement(act, reviewed_on=date.today().isoformat(), authorization=authorization)
        assert finding.classification is Classification.NON_COMPLIANT
        assert finding.blocks is True

    def _report_kwargs(self, **overrides):
        base = dict(period="2026", total=0, by_classification={}, authorizations=0, blocked=0)
        base.update(overrides)
        return base

    @pytest.mark.parametrize(
        ("overrides", "exc"),
        [
            ({"period": "   "}, ValueError),
            ({"total": -1}, ValueError),
            ({"total": "3"}, ValueError),
            ({"by_classification": [("compliant", 1)]}, TypeError),
            ({"by_classification": {"compliant": -1}}, TypeError),
            ({"by_classification": {1: 2}}, TypeError),
            ({"authorizations": -1}, ValueError),
            ({"blocked": -1}, ValueError),
        ],
    )
    def test_transparency_report_rejects(self, overrides, exc):
        with pytest.raises(exc):
            TransparencyReport(**self._report_kwargs(**overrides))

    def test_transparency_report_function_rejects_bad_findings(self):
        with pytest.raises(TypeError):
            transparency_report("findings")
        with pytest.raises(TypeError):
            transparency_report(("not-a-finding",))

    def test_transparency_report_default_period_is_dated(self):
        report = transparency_report(())
        assert report.period.startswith("as of ")
        assert report.total == 0
