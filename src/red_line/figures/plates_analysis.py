"""Analysis-derived figure plates computed from the live evaluator and registry."""

from __future__ import annotations

from collections.abc import Sequence

from red_line.analysis.evidence_sensitivity import run_evidence_sensitivity
from red_line.analysis.monotonicity import run_monotonicity_sweep
from red_line.analysis.outcome_coverage import canonical_battery, run_outcome_coverage
from red_line.analysis.registry_metrics import (
    EVIDENCE_KIND_COLUMNS,
    evidence_kind_demand,
    exemption_evidence_matrix,
    line_summaries,
    scope_token_membership,
    severity_distribution,
    tier_floor_distribution,
    unevidenced_exemptions,
)
from red_line.analysis.trigger_semantics import run_trigger_semantics
from red_line.model import EvidenceRecord, RedLine
from red_line.model.enums import Classification, DeploymentTier, EvidenceStatus
from red_line.registry import PERSONAL_RED_LINES

from .svg import circle, figure_header, label, line, paragraph, rect, svg_document
from .text import FIGURE_TEXT
from .theme import (
    AMBER, BLUE, GRID, INK,
    MUTED, MUTED_FILL,
    PALE_AMBER, PALE_BLUE,
    PALE_RED, PALE_TEAL,
    PALE_TEAL_BG, PAPER, RED,
    TABLE_ROW_ALT, TEAL, WHITE,
)

_MONOTONICITY = run_monotonicity_sweep()


def exemption_evidence_matrix_figure() -> str:
    """Render the analysis-derived exemption × evidence-kind matrix."""

    rows = exemption_evidence_matrix()
    demand = evidence_kind_demand()
    body = [
        figure_header(
            FIGURE_TEXT["fig:exemption-evidence-matrix"]["title"],
            "Filled cells are typed evidence requirements computed from the live registry, never hand-authored.",
        )
    ]
    x0, y0 = 45, 150
    # Column widths are sized for 16-unit type (the legibility floor in
    # theme.MIN_FONT_PX): the widest evidence-kind word is ten characters, and
    # the widest exemption id is twenty-eight.
    label_w, col_w, row_h = 290, 98, 42
    tail_w = 150
    total_w = label_w + col_w * len(EVIDENCE_KIND_COLUMNS) + tail_w
    header_h = 72
    body.append(
        rect(x0, y0, total_w, header_h + row_h * len(rows) + 50, fill=WHITE, stroke=GRID, radius=10)
    )
    body.append(label(x0 + 16, y0 + 30, "LINE · EXEMPTION", size=16, fill=MUTED, weight="700"))
    for index, kind in enumerate(EVIDENCE_KIND_COLUMNS):
        x = x0 + label_w + index * col_w
        parts = kind.value.split("_")
        for line_index, part in enumerate(parts[:2]):
            body.append(
                label(
                    x + col_w / 2,
                    y0 + 26 + line_index * 21,
                    part,
                    size=16,
                    fill=MUTED,
                    weight="700",
                    anchor="middle",
                )
            )
    body.append(
        label(
            x0 + label_w + col_w * len(EVIDENCE_KIND_COLUMNS) + tail_w / 2,
            y0 + 26,
            "REQUIRED",
            size=16,
            fill=MUTED,
            weight="700",
            anchor="middle",
        )
    )
    body.append(
        label(
            x0 + label_w + col_w * len(EVIDENCE_KIND_COLUMNS) + tail_w / 2,
            y0 + 47,
            "· MODE",
            size=16,
            fill=MUTED,
            weight="700",
            anchor="middle",
        )
    )
    body.append(line(x0, y0 + header_h, x0 + total_w, y0 + header_h, stroke=GRID, width=1.5))
    previous_line_id = None
    for row_index, row in enumerate(rows):
        y = y0 + header_h + row_index * row_h
        if row.line_id != previous_line_id:
            body.append(rect(x0, y, total_w, row_h, fill=PALE_TEAL_BG, stroke="none", radius=0, width=0))
            body.append(label(x0 + 16, y + 18, row.line_id, size=16, fill=TEAL, weight="700"))
            previous_line_id = row.line_id
        elif row_index % 2 == 0:
            body.append(rect(x0, y, total_w, row_h, fill=TABLE_ROW_ALT, stroke="none", radius=0, width=0))
        body.append(label(x0 + 34, y + 37, row.exemption_id, size=16, fill=INK))
        for col_index, needed in enumerate(row.required):
            x = x0 + label_w + col_index * col_w
            body.append(line(x, y, x, y + row_h, stroke=GRID, width=0.8))
            if needed:
                body.append(circle(x + col_w / 2, y + row_h / 2, 8, fill=TEAL))
            else:
                body.append(circle(x + col_w / 2, y + row_h / 2, 6, fill=WHITE, stroke=GRID))
        tail_x = x0 + label_w + col_w * len(EVIDENCE_KIND_COLUMNS)
        body.append(line(tail_x, y, tail_x, y + row_h, stroke=GRID, width=1.2))
        mode_color = AMBER if row.match_mode == "all" else BLUE
        body.append(
            label(
                tail_x + 28, y + 28, str(row.required_count), size=16, fill=INK, weight="700", anchor="middle"
            )
        )
        body.append(
            rect(
                tail_x + 52,
                y + 8,
                84,
                26,
                fill=PALE_AMBER if row.match_mode == "all" else PALE_BLUE,
                stroke=mode_color,
                radius=6,
                width=1.2,
            )
        )
        body.append(
            label(
                tail_x + 94,
                y + 27,
                row.match_mode.upper(),
                size=16,
                fill=mode_color,
                weight="700",
                anchor="middle",
            )
        )
    demand_y = y0 + header_h + len(rows) * row_h
    body.append(line(x0, demand_y, x0 + total_w, demand_y, stroke=GRID, width=1.5))
    body.append(
        label(x0 + 16, demand_y + 32, "exemptions demanding each kind", size=16, fill=MUTED, weight="700")
    )
    for index, kind in enumerate(EVIDENCE_KIND_COLUMNS):
        x = x0 + label_w + index * col_w
        body.append(
            label(
                x + col_w / 2,
                demand_y + 32,
                str(demand[kind]),
                size=16,
                fill=TEAL,
                weight="700",
                anchor="middle",
            )
        )
    total_required = sum(row.required_count for row in rows)
    body.append(
        paragraph(
            x0,
            demand_y + 84,
            f"Computed from the live registry: {len(rows)} typed exemptions declare {total_required} evidence requirements across the nine intake dimensions. "
            "A filled cell is a precondition for narrowing, not proof the evidence is true; the matrix is structure, not a safety score.",
            width=110,
            size=16,
            fill=MUTED,
        )
    )
    height = demand_y + 150
    return svg_document(
        FIGURE_TEXT["fig:exemption-evidence-matrix"]["title"],
        FIGURE_TEXT["fig:exemption-evidence-matrix"]["alt"],
        "".join(body),
        height=height,
    )


def evidence_summary(records: Sequence[EvidenceRecord]) -> str:
    """Summarize how many fixture evidence records are verified."""

    verified = sum(1 for record in records if record.status is EvidenceStatus.VERIFIED)
    if not records:
        return "evidence: none recorded"
    if verified == len(records):
        return f"evidence: {verified} VERIFIED fixture records"
    return f"evidence: {verified} of {len(records)} fixture records VERIFIED"


def outcome_coverage_plate() -> str:
    """Render the exercised outcome-coverage report from the real evaluator."""

    report = run_outcome_coverage()
    outcome_accents = {
        Classification.INSUFFICIENT_INFORMATION: (MUTED, MUTED_FILL),
        Classification.OUTSIDE_SCOPE: (BLUE, PALE_BLUE),
        Classification.COMPLIANT: (TEAL, PALE_TEAL),
        Classification.REQUIRES_MODIFICATION: (AMBER, PALE_AMBER),
        Classification.NON_COMPLIANT: (RED, PALE_RED),
    }
    case_by_name = {case.name: case for case in canonical_battery()}
    body = [
        figure_header(
            FIGURE_TEXT["fig:outcome-coverage-plate"]["title"],
            f"Each case ran through the real evaluate_action at review date {report.as_of}; chips show the returned outcome.",
        )
    ]
    body.append(rect(50, 140, 1300, 118 * len(report.results) + 60, fill=WHITE, stroke=GRID, radius=12))
    body.append(label(80, 172, "BATTERY CASE · DECLARED SCOPE", size=16, fill=MUTED, weight="700"))
    body.append(
        label(1320, 172, "EVALUATOR RESULT · REASON CODES", size=16, fill=MUTED, weight="700", anchor="end")
    )
    for index, result in enumerate(report.results):
        y = 195 + index * 118
        accent, fill = outcome_accents[result.reached]
        body.append(rect(80, y, 470, 96, fill=PAPER, stroke=GRID, radius=14))
        body.append(label(102, y + 30, result.name, size=18, fill=INK, weight="700"))
        case = case_by_name[result.name]
        scope_text = ", ".join(sorted(case.action.scope))
        body.append(label(102, y + 58, f"scope: {scope_text}", size=16, fill=MUTED))
        # Derived from the case's actual context, never a name special-case: a
        # future battery change cannot make this label lie silently.
        evidence_text = evidence_summary(case.action.context.evidence)
        body.append(label(102, y + 82, evidence_text, size=16, fill=MUTED))
        body.append(line(562, y + 56, 652, y + 56, stroke=accent, width=2.5, arrow=True))
        body.append(label(603, y + 44, "evaluate_action", size=16, fill=MUTED, anchor="middle"))
        body.append(rect(665, y, 340, 96, fill=fill, stroke=accent, width=2, radius=14))
        body.append(label(687, y + 36, result.reached.value.upper(), size=16, fill=accent, weight="700"))
        body.append(
            label(
                687,
                y + 66,
                "reached = intended" if result.matched else "MISMATCH vs intent",
                size=16,
                fill=INK,
                weight="700",
            )
        )
        codes = " · ".join(code.value for code in result.reason_codes)
        body.append(paragraph(1025, y + 34, codes, width=25, size=16, leading=22, fill=MUTED))
    summary_y = 195 + len(report.results) * 118 + 20
    body.append(
        rect(
            50,
            summary_y,
            1300,
            106,
            fill=PALE_TEAL if report.complete else PALE_RED,
            stroke=TEAL if report.complete else RED,
            width=2,
            radius=12,
        )
    )
    body.append(
        label(
            80,
            summary_y + 38,
            f"{len(report.reached)} of {len(Classification)} classifications reached · every case matched its intent: {str(report.all_matched).lower()}",
            size=18,
            fill=TEAL if report.complete else RED,
            weight="700",
        )
    )
    body.append(
        paragraph(
            80,
            summary_y + 70,
            "Reachability is a property of the evaluator's control flow exercised with fixture evidence. It is not a safety measurement, an accreditation, or proof that any real engagement was reviewed.",
            width=104,
            size=16,
            fill=INK,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:outcome-coverage-plate"]["title"],
        FIGURE_TEXT["fig:outcome-coverage-plate"]["alt"],
        "".join(body),
        height=summary_y + 150,
    )


def tier_monotonicity_lattice() -> str:
    """Render the executed verdict-strictness lattice from the real evaluator."""

    report = _MONOTONICITY
    verdict_accents = {
        Classification.COMPLIANT: (TEAL, PALE_TEAL),
        Classification.REQUIRES_MODIFICATION: (AMBER, PALE_AMBER),
        Classification.NON_COMPLIANT: (RED, PALE_RED),
    }
    tier_subtitles = {
        DeploymentTier.HOSTED: "full observation + withdrawal",
        DeploymentTier.CONNECTED: "maintained update / suspend",
        DeploymentTier.AIR_GAPPED: "beyond recall",
    }
    body = [
        figure_header(
            FIGURE_TEXT["fig:tier-monotonicity-lattice"]["title"],
            f"Each chip is one executed evaluate_action run at review date {report.as_of}; strictness may only grow as retained oversight drops.",
        )
    ]
    x0, y0 = 55, 150
    label_w, col_w, tail_w, row_h, header_h = 430, 240, 150, 26, 56
    total_w = label_w + col_w * len(report.tiers) + tail_w
    body.append(
        rect(x0, y0, total_w, header_h + row_h * len(report.rows) + 8, fill=WHITE, stroke=GRID, radius=10)
    )
    body.append(label(x0 + 16, y0 + 24, "LINE · SCOPE KEYWORD", size=13, fill=MUTED, weight="700"))
    body.append(label(x0 + 16, y0 + 42, "most oversight → least oversight", size=11, fill=MUTED))
    for index, tier in enumerate(report.tiers):
        x = x0 + label_w + index * col_w
        body.append(
            label(
                x + col_w / 2,
                y0 + 24,
                tier.value.replace("_", "-").upper(),
                size=13,
                fill=INK,
                weight="700",
                anchor="middle",
            )
        )
        body.append(label(x + col_w / 2, y0 + 42, tier_subtitles[tier], size=11, fill=MUTED, anchor="middle"))
    body.append(
        label(
            x0 + label_w + col_w * len(report.tiers) + tail_w / 2,
            y0 + 24,
            "MONOTONE",
            size=11,
            fill=MUTED,
            weight="700",
            anchor="middle",
        )
    )
    body.append(line(x0, y0 + header_h, x0 + total_w, y0 + header_h, stroke=GRID, width=1.5))
    previous_line_id = None
    for row_index, row in enumerate(report.rows):
        y = y0 + header_h + row_index * row_h
        if row.line_id != previous_line_id:
            body.append(rect(x0, y, total_w, row_h, fill=PALE_TEAL_BG, stroke="none", radius=0, width=0))
            body.append(label(x0 + 16, y + 18, row.line_id, size=11, fill=TEAL, weight="700"))
            previous_line_id = row.line_id
        elif row_index % 2 == 0:
            body.append(rect(x0, y, total_w, row_h, fill=TABLE_ROW_ALT, stroke="none", radius=0, width=0))
        body.append(label(x0 + 250, y + 18, row.keyword, size=16, fill=INK))
        for col_index, verdict in enumerate(row.verdicts):
            x = x0 + label_w + col_index * col_w
            body.append(line(x, y, x, y + row_h, stroke=GRID, width=0.8))
            accent, fill = verdict_accents[verdict]
            body.append(
                rect(x + 18, y + 4, col_w - 36, row_h - 8, fill=fill, stroke=accent, radius=6, width=1.2)
            )
            body.append(
                label(
                    x + col_w / 2,
                    y + 18,
                    verdict.value.replace("_", " ").upper(),
                    size=10,
                    fill=accent,
                    weight="700",
                    anchor="middle",
                )
            )
        tail_x = x0 + label_w + col_w * len(report.tiers)
        body.append(line(tail_x, y, tail_x, y + row_h, stroke=GRID, width=1.2))
        body.append(
            label(
                tail_x + tail_w / 2,
                y + 19,
                "✓" if row.monotone else "✗",
                size=13,
                fill=TEAL if row.monotone else RED,
                weight="700",
                anchor="middle",
            )
        )
    summary_y = y0 + header_h + len(report.rows) * row_h + 28
    ok = report.monotone
    body.append(
        rect(
            x0,
            summary_y,
            total_w,
            74,
            fill=PALE_TEAL if ok else PALE_RED,
            stroke=TEAL if ok else RED,
            width=2,
            radius=10,
        )
    )
    body.append(
        label(
            x0 + 24,
            summary_y + 32,
            f"{report.keyword_count} line/keyword slots ({report.distinct_keyword_count} distinct tokens) × {len(report.tiers)} tiers = {report.evaluation_count} executed evaluate_action runs · inversions: {report.inversion_count}",
            size=17,
            fill=TEAL if ok else RED,
            weight="700",
        )
    )
    body.append(
        label(
            x0 + 24,
            summary_y + 58,
            "Positive control lives in the regression suite: the identical sweep flags the replicated pre-fix defect, so this green is falsifiable.",
            size=13,
            fill=INK,
        )
    )
    body.append(
        paragraph(
            x0,
            summary_y + 106,
            "Monotone strictness is a consistency property of the local decision procedure run on fixture evidence. It is not a safety score, an accreditation, or evidence that any real engagement was reviewed.",
            width=125,
            size=14,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:tier-monotonicity-lattice"]["title"],
        FIGURE_TEXT["fig:tier-monotonicity-lattice"]["alt"],
        "".join(body),
        height=summary_y + 150,
    )


#: Severity accents. Grade is repeated as text in every chip, so the colour is
#: an accent and never the encoding — the plate reads unchanged in greyscale.
_SEVERITY_ACCENTS = {
    "canary": (RED, PALE_RED),
    "absolute": (AMBER, PALE_AMBER),
    "strong": (BLUE, PALE_BLUE),
}

#: The four structural counts profiled per line, in drawing order. Each entry
#: is (column heading, second heading line, accessor).
_COMPOSITION_METRICS = (
    ("SCOPE", "tokens", lambda summary: summary.scope_size),
    ("CARVE-OUTS", "narrative", lambda summary: summary.carve_out_count),
    ("EXEMPTIONS", "typed", lambda summary: summary.exemption_count),
    ("EVIDENCE", "kinds used", lambda summary: len(summary.evidence_kinds_used)),
)


def registry_composition_profile(lines: tuple[RedLine, ...] = PERSONAL_RED_LINES) -> str:
    """Render the per-line structural profile of the live registry.

    Every number is read from
    :func:`red_line.analysis.registry_metrics.line_summaries` and the two
    distribution views at build time; nothing is written into the generator.
    The bottom band renders ``len(unevidenced_exemptions())`` so a zero is a
    visible result rather than an absent panel.

    ``lines`` defaults to the live registry, which is how ``GENERATORS`` calls
    it. The parameter exists so a test can plant an evidence-free exemption and
    watch the band change — a zero nobody can make non-zero is decoration.
    """

    summaries = line_summaries(lines)
    severities = severity_distribution(lines)
    floors = tier_floor_distribution(lines)
    free_passes = unevidenced_exemptions(lines)
    # One shared scale across all four metric columns, so a bar's length means
    # the same thing everywhere on the plate. Derived from the data, not fixed.
    scale = max(accessor(summary) for _, _, accessor in _COMPOSITION_METRICS for summary in summaries)

    body = [
        figure_header(
            FIGURE_TEXT["fig:registry-composition-profile"]["title"],
            "Per-line structural counts read from the live registry; bars share one scale and every bar carries its number.",
        )
    ]
    x0, y0 = 50, 150
    label_w, severity_w, tier_w, metric_w = 300, 152, 176, 152
    bar_w = 96
    total_w = label_w + severity_w + tier_w + metric_w * len(_COMPOSITION_METRICS)
    header_h, row_h = 84, 60
    grid_h = header_h + row_h * len(summaries) + 10
    body.append(rect(x0, y0, total_w, grid_h, fill=WHITE, stroke=GRID, radius=10))
    body.append(label(x0 + 16, y0 + 30, "RED LINE", size=16, fill=MUTED, weight="700"))
    body.append(label(x0 + 16, y0 + 54, "sorted by id", size=16, fill=MUTED))
    body.append(label(x0 + label_w + 16, y0 + 30, "SEVERITY", size=16, fill=MUTED, weight="700"))
    body.append(label(x0 + label_w + severity_w + 16, y0 + 30, "TIER FLOOR", size=16, fill=MUTED, weight="700"))
    metric_x0 = x0 + label_w + severity_w + tier_w
    for index, (heading, subheading, _) in enumerate(_COMPOSITION_METRICS):
        x = metric_x0 + index * metric_w
        body.append(label(x + 12, y0 + 30, heading, size=16, fill=MUTED, weight="700"))
        body.append(label(x + 12, y0 + 54, subheading, size=16, fill=MUTED))
    body.append(line(x0, y0 + header_h, x0 + total_w, y0 + header_h, stroke=GRID, width=1.5))

    for row_index, summary in enumerate(summaries):
        y = y0 + header_h + row_index * row_h
        if row_index % 2 == 0:
            body.append(rect(x0, y, total_w, row_h, fill=TABLE_ROW_ALT, stroke="none", radius=0, width=0))
        body.append(label(x0 + 16, y + 38, summary.line_id, size=16, fill=TEAL, weight="700"))
        accent, fill = _SEVERITY_ACCENTS[summary.severity]
        body.append(
            rect(x0 + label_w + 12, y + 14, severity_w - 28, 32, fill=fill, stroke=accent, radius=8, width=1.5)
        )
        body.append(
            label(
                x0 + label_w + 12 + (severity_w - 28) / 2,
                y + 36,
                summary.severity.upper(),
                size=16,
                fill=accent,
                weight="700",
                anchor="middle",
            )
        )
        tier_x = x0 + label_w + severity_w
        body.append(rect(tier_x + 12, y + 14, tier_w - 28, 32, fill=PAPER, stroke=MUTED, radius=8, width=1.5))
        body.append(
            label(
                tier_x + 12 + (tier_w - 28) / 2,
                y + 36,
                summary.max_tier.replace("_", "-").upper(),
                size=16,
                fill=INK,
                weight="700",
                anchor="middle",
            )
        )
        for index, (_, _, accessor) in enumerate(_COMPOSITION_METRICS):
            value = accessor(summary)
            x = metric_x0 + index * metric_w
            body.append(line(x, y, x, y + row_h, stroke=GRID, width=0.8))
            body.append(rect(x + 12, y + 22, bar_w, 16, fill=WHITE, stroke=GRID, radius=3, width=1))
            body.append(
                rect(x + 12, y + 22, bar_w * value / scale, 16, fill=TEAL, stroke=TEAL, radius=3, width=1)
            )
            body.append(label(x + 12 + bar_w + 10, y + 38, str(value), size=16, fill=INK, weight="700"))

    strip_y = y0 + grid_h + 22
    body.append(rect(x0, strip_y, total_w, 92, fill=WHITE, stroke=GRID, radius=10))
    severity_text = " · ".join(
        f"{severity.value.upper()} {count}" for severity, count in severities.items()
    )
    floor_text = " · ".join(
        f"{tier.value.replace('_', '-').upper()} {count}" for tier, count in floors.items()
    )
    body.append(label(x0 + 20, strip_y + 34, f"severity split — {severity_text}", size=16, fill=INK))
    body.append(label(x0 + 20, strip_y + 68, f"tier-floor split — {floor_text}", size=16, fill=INK))

    floor_y = strip_y + 108
    clean = not free_passes
    body.append(
        rect(
            x0,
            floor_y,
            total_w,
            96,
            fill=PALE_TEAL if clean else PALE_RED,
            stroke=TEAL if clean else RED,
            width=2,
            radius=10,
        )
    )
    body.append(
        label(
            x0 + 24,
            floor_y + 40,
            f"EXEMPTIONS REQUIRING NO EVIDENCE AT ALL: {len(free_passes)}",
            size=20,
            fill=TEAL if clean else RED,
            weight="700",
        )
    )
    body.append(
        label(
            x0 + 24,
            floor_y + 72,
            (
                "every typed exemption demands at least one VERIFIED record"
                if clean
                else "free pass: " + ", ".join(row.exemption_id for row in free_passes)
            ),
            size=16,
            fill=INK,
        )
    )
    body.append(
        paragraph(
            x0,
            floor_y + 140,
            "These are structural counts over the author's own registry. A longer bar means a wider declared "
            "surface, not a stronger commitment, a safer practice, or a basis for comparing one author's "
            "boundary with another's.",
            width=118,
            size=16,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:registry-composition-profile"]["title"],
        FIGURE_TEXT["fig:registry-composition-profile"]["alt"],
        "".join(body),
        height=floor_y + 236,
    )


def _stacked_line_id(line_id: str) -> tuple[str, ...]:
    """Split a hyphenated line id into stacked header lines, hyphens kept."""

    parts = line_id.split("-")
    return tuple(part + "-" if index < len(parts) - 1 else part for index, part in enumerate(parts))


def scope_vocabulary_collisions(lines: tuple[RedLine, ...] = PERSONAL_RED_LINES) -> str:
    """Render the token × line presence grid for the whole declared vocabulary.

    Derived from
    :func:`red_line.analysis.registry_metrics.scope_token_membership`, with the
    executed verdict for each shared token read out of the same monotonicity
    sweep the lattice plate uses, so the consequence stated in the footer is a
    result the evaluator returned rather than a claim about it.

    ``lines`` defaults to the live registry. For the default the cached sweep is
    reused so the build does not evaluate the lattice twice; any other registry
    is swept on the spot, which is what lets a test plant a shared token and
    watch the grid and footer follow.
    """

    membership = scope_token_membership(lines)
    line_ids = sorted({line_id for _, owners in membership for line_id in owners})
    shared = tuple((token, owners) for token, owners in membership if len(owners) > 1)
    sweep = _MONOTONICITY if lines is PERSONAL_RED_LINES else run_monotonicity_sweep(lines)
    verdict_by_keyword = {row.keyword: row.verdicts[0] for row in sweep.rows}

    body = [
        figure_header(
            FIGURE_TEXT["fig:scope-vocabulary-collisions"]["title"],
            "Every canonical scope token in the registry against every line that declares it; the count column repeats the row in text.",
        )
    ]
    x0, y0 = 50, 150
    token_w, line_w, tail_w = 276, 118, 190
    total_w = token_w + line_w * len(line_ids) + tail_w
    header_h, row_h = 118, 32
    grid_h = header_h + row_h * len(membership) + 10
    body.append(rect(x0, y0, total_w, grid_h, fill=WHITE, stroke=GRID, radius=10))
    body.append(label(x0 + 16, y0 + 30, "SCOPE TOKEN", size=16, fill=MUTED, weight="700"))
    body.append(label(x0 + 16, y0 + 54, "sorted", size=16, fill=MUTED))
    for index, line_id in enumerate(line_ids):
        x = x0 + token_w + index * line_w
        for part_index, part in enumerate(_stacked_line_id(line_id)):
            body.append(
                label(
                    x + line_w / 2,
                    y0 + 30 + part_index * 21,
                    part,
                    size=16,
                    fill=INK,
                    weight="700",
                    anchor="middle",
                )
            )
    tail_x = x0 + token_w + line_w * len(line_ids)
    body.append(label(tail_x + tail_w / 2, y0 + 30, "LINES", size=16, fill=MUTED, weight="700", anchor="middle"))
    body.append(
        label(tail_x + tail_w / 2, y0 + 54, "declaring it", size=16, fill=MUTED, anchor="middle")
    )
    body.append(line(x0, y0 + header_h, x0 + total_w, y0 + header_h, stroke=GRID, width=1.5))

    for row_index, (token, owners) in enumerate(membership):
        y = y0 + header_h + row_index * row_h
        collision = len(owners) > 1
        if collision:
            body.append(rect(x0, y, total_w, row_h, fill=PALE_AMBER, stroke="none", radius=0, width=0))
        elif row_index % 2 == 0:
            body.append(rect(x0, y, total_w, row_h, fill=TABLE_ROW_ALT, stroke="none", radius=0, width=0))
        body.append(
            label(x0 + 16, y + 22, token, size=16, fill=AMBER if collision else INK, weight="700" if collision else "400")
        )
        for index, line_id in enumerate(line_ids):
            x = x0 + token_w + index * line_w
            body.append(line(x, y, x, y + row_h, stroke=GRID, width=0.8))
            if line_id in owners:
                body.append(circle(x + line_w / 2, y + row_h / 2, 8, fill=AMBER if collision else TEAL))
            else:
                body.append(circle(x + line_w / 2, y + row_h / 2, 6, fill=WHITE, stroke=GRID))
        body.append(line(tail_x, y, tail_x, y + row_h, stroke=GRID, width=1.2))
        body.append(
            label(
                tail_x + 34,
                y + 22,
                str(len(owners)),
                size=16,
                fill=AMBER if collision else INK,
                weight="700",
                anchor="middle",
            )
        )
        if collision:
            body.append(
                label(tail_x + 62, y + 22, "SHARED", size=16, fill=AMBER, weight="700")
            )

    strip_y = y0 + grid_h + 22
    strip_h = 54 + 30 * len(shared)
    body.append(rect(x0, strip_y, total_w, strip_h, fill=WHITE, stroke=GRID, radius=10))
    single = len(membership) - len(shared)
    body.append(
        label(
            x0 + 20,
            strip_y + 34,
            f"{len(membership)} distinct tokens · {single} declared by exactly one line · {len(shared)} shared",
            size=16,
            fill=INK,
            weight="700",
        )
    )
    for index, (token, owners) in enumerate(shared):
        verdict = verdict_by_keyword[token].value.replace("_", " ").upper()
        body.append(
            label(
                x0 + 20,
                strip_y + 66 + index * 30,
                f"{token} → {' + '.join(owners)} · executed verdict at hosted: {verdict}",
                size=16,
                fill=AMBER,
            )
        )
    body.append(
        paragraph(
            x0,
            strip_y + strip_h + 46,
            "A shared token implicates both of its lines at once, so one line's verified exemption cannot clear "
            "it — the other line is still evaluated on its own terms. This is the registry's declared vocabulary, "
            "not a map of what an action actually does: matching stays lexical over the declared scope and is not "
            "a semantic safety classifier.",
            width=118,
            size=16,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:scope-vocabulary-collisions"]["title"],
        FIGURE_TEXT["fig:scope-vocabulary-collisions"]["alt"],
        "".join(body),
        height=strip_y + strip_h + 156,
    )


#: Abbreviated verdict wording used inside grid cells, where the full enum
#: spelling would not fit at the 16-unit legibility floor. The unabbreviated
#: name appears in each plate's own summary band, so nothing depends on the
#: reader decoding the short form alone.
_VERDICT_SHORT = {
    Classification.INSUFFICIENT_INFORMATION: "INSUFF. INFO",
    Classification.OUTSIDE_SCOPE: "OUTSIDE SCOPE",
    Classification.COMPLIANT: "COMPLIANT",
    Classification.REQUIRES_MODIFICATION: "REQ. MODIFICATION",
    Classification.NON_COMPLIANT: "NON-COMPLIANT",
}

#: Accent and fill per verdict. The verdict is spelled out in every chip, so
#: colour stays an accent and the plates read unchanged in greyscale.
_VERDICT_ACCENTS = {
    Classification.INSUFFICIENT_INFORMATION: (MUTED, MUTED_FILL),
    Classification.OUTSIDE_SCOPE: (BLUE, PALE_BLUE),
    Classification.COMPLIANT: (TEAL, PALE_TEAL),
    Classification.REQUIRES_MODIFICATION: (AMBER, PALE_AMBER),
    Classification.NON_COMPLIANT: (RED, PALE_RED),
}

#: Reason codes that name *which* kind of defect stopped the intake. A cell
#: prints the ones its perturbation raised, so the five columns stay
#: distinguishable by text rather than by position alone.
_SIGNATURE_CODES = ("missing_evidence", "unresolved_evidence", "stale_evidence")


def blocking_signature(codes: Sequence[object]) -> str:
    """Render one cell's blocking signature from its returned reason codes."""

    present = [
        getattr(code, "value", "") for code in codes if getattr(code, "value", "") in _SIGNATURE_CODES
    ]
    return " + ".join(name.replace("_evidence", "") for name in present) or "no evidence code"


def evidence_gate_sensitivity(lines: tuple[RedLine, ...] = PERSONAL_RED_LINES) -> str:
    """Render the executed single-dimension evidence perturbation sweep.

    Every cell is one real ``evaluate_action`` run reported by
    :func:`red_line.analysis.evidence_sensitivity.run_evidence_sensitivity`.
    ``lines`` defaults to the live registry; the parameter exists so a test can
    pass a mutated registry and watch the plate follow it, because a grid nobody
    can make disagree is decoration.
    """

    report = run_evidence_sensitivity(lines)
    body = [
        figure_header(
            FIGURE_TEXT["fig:evidence-gate-sensitivity"]["title"],
            f"One dimension degraded per cell against an otherwise unchanged {report.baseline.value} baseline at review date {report.as_of}.",
        )
    ]
    x0, y0 = 30, 150
    label_w, col_w, tail_w, row_h, header_h = 260, 190, 130, 56, 74
    total_w = label_w + col_w * len(report.perturbations) + tail_w

    baseline_accent, baseline_fill = _VERDICT_ACCENTS[report.baseline]
    body.append(rect(x0, y0, total_w, 60, fill=baseline_fill, stroke=baseline_accent, width=2, radius=10))
    body.append(
        label(
            x0 + 20,
            y0 + 38,
            f"BASELINE  scope {' + '.join(report.scope)}  ·  tier {report.tier.value.upper()}"
            f"  ·  nine VERIFIED records  →  {report.baseline.value.upper()}",
            size=17,
            fill=baseline_accent,
            weight="700",
        )
    )

    grid_y = y0 + 84
    grid_h = header_h + row_h * len(EVIDENCE_KIND_COLUMNS) + 8
    body.append(rect(x0, grid_y, total_w, grid_h, fill=WHITE, stroke=GRID, radius=10))
    body.append(label(x0 + 16, grid_y + 28, "DEGRADED", size=16, fill=MUTED, weight="700"))
    body.append(label(x0 + 16, grid_y + 52, "DIMENSION", size=16, fill=MUTED, weight="700"))
    for index, perturbation in enumerate(report.perturbations):
        x = x0 + label_w + index * col_w
        body.append(
            label(
                x + col_w / 2,
                grid_y + 28,
                perturbation.replace("_", "-").upper(),
                size=16,
                fill=INK,
                weight="700",
                anchor="middle",
            )
        )
    tail_center = x0 + label_w + col_w * len(report.perturbations) + tail_w / 2
    body.append(label(tail_center, grid_y + 28, "BLAMED", size=16, fill=MUTED, weight="700", anchor="middle"))
    body.append(
        label(tail_center, grid_y + 52, "ONLY IT", size=16, fill=MUTED, weight="700", anchor="middle")
    )
    body.append(line(x0, grid_y + header_h, x0 + total_w, grid_y + header_h, stroke=GRID, width=1.5))

    for row_index, kind in enumerate(EVIDENCE_KIND_COLUMNS):
        y = grid_y + header_h + row_index * row_h
        if row_index % 2 == 0:
            body.append(rect(x0, y, total_w, row_h, fill=TABLE_ROW_ALT, stroke="none", radius=0, width=0))
        body.append(label(x0 + 16, y + 34, kind.value, size=16, fill=TEAL, weight="700"))
        localized = 0
        for col_index, perturbation in enumerate(report.perturbations):
            cell = report.cell(kind, perturbation)
            localized += 1 if cell.localized else 0
            x = x0 + label_w + col_index * col_w
            accent, fill = _VERDICT_ACCENTS[cell.reached]
            body.append(line(x, y, x, y + row_h, stroke=GRID, width=0.8))
            body.append(
                rect(x + 8, y + 6, col_w - 16, row_h - 12, fill=fill, stroke=accent, radius=8, width=1.2)
            )
            body.append(
                label(
                    x + col_w / 2,
                    y + 26,
                    _VERDICT_SHORT[cell.reached],
                    size=16,
                    fill=accent,
                    weight="700",
                    anchor="middle",
                )
            )
            body.append(
                label(
                    x + col_w / 2,
                    y + 46,
                    blocking_signature(cell.reason_codes),
                    size=16,
                    fill=INK,
                    anchor="middle",
                )
            )
        tail_x = x0 + label_w + col_w * len(report.perturbations)
        body.append(line(tail_x, y, tail_x, y + row_h, stroke=GRID, width=1.2))
        complete = localized == len(report.perturbations)
        body.append(
            label(
                tail_x + tail_w / 2,
                y + 34,
                f"{'YES' if complete else 'NO'} {localized}/{len(report.perturbations)}",
                size=16,
                fill=TEAL if complete else RED,
                weight="700",
                anchor="middle",
            )
        )

    summary_y = grid_y + grid_h + 24
    ok = report.conjunctive
    body.append(
        rect(
            x0,
            summary_y,
            total_w,
            80,
            fill=PALE_TEAL if ok else PALE_RED,
            stroke=TEAL if ok else RED,
            width=2,
            radius=10,
        )
    )
    body.append(
        label(
            x0 + 22,
            summary_y + 34,
            f"{report.blocked_count} of {report.evaluation_count} perturbations withdrew the "
            f"{report.baseline.value} result · {report.localized_count} of {report.evaluation_count} "
            "named only the degraded dimension",
            size=17,
            fill=TEAL if ok else RED,
            weight="700",
        )
    )
    body.append(
        label(
            x0 + 22,
            summary_y + 62,
            "Every stop is INSUFFICIENT_INFORMATION — an information gap, not a finding against the work.",
            size=16,
            fill=INK,
        )
    )
    body.append(
        paragraph(
            x0,
            summary_y + 116,
            "The sweep shows that the local gate is conjunctive over its nine declared dimensions and that it "
            "names the field it stopped on. It does not show that a VERIFIED record is true, that these nine "
            "dimensions are the right ones, or that any real intake was reviewed.",
            width=124,
            size=16,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:evidence-gate-sensitivity"]["title"],
        FIGURE_TEXT["fig:evidence-gate-sensitivity"]["alt"],
        "".join(body),
        height=summary_y + 210,
    )


def exemption_trigger_semantics(lines: tuple[RedLine, ...] = PERSONAL_RED_LINES) -> str:
    """Render the executed ANY/ALL trigger probe for every typed exemption.

    Both probe columns are real results from
    :func:`red_line.analysis.trigger_semantics.run_trigger_semantics`: the left
    reports what the evaluator returned when the action declared one trigger
    token beside the line's anchor, the right when it declared all of them.
    ``lines`` defaults to the live registry so a test can pass a mutated one and
    require the plate to change with it.
    """

    report = run_trigger_semantics(lines)
    body = [
        figure_header(
            FIGURE_TEXT["fig:exemption-trigger-semantics"]["title"],
            f"Each row runs one exemption's trigger tokens singly and then together through the real evaluator at review date {report.as_of}.",
        )
    ]
    x0, y0 = 32, 150
    label_w, mode_w, probe_w, row_h, header_h = 420, 108, 400, 44, 74
    total_w = label_w + mode_w + probe_w * 2

    body.append(
        rect(x0, y0, total_w, header_h + row_h * len(report.rows) + 8, fill=WHITE, stroke=GRID, radius=10)
    )
    body.append(label(x0 + 16, y0 + 28, "RED LINE · TYPED EXEMPTION", size=16, fill=MUTED, weight="700"))
    body.append(label(x0 + 16, y0 + 52, "anchor token in parentheses", size=16, fill=MUTED))
    body.append(
        label(x0 + label_w + mode_w / 2, y0 + 28, "MODE", size=16, fill=MUTED, weight="700", anchor="middle")
    )
    for index, heading in enumerate(("ONE TRIGGER TOKEN", "ALL TRIGGER TOKENS")):
        x = x0 + label_w + mode_w + index * probe_w
        body.append(
            label(x + probe_w / 2, y0 + 28, heading, size=16, fill=INK, weight="700", anchor="middle")
        )
        body.append(
            label(
                x + probe_w / 2, y0 + 52, "declared beside the anchor", size=16, fill=MUTED, anchor="middle"
            )
        )
    body.append(line(x0, y0 + header_h, x0 + total_w, y0 + header_h, stroke=GRID, width=1.5))

    previous_line_id = None
    for row_index, row in enumerate(report.rows):
        y = y0 + header_h + row_index * row_h
        if row.line_id != previous_line_id:
            body.append(rect(x0, y, total_w, row_h, fill=PALE_TEAL_BG, stroke="none", radius=0, width=0))
            body.append(
                label(
                    x0 + 16,
                    y + 18,
                    f"{row.line_id}  ({row.anchor}{' · shared' if row.anchor_shared else ''})",
                    size=16,
                    fill=TEAL,
                    weight="700",
                )
            )
            previous_line_id = row.line_id
        elif row_index % 2 == 0:
            body.append(rect(x0, y, total_w, row_h, fill=TABLE_ROW_ALT, stroke="none", radius=0, width=0))
        body.append(label(x0 + 34, y + 38, row.exemption_id, size=16, fill=INK))

        mode_x = x0 + label_w
        body.append(line(mode_x, y, mode_x, y + row_h, stroke=GRID, width=1.2))
        mode_all = row.match_mode == "all"
        mode_color = AMBER if mode_all else BLUE
        body.append(
            rect(
                mode_x + 10,
                y + 9,
                mode_w - 20,
                26,
                fill=PALE_AMBER if mode_all else PALE_BLUE,
                stroke=mode_color,
                radius=6,
                width=1.2,
            )
        )
        body.append(
            label(
                mode_x + mode_w / 2,
                y + 28,
                row.match_mode.upper(),
                size=16,
                fill=mode_color,
                weight="700",
                anchor="middle",
            )
        )

        columns = (
            (f"{row.single_match_count} of {len(row.trigger_scope)} match", {p.reached for p in row.singles}),
            (
                f"all {len(row.trigger_scope)} {'match' if row.full.matched else 'unmatched'}",
                {row.full.reached},
            ),
        )
        for index, (matched_text, verdicts) in enumerate(columns):
            x = x0 + label_w + mode_w + index * probe_w
            body.append(line(x, y, x, y + row_h, stroke=GRID, width=0.8))
            verdict = sorted(verdicts, key=lambda item: item.value)[0]
            accent, fill = _VERDICT_ACCENTS[verdict]
            mixed = len(verdicts) > 1
            body.append(
                rect(x + 10, y + 6, probe_w - 20, row_h - 12, fill=fill, stroke=accent, radius=8, width=1.2)
            )
            body.append(label(x + 26, y + 29, matched_text, size=16, fill=INK, weight="700"))
            body.append(
                label(
                    x + probe_w - 26,
                    y + 29,
                    ("MIXED · " if mixed else "") + _VERDICT_SHORT[verdict],
                    size=16,
                    fill=accent,
                    weight="700",
                    anchor="end",
                )
            )

    summary_y = y0 + header_h + row_h * len(report.rows) + 32
    ok = report.consistent
    body.append(
        rect(
            x0,
            summary_y,
            total_w,
            80,
            fill=PALE_TEAL if ok else PALE_RED,
            stroke=TEAL if ok else RED,
            width=2,
            radius=10,
        )
    )
    body.append(
        label(
            x0 + 22,
            summary_y + 34,
            f"{len(report.rows)} typed exemptions · {report.any_mode_count} ANY · {report.all_mode_count} ALL"
            f" · {report.evaluation_count} executed evaluate_action runs · rows behaving as their mode"
            f" requires: {sum(1 for row in report.rows if row.mode_consistent)} of {len(report.rows)}",
            size=17,
            fill=TEAL if ok else RED,
            weight="700",
        )
    )
    body.append(
        label(
            x0 + 22,
            summary_y + 62,
            "An ALL-mode exemption cannot be reached by naming one convenient word; an ANY-mode one can.",
            size=16,
            fill=INK,
        )
    )
    body.append(
        paragraph(
            x0,
            summary_y + 116,
            "Every probe carries a fully evidenced fixture intake, so the only variable is which trigger tokens "
            "the action declares. A matched trigger is a declaration and never proof: the exemption still cannot "
            "narrow its line until the typed evidence it demands is VERIFIED.",
            width=124,
            size=16,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:exemption-trigger-semantics"]["title"],
        FIGURE_TEXT["fig:exemption-trigger-semantics"]["alt"],
        "".join(body),
        height=summary_y + 210,
    )
