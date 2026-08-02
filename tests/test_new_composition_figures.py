"""Derivation and falsifiability tests for the two composition figures.

Both plates were added because the figure set showed the registry's
*eligibility* (which tiers each line permits) and never its *shape* (severity,
breadth, and which words two lines share). A figure whose numbers were typed
into the generator would be worse than no figure, so every assertion here
recomputes the expected content from `red_line.analysis` and compares it to the
emitted SVG.

Three of these tests plant a defect in a copy of the registry and require the
plate to follow it, so no green here is green-by-construction:

* an evidence-free exemption must change the free-pass band, which is the whole
  point of rendering a zero rather than omitting the panel;
* an added evidenced exemption must move the per-line bar counts;
* a widened scope must add a shared token to the collision grid.

Reads are anchored to drawn x positions rather than to text content, because a
scope token can also appear inside a stacked column header — matching on
content alone would compare the wrong run and pass for the wrong reason.
"""

from __future__ import annotations

import re
from dataclasses import replace

import pytest

from red_line.analysis.registry_metrics import (
    line_summaries,
    scope_token_frequency,
    scope_token_membership,
    severity_distribution,
    tier_floor_distribution,
    unevidenced_exemptions,
)
from red_line.figures.plates_analysis import (
    registry_composition_profile,
    scope_vocabulary_collisions,
)
from red_line.figures.registry import GENERATORS
from red_line.figures.text import FIGURE_TEXT
from red_line.model import EvidenceKind, Exemption, ExemptionMatchMode
from red_line.registry import PERSONAL_RED_LINES

_TEXT_RE = re.compile(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>([^<]+)</text>')


def _runs(svg: str) -> list[tuple[float, float, str]]:
    """Every rendered text run as ``(x, y, content)``, in document order."""

    return [
        (float(x), float(y), content.replace("&amp;", "&").replace("&#x27;", "'"))
        for x, y, content in _TEXT_RE.findall(svg)
    ]


def _texts(svg: str) -> list[str]:
    """Every rendered text run, in document order."""

    return [content for _, _, content in _runs(svg)]


def _column(svg: str, x: float, *, below: float = 0.0) -> list[str]:
    """Text runs drawn at one x position, ordered top to bottom.

    Column-anchored reads keep these assertions honest: a token name can also
    appear inside a stacked column header, so matching on content alone would
    silently compare the wrong run.
    """

    return [
        content
        for run_x, run_y, content in sorted(_runs(svg), key=lambda run: run[1])
        if run_x == x and run_y > below
    ]


def _free_pass_line(svg: str) -> str:
    return next(run for run in _texts(svg) if run.startswith("EXEMPTIONS REQUIRING NO EVIDENCE"))


# --------------------------------------------------------------------------
# fig:registry-composition-profile
# --------------------------------------------------------------------------


#: Drawn x positions of the composition plate's columns, read off the emitted
#: SVG rather than recomputed from the generator's arithmetic.
_PROFILE_LINE_ID_X = 66.0
_PROFILE_SEVERITY_X = 424.0
_PROFILE_TIER_X = 588.0
_PROFILE_METRIC_X = (796.0, 948.0, 1100.0, 1252.0)
_PROFILE_ROWS_BELOW = 240.0


def test_composition_profile_renders_one_row_per_line_in_sorted_id_order() -> None:
    """Row order is the analysis module's order, not dict or set order."""

    drawn = _column(registry_composition_profile(), _PROFILE_LINE_ID_X, below=_PROFILE_ROWS_BELOW)
    summaries = line_summaries()

    assert drawn == [summary.line_id for summary in summaries]
    assert drawn == sorted(drawn), "line_summaries must already be id-sorted"


def test_composition_profile_prints_every_structural_count_it_claims() -> None:
    """Each row's four numbers and two chips are the summary's own values."""

    svg = registry_composition_profile()
    summaries = line_summaries()

    assert _column(svg, _PROFILE_SEVERITY_X, below=_PROFILE_ROWS_BELOW) == [
        summary.severity.upper() for summary in summaries
    ]
    assert _column(svg, _PROFILE_TIER_X, below=_PROFILE_ROWS_BELOW) == [
        summary.max_tier.replace("_", "-").upper() for summary in summaries
    ]
    accessors = (
        lambda summary: summary.scope_size,
        lambda summary: summary.carve_out_count,
        lambda summary: summary.exemption_count,
        lambda summary: len(summary.evidence_kinds_used),
    )
    for x, accessor in zip(_PROFILE_METRIC_X, accessors):
        assert _column(svg, x, below=_PROFILE_ROWS_BELOW) == [
            str(accessor(summary)) for summary in summaries
        ]


def test_composition_profile_bars_share_one_scale_derived_from_the_data() -> None:
    """The longest bar is the largest count; equal counts get equal bars.

    Reads the drawn rect widths rather than trusting the generator's arithmetic.
    """

    svg = registry_composition_profile()
    summaries = line_summaries()
    metrics = [
        (summary.scope_size, summary.carve_out_count, summary.exemption_count, len(summary.evidence_kinds_used))
        for summary in summaries
    ]
    scale = max(value for row in metrics for value in row)
    # Filled bars are the only teal rects with a 16-unit height in this plate.
    widths = [
        float(match)
        for match in re.findall(r'<rect x="[\d.]+" y="[\d.]+" width="([\d.]+)" height="16"', svg)
    ]
    filled = widths[1::2]  # each bar is a track rect followed by its fill rect

    assert len(filled) == len(summaries) * 4
    expected = [96 * value / scale for row in metrics for value in row]
    assert filled == pytest.approx(expected)
    assert max(filled) == pytest.approx(96.0), "the largest count must fill the track"


def test_composition_profile_footer_states_the_two_distributions() -> None:
    texts = " | ".join(_texts(registry_composition_profile()))

    for severity, count in severity_distribution().items():
        assert f"{severity.value.upper()} {count}" in texts
    for tier, count in tier_floor_distribution().items():
        assert f"{tier.value.replace('_', '-').upper()} {count}" in texts


def test_composition_profile_renders_todays_zero_free_pass_as_a_result() -> None:
    """The band exists when the count is zero — that is the VIZ-17 point."""

    assert unevidenced_exemptions() == ()
    band = _free_pass_line(registry_composition_profile())

    assert band == "EXEMPTIONS REQUIRING NO EVIDENCE AT ALL: 0"
    assert "every typed exemption demands at least one VERIFIED record" in _texts(
        registry_composition_profile()
    )


def test_a_planted_evidence_free_exemption_changes_the_free_pass_band() -> None:
    """Positive control: plant a free pass and require the plate to say so.

    Without this the zero above would be unfalsifiable — a band that can only
    ever print 0 certifies nothing.
    """

    victim = PERSONAL_RED_LINES[0]
    free_pass = Exemption(
        id="planted-free-pass",
        description="planted exemption requiring no evidence at all",
        trigger_scope=frozenset({"not_applicable"}),
        required_evidence=frozenset(),
        match_mode=ExemptionMatchMode.ANY,
    )
    planted = (replace(victim, exemptions=(*victim.exemptions, free_pass)), *PERSONAL_RED_LINES[1:])

    assert len(unevidenced_exemptions(planted)) == 1

    svg = registry_composition_profile(planted)
    texts = _texts(svg)

    assert _free_pass_line(svg) == "EXEMPTIONS REQUIRING NO EVIDENCE AT ALL: 1"
    assert "free pass: planted-free-pass" in texts
    assert _free_pass_line(svg) != _free_pass_line(registry_composition_profile())


def test_a_planted_exemption_also_moves_the_row_counts() -> None:
    """The per-line bars follow the planted registry, not the live one."""

    victim = PERSONAL_RED_LINES[0]
    free_pass = Exemption(
        id="planted-free-pass",
        description="planted exemption requiring no evidence at all",
        trigger_scope=frozenset({"not_applicable"}),
        required_evidence=frozenset({EvidenceKind.PURPOSE}),
        match_mode=ExemptionMatchMode.ANY,
    )
    planted = (replace(victim, exemptions=(*victim.exemptions, free_pass)), *PERSONAL_RED_LINES[1:])

    live_texts = _texts(registry_composition_profile())
    planted_texts = _texts(registry_composition_profile(planted))

    assert live_texts != planted_texts
    live = next(summary for summary in line_summaries() if summary.line_id == victim.id)
    grown = next(summary for summary in line_summaries(planted) if summary.line_id == victim.id)
    assert grown.exemption_count == live.exemption_count + 1


# --------------------------------------------------------------------------
# fig:scope-vocabulary-collisions
# --------------------------------------------------------------------------


#: Drawn x positions of the collision grid's token and count columns.
_GRID_TOKEN_X = 66.0
_GRID_COUNT_X = 1186.0
_GRID_ROWS_BELOW = 260.0


def test_collision_grid_rows_are_every_token_in_sorted_order() -> None:
    svg = scope_vocabulary_collisions()
    tokens = [token for token, _ in scope_token_membership()]

    assert _column(svg, _GRID_TOKEN_X, below=_GRID_ROWS_BELOW) == tokens
    assert tokens == sorted(tokens)
    assert len(tokens) == len(scope_token_frequency())


def test_collision_grid_counts_match_membership_and_flag_shared_rows() -> None:
    """The count column and the SHARED tag are recomputed from membership."""

    svg = scope_vocabulary_collisions()
    membership = scope_token_membership()
    shared = [token for token, owners in membership if len(owners) > 1]

    assert shared == ["handoff", "provenance"]
    assert _texts(svg).count("SHARED") == len(shared)
    assert _column(svg, _GRID_COUNT_X, below=_GRID_ROWS_BELOW) == [
        str(len(owners)) for _, owners in membership
    ]


def test_collision_grid_footer_derives_the_single_line_token_count() -> None:
    membership = scope_token_membership()
    shared = [token for token, owners in membership if len(owners) > 1]
    expected = (
        f"{len(membership)} distinct tokens · {len(membership) - len(shared)} "
        f"declared by exactly one line · {len(shared)} shared"
    )

    assert expected in _texts(scope_vocabulary_collisions())


def test_collision_grid_footer_reads_out_the_executed_verdict() -> None:
    """The consequence line is the evaluator's own result, not a claim."""

    texts = _texts(scope_vocabulary_collisions())
    for token, owners in scope_token_membership():
        if len(owners) < 2:
            continue
        expected = f"{token} → {' + '.join(owners)} · executed verdict at hosted: NON COMPLIANT"
        assert expected in texts


def test_a_planted_shared_token_appears_as_a_new_collision() -> None:
    """Positive control: widen one line's scope onto another line's token."""

    donor, victim = PERSONAL_RED_LINES[0], PERSONAL_RED_LINES[1]
    borrowed = sorted(donor.scope)[0]
    assert borrowed not in victim.scope
    planted = (
        donor,
        replace(victim, scope=frozenset({*victim.scope, borrowed})),
        *PERSONAL_RED_LINES[2:],
    )

    live = [token for token, owners in scope_token_membership() if len(owners) > 1]
    planted_shared = [token for token, owners in scope_token_membership(planted) if len(owners) > 1]

    assert set(planted_shared) - set(live) == {borrowed}
    texts = _texts(scope_vocabulary_collisions(planted))
    assert texts.count("SHARED") == len(planted_shared)
    assert texts.count("SHARED") > _texts(scope_vocabulary_collisions()).count("SHARED")


# --------------------------------------------------------------------------
# Registration and determinism.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "label",
    ["fig:registry-composition-profile", "fig:scope-vocabulary-collisions"],
)
def test_both_new_figures_are_fully_registered(label: str) -> None:
    assert label in GENERATORS
    assert label in FIGURE_TEXT
    assert FIGURE_TEXT[label]["source_ids" if "source_ids" in FIGURE_TEXT[label] else "source"]
    assert FIGURE_TEXT[label]["caption"].strip()
    assert FIGURE_TEXT[label]["alt"].strip()


@pytest.mark.parametrize(
    "generator", [registry_composition_profile, scope_vocabulary_collisions]
)
def test_new_figures_are_byte_identical_across_two_calls(generator) -> None:
    assert generator() == generator()


@pytest.mark.parametrize(
    "label",
    ["fig:registry-composition-profile", "fig:scope-vocabulary-collisions"],
)
def test_new_figure_captions_name_no_colour_the_palette_does_not_use(label: str) -> None:
    """A caption must not tell a reader to look for a colour that is not there.

    The palette is teal / blue / amber / red plus ink and paper; green, purple,
    orange, yellow, and grey are never drawn.
    """

    caption = FIGURE_TEXT[label]["caption"].lower() + " " + FIGURE_TEXT[label]["alt"].lower()

    for absent in ("green", "purple", "orange", "yellow", "grey", "gray", "pink"):
        assert absent not in caption, absent


@pytest.mark.parametrize(
    "label",
    ["fig:registry-composition-profile", "fig:scope-vocabulary-collisions"],
)
def test_new_figure_captions_separate_fact_from_interpretation(label: str) -> None:
    caption = FIGURE_TEXT[label]["caption"]

    assert "Implementation fact:" in caption
    assert "Interpretation, stated as a limit:" in caption
