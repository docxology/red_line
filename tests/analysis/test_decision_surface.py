"""Decision-surface analysis: evidence sensitivity and trigger semantics.

No mocks. Both sweeps run the real ``evaluate_action`` against the live
registry, and both carry positive controls: a registry whose exemption is
degraded on purpose has to make the report say so, otherwise a green sweep is
green by construction.
"""

from __future__ import annotations

import dataclasses
from datetime import date, timedelta

import pytest

from red_line.analysis.evidence_sensitivity import (
    BASELINE_SCOPE,
    BASELINE_TIER,
    PERTURBATIONS,
    run_evidence_sensitivity,
)
from red_line.analysis.trigger_semantics import PROBE_TIER, _anchor_for, run_trigger_semantics
from red_line.model import (
    AssessmentReasonCode,
    Classification,
    EvidenceKind,
    ExemptionMatchMode,
    RedLine,
)
from red_line.model.action import DEFAULT_EVIDENCE_MAX_AGE_DAYS
from red_line.model.red_line import Exemption, normalize_scope
from red_line.registry import PERSONAL_RED_LINES


def _registry_with(line_id: str, **changes: object) -> tuple[RedLine, ...]:
    """Swap one line of the live registry for a modified copy."""

    return tuple(
        dataclasses.replace(line, **changes) if line.id == line_id else line
        for line in PERSONAL_RED_LINES
    )


# --------------------------------------------------------------------------
# Evidence sensitivity.
# --------------------------------------------------------------------------


def test_sweep_covers_every_dimension_and_perturbation_exactly_once():
    """The grid is the full nine-by-five product, in a deterministic order."""

    report = run_evidence_sensitivity()
    coordinates = [(cell.kind, cell.perturbation) for cell in report.cells]

    assert len(coordinates) == len(set(coordinates))
    assert set(coordinates) == {
        (kind, perturbation) for kind in EvidenceKind for perturbation in PERTURBATIONS
    }
    assert report.evaluation_count == len(EvidenceKind) * len(PERTURBATIONS)
    assert coordinates == [
        (kind, perturbation) for kind in EvidenceKind for perturbation in PERTURBATIONS
    ]


def test_baseline_is_compliant_and_every_perturbation_withdraws_it():
    """The property the manuscript states, exercised on the live registry."""

    report = run_evidence_sensitivity()

    assert report.baseline is Classification.COMPLIANT
    assert report.scope == tuple(sorted(normalize_scope(BASELINE_SCOPE)))
    assert report.tier is BASELINE_TIER
    assert report.conjunctive
    assert report.blocked_count == report.evaluation_count
    assert report.localized_count == report.evaluation_count
    for cell in report.cells:
        assert cell.reached is Classification.INSUFFICIENT_INFORMATION
        assert cell.blocking_kinds == (cell.kind,)
        assert AssessmentReasonCode.INTAKE_BLOCKED in cell.reason_codes


def test_each_perturbation_raises_the_reason_code_it_is_named_for():
    """A removal reads as missing, a bad status as unresolved, an old date as stale."""

    report = run_evidence_sensitivity()
    signatures = {
        perturbation: {
            code
            for cell in report.cells
            if cell.perturbation == perturbation
            for code in cell.reason_codes
        }
        for perturbation in PERTURBATIONS
    }

    assert AssessmentReasonCode.UNRESOLVED_EVIDENCE not in signatures["absent"]
    assert AssessmentReasonCode.STALE_EVIDENCE not in signatures["absent"]
    for perturbation in ("self_asserted", "unverified", "contradicted"):
        assert AssessmentReasonCode.UNRESOLVED_EVIDENCE in signatures[perturbation]
        assert AssessmentReasonCode.STALE_EVIDENCE not in signatures[perturbation]
    assert AssessmentReasonCode.STALE_EVIDENCE in signatures["stale"]
    assert AssessmentReasonCode.UNRESOLVED_EVIDENCE not in signatures["stale"]


def test_the_stale_perturbation_sits_just_outside_the_configured_window():
    """The aged record is one day past the window, not an arbitrary old date."""

    report = run_evidence_sensitivity()
    review = date.fromisoformat(report.as_of)
    expected = (review - timedelta(days=DEFAULT_EVIDENCE_MAX_AGE_DAYS + 1)).isoformat()

    assert (review - date.fromisoformat(expected)).days == DEFAULT_EVIDENCE_MAX_AGE_DAYS + 1
    assert report.cell(EvidenceKind.PURPOSE, "stale").reached is (
        Classification.INSUFFICIENT_INFORMATION
    )


def test_sweep_is_deterministic_across_runs():
    assert run_evidence_sensitivity() == run_evidence_sensitivity()


def test_sensitivity_cell_lookup_rejects_an_unswept_coordinate():
    with pytest.raises(KeyError, match="no swept cell"):
        run_evidence_sensitivity().cell(EvidenceKind.PURPOSE, "shredded")


def test_degradation_rejects_an_unknown_perturbation_name():
    """Fail closed: an unrecognised label must raise, never be a silent no-op."""

    from red_line.analysis.evidence_sensitivity import _degraded_context
    from red_line.analysis.outcome_coverage import _verified_context

    with pytest.raises(ValueError, match="unknown perturbation"):
        _degraded_context(_verified_context(), EvidenceKind.PURPOSE, "shredded", date(2026, 7, 15))


def test_a_blocked_baseline_is_refused_rather_than_reported():
    """Positive control: without a compliant baseline the sweep proves nothing.

    Removing the exemption that narrows the baseline's line makes the baseline
    ``NON_COMPLIANT``. Every perturbation would still "block", so a report would
    read as a clean green while measuring nothing. The function must refuse.
    """

    crippled = _registry_with("cogsec-integrity", exemptions=())

    with pytest.raises(ValueError, match="baseline must be COMPLIANT"):
        run_evidence_sensitivity(crippled)


def test_sweep_rejects_a_malformed_review_date_and_a_non_red_line():
    with pytest.raises(ValueError):
        run_evidence_sensitivity(as_of="2026-13-40")
    with pytest.raises(TypeError, match="ISO date string"):
        run_evidence_sensitivity(as_of=20260715)
    with pytest.raises(TypeError, match="tuple or list"):
        run_evidence_sensitivity(lines="not a registry")
    with pytest.raises(TypeError, match="only RedLine values"):
        run_evidence_sensitivity(lines=("not a line",))


# --------------------------------------------------------------------------
# Trigger semantics.
# --------------------------------------------------------------------------


def test_probe_covers_every_typed_exemption_in_a_deterministic_order():
    report = run_trigger_semantics()
    expected = {
        (line.id, exemption.id) for line in PERSONAL_RED_LINES for exemption in line.exemptions
    }
    seen = [(row.line_id, row.exemption_id) for row in report.rows]

    assert set(seen) == expected
    assert seen == sorted(seen)
    assert report.tier is PROBE_TIER
    assert report.any_mode_count + report.all_mode_count == len(report.rows)
    assert report.evaluation_count == sum(len(row.trigger_scope) + 1 for row in report.rows)


def test_mode_semantics_hold_on_the_live_registry():
    """ANY fires on any single token; ALL fires only on the full trigger set."""

    report = run_trigger_semantics()

    assert report.consistent
    for row in report.rows:
        assert row.full.matched
        assert row.full.tokens == row.trigger_scope
        if row.match_mode == ExemptionMatchMode.ANY.value:
            assert row.single_match_count == len(row.trigger_scope)
            assert all(probe.matched for probe in row.singles)
        else:
            assert len(row.trigger_scope) >= 2
            assert row.single_match_count == 0
            assert not any(probe.matched for probe in row.singles)


def test_all_mode_rows_are_blocked_on_one_token_and_clear_on_the_full_set():
    """The executed consequence, not just the predicate."""

    report = run_trigger_semantics()
    all_rows = [row for row in report.rows if row.match_mode == ExemptionMatchMode.ALL.value]

    assert all_rows, "the registry declares no ALL-mode exemption; this check would be vacuous"
    for row in all_rows:
        assert {probe.reached for probe in row.singles} == {Classification.NON_COMPLIANT}
        assert row.full.reached is Classification.COMPLIANT


def test_every_anchor_belongs_to_its_own_line_and_is_unshared_when_possible():
    """The probe's anchor must implicate the line under test, not a neighbour."""

    report = run_trigger_semantics()
    by_id = {line.id: line for line in PERSONAL_RED_LINES}

    for row in report.rows:
        assert row.anchor in normalize_scope(by_id[row.line_id].scope)
        assert not row.anchor_shared, "every current line has a token no other line declares"


def test_anchor_selection_reports_a_shared_fallback_rather_than_hiding_it():
    """Positive control: a line whose every token is shared must be flagged.

    The live registry has no such line, so the flag is never set above. A gate
    on a field nothing can set is decoration, so the selector is exercised
    directly against an owner map in which both of a line's tokens are shared.
    """

    line = next(entry for entry in PERSONAL_RED_LINES if entry.id == "dual-use-ablation")
    tokens = sorted(normalize_scope(line.scope))
    solo_owners = {token: (line.id,) for token in tokens}
    shared_owners = {token: (line.id, "some-other-line") for token in tokens}

    assert _anchor_for(line, solo_owners) == (tokens[0], False)
    assert _anchor_for(line, shared_owners) == (tokens[0], True)


def test_probe_is_deterministic_across_runs():
    assert run_trigger_semantics() == run_trigger_semantics()


def test_probe_detects_a_mode_that_stopped_behaving_like_its_label():
    """Positive control: relabel an ALL-mode exemption ANY and require a change.

    The declared mode still says ``all`` in the row, but the exemption now
    matches on a single token, so the row must stop being mode-consistent.
    """

    line = next(entry for entry in PERSONAL_RED_LINES if entry.id == "s1-human-control-force")
    target = next(ex for ex in line.exemptions if ex.match_mode is ExemptionMatchMode.ALL)
    widened = Exemption(
        id=target.id,
        description=target.description,
        trigger_scope=target.trigger_scope,
        required_evidence=target.required_evidence,
        match_mode=ExemptionMatchMode.ANY,
    )
    planted = _registry_with(
        line.id,
        exemptions=tuple(widened if ex.id == target.id else ex for ex in line.exemptions),
    )

    report = run_trigger_semantics(planted)
    row = next(entry for entry in report.rows if entry.exemption_id == target.id)

    assert row.match_mode == ExemptionMatchMode.ANY.value
    assert row.single_match_count == len(row.trigger_scope)
    assert {probe.reached for probe in row.singles} == {Classification.COMPLIANT}
    assert report.all_mode_count == 2, "the registry lost one ALL-mode exemption"


def test_probe_rejects_a_malformed_review_date_and_a_non_red_line():
    with pytest.raises(ValueError):
        run_trigger_semantics(as_of="not-a-date")
    with pytest.raises(TypeError, match="ISO date string"):
        run_trigger_semantics(as_of=None)
    with pytest.raises(TypeError, match="tuple or list"):
        run_trigger_semantics(lines={"not": "a registry"})
    with pytest.raises(TypeError, match="only RedLine values"):
        run_trigger_semantics(lines=(42,))


def test_anchor_selection_fails_closed_on_a_zero_scope_line():
    """A line with no coverage token cannot be implicated, so it must raise."""

    line = PERSONAL_RED_LINES[0]
    zero_scope = object.__new__(RedLine)
    for field in dataclasses.fields(RedLine):
        object.__setattr__(zero_scope, field.name, getattr(line, field.name))
    object.__setattr__(zero_scope, "scope", ())

    with pytest.raises(ValueError, match="zero-scope line"):
        _anchor_for(zero_scope, {})
