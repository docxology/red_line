"""Hand-authored scholarship and editorial figure plates."""

from __future__ import annotations

from red_line.model.enums import Classification, EvidenceKind
from red_line.registry.lines import PERSONAL_RED_LINES

from .svg import circle, figure_header, label, line, paragraph, path, rect, svg_document, text_lines
from .text import FIGURE_TEXT
from .theme import (
    AMBER, BLUE, CREAM, GOLD_STROKE, GRID, INK,
    MUTED, PALE_AMBER, PALE_AMBER_BG, PALE_BLUE, PALE_RED,
    PALE_TEAL, PALE_TEAL_BG, PAPER, RED, TABLE_HEADER,
    TABLE_ROW_ALT, TEAL, TEAL_STROKE, WHITE,
)

READING_CARDS = [
    ("c. 5th BCE", "China", "Sunzi", "information, deception, judgment", PALE_BLUE),
    ("c. 3rd BCE–3rd CE", "India", "Kauṭilya / Arthaśāstra", "statecraft, intelligence", PALE_AMBER),
    ("4th BCE", "Greece", "Aristotle", "law, authority, constitutions", PALE_TEAL),
    ("10th c.", "Central Asia / Islamic world", "al-Fārābī", "order, knowledge, flourishing", PALE_TEAL),
    ("14th c.", "North Africa", "Ibn Khaldūn", "cohesion, justice, power", PALE_AMBER),
    ("1513", "Italy", "Machiavelli", "institutions, incentives, realism", PALE_BLUE),
    ("1552", "Spanish colonial Americas", "Las Casas", "violence hidden by authority", PALE_RED),
    ("1787", "Gold Coast / Black Atlantic", "Ottobah Cugoano", "liberty, consent, responsibility", PALE_RED),
    ("1792", "England", "Wollstonecraft", "capacity, education, standing", PALE_TEAL),
    ("1990", "United States / global commons", "Ostrom", "self-governance and rules in use", PALE_AMBER),
    (
        "1998",
        "United States / Southeast Asia",
        "James C. Scott",
        "legibility, simplification, state power",
        PALE_RED,
    ),
    (
        "1999",
        "Aotearoa New Zealand / Māori scholarship",
        "Linda Tuhiwai Smith",
        "research power and decolonization",
        PALE_TEAL,
    ),
    ("2004", "United States", "Nissenbaum", "contextual integrity of information flows", PALE_BLUE),
    (
        "2016",
        "Aotearoa / Indigenous data governance",
        "Kukutai · Taylor",
        "collective data authority",
        PALE_AMBER,
    ),
    (
        "2019–20",
        "Global / Africa / decolonial AI",
        "Jobin · Birhane · Mohamed et al.",
        "plural ethics, coloniality, sociotechnical limits",
        PALE_RED,
    ),
    (
        "2021–23",
        "Global institutions",
        "UNESCO · OECD · NIST",
        "policy action, rights, operational risk",
        PALE_AMBER,
    ),
]


def scholarship_map() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:scholarship-reading-map"]["title"],
            "Situated questions; placement does not imply influence or equivalence.",
        )
    ]
    columns = [
        ("BEFORE 1900", "early and early-modern questions", TEAL),
        ("1900–2000", "institutional and methodological critiques", BLUE),
        ("2000–PRESENT", "AI governance and implementation", AMBER),
    ]
    groups = [READING_CARDS[:9], READING_CARDS[9:12], READING_CARDS[12:]]
    card_w, question_wrap = 375, 44
    # Card heights follow the wrapped question, and the panel follows the
    # tallest column, so a longer source line grows the plate instead of
    # spilling text past the card and panel borders.
    column_bottoms: list[float] = []
    cards_svg: list[str] = []
    for col, cards in enumerate(groups):
        x = 75 + col * 425
        y = 235
        for period, region, author, question, fill in cards:
            question_lines = text_lines(question, question_wrap)
            h = 78 + 22 * (len(question_lines) - 1)
            cards_svg.append(rect(x, y, card_w, h, fill=fill, stroke=GRID, radius=8))
            cards_svg.append(label(x + 12, y + 24, period, size=16, fill=MUTED, weight="700"))
            cards_svg.append(
                label(x + card_w - 12, y + 24, author, size=16, fill=INK, weight="700", anchor="end")
            )
            cards_svg.append(label(x + 12, y + 46, region, size=16, fill=MUTED))
            cards_svg.append(
                paragraph(x + 12, y + 68, question, width=question_wrap, size=16, leading=22, fill=INK)
            )
            y += h + 8
        column_bottoms.append(y)
    panel_bottom = max(column_bottoms) + 18
    body.append(rect(50, 132, 1300, panel_bottom - 132, fill=WHITE, stroke=GRID, radius=12))
    for i, (heading, sub, accent) in enumerate(columns):
        x = 75 + i * 425
        body.append(label(x, 172, heading, size=16, fill=accent, weight="700"))
        body.append(label(x, 197, sub, size=16, fill=MUTED))
        body.append(line(x, 212, x + card_w, 212, stroke=GRID, width=1))
    body.extend(cards_svg)
    body.append(label(75, panel_bottom + 40, "Reading rule", size=16, fill=RED, weight="700"))
    body.append(
        label(
            75,
            panel_bottom + 66,
            "borrow questions; do not claim inheritance, consensus, or endorsement",
            size=16,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:scholarship-reading-map"]["title"],
        FIGURE_TEXT["fig:scholarship-reading-map"]["alt"],
        "".join(body),
        height=int(panel_bottom) + 110,
    )


TRANSFER_ROWS = [
    ("Sunzi · China", "judgment under deception", "descriptive", "not a modern ethics code"),
    ("Kauṭilya · India", "administration and intelligence", "descriptive", "not a universal model of rule"),
    (
        "al-Fārābī · Islamic world",
        "knowledge and political order",
        "transfer",
        "not a rights-equivalent framework",
    ),
    ("Ibn Khaldūn · North Africa", "cohesion, justice, power", "transfer", "not a timeless sociology"),
    (
        "Cugoano · Black Atlantic",
        "liberty, consent, responsibility",
        "transfer",
        "not generic continental representation",
    ),
    ("Wollstonecraft · England", "equal intellectual standing", "transfer", "not a complete justice theory"),
    ("Smith · Aotearoa / Māori", "research power and extraction", "transfer", "not decorative diversity"),
    (
        "Kukutai · Taylor · Indigenous data",
        "collective authority and governance",
        "transfer",
        "not a consent shortcut",
    ),
    ("Birhane · Africa", "dependency and coloniality", "descriptive", "not one effect for every import"),
    ("UNESCO / AU / NIST", "policy and operational vocabulary", "implementation", "not Red Line approval"),
]


def scholarship_transfer_matrix() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:scholarship-transfer-matrix"]["title"],
            "Every row records a source question, claim class, and explicit interpretation limit.",
        )
    ]
    x0, y0 = 55, 145
    widths = (300, 360, 190, 430)
    headers = ("SITUATED SOURCE", "QUESTION CARRIED", "CLAIM CLASS", "STOPPING POINT")
    total_w = sum(widths)
    body.append(rect(x0, y0, total_w, 650, fill=WHITE, stroke=GRID, radius=10))
    x = x0
    for width, header in zip(widths, headers):
        body.append(rect(x, y0, width, 50, fill=TABLE_HEADER, stroke=GRID, radius=0))
        body.append(label(x + 14, y0 + 31, header, size=13, fill=MUTED, weight="700"))
        x += width
    row_h = 60
    accents = {"descriptive": BLUE, "transfer": AMBER, "implementation": TEAL}
    fills = {"descriptive": PALE_BLUE, "transfer": PALE_AMBER, "implementation": PALE_TEAL}
    for row, (source, question, claim_class, limit) in enumerate(TRANSFER_ROWS):
        y = y0 + 50 + row * row_h
        if row % 2 == 0:
            body.append(rect(x0, y, total_w, row_h, fill=TABLE_ROW_ALT, stroke="none", radius=0, width=0))
        values = (source, question, claim_class, limit)
        x = x0
        for col, (width, value) in enumerate(zip(widths, values)):
            body.append(line(x, y, x, y + row_h, stroke=GRID, width=1))
            if col == 2:
                body.append(
                    rect(
                        x + 12,
                        y + 17,
                        width - 24,
                        30,
                        fill=fills[claim_class],
                        stroke=accents[claim_class],
                        radius=7,
                    )
                )
                body.append(
                    label(
                        x + width / 2,
                        y + 38,
                        value.upper(),
                        size=12,
                        fill=accents[claim_class],
                        weight="700",
                        anchor="middle",
                    )
                )
            else:
                body.append(
                    paragraph(
                        x + 14,
                        y + 23,
                        value,
                        width=max(16, int(width / 11)),
                        size=13,
                        leading=16,
                        fill=INK,
                        weight="700" if col == 0 else "400",
                    )
                )
            x += width
    body.append(
        paragraph(
            55,
            835,
            "Reading rule: transfer a question, never a universal endorsement; claim class and stopping point travel together.",
            width=120,
            size=15,
            fill=MUTED,
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:scholarship-transfer-matrix"]["title"],
        FIGURE_TEXT["fig:scholarship-transfer-matrix"]["alt"],
        "".join(body),
        height=880,
    )


def boundary_instrument_plate() -> str:
    """Render an art-directed but source-driven overview of the instrument."""

    dimensions = [kind.value.replace("_", " ") for kind in EvidenceKind]
    outcomes = [classification.value.replace("_", " ") for classification in Classification]
    body = [
        figure_header(
            FIGURE_TEXT["fig:boundary-instrument-plate"]["title"],
            "A visual field for the decision moment: what is declared, what is evidenced, and where the claim stops.",
        )
    ]

    # A quiet registration grid carries the cover's paper-and-print language
    # without turning the plate into an empirical chart.
    for x in range(70, 1341, 80):
        body.append(line(x, 140, x, 733, stroke=GRID, width=1, opacity=0.45))
    for y in range(170, 734, 70):
        body.append(line(52, y, 1348, y, stroke=GRID, width=1, opacity=0.45))
    body.append(rect(52, 142, 785, 586, fill=PALE_TEAL_BG, stroke=TEAL_STROKE, dash=True, width=1.8))
    body.append(rect(895, 142, 453, 586, fill=PALE_AMBER_BG, stroke=GOLD_STROKE, dash=True, width=1.8))
    body.append(label(78, 174, "LOCAL DECISION FIELD", size=16, fill=TEAL, weight="700"))
    body.append(label(922, 174, "OUTSIDE THE WRITE BOUNDARY", size=16, fill=AMBER, weight="700"))

    # Three flowing traces turn the intake into a visual instrument rather than
    # another rectangular flowchart. Each trace remains explicitly labelled.
    traces = [
        (
            "DECLARATION",
            "scope + tier",
            TEAL,
            252,
            "M 104 252 C 205 194, 238 307, 336 260 S 477 205, 596 305",
        ),
        (
            "EVIDENCE",
            f"{len(dimensions)} required dimensions",
            BLUE,
            371,
            "M 104 371 C 217 432, 253 291, 365 350 S 498 449, 596 359",
        ),
        (
            "BOUNDARY",
            f"{len(PERSONAL_RED_LINES)} current lines",
            RED,
            496,
            "M 104 496 C 227 441, 284 558, 393 473 S 504 430, 596 414",
        ),
    ]
    for title, subtitle, accent, start_y, trace in traces:
        body.append(path(trace, stroke=accent, width=5, opacity=0.86))
        body.append(circle(104, start_y, 8, fill=accent, stroke=PAPER, width=3))
        body.append(label(124, start_y - 14, title, size=16, fill=accent, weight="700"))
        body.append(label(124, start_y + 12, subtitle, size=16, fill=INK))

    body.append(rect(578, 286, 214, 238, fill=PALE_AMBER, stroke=AMBER, width=2, radius=22))
    body.append(circle(685, 338, 30, fill=RED, stroke=PALE_AMBER, width=5))
    body.append(label(685, 346, "!", size=26, fill=PAPER, weight="700", anchor="middle"))
    body.append(label(685, 405, "LOCAL REVIEW", size=17, fill=INK, weight="700", anchor="middle"))
    body.append(label(685, 433, "typed context", size=14, fill=MUTED, anchor="middle"))
    body.append(label(685, 456, "stable reason codes", size=14, fill=MUTED, anchor="middle"))
    body.append(
        label(685, 488, "record, narrow, or stop", size=13, fill=AMBER, weight="700", anchor="middle")
    )

    # The live enum gives the plate its semantic compass: no color-only legend
    # is needed because every node is text-labelled.
    body.append(
        label(86, 594, f"{len(dimensions)} REQUIRED INTAKE DIMENSIONS", size=12, fill=BLUE, weight="700")
    )
    for index, dimension in enumerate(dimensions):
        row, col = divmod(index, 3)
        # 175 units per column: the widest dimension name ("downstream
        # transfer") is 19 characters, which is 152 units at the font floor.
        x = 86 + col * 175
        y = 622 + row * 30
        body.append(circle(x, y - 5, 4, fill=BLUE, stroke=BLUE, width=1))
        body.append(label(x + 12, y, dimension, size=16, fill=INK))
    body.append(
        label(
            86, 716, "Evidence is a condition for a local result, not a proxy for truth.", size=16, fill=MUTED
        )
    )

    # The boundary is intentionally a single strong mark, echoing the cover.
    body.append(line(852, 148, 852, 726, stroke=RED, width=8))
    body.append(circle(852, 279, 12, fill=RED, stroke=PAPER, width=4))
    body.append(circle(852, 579, 12, fill=RED, stroke=PAPER, width=4))
    body.append(label(852, 752, "COMMITMENT", size=16, fill=RED, weight="700", anchor="middle"))

    body.append(label(922, 218, "FIVE DISTINCT OUTCOMES", size=16, fill=AMBER, weight="700"))
    center_x, center_y = 1118, 366
    body.append(circle(center_x, center_y, 104, fill="none", stroke=GOLD_STROKE, width=2))
    body.append(circle(center_x, center_y, 73, fill=CREAM, stroke=AMBER, width=1.5))
    body.append(label(center_x, center_y - 8, "LOCAL", size=18, fill=INK, weight="700", anchor="middle"))
    body.append(label(center_x, center_y + 16, "RESULT", size=18, fill=INK, weight="700", anchor="middle"))
    outcome_colors = {
        "compliant": TEAL,
        "requires modification": AMBER,
        "non compliant": RED,
        "outside scope": BLUE,
        "insufficient information": MUTED,
    }
    # Node, then its name placed outward along the same radius with an anchor
    # chosen by side, so no name overprints the ring, the hub, or a neighbour
    # at the 16-unit font floor. Long names split at their own word break.
    outcome_layout = [
        ((1118, 266), 1118, 238, "middle"),
        ((1210, 334), 1234, 322, "start"),
        ((1176, 446), 1192, 468, "start"),
        ((1060, 446), 1044, 468, "end"),
        ((1026, 334), 1002, 322, "end"),
    ]
    for outcome, ((x, y), label_x, label_y, anchor) in zip(outcomes, outcome_layout):
        accent = outcome_colors[outcome]
        body.append(circle(x, y, 11, fill=accent, stroke=PALE_AMBER_BG, width=4))
        words = outcome.split(" ")
        parts = [outcome] if len(outcome) <= 14 else [words[0], " ".join(words[1:])]
        for part_index, part in enumerate(parts):
            body.append(
                label(label_x, label_y + part_index * 22, part, size=16, fill=INK, anchor=anchor)
            )
    body.append(path("M 1215 486 C 1275 522, 1265 578, 1198 610", stroke=AMBER, width=3, dash=True))
    body.append(circle(1198, 610, 9, fill=AMBER, stroke=PALE_AMBER_BG, width=3))
    body.append(label(1217, 615, "external prior", size=16, fill=AMBER, weight="700"))
    body.append(
        paragraph(
            922,
            520,
            "Only a copy held beyond the author's write boundary can make a later change observable.",
            width=30,
            size=16,
            leading=22,
            fill=INK,
        )
    )
    body.append(label(922, 628, "NOT ESTABLISHED HERE", size=16, fill=RED, weight="700"))
    body.append(
        paragraph(
            922,
            654,
            "semantic truth · legal validity · enforcement · real-world safety",
            width=40,
            size=16,
            leading=20,
            fill=MUTED,
        )
    )
    body.append(
        label(
            52,
            796,
            "SOURCE-DRIVEN EDITORIAL PLATE · REGISTRY / EVALUATOR / CANARY · NO EMPIRICAL PERFORMANCE CLAIM",
            size=16,
            fill=MUTED,
            weight="700",
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:boundary-instrument-plate"]["title"],
        FIGURE_TEXT["fig:boundary-instrument-plate"]["alt"],
        "".join(body),
        height=840,
    )


SCHOLARSHIP_BRIDGE_ROWS = [
    (
        "HARAWAY · 1988",
        "situated perspective",
        "PROVENANCE + AFFECTED PARTIES",
        "name whose view is missing",
        TEAL,
        PALE_TEAL,
    ),
    (
        "JASANOFF · 2003",
        "framing · vulnerability · distribution · learning",
        "PURPOSE + END USE + UNKNOWNS",
        "inspect uncertainty before optimism",
        BLUE,
        PALE_BLUE,
    ),
    (
        "COSTANZA-CHOCK · 2020",
        "participation · contestability",
        "HUMAN CONTROL + DOWNSTREAM TRANSFER",
        "ask who can say no or repair",
        AMBER,
        PALE_AMBER,
    ),
    (
        "D'IGNAZIO + KLEIN · 2020",
        "power · classification · invisible labor",
        "CAPABILITY SCOPE + DATA PROVENANCE",
        "ask what the data hides",
        RED,
        PALE_RED,
    ),
]


def scholarship_intake_bridge() -> str:
    body = [
        figure_header(
            FIGURE_TEXT["fig:scholarship-intake-bridge"]["title"],
            "A translation layer for turning reading into better questions without laundering authority.",
        )
    ]
    for x in range(70, 1341, 90):
        body.append(line(x, 140, x, 760, stroke=GRID, width=1, opacity=0.38))
    for y in range(180, 761, 70):
        body.append(line(55, y, 1345, y, stroke=GRID, width=1, opacity=0.38))
    body.append(label(78, 160, "SCHOLARSHIP / QUESTION", size=12, fill=TEAL, weight="700"))
    body.append(label(790, 160, "INTAKE / OPERATIONAL CONSEQUENCE", size=12, fill=BLUE, weight="700"))
    body.append(line(55, 174, 1345, 174, stroke=GRID, width=1.5))
    body.append(line(690, 145, 690, 758, stroke=RED, width=7))
    body.append(
        label(690, 728, "TRANSLATION ≠ AUTHORIZATION", size=11, fill=RED, weight="700", anchor="middle")
    )

    for index, (source, question, fields, consequence, accent, fill) in enumerate(SCHOLARSHIP_BRIDGE_ROWS):
        y = 205 + index * 132
        body.append(rect(70, y, 520, 96, fill=fill, stroke=accent, width=2, radius=18))
        body.append(label(92, y + 27, source, size=14, fill=accent, weight="700"))
        body.append(label(92, y + 58, question, size=17, fill=INK, weight="700"))
        body.append(circle(618, y + 48, 10, fill=accent, stroke=PAPER, width=3))
        body.append(
            path(
                f"M 590 {y + 48} C 620 {y + 20}, 650 {y + 76}, 675 {y + 48}",
                stroke=accent,
                width=3,
                dash=True,
                opacity=0.8,
            )
        )
        body.append(circle(705, y + 48, 10, fill="none", stroke=accent, width=2))
        body.append(rect(770, y, 560, 96, fill=CREAM, stroke=accent, width=2, radius=18))
        body.append(label(794, y + 27, fields, size=14, fill=accent, weight="700"))
        body.append(label(794, y + 61, consequence, size=17, fill=INK, weight="700"))
        body.append(
            label(794, y + 83, "question transferred; local result still bounded", size=12, fill=MUTED)
        )

    body.append(rect(70, 742, 1260, 34, fill=PALE_AMBER_BG, stroke=AMBER, dash=True, radius=10))
    body.append(
        label(
            700,
            765,
            "A broader reading base changes what the operator asks; it does not make the registry universal.",
            size=13,
            fill=AMBER,
            weight="700",
            anchor="middle",
        )
    )
    return svg_document(
        FIGURE_TEXT["fig:scholarship-intake-bridge"]["title"],
        FIGURE_TEXT["fig:scholarship-intake-bridge"]["alt"],
        "".join(body),
        height=800,
    )
