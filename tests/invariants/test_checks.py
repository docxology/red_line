"""Tests for structural invariants — including proof-of-detection on planted-bad.

Per Algorithm doctrine: an invariant battery is only trustworthy if it actually
fails on a known-bad input. Each check is exercised against both the real
registry (must pass) and a deliberately broken registry (must fail).
"""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path

from red_line.invariants import checks

from red_line.invariants import (
    all_invariants,
    check_each_has_carve_out,
    check_has_both_standards,
    check_standard_analogs_not_air_gapped,
    check_unique_ids,
    invariants_pass,
)
from red_line import DeploymentTier, PERSONAL_RED_LINES, Severity
from red_line.model import EvidenceKind, Exemption


def _corrupt(record, **changes):
    """Plant an invalid state without bypassing normal constructor validation."""
    corrupted = replace(record)
    for name, value in changes.items():
        object.__setattr__(corrupted, name, value)
    return corrupted


def test_all_invariants_pass_on_real_registry():
    results = all_invariants(PERSONAL_RED_LINES)
    assert results, "battery must not be empty"
    assert all(r.passed for r in results), [r for r in results if not r.passed]
    assert invariants_pass(PERSONAL_RED_LINES) is True


def test_result_names_are_distinct():
    names = [r.name for r in all_invariants(PERSONAL_RED_LINES)]
    assert len(names) == len(set(names))


# ---- proof-of-detection: each check must FIRE on a planted defect ---------- #


def test_unique_ids_detects_duplicate():
    dupe = PERSONAL_RED_LINES + (replace(PERSONAL_RED_LINES[0]),)
    result = check_unique_ids(dupe)[0]
    assert result.passed is False
    assert "duplicate" in result.detail


def test_carve_out_check_detects_missing():
    stripped = (replace(PERSONAL_RED_LINES[0], carve_outs=()),) + PERSONAL_RED_LINES[1:]
    result = check_each_has_carve_out(stripped)[0]
    assert result.passed is False
    assert PERSONAL_RED_LINES[0].id in result.detail


def test_air_gap_check_detects_canary_air_gapped():
    # Force a CANARY line to permit air-gapped release — the pinned violation.
    s1 = next(rl for rl in PERSONAL_RED_LINES if rl.severity is Severity.CANARY)
    bad = tuple(
        replace(rl, max_tier=DeploymentTier.AIR_GAPPED) if rl.id == s1.id else rl for rl in PERSONAL_RED_LINES
    )
    result = check_standard_analogs_not_air_gapped(bad)[0]
    assert result.passed is False
    assert s1.id in result.detail
    assert invariants_pass(bad) is False


def test_has_both_standards_detects_missing_standard():
    without_s2 = tuple(rl for rl in PERSONAL_RED_LINES if rl.id != "s2-untargeted-profiling")
    result = check_has_both_standards(without_s2)[0]
    assert result.passed is False


def test_nonempty_text_detects_blank():
    blanked = (_corrupt(PERSONAL_RED_LINES[0], standard="   "),) + PERSONAL_RED_LINES[1:]
    assert invariants_pass(blanked) is False


def test_canary_demotion_detected():
    """Downgrading a Standard-analog line from CANARY severity trips the battery."""
    from red_line.invariants import check_standard_analogs_are_canary

    demoted = tuple(
        replace(rl, severity=Severity.STRONG) if rl.id == "s1-human-control-force" else rl
        for rl in PERSONAL_RED_LINES
    )
    result = check_standard_analogs_are_canary(demoted)[0]
    assert result.passed is False
    assert "s1-human-control-force" in result.detail
    assert invariants_pass(demoted) is False


def test_invalid_enum_field_detected():
    """A non-enum max_tier (possible via dataclasses.replace) trips the battery."""
    from red_line.invariants import check_enum_field_types

    corrupted = (_corrupt(PERSONAL_RED_LINES[0], max_tier="garbage"),) + PERSONAL_RED_LINES[1:]
    result = check_enum_field_types(corrupted)[0]
    assert result.passed is False
    assert invariants_pass(corrupted) is False


def test_zero_scope_line_detected():
    """Gutting a line's scope makes it unreachable — the battery must catch it."""
    from red_line.invariants import check_nonempty_scope

    gutted = (_corrupt(PERSONAL_RED_LINES[0], scope=()),) + PERSONAL_RED_LINES[1:]
    result = check_nonempty_scope(gutted)[0]
    assert result.passed is False
    assert PERSONAL_RED_LINES[0].id in result.detail
    assert invariants_pass(gutted) is False


def test_empty_carve_out_clause_detected():
    """A carve-out clause with no content tokens is a carve-out in name only."""
    blanked = (replace(PERSONAL_RED_LINES[0], carve_outs=("does not",)),) + PERSONAL_RED_LINES[1:]
    assert invariants_pass(blanked) is False
    empty = (_corrupt(PERSONAL_RED_LINES[0], carve_outs=("",)),) + PERSONAL_RED_LINES[1:]
    assert invariants_pass(empty) is False


def test_typed_exemption_check_detects_missing_exemption():
    """A line without an executable exemption surface must fail closed."""
    from red_line.invariants import check_typed_exemptions

    stripped = (replace(PERSONAL_RED_LINES[0], exemptions=()),) + PERSONAL_RED_LINES[1:]
    result = check_typed_exemptions(stripped)[0]
    assert result.passed is False
    assert PERSONAL_RED_LINES[0].id in result.detail
    assert invariants_pass(stripped) is False


def test_typed_exemption_check_detects_hollow_and_invalid_exemptions():
    from red_line.invariants import check_typed_exemptions

    line = PERSONAL_RED_LINES[0]
    invalid_id = _corrupt(
        Exemption("valid-id", "description", frozenset({"support"}), frozenset({EvidenceKind.PURPOSE})),
        id=" ",
    )
    hollow = replace(line, exemptions=(invalid_id,))
    assert check_typed_exemptions((hollow,) + PERSONAL_RED_LINES[1:])[0].passed is False

    empty_trigger = _corrupt(
        Exemption("empty-trigger", "description", frozenset({"support"}), frozenset({EvidenceKind.PURPOSE})),
        trigger_scope=frozenset(),
    )
    empty_trigger = replace(line, exemptions=(empty_trigger,))
    assert check_typed_exemptions((empty_trigger,) + PERSONAL_RED_LINES[1:])[0].passed is False

    empty_evidence = _corrupt(
        Exemption("empty-evidence", "description", frozenset({"support"}), frozenset({EvidenceKind.PURPOSE})),
        required_evidence=frozenset(),
    )
    empty_evidence = replace(line, exemptions=(empty_evidence,))
    assert check_typed_exemptions((empty_evidence,) + PERSONAL_RED_LINES[1:])[0].passed is False

    invalid_kind = _corrupt(
        Exemption("invalid-kind", "description", frozenset({"support"}), frozenset({EvidenceKind.PURPOSE})),
        required_evidence=frozenset({"purpose"}),
    )
    invalid_kind = replace(line, exemptions=(invalid_kind,))
    assert check_typed_exemptions((invalid_kind,) + PERSONAL_RED_LINES[1:])[0].passed is False


# ---------------------------------------------------------------------------
# The documentation is part of the battery's surface: a reader who trusts
# docs/invariants.md to enumerate the checks was reading ten while the code ran
# fourteen. These recompute the document from `all_invariants()`.
# ---------------------------------------------------------------------------

_DOC = Path(__file__).resolve().parents[2] / "docs" / "invariants.md"

_SECTION_RE = re.compile(r"^### (\d+)\. `([a-z_]+)` — `(check_[a-z_]+)`$", re.MULTILINE)
_TABLE_ROW_RE = re.compile(r"^\| `([a-z_]+)` \| `(check_[a-z_]+)` \| [^|]+ \|$", re.MULTILINE)


def _live_invariant_names() -> list[str]:
    """Invariant names in the order `all_invariants` emits them."""

    return [result.name for result in all_invariants()]


def test_the_live_battery_is_not_empty():
    """A documentation gate over an empty battery would certify nothing."""

    assert len(_live_invariant_names()) >= 10


def test_documented_invariants_are_exactly_the_live_battery():
    """Numbered sections, in order, equal the checks the code actually runs."""

    body = _DOC.read_text(encoding="utf-8")
    sections = _SECTION_RE.findall(body)
    numbers = [int(number) for number, _, _ in sections]
    documented = [name for _, name, _ in sections]

    assert documented == _live_invariant_names()
    assert numbers == list(range(1, len(documented) + 1)), "sections must be numbered 1..N in order"


def test_documented_sections_name_the_function_that_produces_each_result():
    """Each section's `check_*` must exist and emit the name in its heading."""

    body = _DOC.read_text(encoding="utf-8")

    for _, name, function_name in _SECTION_RE.findall(body):
        function = getattr(checks, function_name)
        produced = {result.name for result in function(PERSONAL_RED_LINES)}
        assert produced == {name}, f"{function_name} does not emit {name!r}"


def test_summary_table_covers_the_same_battery_as_the_sections():
    """The table is the part a skimmer reads; it must not drift on its own."""

    body = _DOC.read_text(encoding="utf-8")
    rows = _TABLE_ROW_RE.findall(body)

    assert [name for name, _ in rows] == _live_invariant_names()
    assert [function for _, function in rows] == [
        function for _, _, function in _SECTION_RE.findall(body)
    ]


def test_the_documentation_gate_fails_on_a_removed_section(tmp_path):
    """Planted defect: drop one section and assert the comparison goes red."""

    body = _DOC.read_text(encoding="utf-8")
    sections = _SECTION_RE.findall(body)
    victim = sections[-1]
    mutilated = body.replace(f"### {victim[0]}. `{victim[1]}` — `{victim[2]}`", "### removed", 1)
    assert mutilated != body

    documented = [name for _, name, _ in _SECTION_RE.findall(mutilated)]

    assert documented != _live_invariant_names()
