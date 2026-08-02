"""Derivation and falsifiability tests for the two decision-surface plates.

The registry plates show what the boundary *is*. These two show what the
decision procedure *does* when one input moves: degrade a single evidence
record, or declare one trigger token instead of all of them. A plate whose
numbers were typed into the generator would be worse than no plate, so every
assertion recomputes the expected content from `red_line.analysis` and compares
it to the emitted SVG.

Three tests plant a defect in a copy of the registry and require the plate to
follow it, so no green here is green-by-construction:

* relabelling an ALL-mode exemption as ANY must flip its single-token row from
  a block to a compliant result;
* removing an exemption must make the sensitivity plate refuse to render at all,
  because its baseline is no longer compliant;
* adding a second ALL-mode exemption must move the summary band's mode counts.

Reads are anchored to drawn x positions where a token could also appear in a
header, for the same reason as the composition plates: matching on content
alone can compare the wrong run and pass for the wrong reason.
"""

from __future__ import annotations

import re
from dataclasses import replace

import pytest

from red_line.analysis.evidence_sensitivity import PERTURBATIONS, run_evidence_sensitivity
from red_line.analysis.trigger_semantics import run_trigger_semantics
from red_line.figures.plates_analysis import (
    blocking_signature,
    evidence_gate_sensitivity,
    exemption_trigger_semantics,
)
from red_line.figures.registry import GENERATORS
from red_line.figures.text import FIGURE_TEXT
from red_line.model import AssessmentReasonCode, EvidenceKind, Exemption, ExemptionMatchMode
from red_line.registry import PERSONAL_RED_LINES

_TEXT_RE = re.compile(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>([^<]+)</text>')


def _runs(svg: str) -> list[tuple[float, float, str]]:
    return [
        (float(x), float(y), content.replace("&amp;", "&").replace("&#x27;", "'"))
        for x, y, content in _TEXT_RE.findall(svg)
    ]


def _texts(svg: str) -> list[str]:
    return [content for _, _, content in _runs(svg)]


def _registry_with(line_id: str, **changes: object) -> tuple:
    return tuple(
        replace(line, **changes) if line.id == line_id else line for line in PERSONAL_RED_LINES
    )


# --------------------------------------------------------------------------
# Both plates are registered and reachable through the shared figure set.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "generator"),
    [
        ("fig:evidence-gate-sensitivity", evidence_gate_sensitivity),
        ("fig:exemption-trigger-semantics", exemption_trigger_semantics),
    ],
)
def test_plate_is_registered_and_captioned(label: str, generator) -> None:
    assert GENERATORS[label] is generator
    assert FIGURE_TEXT[label]["filename"].endswith(".png")
    assert FIGURE_TEXT[label]["caption"].strip()
    assert FIGURE_TEXT[label]["alt"].strip()
    assert FIGURE_TEXT[label]["source"].startswith("src/red_line/analysis/")


@pytest.mark.parametrize(
    "generator", [evidence_gate_sensitivity, exemption_trigger_semantics]
)
def test_plate_is_byte_identical_across_two_builds(generator) -> None:
    assert generator() == generator()


# --------------------------------------------------------------------------
# Evidence-gate sensitivity.
# --------------------------------------------------------------------------


def test_sensitivity_plate_draws_every_dimension_and_perturbation() -> None:
    """Row and column headings are the live enum and the declared columns."""

    svg = evidence_gate_sensitivity()
    texts = _texts(svg)

    for kind in EvidenceKind:
        assert kind.value in texts
    for perturbation in PERTURBATIONS:
        assert perturbation.replace("_", "-").upper() in texts


def test_sensitivity_plate_summary_reproduces_the_executed_counts() -> None:
    """The band restates the report, and the report is recomputed here."""

    report = run_evidence_sensitivity()
    svg = evidence_gate_sensitivity()

    assert (
        f"{report.blocked_count} of {report.evaluation_count} perturbations withdrew the "
        f"{report.baseline.value} result · {report.localized_count} of "
        f"{report.evaluation_count} named only the degraded dimension" in _texts(svg)
    )
    assert f"YES {len(PERTURBATIONS)}/{len(PERTURBATIONS)}" in _texts(svg)


def test_sensitivity_plate_cell_text_is_the_returned_verdict_and_codes() -> None:
    """Every cell's two lines come from the assessment, not from the layout."""

    report = run_evidence_sensitivity()
    texts = _texts(evidence_gate_sensitivity())
    signatures = {blocking_signature(cell.reason_codes) for cell in report.cells}

    assert signatures == {"missing", "missing + unresolved", "missing + stale"}
    for signature in signatures:
        assert signature in texts
    assert "INSUFF. INFO" in texts


def test_blocking_signature_names_only_evidence_codes() -> None:
    """The helper reads reason codes, and says so when there are none."""

    assert blocking_signature(()) == "no evidence code"
    assert blocking_signature((AssessmentReasonCode.INTAKE_BLOCKED,)) == "no evidence code"
    assert (
        blocking_signature(
            (AssessmentReasonCode.MISSING_EVIDENCE, AssessmentReasonCode.STALE_EVIDENCE)
        )
        == "missing + stale"
    )


def test_sensitivity_plate_refuses_a_registry_whose_baseline_is_not_compliant() -> None:
    """Planted defect: strip the narrowing exemption and require a refusal.

    A plate that still rendered would show forty-five "blocks" against a
    baseline that was itself blocked — a green reading of a meaningless sweep.
    """

    crippled = _registry_with("cogsec-integrity", exemptions=())

    with pytest.raises(ValueError, match="baseline must be COMPLIANT"):
        evidence_gate_sensitivity(crippled)


# --------------------------------------------------------------------------
# Exemption trigger semantics.
# --------------------------------------------------------------------------


def test_trigger_plate_draws_every_exemption_with_its_line_and_anchor() -> None:
    report = run_trigger_semantics()
    texts = _texts(exemption_trigger_semantics())

    for row in report.rows:
        assert row.exemption_id in texts
    for line_id in {row.line_id for row in report.rows}:
        anchor = next(row.anchor for row in report.rows if row.line_id == line_id)
        assert f"{line_id}  ({anchor})" in texts


def test_trigger_plate_cells_report_the_executed_match_counts_and_verdicts() -> None:
    report = run_trigger_semantics()
    texts = _texts(exemption_trigger_semantics())

    for row in report.rows:
        assert f"{row.single_match_count} of {len(row.trigger_scope)} match" in texts
        assert f"all {len(row.trigger_scope)} match" in texts
        assert row.match_mode.upper() in texts
    assert "NON-COMPLIANT" in texts, "the ALL-mode single-token rows must read as blocks"


def test_trigger_plate_summary_reproduces_the_executed_counts() -> None:
    report = run_trigger_semantics()
    consistent = sum(1 for row in report.rows if row.mode_consistent)

    assert (
        f"{len(report.rows)} typed exemptions · {report.any_mode_count} ANY · "
        f"{report.all_mode_count} ALL · {report.evaluation_count} executed evaluate_action runs "
        f"· rows behaving as their mode requires: {consistent} of {len(report.rows)}"
        in _texts(exemption_trigger_semantics())
    )


def test_trigger_plate_follows_a_relabelled_exemption_mode() -> None:
    """Planted defect: widen an ALL-mode exemption and require the plate to move."""

    line = next(entry for entry in PERSONAL_RED_LINES if entry.id == "s2-untargeted-profiling")
    target = next(ex for ex in line.exemptions if ex.match_mode is ExemptionMatchMode.ALL)
    widened = Exemption(
        id=target.id,
        description=target.description,
        trigger_scope=target.trigger_scope,
        required_evidence=target.required_evidence,
        match_mode=ExemptionMatchMode.ANY,
    )
    planted = _registry_with(
        line.id, exemptions=tuple(widened if ex.id == target.id else ex for ex in line.exemptions)
    )

    before = run_trigger_semantics()
    after = run_trigger_semantics(planted)
    planted_svg = _texts(exemption_trigger_semantics(planted))

    assert after.all_mode_count == before.all_mode_count - 1
    assert after.any_mode_count == before.any_mode_count + 1
    assert (
        f"{len(after.rows)} typed exemptions · {after.any_mode_count} ANY · "
        f"{after.all_mode_count} ALL" in " ".join(planted_svg)
    )
    row = next(entry for entry in after.rows if entry.exemption_id == target.id)
    assert f"{row.single_match_count} of {len(row.trigger_scope)} match" in planted_svg
    assert row.single_match_count == len(row.trigger_scope)


def test_trigger_plate_follows_an_added_all_mode_exemption() -> None:
    """Planted defect: add a second ALL-mode exemption and require new counts."""

    line = next(entry for entry in PERSONAL_RED_LINES if entry.id == "cogsec-integrity")
    added = Exemption(
        id="planted-all-mode-probe",
        description="Planted probe requiring two declared tokens at once",
        trigger_scope=frozenset({"planted_alpha", "planted_beta"}),
        required_evidence=frozenset({EvidenceKind.PURPOSE, EvidenceKind.END_USE}),
        match_mode=ExemptionMatchMode.ALL,
    )
    planted = _registry_with(line.id, exemptions=line.exemptions + (added,))

    before = run_trigger_semantics()
    after = run_trigger_semantics(planted)
    texts = _texts(exemption_trigger_semantics(planted))

    assert after.all_mode_count == before.all_mode_count + 1
    assert len(after.rows) == len(before.rows) + 1
    assert "planted-all-mode-probe" in texts
    row = next(entry for entry in after.rows if entry.exemption_id == added.id)
    assert row.single_match_count == 0
    assert row.full.matched
