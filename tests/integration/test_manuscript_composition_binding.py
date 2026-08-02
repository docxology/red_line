"""Composition-section binding: manuscript numbers must equal derived metrics.

The registry-composition section (``manuscript/09a_registry_composition.md``)
states structural numbers — the per-line table, scope-token totals, shared
tokens, evidence-depth distribution, and trigger-scope sizes — as *derived*
data. These tests recompute every one of those numbers from
``red_line.analysis.registry_metrics`` and fail the build if the prose has
drifted from the registry. The reason-code paragraph added to the evaluation
section is bound the same way against an executed ``run_outcome_coverage``.

No mocks; reads the real manuscript files, runs the real analysis code.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from red_line.analysis.outcome_coverage import BATTERY_AS_OF, _verified_context, run_outcome_coverage
from red_line import PERSONAL_RED_LINES
from red_line.evaluation import evaluate_action
from red_line.model import Classification, DeploymentTier, ProposedAction
from red_line.analysis.registry_metrics import (
    evidence_kind_demand,
    exemption_evidence_matrix,
    line_summaries,
    scope_token_frequency,
    unevidenced_exemptions,
)

ROOT = Path(__file__).resolve().parent.parent.parent
COMPOSITION = ROOT / "manuscript" / "09a_registry_composition.md"
EVALUATION = ROOT / "manuscript" / "08_ambiguity_and_evaluation.md"

_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
}


def _composition_text() -> str:
    return COMPOSITION.read_text(encoding="utf-8")


def test_per_line_table_matches_line_summaries():
    """Every row of the composition table equals the computed LineSummary."""
    body = _composition_text()
    rows = re.findall(
        r"^\| `([a-z0-9-]+)` \| (\w+) \| (\w+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) / (\d+) \|$",
        body,
        re.MULTILINE,
    )
    summaries = line_summaries()
    assert len(rows) == len(summaries), "table must have one row per line"
    by_id = {summary.line_id: summary for summary in summaries}
    assert {row[0] for row in rows} == set(by_id), "table rows must cover every line id exactly once"
    for line_id, severity, tier, scope, carve, exempt, any_n, all_n in rows:
        summary = by_id[line_id]
        assert severity == summary.severity
        assert tier == summary.max_tier
        assert int(scope) == summary.scope_size
        assert int(carve) == summary.carve_out_count
        assert int(exempt) == summary.exemption_count
        assert int(any_n) == summary.any_mode_count
        assert int(all_n) == summary.all_mode_count


def test_scope_token_totals_match():
    """'N scope-token slots over M distinct canonical tokens' is derived."""
    body = _composition_text()
    match = re.search(r"(\d+) scope-token\s+slots? over (\d+) distinct canonical", body)
    assert match is not None, "composition section must state token totals"
    frequency = scope_token_frequency()
    assert int(match.group(1)) == sum(frequency.values())
    assert int(match.group(2)) == len(frequency)


def test_shared_tokens_are_exactly_the_named_overlap_points():
    """The named shared tokens equal the computed >1-frequency token set."""
    body = _composition_text()
    shared = {token for token, count in scope_token_frequency().items() if count > 1}
    assert shared == {"handoff", "provenance"}
    for token in shared:
        assert f"`{token}`" in body, f"shared token {token} must be named"
    disjoint = re.search(r"remaining (\d+) tokens", body)
    assert disjoint is not None
    assert int(disjoint.group(1)) == len(scope_token_frequency()) - len(shared)


def test_the_named_applied_exemption_is_the_one_the_evaluator_reports():
    """The exemption id in the shared-token paragraph must be the applied one.

    The counts around this sentence were bound; the sentence itself was not,
    and it drifted: it named ``dual-use-ablation``'s methods-publication
    exemption, whose trigger tokens are ``methods``/``paper``/``benchmark`` and
    which a scope of exactly ``handoff`` cannot reach. The evaluator applies
    ``retained-oversight``. This re-derives the id from the assessment's own
    reason strings, so the prose cannot name a plausible-but-wrong mechanism
    again.
    """

    body = _composition_text()
    action = ProposedAction(
        description="monotonicity sweep fixture for handoff",
        scope=frozenset({"handoff"}),
        context=_verified_context(),
        tier=DeploymentTier.HOSTED,
    )
    assessment = evaluate_action(action, PERSONAL_RED_LINES, as_of=BATTERY_AS_OF)

    applied = {
        match.group(1)
        for reason in assessment.reasons
        for match in [re.search(r"narrowed by verified exemption ([a-z0-9-]+)", reason)]
        if match
    }
    unexempted = {
        reason.split(":", 1)[0] for reason in assessment.reasons if "not exempted" in reason
    }

    assert applied, "no exemption was applied; this binding would be vacuous"
    assert assessment.classification is Classification.NON_COMPLIANT
    assert "`NON_COMPLIANT`" in body
    for exemption_id in applied:
        assert f"`{exemption_id}`" in body, (
            f"09a names an exemption the evaluator did not apply; it applied {sorted(applied)}"
        )
    for line_id in unexempted:
        assert f"`{line_id}`" in body

    # The wrong id must be absent, not merely unmentioned alongside the right one.
    every_exemption = {
        exemption.id for line in PERSONAL_RED_LINES for exemption in line.exemptions
    }
    for exemption_id in sorted(every_exemption - applied):
        assert f"`{exemption_id}` exemption is satisfied" not in body


def test_evidence_depth_distribution_matches():
    """'eleven ... exactly two ... five ... exactly three' binds to the matrix."""
    body = _composition_text()
    match = re.search(
        r"(\w+) exemptions require exactly two evidence\s+kinds and\s+(\w+) require\s+exactly\s+three",
        body,
    )
    assert match is not None, "composition section must state evidence depth"
    counts = Counter(row.required_count for row in exemption_evidence_matrix())
    assert set(counts) == {2, 3}, "depth classes drifted; update prose and test"
    assert _NUMBER_WORDS[match.group(1)] == counts[2]
    assert _NUMBER_WORDS[match.group(2)] == counts[3]


def test_trigger_scope_size_distribution_matches():
    """'nine ... two tokens, six on three, and one on six' binds to the matrix."""
    body = _composition_text()
    match = re.search(
        r"(\w+) exemptions trigger\s+on two tokens, (\w+) on three, and (\w+) on six",
        body,
    )
    assert match is not None, "composition section must state trigger sizes"
    sizes = Counter(len(row.trigger_scope) for row in exemption_evidence_matrix())
    assert set(sizes) == {2, 3, 6}, "trigger-size classes drifted; update prose"
    assert _NUMBER_WORDS[match.group(1)] == sizes[2]
    assert _NUMBER_WORDS[match.group(2)] == sizes[3]
    assert _NUMBER_WORDS[match.group(3)] == sizes[6]


def test_beacon_derived_numbers_paragraph_matches_the_registry():
    """Every number in the 09_red_lines derived-numbers paragraph re-derives."""
    body = (ROOT / "manuscript" / "09_red_lines.md").read_text(encoding="utf-8")
    matrix = exemption_evidence_matrix()
    demand = evidence_kind_demand()
    by_name = {kind.name: count for kind, count in demand.items()}
    totals = re.search(
        r"the (\w+) lines carry (\d+)\s+typed exemptions that together declare"
        r"\s+(\d+) evidence requirements across the\s+(\w+) intake dimensions",
        body,
    )
    assert totals is not None, "beacon must state the derived totals"
    assert _NUMBER_WORDS[totals.group(1)] == len(PERSONAL_RED_LINES)
    assert int(totals.group(2)) == len(matrix)
    assert int(totals.group(3)) == sum(row.required_count for row in matrix)
    assert _NUMBER_WORDS[totals.group(4)] == len(demand)
    profile = re.search(
        r"Affected parties is the most-demanded dimension \((\w+)\s+exemptions"
        r"\s+require it\), followed by purpose, legal basis, and capability"
        r" scope\s+\((\w+) each\); end use and deployment are the least"
        r" demanded \((\w+) each\)",
        body,
    )
    assert profile is not None, "beacon must state the demand profile"
    assert _NUMBER_WORDS[profile.group(1)] == by_name["AFFECTED_PARTIES"]
    assert by_name["AFFECTED_PARTIES"] == max(demand.values())
    for name in ("PURPOSE", "LEGAL_BASIS", "CAPABILITY_SCOPE"):
        assert by_name[name] == _NUMBER_WORDS[profile.group(2)]
    for name in ("END_USE", "DEPLOYMENT"):
        assert by_name[name] == _NUMBER_WORDS[profile.group(3)]
        assert by_name[name] == min(demand.values())
    modes = re.search(
        r"(\w+)\s+exemptions match their trigger scope with `ANY` semantics"
        r" and (\w+) require\s+`ALL` trigger tokens",
        body,
    )
    assert modes is not None, "beacon must state trigger-mode counts"
    summaries = line_summaries()
    assert _NUMBER_WORDS[modes.group(1).lower()] == sum(s.any_mode_count for s in summaries)
    assert _NUMBER_WORDS[modes.group(2)] == sum(s.all_mode_count for s in summaries)


def test_limitations_structural_counts_match():
    """The limitations section's structural count words match the code."""
    body = (ROOT / "manuscript" / "10_limitations.md").read_text(encoding="utf-8")
    assert re.search(r"bounded by seven personal\s+lines", body) is not None
    assert len(PERSONAL_RED_LINES) == _NUMBER_WORDS["seven"]
    report = run_outcome_coverage()
    assert re.search(r"produce all five\s+classifications", body) is not None
    assert len(report.results) == _NUMBER_WORDS["five"]


def test_exemption_and_evidence_totals_match():
    """'The N typed exemptions distribute their M evidence requirements' derives."""
    body = _composition_text()
    match = re.search(
        r"The (\d+) typed exemptions distribute their (\d+) evidence\s+requirements",
        body,
    )
    assert match is not None, "composition section must state exemption totals"
    matrix = exemption_evidence_matrix()
    assert int(match.group(1)) == len(matrix)
    assert int(match.group(2)) == sum(row.required_count for row in matrix)


def test_free_pass_detector_empty_claim_is_true():
    """The stated empty free-pass result holds on the live registry."""
    body = _composition_text()
    assert "empty tuple" in body
    assert unevidenced_exemptions() == ()


def test_reason_code_paragraph_matches_executed_battery():
    """Every reason code the evaluation section names was actually returned."""
    body = EVALUATION.read_text(encoding="utf-8")
    report = run_outcome_coverage()
    assert report.complete and report.all_matched
    for result in report.results:
        for code in result.reason_codes:
            assert f"`{code.value}`" in body, (
                f"reason code {code.value} (case {result.name}) missing from prose"
            )
