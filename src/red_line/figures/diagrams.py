"""Schematic figure generators."""

from __future__ import annotations

from red_line.model.enums import DeploymentTier
from red_line.registry.lines import PERSONAL_RED_LINES

from .svg import circle, figure_header, label, line, paragraph, rect, svg_document
from .text import FIGURE_TEXT
from .theme import (
    AMBER, BLUE, GRID, INK,
    MUTED, MUTED_FILL, MUTED_FILL_ALT,
    PALE_AMBER, PALE_AMBER_BG, PALE_BLUE, PALE_RED, PALE_TEAL,
    PALE_TEAL_BG, PAPER, RED, TABLE_HEADER, TABLE_ROW_ALT,
    TABLE_ROW_ALT2, TEAL, TEAL_STROKE, WHITE,
)


def governance_architecture() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:governance-architecture"]["title"],
            "Schematic of the inspectable artifact; arrows indicate records and review flow, not enforcement.",
        )
    ]
    body.append(rect(42, 130, 1010, 540, fill=PALE_TEAL_BG, stroke=TEAL_STROKE, dash=True))
    body.append(label(70, 160, "LOCAL AUTHOR BOUNDARY", size=13, fill=TEAL, weight="700"))
    boxes = [
        (
            80,
            215,
            255,
            150,
            "1  Beacon",
            f"{len(PERSONAL_RED_LINES)} red lines",
            "src/red_line/registry",
            PALE_TEAL,
        ),
        (395, 215, 255, 150, "2  Intake", "context · evidence records", "ActionContext", PALE_BLUE),
        (
            710,
            215,
            255,
            150,
            "3  Evidence gate",
            "complete · verified · canonical",
            "evaluate_action",
            PALE_AMBER,
        ),
        (235, 460, 255, 150, "4  Policy", "coverage · exemption · tier", "RedLine + Exemption", PALE_AMBER),
        (550, 460, 255, 150, "5  Transparency", "tally · authorizations", "transparency_report", PALE_TEAL),
        (865, 460, 255, 150, "6  Canary", "hash · prior · freshness", "verify_canary", PALE_RED),
    ]
    for x, y, w, h, title, sub, code, fill in boxes:
        body.append(rect(x, y, w, h, fill=fill, stroke=GRID))
        body.append(label(x + 20, y + 34, title, size=20, weight="700"))
        body.append(paragraph(x + 20, y + 70, sub, width=25, size=16, fill=INK))
        body.append(label(x + 20, y + 123, code, size=13, fill=MUTED))
    body.extend(
        [
            line(335, 290, 390, 290, stroke=MUTED, arrow=True),
            line(650, 290, 705, 290, stroke=MUTED, arrow=True),
            line(837, 365, 365, 455, stroke=MUTED, arrow=True),
            line(492, 535, 545, 535, stroke=MUTED, arrow=True),
            line(807, 535, 860, 535, stroke=MUTED, arrow=True),
        ]
    )
    body.append(rect(1090, 210, 260, 300, fill=PALE_AMBER_BG, stroke=AMBER, dash=True))
    body.append(label(1115, 245, "INDEPENDENT WITNESS", size=14, fill=AMBER, weight="700"))
    body.append(
        paragraph(
            1115,
            282,
            "Holds the prior statement outside the author's write boundary.",
            width=22,
            size=17,
            fill=INK,
            leading=25,
        )
    )
    body.append(line(1120, 430, 1035, 540, stroke=AMBER, width=2.5, dash=True, arrow=True))
    body.append(label(1115, 470, "Required for", size=14, fill=MUTED))
    body.append(label(1115, 493, "tamper evidence", size=16, fill=INK, weight="700"))
    body.append(
        paragraph(
            70,
            700,
            "The artifact records decisions and drift; it does not force execution or create an external auditor.",
            width=115,
            size=15,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:governance-architecture"]["title"],
        FIGURE_TEXT["fig:governance-architecture"]["alt"],
        "".join(body),
        height=760,
    )


def tier_ladder() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:oversight-tier-ladder"]["title"],
            "Filled cells mark an oversight floor; blank cells are release boundaries, not a safety score.",
        )
    ]
    x0, y0 = 60, 150
    row_h, title_w, col_w = 57, 445, 260
    tiers = [
        (DeploymentTier.HOSTED, "HOSTED", "full observation + withdrawal", TEAL),
        (DeploymentTier.CONNECTED, "CONNECTED", "maintained update / suspend", BLUE),
        (DeploymentTier.AIR_GAPPED, "AIR-GAPPED", "beyond recall", AMBER),
    ]
    ordered = sorted(PERSONAL_RED_LINES, key=lambda r: r.id)
    # Table height is derived from the live row count, so adopting a line grows
    # the frame instead of letting the last row spill past the border.
    table_h = 82 + row_h * len(ordered)
    body.append(rect(x0, y0, title_w + col_w * 3, table_h, fill=WHITE, stroke=GRID, radius=10))
    body.append(label(x0 + 18, y0 + 34, "Registry line", size=16, fill=MUTED, weight="700"))
    for i, (_, name, sub, color) in enumerate(tiers):
        x = x0 + title_w + i * col_w
        body.append(rect(x, y0, col_w, 82, fill=TABLE_HEADER, stroke=GRID, radius=0))
        body.append(label(x + 18, y0 + 33, name, size=18, fill=color, weight="700"))
        body.append(label(x + 18, y0 + 58, sub, size=16, fill=MUTED))
    rank = {DeploymentTier.HOSTED: 2, DeploymentTier.CONNECTED: 1, DeploymentTier.AIR_GAPPED: 0}
    for idx, red_line in enumerate(ordered):
        y = y0 + 82 + idx * row_h
        if idx % 2 == 0:
            body.append(
                rect(x0, y, title_w + col_w * 3, row_h, fill=TABLE_ROW_ALT, stroke="none", radius=0, width=0)
            )
        title = red_line.title + ("  [CANARY]" if red_line.severity.value == "canary" else "")
        body.append(
            paragraph(
                x0 + 18,
                y + 23,
                title,
                width=43,
                size=14,
                leading=17,
                fill=INK,
                weight="700" if red_line.severity.value == "canary" else "400",
            )
        )
        for i, (tier, _, _, color) in enumerate(tiers):
            x = x0 + title_w + i * col_w
            body.append(line(x, y, x, y + row_h, stroke=GRID, width=1))
            allowed = rank[tier] >= rank[red_line.max_tier]
            if allowed:
                body.append(circle(x + col_w / 2, y + row_h / 2, 12, fill=color))
                body.append(
                    label(
                        x + col_w / 2,
                        y + row_h / 2 + 5,
                        "✓",
                        size=16,
                        fill=PAPER,
                        weight="700",
                        anchor="middle",
                    )
                )
            else:
                body.append(circle(x + col_w / 2, y + row_h / 2, 11, fill=WHITE, stroke=GRID))
                body.append(
                    label(x + col_w / 2, y + row_h / 2 + 5, "—", size=16, fill=MUTED, anchor="middle")
                )
        body.append(
            label(
                x0 + title_w + col_w * 3 - 18,
                y + 35,
                red_line.max_tier.value.replace("_", " "),
                size=16,
                fill=MUTED,
                anchor="end",
            )
        )
    body.append(
        label(
            x0 + title_w + col_w * 3 - 18,
            y0 + table_h + 26,
            "floor",
            size=16,
            fill=MUTED,
            anchor="end",
        )
    )
    body.append(
        paragraph(
            60,
            y0 + table_h + 76,
            "Thresholds are derived from RedLine.max_tier; the evaluator still checks scope, carve-outs, and hard blocks.",
            width=110,
            size=16,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:oversight-tier-ladder"]["title"],
        FIGURE_TEXT["fig:oversight-tier-ladder"]["alt"],
        "".join(body),
        height=y0 + table_h + 120,
    )


def evaluation_path() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:evaluation-decision-path"]["title"],
            "Normalization is input hygiene; verified evidence precedes every policy verdict.",
        )
    ]
    body.append(rect(50, 140, 1310, 670, fill=WHITE, stroke=GRID, radius=12))
    # Main spine.
    nodes = [
        (100, 220, 245, 82, "Canonical scope", "NFKC + ASCII + aliases", PALE_AMBER),
        (410, 220, 245, 82, "Mandatory context", "nine fields + evidence", PALE_BLUE),
        (720, 220, 245, 82, "Evidence verified?", "missing → information stop", PALE_RED),
        (1030, 220, 245, 82, "Line + exemption", "typed evidence + tier", PALE_TEAL),
    ]
    for x, y, w, h, title, sub, fill in nodes:
        body.append(rect(x, y, w, h, fill=fill, stroke=GRID))
        body.append(label(x + 18, y + 33, title, size=18, weight="700"))
        body.append(label(x + 18, y + 61, sub, size=14, fill=MUTED))
    for x1, x2 in ((345, 405), (655, 715), (965, 1025)):
        body.append(line(x1, 261, x2, 261, stroke=MUTED, arrow=True))
    # Outcomes and side branches.
    outcomes = [
        (65, 470, 240, 132, "INSUFFICIENT_INFORMATION", "missing / asserted / contradicted", PALE_RED, RED),
        (325, 470, 240, 132, "OUTSIDE_SCOPE", "complete; no line", PALE_BLUE, BLUE),
        (585, 470, 240, 132, "COMPLIANT", "verified exemption + tier", PALE_TEAL, TEAL),
        (845, 470, 240, 132, "REQUIRES_MODIFICATION", "multi-hit / tier", PALE_AMBER, AMBER),
        (1105, 470, 240, 132, "NON_COMPLIANT", "uncarved line", PALE_RED, RED),
    ]
    for x, y, w, h, title, sub, fill, color in outcomes:
        body.append(rect(x, y, w, h, fill=fill, stroke=color, width=2))
        # Classification names are single underscore-joined tokens that no word
        # wrapper will break, so a long one is split on its own underscore
        # rather than shrunk below the legibility floor.
        parts = [title] if len(title) <= 15 else [f"{title.split('_')[0]}_", title.split("_", 1)[1]]
        for part_index, part in enumerate(parts):
            body.append(label(x + 18, y + 32 + part_index * 22, part, size=16, fill=color, weight="700"))
        body.append(
            paragraph(
                x + 18,
                y + 32 + len(parts) * 22 + 14,
                sub,
                width=25,
                size=16,
                leading=22,
                fill=INK,
            )
        )
    # branch lines
    body.extend(
        [
            line(842, 302, 185, 465, stroke=RED, arrow=True),
            label(330, 372, "NO", size=16, fill=RED, weight="700"),
            line(1152, 302, 445, 465, stroke=BLUE, arrow=True),
            label(640, 372, "NO LINE", size=16, fill=BLUE, weight="700"),
            line(1152, 302, 705, 465, stroke=TEAL, arrow=True),
            label(860, 350, "verified exemption", size=16, fill=TEAL, weight="700"),
            line(1152, 302, 965, 465, stroke=AMBER, arrow=True),
            label(975, 438, "multi-hit / tier", size=16, fill=AMBER, weight="700", anchor="end"),
            line(1152, 302, 1225, 465, stroke=RED, arrow=True),
            label(1215, 372, "uncarved", size=16, fill=RED, weight="700"),
        ]
    )
    body.append(rect(100, 655, 1110, 112, fill=TABLE_ROW_ALT2, stroke=GRID, radius=10))
    body.append(label(125, 690, "Red-team boundary", size=16, fill=RED, weight="700"))
    body.append(
        paragraph(
            125,
            722,
            "The path can block missing context, but it cannot recover omitted semantics, prove a source truthful, enforce execution, or turn a self-report into independent review.",
            width=104,
            size=16,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:evaluation-decision-path"]["title"],
        FIGURE_TEXT["fig:evaluation-decision-path"]["alt"],
        "".join(body),
        height=845,
    )


def canary_trust_boundary() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:canary-trust-boundary"]["title"],
            "Conditional tamper evidence: the outside-the-boundary prior is the security-critical witness.",
        )
    ]
    body.append(rect(45, 140, 600, 540, fill=PALE_TEAL_BG, stroke=TEAL_STROKE, dash=True))
    body.append(label(70, 172, "AUTHOR-WRITABLE SIDE", size=14, fill=TEAL, weight="700"))
    body.append(rect(80, 220, 235, 115, fill=PALE_TEAL, stroke=GRID))
    body.append(label(100, 255, "Live registry", size=20, weight="700"))
    body.append(paragraph(100, 285, "canonical lines + scopes + tiers", width=22, size=15, fill=MUTED))
    body.append(rect(375, 220, 235, 115, fill=PALE_BLUE, stroke=GRID))
    body.append(label(395, 255, "Issue canary", size=20, weight="700"))
    body.append(paragraph(395, 285, "hash + ids + per-line digests", width=22, size=15, fill=MUTED))
    body.append(line(320, 278, 368, 278, stroke=MUTED, arrow=True))
    body.append(rect(80, 420, 530, 160, fill=WHITE, stroke=GRID))
    body.append(label(100, 455, "Re-issuance guard", size=18, weight="700"))
    body.append(
        paragraph(
            100,
            488,
            "A changed registry requires a rationale when replacing a prior canary; silent successor issuance is rejected by issue_canary.",
            width=54,
            size=15,
            fill=MUTED,
            leading=22,
        )
    )
    body.append(line(495, 335, 350, 415, stroke=TEAL, arrow=True))
    body.append(rect(765, 140, 590, 540, fill=PALE_AMBER_BG, stroke=AMBER, dash=True))
    body.append(label(790, 172, "OUTSIDE AUTHOR'S WRITE BOUNDARY", size=14, fill=AMBER, weight="700"))
    body.append(rect(805, 220, 250, 115, fill=PALE_AMBER, stroke=GRID))
    body.append(label(825, 255, "Prior copy", size=20, weight="700"))
    body.append(paragraph(825, 285, "git / archive / witness-held statement", width=24, size=15, fill=MUTED))
    body.append(rect(1100, 220, 210, 115, fill=PALE_RED, stroke=GRID))
    body.append(label(1120, 255, "Verify", size=20, weight="700"))
    body.append(paragraph(1120, 285, "drift + stale + metadata", width=19, size=15, fill=MUTED))
    body.append(line(1065, 278, 1093, 278, stroke=AMBER, width=2.5, arrow=True))
    body.append(rect(805, 420, 505, 160, fill=WHITE, stroke=GRID))
    body.append(label(825, 455, "Signals", size=18, weight="700"))
    body.append(label(825, 489, "intact · stale · drift · canary-grade altered", size=15, fill=INK))
    body.append(label(825, 523, "No signal", size=15, fill=RED, weight="700"))
    body.append(label(920, 523, "semantic relabeling · malicious re-issue · execution", size=15, fill=MUTED))
    body.append(line(1205, 335, 1055, 415, stroke=AMBER, width=2.5, arrow=True))
    body.append(
        paragraph(
            70,
            720,
            "Security claim: drift is observable only if the witness-held prior remains independent.",
            width=115,
            size=15,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:canary-trust-boundary"]["title"],
        FIGURE_TEXT["fig:canary-trust-boundary"]["alt"],
        "".join(body),
        height=760,
    )


def line_set_compass() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:line-set-compass"]["title"],
            "Each line has one job; cross-reference is not substitution.",
        )
    ]
    body.append(rect(50, 145, 1300, 560, fill=WHITE, stroke=GRID, radius=14))
    cards = [
        (
            90,
            "RED",
            "What must be refused?",
            "Security boundary · explicit No document",
            PALE_RED,
            RED,
            "scope, prohibition, review, canary",
        ),
        (
            405,
            "BLACK",
            "How do I do strong work?",
            "Positive wire for concise, rigorous practice",
            MUTED_FILL,
            INK,
            "method, evidence, revision, craft",
        ),
        (
            720,
            "GOLDEN",
            "What is worth reaching toward?",
            "Higher thread without compliance theater",
            PALE_AMBER,
            AMBER,
            "direction, aspiration, horizon, growth",
        ),
        (
            1035,
            "WHITE",
            "What is absent or unknowable?",
            "Negative space without mystical certainty",
            MUTED_FILL_ALT,
            MUTED,
            "unknowns, omission, restraint, silence",
        ),
    ]
    for x, name, question, sub, fill, accent, terms in cards:
        body.append(
            rect(x, 220, 245, 300, fill=fill, stroke=accent, width=2, radius=12, dash=name == "WHITE")
        )
        body.append(label(x + 20, 260, name, size=16, fill=accent, weight="700"))
        body.append(paragraph(x + 20, 305, question, width=17, size=20, leading=26, fill=INK, weight="700"))
        body.append(paragraph(x + 20, 390, sub, width=24, size=16, leading=22, fill=MUTED))
        body.append(paragraph(x + 20, 462, terms, width=22, size=16, leading=22, fill=accent, weight="700"))
    for x1, x2 in ((340, 395), (655, 710), (970, 1025)):
        body.append(line(x1, 355, x2, 355, stroke=GRID, width=2, dash=True, arrow=True))
    body.append(
        paragraph(
            90,
            575,
            # The set map (../../docs/line-set.md) states the working order as
            # refuse → method → aspire → account-for-absence. This caption uses
            # the same four jobs in noun form, matching the figure's own title.
            "The set is ordered as refusal → method → aspiration → absence. Each work remains complete when separated from the others.",
            width=118,
            size=16,
            leading=22,
            fill=MUTED,
        )
    )
    body.append(label(90, 640, "Reading rule", size=16, fill=RED, weight="700"))
    body.append(
        paragraph(
            90,
            668,
            "Red does not become method; Black does not become permission; Golden does not become proof; White does not become evidence.",
            width=118,
            size=16,
            leading=22,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:line-set-compass"]["title"],
        FIGURE_TEXT["fig:line-set-compass"]["alt"],
        "".join(body),
        height=760,
    )


def outcome_precedence() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:outcome-precedence"]["title"],
            "Precedence is read top to bottom; the first satisfied condition fixes the result.",
        )
    ]
    body.append(rect(50, 140, 1300, 800, fill=WHITE, stroke=GRID, radius=12))

    # Pre-policy short circuit.
    body.append(rect(80, 185, 1240, 110, fill=PALE_RED, stroke=RED, width=2, dash=True))
    body.append(circle(140, 240, 24, fill=RED))
    body.append(label(140, 246, "0", size=22, fill=PAPER, weight="700", anchor="middle"))
    body.append(label(190, 224, "INSUFFICIENT_INFORMATION", size=21, fill=RED, weight="700"))
    body.append(
        label(190, 250, "any missing, unverified, stale, or malformed-scope field", size=15, fill=INK)
    )
    body.append(
        label(
            190, 274, "returns before the line loop — a policy verdict is never reached", size=14, fill=MUTED
        )
    )
    body.append(label(1300, 224, "SHORT CIRCUIT", size=13, fill=RED, weight="700", anchor="end"))
    body.append(label(1300, 250, "evaluate_action ▸ intake gate", size=13, fill=MUTED, anchor="end"))

    body.append(
        label(
            80,
            340,
            "OTHERWISE — reduce over the implicated lines to the single most severe outcome:",
            size=15,
            fill=INK,
            weight="700",
        )
    )

    rungs = [
        ("1", "NON_COMPLIANT", RED, PALE_RED, "hard_block", "an implicated line has no verified exemption"),
        (
            "2",
            "REQUIRES_MODIFICATION",
            AMBER,
            PALE_AMBER,
            "needs_modification",
            "exemption verified, but ≥2 prohibited dimensions or a use below the tier floor",
        ),
        (
            "3",
            "COMPLIANT",
            TEAL,
            PALE_TEAL,
            "implicated",
            "every implicated line is narrowed by verified evidence and tier",
        ),
        (
            "4",
            "OUTSIDE_SCOPE",
            BLUE,
            PALE_BLUE,
            "else",
            "no current line is implicated by the complete, evidenced intake",
        ),
    ]
    y = 365
    row_h, gap = 100, 12
    for idx, (rank, name, accent, fill, symbol, trigger) in enumerate(rungs):
        ry = y + idx * (row_h + gap)
        body.append(rect(80, ry, 1240, row_h, fill=fill, stroke=accent, width=2))
        body.append(circle(140, ry + 50, 24, fill=accent))
        body.append(label(140, ry + 56, rank, size=22, fill=PAPER, weight="700", anchor="middle"))
        body.append(label(190, ry + 42, name, size=21, fill=accent, weight="700"))
        body.append(paragraph(190, ry + 72, trigger, width=78, size=15, leading=19, fill=INK))
        body.append(rect(1055, ry + 30, 245, 40, fill=WHITE, stroke=accent, radius=8))
        body.append(label(1177, ry + 55, symbol, size=15, fill=accent, weight="700", anchor="middle"))
        if idx < len(rungs) - 1:
            body.append(line(140, ry + row_h, 140, ry + row_h + gap, stroke=GRID, width=2, arrow=True))
    body.append(
        paragraph(
            80,
            895,
            "Derived from evaluate_action: the intake gate returns first; a less severe classification never overrides a more severe one, so the reduction is monotone in severity.",
            width=120,
            size=15,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:outcome-precedence"]["title"],
        FIGURE_TEXT["fig:outcome-precedence"]["alt"],
        "".join(body),
        height=945,
    )


def improvement_method_loop() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:improvement-method-loop"]["title"],
            "A bounded workflow for turning uncertainty into inspectable revision.",
        )
    ]
    body.append(rect(42, 132, 1008, 690, fill=PALE_TEAL_BG, stroke=TEAL_STROKE, dash=True))
    body.append(label(70, 163, "LOCAL, REPRODUCIBLE ARTIFACT", size=16, fill=TEAL, weight="700"))

    cards = [
        (78, 215, "1  DECONSTRUCT", "What is the actual function?", "purpose before labels", PALE_BLUE, BLUE),
        (
            318,
            215,
            "2  CHALLENGE",
            "Which assumptions can fail?",
            "scope · authority · evidence",
            PALE_AMBER,
            AMBER,
        ),
        (
            558,
            215,
            "3  DECLARE",
            "What claim is being made?",
            "class · state · stopping point",
            PALE_TEAL,
            TEAL,
        ),
        (
            798,
            215,
            "4  RECONSTRUCT",
            "What is the smallest honest rule?",
            "typed action · explicit boundary",
            PALE_TEAL,
            TEAL,
        ),
        (798, 480, "5  EVALUATE", "What does the record support?", "fail-closed precedence", PALE_RED, RED),
        (
            558,
            480,
            "6  FREEZE",
            "What must remain inspectable?",
            "finding · rationale · revision",
            PALE_BLUE,
            BLUE,
        ),
        (
            318,
            480,
            "7  VERIFY",
            "Did source reach the reader?",
            "tests · figures · PDF · HTML",
            PALE_AMBER,
            AMBER,
        ),
        (78, 480, "8  REVISE", "What changed, and why?", "dated amendment or stop", PALE_TEAL, TEAL),
    ]
    for x, y, title, question, detail, fill, accent in cards:
        body.append(rect(x, y, 205, 190, fill=fill, stroke=accent, width=2, radius=12))
        body.append(label(x + 16, y + 31, title, size=16, fill=accent, weight="700"))
        body.append(
            paragraph(x + 16, y + 67, question, width=17, size=17, leading=22, fill=INK, weight="700")
        )
        body.append(paragraph(x + 16, y + 145, detail, width=20, size=16, leading=22, fill=MUTED))

    for x1, x2 in ((283, 313), (523, 553), (763, 793)):
        body.append(line(x1, 310, x2, 310, stroke=MUTED, width=2, arrow=True))
    body.append(line(900, 410, 900, 472, stroke=MUTED, width=2, arrow=True))
    # Return leg: each arrow spans only the gap between two cards. The earlier
    # coordinates started inside a card and struck through its own text.
    for x1, x2 in ((793, 768), (553, 528), (313, 288)):
        body.append(line(x1, 575, x2, 575, stroke=MUTED, width=2, arrow=True))
    body.append(line(180, 472, 180, 442, stroke=MUTED, width=2, arrow=True))
    body.append(line(180, 442, 180, 410, stroke=TEAL, width=2, dash=True, arrow=True))
    body.append(label(205, 452, "iterate only with a dated reason", size=16, fill=TEAL, weight="700"))

    body.append(rect(1080, 205, 270, 465, fill=PALE_AMBER_BG, stroke=AMBER, dash=True))
    body.append(label(1105, 240, "OUTSIDE THE ARTIFACT", size=16, fill=AMBER, weight="700"))
    body.append(
        paragraph(
            1105,
            282,
            "The loop can record a local decision and validate a generated release.",
            width=22,
            size=16,
            leading=24,
            fill=INK,
        )
    )
    body.append(label(1105, 409, "It cannot establish:", size=16, fill=MUTED, weight="700"))
    for index, item in enumerate(
        ("semantic truth", "legal validity", "enforcement", "independent witnessing", "real-world safety")
    ):
        body.append(circle(1118, 445 + index * 34, 5, fill=RED, stroke=RED, width=1))
        body.append(label(1135, 451 + index * 34, item, size=16, fill=INK))
    body.append(
        paragraph(
            70,
            770,
            "A green local result is a bounded record, not a safety certificate; a failed gate is a reason to stop or revise, not a reason to hide uncertainty.",
            width=108,
            size=16,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:improvement-method-loop"]["title"],
        FIGURE_TEXT["fig:improvement-method-loop"]["alt"],
        "".join(body),
        height=860,
    )
