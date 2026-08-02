"""Registry-metrics tests: real registry values plus proof-of-detection.

No mocks. Every assertion binds to the live registry or to a deliberately
planted-bad registry built from real ``RedLine``/``Exemption`` objects, so a
metrics function that stops seeing defects fails here (mirroring the
``invariants/checks.py`` proof-of-detection pattern).
"""

from __future__ import annotations

import pytest

from red_line.analysis.registry_metrics import (
    EVIDENCE_KIND_COLUMNS,
    evidence_kind_demand,
    exemption_evidence_matrix,
    line_summaries,
    scope_token_frequency,
    severity_distribution,
    tier_floor_distribution,
    unevidenced_exemptions,
)
from red_line.invariants import invariants_pass
from red_line.model import DeploymentTier, EvidenceKind, ExemptionMatchMode, Severity
from red_line.model.red_line import Exemption, RedLine
from red_line.registry import PERSONAL_RED_LINES


def _planted_bad_line() -> RedLine:
    """A structurally constructible line whose exemption demands no evidence."""

    return RedLine(
        id="planted-free-pass",
        title="Planted line with an unevidenced exemption",
        standard="I will not allow this planted line into the real registry.",
        rationale="Exists only to prove the metrics detect a free-pass exemption.",
        scope=("planted_scope",),
        carve_outs=("Does not restrict the detection test itself",),
        exemptions=(
            Exemption(
                id="planted-free-pass-exemption",
                description="Matches on declaration alone; requires no evidence",
                trigger_scope=frozenset({"planted_trigger"}),
                required_evidence=frozenset(),
            ),
        ),
        max_tier=DeploymentTier.HOSTED,
        severity=Severity.STRONG,
    )


class TestExemptionEvidenceMatrix:
    def test_one_row_per_registry_exemption(self) -> None:
        rows = exemption_evidence_matrix()
        expected = sum(len(line.exemptions) for line in PERSONAL_RED_LINES)
        assert len(rows) == expected == 16

    def test_rows_are_sorted_and_column_aligned(self) -> None:
        rows = exemption_evidence_matrix()
        keys = [(row.line_id, row.exemption_id) for row in rows]
        assert keys == sorted(keys)
        assert all(len(row.required) == len(EVIDENCE_KIND_COLUMNS) for row in rows)
        assert EVIDENCE_KIND_COLUMNS == tuple(EvidenceKind)

    def test_required_kinds_match_registry_source(self) -> None:
        rows = {(row.line_id, row.exemption_id): row for row in exemption_evidence_matrix()}
        for line in PERSONAL_RED_LINES:
            for exemption in line.exemptions:
                row = rows[(line.id, exemption.id)]
                assert set(row.required_kinds) == set(exemption.required_evidence)
                assert row.required_count == len(exemption.required_evidence)
                assert row.match_mode == exemption.match_mode.value

    def test_every_real_exemption_requires_evidence(self) -> None:
        assert all(row.required_count >= 1 for row in exemption_evidence_matrix())

    def test_deterministic_across_runs(self) -> None:
        assert exemption_evidence_matrix() == exemption_evidence_matrix()

    def test_empty_registry_yields_empty_matrix(self) -> None:
        assert exemption_evidence_matrix(()) == ()

    def test_rejects_non_redline_input(self) -> None:
        with pytest.raises(TypeError):
            exemption_evidence_matrix(("not a red line",))  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            exemption_evidence_matrix("not a collection")  # type: ignore[arg-type]


class TestEvidenceKindDemand:
    def test_every_kind_is_a_key(self) -> None:
        demand = evidence_kind_demand()
        assert set(demand) == set(EvidenceKind)

    def test_totals_match_matrix_cells(self) -> None:
        demand = evidence_kind_demand()
        matrix_total = sum(row.required_count for row in exemption_evidence_matrix())
        assert sum(demand.values()) == matrix_total == 37

    def test_known_registry_profile(self) -> None:
        demand = evidence_kind_demand()
        assert demand[EvidenceKind.AFFECTED_PARTIES] == 6
        assert demand[EvidenceKind.PURPOSE] == 5
        assert demand[EvidenceKind.END_USE] == 2
        assert demand[EvidenceKind.DEPLOYMENT] == 2

    def test_zero_demand_kinds_still_reported(self) -> None:
        demand = evidence_kind_demand(())
        assert set(demand) == set(EvidenceKind)
        assert all(count == 0 for count in demand.values())


class TestUnevidencedExemptionDetection:
    def test_real_registry_has_no_free_pass_exemption(self) -> None:
        assert unevidenced_exemptions() == ()

    def test_planted_free_pass_is_detected(self) -> None:
        planted = (*PERSONAL_RED_LINES, _planted_bad_line())
        flagged = unevidenced_exemptions(planted)
        assert [row.exemption_id for row in flagged] == ["planted-free-pass-exemption"]
        assert flagged[0].required_count == 0
        # The invariant battery rejects the same planted registry — the metric
        # and the invariant agree on what a defect is.
        assert invariants_pass(planted) is False
        assert invariants_pass(PERSONAL_RED_LINES) is True


class TestLineSummaries:
    def test_one_summary_per_line_sorted_by_id(self) -> None:
        summaries = line_summaries()
        assert len(summaries) == len(PERSONAL_RED_LINES) == 7
        assert [s.line_id for s in summaries] == sorted(s.line_id for s in summaries)

    def test_match_mode_counts_partition_exemptions(self) -> None:
        for summary in line_summaries():
            assert summary.any_mode_count + summary.all_mode_count == summary.exemption_count

    def test_summary_binds_to_registry_source(self) -> None:
        by_id = {line.id: line for line in PERSONAL_RED_LINES}
        for summary in line_summaries():
            line = by_id[summary.line_id]
            assert summary.severity == line.severity.value
            assert summary.max_tier == line.max_tier.value
            assert summary.exemption_count == len(line.exemptions)
            assert summary.carve_out_count == len(line.carve_outs)
            assert summary.stated_on == line.stated_on
            expected_all = sum(1 for ex in line.exemptions if ex.match_mode is ExemptionMatchMode.ALL)
            assert summary.all_mode_count == expected_all
            union = {kind for ex in line.exemptions for kind in ex.required_evidence}
            assert set(summary.evidence_kinds_used) == union

    def test_registry_wide_match_mode_split(self) -> None:
        summaries = line_summaries()
        assert sum(s.any_mode_count for s in summaries) == 13
        assert sum(s.all_mode_count for s in summaries) == 3


class TestDistributions:
    def test_severity_distribution_matches_registry(self) -> None:
        distribution = severity_distribution()
        assert distribution[Severity.CANARY] == 2
        assert distribution[Severity.ABSOLUTE] == 1
        assert distribution[Severity.STRONG] == 4
        assert sum(distribution.values()) == len(PERSONAL_RED_LINES)

    def test_tier_floor_distribution_matches_registry(self) -> None:
        distribution = tier_floor_distribution()
        assert distribution[DeploymentTier.HOSTED] == 2
        assert distribution[DeploymentTier.CONNECTED] == 3
        assert distribution[DeploymentTier.AIR_GAPPED] == 2
        assert sum(distribution.values()) == len(PERSONAL_RED_LINES)

    def test_all_enum_members_present_even_when_empty(self) -> None:
        assert set(severity_distribution(())) == set(Severity)
        assert set(tier_floor_distribution(())) == set(DeploymentTier)


class TestScopeTokenFrequency:
    def test_shared_tokens_are_exactly_the_known_overlaps(self) -> None:
        frequency = scope_token_frequency()
        shared = {token: count for token, count in frequency.items() if count > 1}
        assert shared == {"handoff": 2, "provenance": 2}

    def test_total_distinct_tokens(self) -> None:
        assert len(scope_token_frequency()) == 34

    def test_keys_are_sorted_canonical_tokens(self) -> None:
        tokens = list(scope_token_frequency())
        assert tokens == sorted(tokens)

    def test_counts_bind_to_registry_source(self) -> None:
        frequency = scope_token_frequency()
        from red_line.model.red_line import normalize_scope

        for token, count in frequency.items():
            actual = sum(1 for line in PERSONAL_RED_LINES if token in normalize_scope(line.scope))
            assert count == actual
