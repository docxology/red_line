"""Monotonicity-sweep analysis tests: real evaluator, proof-of-detection.

No mocks. Every assertion binds to the live registry and the real
``evaluate_action``; the helper's positive controls prove the lattice check
CAN reject an inverted row instead of being green by construction.
"""

from __future__ import annotations

import pytest

from red_line.analysis.monotonicity import (
    STRICTNESS_ORDER,
    TIERS_BY_DESCENDING_OVERSIGHT,
    KeywordStrictnessRow,
    run_monotonicity_sweep,
    strictness_is_monotone,
)
from red_line.model import Classification, DeploymentTier
from red_line.registry import PERSONAL_RED_LINES


def test_sweep_is_exhaustive_over_the_registry_keyword_lattice():
    """Every scope keyword of every line appears exactly once, in sorted order."""
    report = run_monotonicity_sweep()
    expected = {(line.id, keyword) for line in PERSONAL_RED_LINES for keyword in line.scope}
    assert {(row.line_id, row.keyword) for row in report.rows} == expected
    assert report.keyword_count == len(expected) > 0
    assert report.evaluation_count == report.keyword_count * len(report.tiers)
    assert report.tiers == TIERS_BY_DESCENDING_OVERSIGHT
    ordered = [(row.line_id, row.keyword) for row in report.rows]
    assert ordered == sorted(ordered), "rows must be deterministic (line id, keyword)"


def test_live_evaluator_is_monotone_with_zero_inversions():
    """The real evaluator shows no strictness inversion anywhere on the lattice."""
    report = run_monotonicity_sweep()
    assert report.monotone is True
    assert report.inversion_count == 0
    assert all(row.monotone for row in report.rows)
    for row in report.rows:
        assert len(row.verdicts) == len(TIERS_BY_DESCENDING_OVERSIGHT)
        for verdict in row.verdicts:
            assert verdict in STRICTNESS_ORDER, (
                "a fully evidenced single-keyword intake must land on the policy lattice"
            )


def test_sweep_is_deterministic_across_runs():
    report_a = run_monotonicity_sweep()
    report_b = run_monotonicity_sweep()
    assert report_a == report_b


def test_strictness_check_rejects_an_inverted_row():
    """Positive control: the lattice check CAN go red on a softened verdict."""
    inverted = (
        Classification.NON_COMPLIANT,
        Classification.COMPLIANT,
        Classification.COMPLIANT,
    )
    assert strictness_is_monotone(inverted) is False
    monotone = (
        Classification.COMPLIANT,
        Classification.COMPLIANT,
        Classification.NON_COMPLIANT,
    )
    assert strictness_is_monotone(monotone) is True


def test_strictness_check_fails_closed_on_off_lattice_verdicts():
    """An intake stop or out-of-scope result is never silently ranked."""
    with pytest.raises(ValueError):
        strictness_is_monotone((Classification.COMPLIANT, Classification.OUTSIDE_SCOPE))
    with pytest.raises(ValueError):
        strictness_is_monotone((Classification.INSUFFICIENT_INFORMATION,))


def test_sweep_fails_closed_on_malformed_inputs():
    with pytest.raises(ValueError):
        run_monotonicity_sweep(as_of="not-a-date")
    with pytest.raises(TypeError):
        run_monotonicity_sweep(as_of=20260715)
    with pytest.raises(TypeError):
        run_monotonicity_sweep(lines="not-lines")
    with pytest.raises(TypeError):
        run_monotonicity_sweep(lines=("not-a-red-line",))


def test_report_agrees_with_the_regression_suite_property():
    """Cross-check: the report's lattice equals a direct per-tier re-derivation."""
    report = run_monotonicity_sweep()
    by_key = {(row.line_id, row.keyword): row for row in report.rows}
    # The two known tier-sensitive keywords soften nowhere and harden at
    # AIR_GAPPED; every other row is uniform. Derived, not asserted by name:
    non_uniform = {key for key, row in by_key.items() if len(set(row.verdicts)) > 1}
    for key in non_uniform:
        row = by_key[key]
        assert isinstance(row, KeywordStrictnessRow)
        ranks = [STRICTNESS_ORDER[v] for v in row.verdicts]
        assert ranks == sorted(ranks)
    # The AIR_GAPPED column can never be strictly softer than HOSTED anywhere.
    hosted_index = report.tiers.index(DeploymentTier.HOSTED)
    air_index = report.tiers.index(DeploymentTier.AIR_GAPPED)
    for row in report.rows:
        assert STRICTNESS_ORDER[row.verdicts[air_index]] >= STRICTNESS_ORDER[row.verdicts[hosted_index]]
def test_review_synthetic_sweep_threads_review_date():
    from red_line.analysis import run_monotonicity_sweep

    baseline = run_monotonicity_sweep()
    for review_date in ("2000-01-01", "2035-12-31"):
        current = run_monotonicity_sweep(as_of=review_date)
        assert current.rows == baseline.rows


def test_review_combination_sweep_covers_triggers_conflicts_and_aliases():
    from red_line.analysis.monotonicity import run_combination_sweep

    report = run_combination_sweep()
    assert report.monotone
    assert report.conflicts_blocked
    assert report.aliases_agree
    assert report.evaluation_count > run_monotonicity_sweep().evaluation_count
    assert report == run_combination_sweep()
    assert report.rows == run_combination_sweep(as_of="2035-12-31").rows
    from pathlib import Path

    prose = (Path(__file__).resolve().parents[2] / "manuscript" / "05_deployment_tiers.md").read_text()
    assert f"executes {report.evaluation_count} evaluations" in prose
    assert f"{len(report.rows)} compound scope rows" in prose


def test_review_custom_registry_does_not_inherit_monotonicity():
    from dataclasses import replace
    from red_line import ExemptionMatchMode
    from red_line.analysis.monotonicity import run_combination_sweep

    line = PERSONAL_RED_LINES[0]
    exemption = replace(line.exemptions[0], trigger_scope=frozenset({"air_gapped"}),
                        match_mode=ExemptionMatchMode.ANY)
    planted = replace(line, exemptions=(exemption,), max_tier=DeploymentTier.AIR_GAPPED)
    assert not run_combination_sweep((planted,)).monotone
