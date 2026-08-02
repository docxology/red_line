"""Tests for canary verification and freshness checks."""

from __future__ import annotations

from dataclasses import replace

from red_line.canary import (
    CanaryStatement,
    DEFAULT_CANARY_TEXT,
    DEFAULT_MAX_AGE_DAYS,
    detect_line_removal,
    is_stale,
    issue_canary,
    registry_hash,
    verify_canary,
)
from red_line.model import DeploymentTier, RedLine, Severity
from red_line.registry import PERSONAL_RED_LINES


def test_verify_canary_intact():
    canary = issue_canary("2026-07-15")
    # Explicit as_of so this never decays into a time-bomb once the issue date
    # ages past the freshness window.
    v = verify_canary(canary, PERSONAL_RED_LINES, as_of="2026-07-20")
    assert v.intact is True
    assert v.drift is False
    assert v.stale is False
    assert v.removed_ids == ()
    assert v.modified_ids == ()
    assert v.metadata_consistent is True
    assert v.canary_altered_ids == ()
    assert "intact" in v.detail


def test_missing_canary_is_stale():
    # Absence of any attestation is the signal.
    assert is_stale(None, as_of="2026-07-15") is True


def test_fresh_canary_not_stale():
    canary = issue_canary("2026-07-15")
    assert is_stale(canary, as_of="2026-08-01", max_age_days=DEFAULT_MAX_AGE_DAYS) is False


def test_freshness_defaults_to_today_when_no_check_date_is_given():
    assert is_stale(issue_canary("2026-07-17")) is False


def test_is_stale_malformed_date_fails_closed():
    """Unparseable issue/as-of dates cannot affirm freshness → treated as stale."""
    malformed = object.__new__(CanaryStatement)
    object.__setattr__(malformed, "issued_on", "not-a-date")
    assert is_stale(malformed, as_of="2026-07-15") is True
    assert is_stale(issue_canary("2026-07-15"), as_of="garbage") is True


def test_old_canary_is_stale():
    canary = issue_canary("2026-01-01")
    assert is_stale(canary, as_of="2026-12-31", max_age_days=180) is True


def test_verify_canary_stale_blocks_intact():
    # Same registry, but the attestation has aged out → not intact, flagged stale.
    canary = issue_canary("2026-01-01")
    v = verify_canary(canary, PERSONAL_RED_LINES, as_of="2026-12-31", max_age_days=180)
    assert v.drift is False
    assert v.stale is True
    assert v.intact is False
    assert "stale" in v.detail


def test_verify_canary_fresh_and_unchanged_is_intact():
    canary = issue_canary("2026-07-15")
    v = verify_canary(canary, PERSONAL_RED_LINES, as_of="2026-07-20", max_age_days=180)
    assert v.intact is True
    assert v.stale is False


def test_verify_canary_trips_on_removal():
    # Removing a CANARY-grade line from a canary that bound issue-time severities
    # escalates: the detail names it as a canary-grade alteration.
    canary = issue_canary("2026-07-15")
    fewer = tuple(rl for rl in PERSONAL_RED_LINES if rl.id != "s2-untargeted-profiling")
    v = verify_canary(canary, fewer)
    assert v.intact is False
    assert v.drift is True
    assert v.metadata_consistent is False
    assert v.canary_altered_ids == ("s2-untargeted-profiling",)
    assert "s2-untargeted-profiling" in v.removed_ids
    assert "CANARY-GRADE LINE ALTERED" in v.detail
    assert "s2-untargeted-profiling" in v.detail


def test_verify_canary_removed_noncanary_line_trips_not_escalated():
    # Removing a non-canary (STRONG) line trips the pattern but is not escalated
    # to the canary-grade message.
    canary = issue_canary("2026-07-15")
    fewer = tuple(rl for rl in PERSONAL_RED_LINES if rl.id != "dual-use-ablation")
    v = verify_canary(canary, fewer)
    assert v.intact is False
    assert v.drift is True
    assert v.canary_altered_ids == ()
    assert "dual-use-ablation" in v.removed_ids
    assert "TRIPPED" in v.detail
    assert "CANARY-GRADE" not in v.detail


def test_verify_canary_weakened_canary_line_escalates():
    # Weakening (editing) a CANARY-grade line surfaces it in modified_ids AND
    # escalates the detail — issue-time severity is bound, so a later severity
    # weakening cannot hide the change.
    canary = issue_canary("2026-07-15")
    edited = (replace(PERSONAL_RED_LINES[0], rationale="revised rationale"),) + PERSONAL_RED_LINES[1:]
    v = verify_canary(canary, edited)
    assert v.drift is True
    assert v.removed_ids == ()
    assert "s1-human-control-force" in v.modified_ids
    assert "CANARY-GRADE LINE ALTERED" in v.detail
    assert "s1-human-control-force" in v.detail


def test_verify_canary_noncanary_modification_named_not_escalated():
    # Modifying a non-canary (STRONG) line names it in modified_ids and the detail,
    # but is NOT escalated to the canary-grade message.
    canary = issue_canary("2026-07-15")
    idx = next(i for i, rl in enumerate(PERSONAL_RED_LINES) if rl.id == "dual-use-ablation")
    edited = (
        PERSONAL_RED_LINES[:idx]
        + (replace(PERSONAL_RED_LINES[idx], rationale="revised rationale"),)
        + PERSONAL_RED_LINES[idx + 1 :]
    )
    v = verify_canary(canary, edited)
    assert v.drift is True
    assert v.removed_ids == ()
    assert "dual-use-ablation" in v.modified_ids
    assert "modified lines: dual-use-ablation" in v.detail
    assert "CANARY-GRADE" not in v.detail


def test_verify_canary_aggregate_only_statement_reports_removal_without_per_line_detail():
    # An aggregate-only statement carries no per-line digests, so removal is detected
    # through the aggregate hash alone: TRIPPED, with no modification list to escalate.
    aggregate_only = CanaryStatement(
        statement=DEFAULT_CANARY_TEXT,
        issued_on="2026-07-15",
        registry_digest=registry_hash(),
        line_ids=tuple(sorted(rl.id for rl in PERSONAL_RED_LINES)),
    )
    assert aggregate_only.line_digests == ()
    fewer = tuple(rl for rl in PERSONAL_RED_LINES if rl.id != "s2-untargeted-profiling")
    v = verify_canary(aggregate_only, fewer)
    assert v.modified_ids == ()
    assert "TRIPPED" in v.detail
    assert "CANARY-GRADE" not in v.detail


def test_verify_canary_aggregate_only_statement_verifies_intact():
    # An aggregate-only statement over the unchanged registry still verifies intact.
    aggregate_only = CanaryStatement(
        statement=DEFAULT_CANARY_TEXT,
        issued_on="2026-07-15",
        registry_digest=registry_hash(),
        line_ids=tuple(sorted(rl.id for rl in PERSONAL_RED_LINES)),
    )
    v = verify_canary(aggregate_only, PERSONAL_RED_LINES, as_of="2026-07-20")
    assert v.intact is True
    assert v.modified_ids == ()


def test_verify_canary_detects_addition():
    canary = issue_canary("2026-07-15")
    new_line = RedLine(
        id="new-line",
        title="t",
        standard="I will not cross this boundary.",
        rationale="r",
        scope=("x",),
        carve_outs=("does not restrict y",),
        max_tier=DeploymentTier.HOSTED,
        severity=Severity.STRONG,
    )
    added = PERSONAL_RED_LINES + (new_line,)
    v = verify_canary(canary, added)
    assert "new-line" in v.added_ids
    assert v.drift is True


def test_detect_line_removal_direct():
    prev = tuple(rl.id for rl in PERSONAL_RED_LINES)
    fewer = PERSONAL_RED_LINES[:-1]
    removed = detect_line_removal(prev, fewer)
    assert removed == (PERSONAL_RED_LINES[-1].id,)
