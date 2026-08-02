"""Close the count and hash claims that no test read.

Two gaps were shipped together. First, three regions of
``manuscript/09a_registry_composition.md`` stated registry-derived numbers that
``test_manuscript_composition_binding.py`` never touched — the severity and
tier-floor distributions, the joint claim relating them, and the structural
ranges — while ``README.md`` and ``ISA.md`` asserted that *every* number in that
prose is recomputed. Second, the line count and the truncated digest were
restated in the abstract, introduction, beacon opening, conclusion, and canary
section, none of which any test, script, or validator read; the amendment
runbook's propagation list disagreed with two other checklists about which of
those surfaces must be updated.

Every assertion here recomputes its number from ``red_line.analysis``,
``red_line.registry``, or ``red_line.canary``. Adopting an eighth line, moving a
tier floor, or re-issuing the digest reddens these tests instead of leaving a
stale "seven" behind.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from red_line import PERSONAL_RED_LINES, Severity
from red_line.analysis.registry_metrics import (
    line_summaries,
    severity_distribution,
    tier_floor_distribution,
)
from red_line.canary import registry_hash
from red_line.model.enums import DeploymentTier

ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "manuscript"

NUMBER_WORDS = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
}

#: Every manuscript surface that restates the registry line count. The runbook,
#: `docs/development.md`, and `docs/PROPOSED_RED_LINES.md` each listed a
#: different subset; this tuple is the one enumerated list, and the amendment
#: runbook is checked against it below.
LINE_COUNT_SURFACES = (
    "00_abstract.md",
    "01_introduction.md",
    "05_deployment_tiers.md",
    "07_durability_canary.md",
    "09_red_lines.md",
    "09a_registry_composition.md",
    "10_limitations.md",
    "11_conclusion.md",
)


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _composition() -> str:
    return _flat(MANUSCRIPT / "09a_registry_composition.md")


# --------------------------------------------------------------------------
# RL-10: the three unbound regions of 09a.
# --------------------------------------------------------------------------


def test_severity_prose_matches_the_severity_distribution() -> None:
    """"two CANARY, one ABSOLUTE, four STRONG" is recomputed, not asserted."""

    match = re.search(
        r"divide by severity into (\w+) `CANARY` lines, (\w+) `ABSOLUTE` line, "
        r"and (\w+) `STRONG` lines",
        _composition(),
    )
    assert match is not None, "09a must state the severity split"
    distribution = {severity.value: count for severity, count in severity_distribution().items()}

    assert match.group(1) == NUMBER_WORDS[distribution["canary"]]
    assert match.group(2) == NUMBER_WORDS[distribution["absolute"]]
    assert match.group(3) == NUMBER_WORDS[distribution["strong"]]
    assert sum(distribution.values()) == len(PERSONAL_RED_LINES)


def test_tier_floor_prose_matches_the_tier_floor_distribution() -> None:
    """"two hosted, three connected, two air_gapped" is recomputed."""

    match = re.search(
        r"divide into (\w+) lines whose floor is `hosted`, (\w+) at `connected`, "
        r"and (\w+) at `air_gapped`",
        _composition(),
    )
    assert match is not None, "09a must state the tier-floor split"
    distribution = {tier.value: count for tier, count in tier_floor_distribution().items()}

    assert match.group(1) == NUMBER_WORDS[distribution["hosted"]]
    assert match.group(2) == NUMBER_WORDS[distribution["connected"]]
    assert match.group(3) == NUMBER_WORDS[distribution["air_gapped"]]
    assert sum(distribution.values()) == len(PERSONAL_RED_LINES)


def test_orthogonality_claim_is_a_joint_fact_not_two_marginals() -> None:
    """The CANARY/air_gapped cross-claim is checked against the pairs.

    Two marginal distributions cannot establish it: a registry with the same
    severity counts and the same tier-floor counts could still put both CANARY
    lines on one floor. The claim is therefore re-derived from the per-line
    pairs.
    """

    body = _composition()
    canary_floors = {
        summary.max_tier for summary in line_summaries() if summary.severity == Severity.CANARY.value
    }
    air_gapped_severities = {
        summary.severity
        for summary in line_summaries()
        if summary.max_tier == DeploymentTier.AIR_GAPPED.value
    }

    assert "the two `CANARY` lines sit at different tier floors (`hosted` and `connected`)" in body
    assert canary_floors == {"hosted", "connected"}
    assert "the two `air_gapped` floors belong to `STRONG` lines" in body
    assert air_gapped_severities == {Severity.STRONG.value}


def test_structural_range_prose_matches_line_summaries() -> None:
    """"three to six tokens", "two or three" carve-outs and exemptions derive."""

    body = _composition()
    summaries = line_summaries()
    scope_match = re.search(r"scope sizes run from (\w+) to (\w+) tokens", body)
    assert scope_match is not None, "09a must state the scope-size range"

    scope_sizes = [summary.scope_size for summary in summaries]
    assert scope_match.group(1) == NUMBER_WORDS[min(scope_sizes)]
    assert scope_match.group(2) == NUMBER_WORDS[max(scope_sizes)]

    carve_outs = {summary.carve_out_count for summary in summaries}
    exemptions = {summary.exemption_count for summary in summaries}
    assert "every line carries two or three narrative carve-outs" in body
    assert carve_outs == {2, 3}
    assert "carries two or three typed exemptions" in body
    assert exemptions == {2, 3}


def test_all_mode_exemption_owners_are_exactly_the_lines_named() -> None:
    """The three lines named as ALL-mode owners are the ones that own them."""

    body = _composition()
    owners = {summary.line_id for summary in line_summaries() if summary.all_mode_count}
    named = set(re.findall(r"`([a-z0-9-]+)`", body.split("The three `ALL`-mode exemptions sit on")[1]))

    assert owners == {"s1-human-control-force", "s2-untargeted-profiling", "downstream-transfer"}
    assert owners <= named
    assert all(
        summary.all_mode_count == 1 for summary in line_summaries() if summary.line_id in owners
    ), "'one each' must hold per named line"


# --------------------------------------------------------------------------
# RL-11: the count and hash claims no test read.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("filename", "pattern"),
    [
        ("00_abstract.md", r"It records (\w+) first-person refusals"),
        ("01_introduction.md", r"Its (\w+) first-person lines identify"),
        ("05_deployment_tiers.md", r"across the (\w+) current lines"),
        ("07_durability_canary.md", r"the current (\w+) lines yield the pinned digest"),
        ("09_red_lines.md", r"The current registry contains (\w+) lines"),
        ("09a_registry_composition.md", r"The (\w+) lines divide by severity"),
        ("10_limitations.md", r"bounded by (\w+) personal lines"),
        ("11_conclusion.md", r"It makes (\w+) personal No's"),
    ],
)
def test_every_restated_line_count_matches_the_registry(filename: str, pattern: str) -> None:
    """Each surface that restates the line count is recomputed from the code."""

    match = re.search(pattern, _flat(MANUSCRIPT / filename))

    assert match is not None, f"{filename} no longer states the line count in the bound form"
    assert match.group(1) == NUMBER_WORDS[len(PERSONAL_RED_LINES)]


def test_the_bound_surface_list_covers_every_file_that_states_the_count() -> None:
    """A new restatement in an unlisted file must fail rather than hide.

    Scans every manuscript body file for the count word next to a line-ish noun
    and asserts the set equals the enumerated surfaces above, so this gate can
    never quietly run over an empty or shrinking scan set.
    """

    word = NUMBER_WORDS[len(PERSONAL_RED_LINES)]
    pattern = re.compile(rf"\b{word}\b[^.]{{0,40}}\b(lines|refusals|No's|personal)\b")
    found = {
        path.name
        for path in sorted(MANUSCRIPT.glob("*.md"))
        if pattern.search(_flat(path))
    }

    assert found, "scan set is empty; the gate would be vacuous"
    assert found == set(LINE_COUNT_SURFACES)


def test_beacon_canary_count_sentence_matches_the_registry() -> None:
    """09_red_lines' "including two CANARY-grade lines" is recomputed."""

    match = re.search(
        r"contains \w+ lines, including (\w+) CANARY-grade lines",
        _flat(MANUSCRIPT / "09_red_lines.md"),
    )
    canary = sum(1 for line in PERSONAL_RED_LINES if line.severity is Severity.CANARY)

    assert match is not None, "beacon must state the CANARY count"
    assert match.group(1) == NUMBER_WORDS[canary]


def test_canary_section_truncated_digest_matches_the_registry_hash() -> None:
    """The `first8…last6` digest in 07 is the digest the code computes."""

    body = _flat(MANUSCRIPT / "07_durability_canary.md")
    match = re.search(r"`([0-9a-f]{8})…([0-9a-f]{6})`", body)
    digest = registry_hash(PERSONAL_RED_LINES)

    assert match is not None, "the canary section must carry the truncated digest"
    assert match.group(1) == digest[:8]
    assert match.group(2) == digest[-6:]


def test_canary_section_line_count_phrase_matches_the_registry() -> None:
    """"the current seven lines yield the pinned digest" is recomputed."""

    match = re.search(r"the current (\w+) lines yield the pinned digest", _flat(MANUSCRIPT / "07_durability_canary.md"))

    assert match is not None, "the canary section must state the line count"
    assert match.group(1) == NUMBER_WORDS[len(PERSONAL_RED_LINES)]


def test_evidence_dimension_count_in_the_conclusion_matches_the_enum() -> None:
    """"nine evidence dimensions" equals the live EvidenceKind enum."""

    from red_line.model import EvidenceKind

    match = re.search(r"assemble the (\w+) evidence dimensions", _flat(MANUSCRIPT / "11_conclusion.md"))

    assert match is not None, "the conclusion must state the evidence-dimension count"
    assert match.group(1) == NUMBER_WORDS[len(EvidenceKind)]


def test_amendment_runbook_propagation_list_names_every_bound_surface() -> None:
    """The runbook's checklist must not omit a surface the tests now pin.

    The three amendment checklists disagreed; this makes the runbook's list the
    one that has to keep up with the enumerated surfaces.
    """

    runbook = _flat(ROOT / "docs" / "amendment-runbook.md")
    missing = [name for name in LINE_COUNT_SURFACES if name not in runbook]

    assert missing == [], f"amendment runbook omits bound surfaces: {missing}"


# --------------------------------------------------------------------------
# The two composition figures added prose numbers to 08 and 09a. Every one of
# them is recomputed here from `scope_token_membership`, in the same discipline
# as the counts above.
# --------------------------------------------------------------------------

WORD_NUMBERS = {
    30: "Thirty",
    31: "Thirty-one",
    32: "Thirty-two",
    33: "Thirty-three",
    34: "Thirty-four",
    35: "Thirty-five",
    36: "Thirty-six",
}


def test_lexical_limitation_prose_states_the_live_vocabulary_size() -> None:
    """08's "Thirty-four words decide what this evaluator can see" derives."""

    from red_line.analysis.registry_metrics import scope_token_membership

    membership = scope_token_membership()
    shared = [token for token, owners in membership if len(owners) > 1]
    body = _flat(MANUSCRIPT / "08_ambiguity_and_evaluation.md")

    assert f"{WORD_NUMBERS[len(membership)]} words decide what this evaluator can see" in body
    assert NUMBER_WORDS[len(shared)] + " of them belong to more than one line" in body


def test_collision_figure_caption_numbers_derive_from_membership() -> None:
    """09a's caption and cross-reference restate the same derived numbers."""

    from red_line.analysis.registry_metrics import scope_token_membership

    membership = scope_token_membership()
    shared = [token for token, owners in membership if len(owners) > 1]
    single = len(membership) - len(shared)
    body = _flat(MANUSCRIPT / "09a_registry_composition.md")

    assert f"every one of the {len(membership)} distinct canonical scope tokens" in body
    assert f"against each of the {NUMBER_WORDS[len(PERSONAL_RED_LINES)]} lines" in body
    assert f"the other {single} belong to one line each" in body
    for token in shared:
        assert f"`{token}`" in body


def test_composition_profile_caption_states_the_live_line_and_free_pass_counts() -> None:
    """09a's profile caption restates the line count and the zero free pass."""

    from red_line.analysis.registry_metrics import unevidenced_exemptions

    body = _flat(MANUSCRIPT / "09a_registry_composition.md")

    assert f"one of the {NUMBER_WORDS[len(PERSONAL_RED_LINES)]} lines in id order" in body
    assert unevidenced_exemptions() == ()
    assert "requiring no evidence at all, currently zero" in body
