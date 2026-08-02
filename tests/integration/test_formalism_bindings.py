"""Bind `08a_formalism.md` to the code it claims to describe.

Every test here first *derives* a fact by running the real package — the
registry, the evaluator, the analysis reports, the enums — and only then asserts
that the manuscript states exactly that fact. Corrupting a sentence in the
formalism section reddens the matching test; corrupting the code reddens the
derivation inside it. Nothing is asserted that was not first executed.

The module also owns the structural gates for the auto-numbering syntax the
render engine's ``formalism.lua`` filter consumes: every block carries a label,
every ``[@label]`` reference resolves to a declared block, and no manuscript
file writes a formalism number by hand. Hand numbering is the defect the filter
exists to remove, so a reintroduced ``Definition 3`` in the source has to fail
rather than quietly ship a number that renumbers itself on the next insertion.
"""

from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path

import pytest

from red_line import PERSONAL_RED_LINES
from red_line.analysis.evidence_sensitivity import run_evidence_sensitivity
from red_line.analysis.monotonicity import (
    STRICTNESS_ORDER,
    TIERS_BY_DESCENDING_OVERSIGHT,
    run_monotonicity_sweep,
    strictness_is_monotone,
)
from red_line.analysis.outcome_coverage import BATTERY_AS_OF, _verified_context, run_outcome_coverage
from red_line.analysis.registry_metrics import exemption_evidence_matrix, unevidenced_exemptions
from red_line.analysis.trigger_semantics import run_trigger_semantics
from red_line.evaluation import evaluate_action
from red_line.model import (
    ActionAssessment,
    AssessmentReasonCode,
    Classification,
    DeploymentTier,
    EvidenceKind,
    EvidenceStatus,
    ExemptionMatchMode,
    ProposedAction,
    RedLine,
    Severity,
)
from red_line.model.action import DEFAULT_EVIDENCE_MAX_AGE_DAYS
from red_line.model.red_line import normalize_scope

ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "manuscript"
FORMALISM = MANUSCRIPT / "08a_formalism.md"

#: The module the binding table's prose declares once, so each cell can carry a
#: bare function name rather than repeating a 90-character path nine times.
_TEST_MODULE = re.compile(r"names a test in `(tests/[\w/]+\.py)`")
#: A verifying-test cell: a backticked ``test_*`` function name.
_TEST_REF = re.compile(r"`(test_\w+)`")
#: A formalism block opener: ``::: {.definition #def:x title="X"}``.
_BLOCK = re.compile(r"^::: \{\.(?P<kind>[a-z]+)(?P<attrs>[^}]*)\}\s*$", re.M)
_LABEL = re.compile(r"#([a-z]+:[a-z0-9-]+)")
_REFERENCE = re.compile(r"\[@((?:def|prop|thm|lem|cor|rem|ax|claim|ex):[a-z0-9-]+)\]")
#: A hand-written formalism number, which the auto-numbering filter forbids.
_HAND_NUMBER = re.compile(
    r"\b(Definition|Proposition|Theorem|Lemma|Corollary|Remark|Axiom|Claim|Example)\s+\d+\b"
)
#: The nine kinds ``formalism.lua`` numbers, so a Div class typo is caught here
#: rather than shipping an unnumbered block.
_FORMALISM_KINDS = frozenset(
    {
        "definition",
        "proposition",
        "theorem",
        "lemma",
        "corollary",
        "remark",
        "axiom",
        "claim",
        "example",
    }
)

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
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    45: "forty-five",
    58: "fifty-eight",
    108: "one hundred and eight",
}


def _mathtt(value: str) -> str:
    """The LaTeX ``\\mathtt{...}`` spelling of one enum value.

    Built here rather than inline so the underscore escaping is written once
    and so no assertion needs a backslash inside an f-string, which the
    project's Python floor (3.10) does not allow.
    """

    return "\\mathtt{" + value.replace("_", "\\_") + "}"


def _flat(path: Path) -> str:
    """Whitespace-normalized text, so bindings survive hard line wrapping."""

    return " ".join(path.read_text(encoding="utf-8").split())


def _formalism() -> str:
    return _flat(FORMALISM)


def _body_files() -> list[Path]:
    """Every numbered manuscript body file, excluding the renderer preamble."""

    return [path for path in sorted(MANUSCRIPT.glob("*.md")) if path.name != "preamble.md"]


def _blocks(text: str) -> list[tuple[str, str]]:
    """Return ``(kind, label)`` for every formalism block opener in ``text``."""

    found: list[tuple[str, str]] = []
    for match in _BLOCK.finditer(text):
        kind = match.group("kind")
        if kind not in _FORMALISM_KINDS:
            continue
        label = _LABEL.search(match.group("attrs"))
        found.append((kind, label.group(1) if label else ""))
    return found


def _declared_labels() -> dict[str, str]:
    """Map every declared formalism label to its kind, across the manuscript."""

    labels: dict[str, str] = {}
    for path in _body_files():
        for kind, label in _blocks(path.read_text(encoding="utf-8")):
            if label:
                labels[label] = kind
    return labels


def _binding_rows() -> list[tuple[str, str]]:
    """Return ``(proposition label, verifying-test cell)`` for every table row."""

    rows: list[tuple[str, str]] = []
    for line in FORMALISM.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\| \[@(prop:[a-z0-9-]+)\] \|", line)
        if match is None:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        assert len(cells) == 3, line
        rows.append((match.group(1), cells[2]))
    return rows


# --------------------------------------------------------------------------
# Structural gates for the auto-numbering syntax.
# --------------------------------------------------------------------------


def test_the_formalism_scan_set_is_not_empty() -> None:
    """Guards every structural gate below against becoming vacuous."""

    blocks = _blocks(FORMALISM.read_text(encoding="utf-8"))

    assert len(blocks) >= 15, "08a must carry the formalism blocks these gates check"
    assert {kind for kind, _ in blocks} == {"definition", "proposition"}
    assert _body_files(), "no manuscript body files found"


def test_every_formalism_block_carries_a_prefixed_label() -> None:
    """An unlabelled block is numbered but unreferenceable, so it must fail."""

    unlabelled: list[tuple[str, str]] = []
    for path in _body_files():
        for kind, label in _blocks(path.read_text(encoding="utf-8")):
            if not re.fullmatch(r"[a-z]+:[a-z0-9-]+", label):
                unlabelled.append((path.name, kind))

    assert unlabelled == []


def test_every_formalism_label_is_declared_exactly_once() -> None:
    """A duplicate label makes one of two blocks unreachable by reference."""

    seen: list[str] = []
    for path in _body_files():
        seen.extend(label for _, label in _blocks(path.read_text(encoding="utf-8")) if label)

    assert len(seen) == len(set(seen)), sorted({label for label in seen if seen.count(label) > 1})


def test_every_formalism_reference_resolves_to_a_declared_block() -> None:
    """``[@prop:typo]`` must fail here, not ship as literal markup in the PDF."""

    declared = _declared_labels()
    assert declared, "no labels declared; this gate would be vacuous"
    dangling: list[tuple[str, str]] = []
    for path in _body_files():
        for label in _REFERENCE.findall(path.read_text(encoding="utf-8")):
            if label not in declared:
                dangling.append((path.name, label))

    assert dangling == []


def test_reference_prefixes_agree_with_the_kind_they_name() -> None:
    """``[@def:x]`` must point at a definition and ``[@prop:x]`` at a proposition."""

    expected = {"def": "definition", "prop": "proposition"}
    declared = _declared_labels()
    mismatched = [
        (label, kind)
        for label, kind in declared.items()
        if label.split(":", 1)[0] in expected and expected[label.split(":", 1)[0]] != kind
    ]

    assert mismatched == []


def test_no_manuscript_file_hand_writes_a_formalism_number() -> None:
    """The whole point of the filter is that no number lives in the source."""

    offenders: list[tuple[str, str]] = []
    for path in _body_files():
        body = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        body = re.sub(r"`[^`\n]*`", "", body)
        offenders.extend((path.name, match.group(0)) for match in _HAND_NUMBER.finditer(body))

    assert offenders == []


def test_the_hand_number_guard_rejects_a_planted_literal() -> None:
    """Proof of detection: the guard must fire on the wording it forbids."""

    planted = "By Definition 3, the registry is well formed. See Proposition 12 as well."
    stripped = re.sub(r"`[^`\n]*`", "", planted)

    assert [match.group(0) for match in _HAND_NUMBER.finditer(stripped)] == [
        "Definition 3",
        "Proposition 12",
    ]


def test_the_dangling_reference_guard_rejects_a_planted_typo() -> None:
    """Proof of detection: an undeclared label must be reported, not passed."""

    declared = _declared_labels()
    planted = "resolved by [@prop:tier-monotone] but not by [@prop:tier-monotonic]."

    found = _REFERENCE.findall(planted)

    assert found == ["prop:tier-monotone", "prop:tier-monotonic"]
    assert [label for label in found if label not in declared] == ["prop:tier-monotonic"]


def test_the_unlabelled_block_guard_rejects_a_planted_block() -> None:
    """Proof of detection: a block written without a label must be caught."""

    planted = '::: {.definition title="No label"}\nbody\n:::\n'

    assert _blocks(planted) == [("definition", "")]


def test_every_proposition_has_a_binding_table_row_naming_a_real_test() -> None:
    """Each proposition is bound, and every named test exists on disk.

    The module is declared once in the table's own prose and parsed from there,
    so the path is read rather than assumed and a rename that misses the prose
    fails here instead of leaving nine cells pointing at nothing.
    """

    raw = FORMALISM.read_text(encoding="utf-8")
    propositions = [label for kind, label in _blocks(raw) if kind == "proposition"]
    rows = _binding_rows()

    declared_module = _TEST_MODULE.search(" ".join(raw.split()))
    assert declared_module is not None, "the binding table must name its test module"
    module = ROOT / declared_module.group(1)
    assert module.is_file(), declared_module.group(1)
    module_body = module.read_text(encoding="utf-8")

    assert propositions, "08a declares no propositions"
    assert [label for label, _ in rows] == propositions, "table order must follow the propositions"

    for label, cell in rows:
        references = _TEST_REF.findall(cell)
        assert references, f"{label} names no verifying test"
        for function in references:
            assert f"def {function}(" in module_body, function


def test_the_formalism_claim_ledger_matches_the_declared_labels() -> None:
    """The evidence ledger the render engine reads is re-derived, never kept by hand.

    The engine's evidence registry knows ``fig:``/``sec:``/``tbl:``/``eq:``/``lst:``
    label prefixes and treats every other ``[@x]`` as a bibliography key, so a
    formalism reference is reported as an unsupported citation unless the
    project declares it. ``data/formalism_claim_ledger.json`` is that
    declaration; a block added, renamed, or removed without the ledger
    following fails here rather than surfacing as a red output-validation
    report after a render.
    """

    ledger = json.loads((ROOT / "data" / "formalism_claim_ledger.json").read_text(encoding="utf-8"))
    rows = ledger["claims"]
    declared = set(_declared_labels())
    citations = {row["value"] for row in rows if row["kind"] == "citation"}
    numbers = {row["value"] for row in rows if row["kind"] == "number"}

    assert declared, "no labels declared; this gate would be vacuous"
    assert citations == declared, sorted(citations ^ declared)
    assert numbers == {DEFAULT_EVIDENCE_MAX_AGE_DAYS}
    assert len({row["claim_id"] for row in rows}) == len(rows), "claim ids must be unique"
    for row in rows:
        assert (ROOT / row["source_path"]).is_file(), row["source_path"]
        assert row["freshness"] == "active", row["claim_id"]


def test_the_claim_ledger_guard_rejects_an_unlisted_label() -> None:
    """Proof of detection: a label missing from the ledger must be reported."""

    ledger = json.loads((ROOT / "data" / "formalism_claim_ledger.json").read_text(encoding="utf-8"))
    citations = {row["value"] for row in ledger["claims"] if row["kind"] == "citation"}
    planted = citations - {"prop:tier-monotone"}

    assert planted != set(_declared_labels())
    assert sorted(set(_declared_labels()) - planted) == ["prop:tier-monotone"]


def test_the_binding_table_guard_rejects_an_emptied_row() -> None:
    """Proof of detection: a row whose verifying-test cell is blank is caught."""

    rows = _binding_rows()
    assert rows, "no table rows parsed, so this guard would be vacuous"
    planted = [(label, "" if index == 0 else cell) for index, (label, cell) in enumerate(rows)]
    unbound = [label for label, cell in planted if not _TEST_REF.findall(cell)]

    assert unbound == [rows[0][0]]


# --------------------------------------------------------------------------
# Definitions: the domain objects, re-derived and then read back.
# --------------------------------------------------------------------------


def test_tier_rank_definition_matches_the_enum() -> None:
    """[@def:tier]'s ranks are the ones ``oversight_rank`` returns."""

    ranks = {tier.value: tier.oversight_rank for tier in DeploymentTier}
    text = _formalism()

    assert ranks == {"air_gapped": 0, "connected": 1, "hosted": 2}
    assert sorted(ranks.values()) == list(range(len(DeploymentTier)))
    for value, rank in sorted(ranks.items()):
        assert "\\rho(" + _mathtt(value) + ") = " + str(rank) in text
    codomain = ",".join(str(rank) for rank in sorted(ranks.values()))
    assert "\\rho: T \\to \\{" + codomain + "\\}" in text


def test_severity_and_status_vocabularies_are_listed_in_full() -> None:
    """[@def:severity] and [@def:evidence-status] enumerate the live enums."""

    text = _formalism()

    for severity in Severity:
        assert _mathtt(severity.value) in text
    for status in EvidenceStatus:
        assert _mathtt(status.value.upper()) in text
    grades = ", ".join(_mathtt(severity.value) for severity in Severity)
    assert "The severity grades are $\\{" + grades + "\\}$" in text


def test_evidence_kind_definition_lists_all_nine_dimensions_in_enum_order() -> None:
    """[@def:evidence-kind] states the enum's size and every member."""

    kinds = list(EvidenceKind)
    text = _formalism()

    assert f"the {NUMBER_WORDS[len(kinds)]}-element set $K$" in text
    positions = [text.index("\\mathtt{" + kind.value.replace("_", "\\_") + "}") for kind in kinds]
    assert positions == sorted(positions), "the definition must list K in enum order"


def test_staleness_window_in_the_definition_is_the_configured_default() -> None:
    """[@def:evidence-record]'s 180-day window is the package default."""

    assert f"$w = {DEFAULT_EVIDENCE_MAX_AGE_DAYS}$ days" in _formalism()


def test_missing_value_markers_in_the_definition_match_the_code() -> None:
    """[@def:context]'s unsupported-value list is the one the model uses."""

    from red_line.model.action import _MISSING_VALUES

    text = _formalism()
    markers = sorted(value for value in _MISSING_VALUES if value)

    assert markers, "the marker set is empty; this gate would be vacuous"
    for marker in markers:
        assert f"`{marker}`" in text


def test_red_line_field_count_in_the_definition_is_the_dataclass_arity() -> None:
    """[@def:red-line]'s "eleven-field record" is ``dataclasses.fields``."""

    fields = dataclasses.fields(RedLine)

    assert f"{NUMBER_WORDS[len(fields)]}-field record" in _formalism()


def test_classification_definition_lists_all_five_outcomes() -> None:
    """[@def:classification] states the size and every member of the enum."""

    text = _formalism()

    assert f"the {NUMBER_WORDS[len(Classification)]}-element set $C$" in text
    for classification in Classification:
        assert _mathtt(classification.value.upper()) in text


def test_effective_scope_definition_matches_the_evaluator() -> None:
    """[@def:action]: the tier value really is a token in the matched scope.

    Derived by probing the live registry, whose ``retained-oversight``
    exemption triggers on ``hosted`` and ``connected`` — tokens the action
    never declares. If the evaluator stopped unioning the tier in, the same
    action would stop being narrowed.
    """

    scope = frozenset({"model_release", "task_specific"})
    hosted = ProposedAction(
        description="effective-scope probe",
        scope=scope,
        context=_verified_context(),
        tier=DeploymentTier.HOSTED,
    )
    assessment = evaluate_action(hosted, PERSONAL_RED_LINES, as_of=BATTERY_AS_OF)
    triggers = {
        token
        for line in PERSONAL_RED_LINES
        for exemption in line.exemptions
        for token in normalize_scope(exemption.trigger_scope)
    }

    assert assessment.classification is Classification.COMPLIANT
    assert DeploymentTier.HOSTED.value in triggers, "no exemption triggers on a tier token"
    assert "E = \\mathcal{N}(S) \\cup \\{t\\}" in _formalism()


def test_strictness_order_definition_matches_the_analysis_module() -> None:
    """[@def:strictness] ranks exactly the three verdicts the code ranks."""

    ranked = sorted(STRICTNESS_ORDER, key=lambda item: STRICTNESS_ORDER[item])
    unranked = sorted(set(Classification) - set(STRICTNESS_ORDER), key=lambda item: item.value)
    text = _formalism()

    assert [item.value for item in ranked] == [
        "compliant",
        "requires_modification",
        "non_compliant",
    ]
    assert len(unranked) == 2
    chain = " < ".join(_mathtt(item.value.upper()) for item in ranked)
    assert chain in text
    with pytest.raises(ValueError, match="outside the policy strictness lattice"):
        strictness_is_monotone((unranked[0],))


# --------------------------------------------------------------------------
# Propositions: each derived by execution, then read back from the prose.
# --------------------------------------------------------------------------


def test_intake_precedence_holds_against_every_registry() -> None:
    """[@prop:intake-precedence]: a defect stops before any line is read."""

    defective = ProposedAction(
        description="ambiguous intake with a complete evidence ledger",
        scope=frozenset({"targeting"}),
        context=_verified_context(),
        tier=DeploymentTier.HOSTED,
        ambiguous=True,
    )
    for registry in (PERSONAL_RED_LINES, ()):
        assessment = evaluate_action(defective, registry, as_of=BATTERY_AS_OF)
        assert assessment.classification is Classification.INSUFFICIENT_INFORMATION
        assert assessment.implicated == ()
        assert AssessmentReasonCode.INTAKE_BLOCKED in assessment.reason_codes

    # Without the defect the same action is a policy result, so the assertion
    # above is about the gate and not about the scope being harmless.
    clean = dataclasses.replace(defective, ambiguous=False)
    assert evaluate_action(clean, PERSONAL_RED_LINES, as_of=BATTERY_AS_OF).classification is (
        Classification.NON_COMPLIANT
    )

    text = _formalism()
    assert "including the empty one — the result is `INSUFFICIENT_INFORMATION`" in text
    assert "the implicated-line tuple is empty" in text
    assert f"the reason codes include `{AssessmentReasonCode.INTAKE_BLOCKED.value}`" in text


def test_evidence_conjunction_matches_the_executed_sweep() -> None:
    """[@prop:evidence-conjunction]: 45 perturbations, all blocked and localized."""

    report = run_evidence_sensitivity()
    text = _formalism()

    assert report.baseline is Classification.COMPLIANT
    assert report.evaluation_count == len(EvidenceKind) * len(report.perturbations)
    assert report.blocked_count == report.evaluation_count
    assert report.localized_count == report.evaluation_count
    assert report.conjunctive
    assert {cell.reached for cell in report.cells} == {Classification.INSUFFICIENT_INFORMATION}

    assert (
        f"Across the {NUMBER_WORDS[len(EvidenceKind)]} dimensions and the "
        f"{NUMBER_WORDS[len(report.perturbations)]} degradations, all "
        f"{NUMBER_WORDS[report.evaluation_count]} executed evaluations return "
        "`INSUFFICIENT_INFORMATION`" in text
    )
    assert f"each of the {NUMBER_WORDS[report.localized_count]} names exactly the degraded" in text


def test_outcome_precedence_is_exhaustive_and_ordered() -> None:
    """[@prop:outcome-precedence]: the four branches, in the code's order.

    Derived by reading the branch order out of the evaluator source rather than
    restating it, and by exercising one action per branch through the live
    registry so the ordering claim is not merely lexical.
    """

    source = (
        ROOT / "src" / "red_line" / "evaluation" / "evaluator.py"
    ).read_text(encoding="utf-8")
    tail = source.split("    if hard_block:", 1)[1]
    order = re.findall(r"classification = Classification\.([A-Z_]+)", tail)

    assert order == [
        "NON_COMPLIANT",
        "REQUIRES_MODIFICATION",
        "COMPLIANT",
        "OUTSIDE_SCOPE",
    ]

    probes = {
        "NON_COMPLIANT": frozenset({"targeting"}),
        "REQUIRES_MODIFICATION": frozenset({"surveillance", "profiling", "aggregate_research"}),
        "COMPLIANT": frozenset({"cogsec", "education"}),
        "OUTSIDE_SCOPE": frozenset({"static_documentation"}),
    }
    for expected, scope in probes.items():
        action = ProposedAction(
            description=f"precedence probe for {expected}",
            scope=scope,
            context=_verified_context(),
            tier=DeploymentTier.HOSTED,
        )
        reached = evaluate_action(action, PERSONAL_RED_LINES, as_of=BATTERY_AS_OF).classification
        assert reached.value.upper() == expected, expected

    text = _formalism()
    for index, name in enumerate(order):
        marker = "if any covering line has no satisfied exemption" if index == 0 else f"`{name}`"
        assert marker in text
    assert "The four cases are exhaustive and mutually exclusive" in text


def test_outcome_reachability_matches_the_executed_battery() -> None:
    """[@prop:outcome-reachability]: all five reached; the empty registry is not."""

    live = run_outcome_coverage()
    empty = run_outcome_coverage(())

    assert live.complete and live.all_matched
    assert set(live.reached) == set(Classification)
    unreachable = set(empty.unreached)
    assert unreachable == {
        Classification.COMPLIANT,
        Classification.REQUIRES_MODIFICATION,
        Classification.NON_COMPLIANT,
    }

    text = _formalism()
    assert "Each of the five classifications of [@def:classification] is returned" in text
    assert f"the {NUMBER_WORDS[len(unreachable)]} implication-dependent outcomes become unreachable" in text


def test_exemption_evidence_floor_is_derived_from_the_registry() -> None:
    """[@prop:exemption-evidence]: 16 exemptions, minimum two evidence kinds."""

    rows = exemption_evidence_matrix()
    minimum = min(row.required_count for row in rows)

    assert unevidenced_exemptions() == ()
    assert minimum >= 2

    text = _formalism()
    assert f"every one of the {NUMBER_WORDS[len(rows)]} typed exemptions requires at least" in text
    assert f"at least {NUMBER_WORDS[minimum]} evidence kinds" in text


def test_trigger_mode_counts_match_the_executed_probe() -> None:
    """[@prop:trigger-mode]: 13 ANY, 3 ALL, 58 runs, every row consistent."""

    report = run_trigger_semantics()
    all_rows = [row for row in report.rows if row.match_mode == ExemptionMatchMode.ALL.value]
    trigger_sizes = {len(row.trigger_scope) for row in all_rows}

    assert report.consistent
    assert report.any_mode_count + report.all_mode_count == len(report.rows)
    assert trigger_sizes == {2}
    for row in all_rows:
        assert row.single_match_count == 0
        assert row.full.matched
        assert {probe.reached for probe in row.singles} == {Classification.NON_COMPLIANT}
        assert row.full.reached is Classification.COMPLIANT
    for row in report.rows:
        if row.match_mode == ExemptionMatchMode.ANY.value:
            assert row.single_match_count == len(row.trigger_scope)

    text = _formalism()
    assert (
        f"carries {NUMBER_WORDS[report.any_mode_count]} `any`-mode and "
        f"{NUMBER_WORDS[report.all_mode_count]} `all`-mode exemptions" in text
    )
    assert f"exactly {NUMBER_WORDS[max(trigger_sizes)]} trigger tokens" in text
    assert f"{NUMBER_WORDS[report.evaluation_count]} executed evaluations" in text


def test_tier_monotonicity_numbers_match_the_executed_sweep() -> None:
    """[@prop:tier-monotone]: 108 evaluations, zero inversions."""

    report = run_monotonicity_sweep()

    assert report.monotone
    assert report.inversion_count == 0
    assert report.evaluation_count == report.keyword_count * len(TIERS_BY_DESCENDING_OVERSIGHT)
    assert report.tiers == TIERS_BY_DESCENDING_OVERSIGHT

    text = _formalism()
    chain = " \\to ".join(
        "\\mathtt{" + tier.value.replace("_", "\\_") + "}" for tier in report.tiers
    )
    assert chain in text
    assert (
        f"is {NUMBER_WORDS[report.evaluation_count]} executed evaluations with "
        f"{NUMBER_WORDS[report.inversion_count] if report.inversion_count in NUMBER_WORDS else report.inversion_count} inversions"
        in text
        or f"is {NUMBER_WORDS[report.evaluation_count]} executed evaluations with zero inversions" in text
    )


def test_normalization_closure_is_executed_not_asserted() -> None:
    """[@prop:normalization-closure]: idempotence, then the fail-closed stop."""

    declared = frozenset(
        token for line in PERSONAL_RED_LINES for token in line.scope
    ) | frozenset({"Autonomous-Weapons", "BULK  DATA", "opt-in"})
    once = normalize_scope(declared)

    assert normalize_scope(once) == once

    # Layer one: an ordinary caller cannot construct the action at all.
    homoglyph = "surveillancе"  # Cyrillic 'е' in place of the Latin one
    assert not homoglyph.isascii()
    with pytest.raises(ValueError, match="ASCII after Unicode normalization"):
        ProposedAction(
            description="Cyrillic homoglyph masquerading as a declared token",
            scope=frozenset({homoglyph}),
            context=_verified_context(),
            tier=DeploymentTier.HOSTED,
        )

    # Layer two: write the token past the constructor into the frozen record,
    # the way the hardening suite does, and require the evaluator's own
    # defensive normalization to stop it rather than reach policy matching.
    smuggled = ProposedAction(
        description="Cyrillic homoglyph smuggled past the constructor",
        scope=frozenset({"teaching"}),
        context=_verified_context(),
        tier=DeploymentTier.HOSTED,
    )
    object.__setattr__(smuggled, "scope", frozenset({homoglyph}))
    assessment = evaluate_action(smuggled, PERSONAL_RED_LINES, as_of=BATTERY_AS_OF)

    assert assessment.classification is Classification.INSUFFICIENT_INFORMATION
    assert AssessmentReasonCode.INVALID_SCOPE in assessment.reason_codes
    assert assessment.normalized_scope == ()

    text = _formalism()
    assert "\\mathcal{N}(\\mathcal{N}(S)) = \\mathcal{N}(S)" in text
    assert "the rejection is enforced twice" in text
    assert f"`{AssessmentReasonCode.INVALID_SCOPE.value}` reason code" in text


def test_reason_code_vocabulary_is_closed_and_duplicate_free() -> None:
    """[@prop:reason-codes]: codes come from the enum and never repeat."""

    seen: set[AssessmentReasonCode] = set()
    for scope in (
        frozenset({"targeting"}),
        frozenset({"cogsec", "education"}),
        frozenset({"static_documentation"}),
        frozenset({"surveillance", "profiling", "aggregate_research"}),
    ):
        action = ProposedAction(
            description="reason-code probe",
            scope=scope,
            context=_verified_context(),
            tier=DeploymentTier.AIR_GAPPED,
        )
        codes = evaluate_action(action, PERSONAL_RED_LINES, as_of=BATTERY_AS_OF).reason_codes
        assert len(codes) == len(set(codes))
        assert set(codes) <= set(AssessmentReasonCode)
        seen |= set(codes)

    assert len(seen) >= 4, "the probe set exercises too few codes to be meaningful"
    duplicated = tuple(sorted(seen, key=lambda code: code.value))[:1] * 2
    with pytest.raises(ValueError, match="reason_codes must be unique"):
        ActionAssessment(
            action=ProposedAction(
                description="duplicate-code probe",
                scope=frozenset({"targeting"}),
                context=_verified_context(),
            ),
            classification=Classification.NON_COMPLIANT,
            implicated=(),
            reason_codes=duplicated,
        )

    assert "appended in evaluation order and never repeated" in _formalism()


def test_report_envelope_field_count_is_the_dataclass_arity() -> None:
    """[@def:report-envelope]'s "ten fields, in order" is ``dataclasses.fields``."""

    from red_line import ENVELOPE_SCHEMA, REPORT_SCHEMA, ReportEnvelope

    fields = dataclasses.fields(ReportEnvelope)
    text = _formalism()

    assert f"exactly those {NUMBER_WORDS[len(fields)]} fields, in order" in text
    assert f"`{ENVELOPE_SCHEMA}`" in text
    assert f"(`{REPORT_SCHEMA}`)" in text
    for field in fields:
        assert field.name.replace("_", "\\_") in text, field.name


def test_envelope_pointer_agreement_is_executed_not_asserted() -> None:
    """[@prop:envelope-pointer] is re-derived through a live export and edits.

    A real evaluator finding is wrapped, the agreement check must hold, and
    every checked field is edited once to prove the disagreement is visible —
    the manuscript's "editing any checked field afterwards makes the check
    return false" is measured, not transcribed.
    """

    from red_line import (
        envelope_matches_finding,
        finding_envelope,
        review_engagement,
    )
    from tests.helpers import action

    finding = review_engagement(
        action(
            "Targeting component with no adjacent-use narrowing",
            frozenset({"targeting"}),
        ),
        reviewed_on="2026-07-15",
    )
    envelope = finding_envelope(finding, subject_id="formalism-binding")
    assert envelope_matches_finding(envelope, finding)
    for tamper in (
        {"report_ref": "0" * 64},
        {"review_date": "2001-01-01"},
        {"registry_digest": "0" * 64},
        {"native_status": "compliant"},
    ):
        edited = dataclasses.replace(envelope, **tamper)
        assert not envelope_matches_finding(edited, finding), tamper
    text = _formalism()
    assert "editing any checked field afterwards makes the check return false" in text
    assert "does not certify the finding true" in text


def test_staleness_exclusive_boundary_is_derived_from_the_code() -> None:
    """[@prop:staleness-boundary]: the window edge is exclusive and matches the code.

    Derived by constructing a record at a known date and probing exactly at the
    window edge and one day past it, using the same EvidenceRecord.is_stale that
    the evaluator calls.
    """

    from datetime import date, timedelta

    from red_line.model import EvidenceKind, EvidenceRecord, EvidenceStatus

    recorded = date(2026, 7, 15)
    record = EvidenceRecord(
        kind=EvidenceKind.PURPOSE,
        reference="test://evidence/staleness-binding",
        summary="staleness boundary probe",
        status=EvidenceStatus.VERIFIED,
        recorded_on=recorded.isoformat(),
    )
    edge = recorded + timedelta(days=DEFAULT_EVIDENCE_MAX_AGE_DAYS)
    assert record.is_stale(edge) is False
    assert record.is_stale(edge + timedelta(days=1)) is True

    text = _formalism()
    assert "a - d > w" in text
    assert "exactly $w$ days before the review date is fresh" in text
    assert "$w + 1$ days before is stale" in text
    assert "the window's last fresh day is age $w$" in text
