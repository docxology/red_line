"""Tests for canary statement issuance."""

from __future__ import annotations

from dataclasses import replace

import pytest

from red_line.canary import DEFAULT_CANARY_TEXT, issue_canary, line_digest, registry_hash
from red_line.model import DeploymentTier, RedLine, Severity
from red_line.registry import PERSONAL_RED_LINES


def test_issue_canary_binds_hash_and_ids():
    canary = issue_canary("2026-07-15")
    assert canary.registry_digest == registry_hash()
    assert canary.issued_on == "2026-07-15"
    assert canary.statement == DEFAULT_CANARY_TEXT
    assert set(canary.line_ids) == {rl.id for rl in PERSONAL_RED_LINES}


def test_canary_statement_is_frozen():
    c = issue_canary("2026-07-15")
    assert c.statement == DEFAULT_CANARY_TEXT
    assert c.line_digests


def test_issue_canary_populates_line_digests_as_triples():
    canary = issue_canary("2026-07-15")
    ids = {rl.id for rl in PERSONAL_RED_LINES}
    assert {t[0] for t in canary.line_digests} == ids
    by_id = {t[0]: t for t in canary.line_digests}
    for rl in PERSONAL_RED_LINES:
        _id, severity, digest = by_id[rl.id]
        assert severity == rl.severity.value
        assert digest == line_digest(rl)


def _drifted_lines():
    """Registry variant with a materially modified line (hash drifts, no removal)."""
    return (replace(PERSONAL_RED_LINES[0], rationale="revised rationale"),) + PERSONAL_RED_LINES[1:]


def test_issue_canary_prev_drift_default_no_rationale_raises():
    prev = issue_canary("2026-07-15")
    drifted = _drifted_lines()
    with pytest.raises(ValueError) as excinfo:
        issue_canary("2026-08-01", drifted, prev=prev)
    msg = str(excinfo.value)
    assert prev.registry_digest[:8] in msg
    assert registry_hash(drifted)[:8] in msg


def test_issue_canary_prev_drift_with_rationale_emits_successor():
    prev = issue_canary("2026-07-15")
    drifted = _drifted_lines()
    successor = issue_canary(
        "2026-08-01", drifted, prev=prev, rationale="tightened S1 rationale after review"
    )
    assert successor.registry_digest == registry_hash(drifted)
    assert f"Supersedes canary {prev.registry_digest[:8]}" in successor.statement
    assert "Removed: [none]" in successor.statement
    assert "Added: [none]" in successor.statement
    assert "Rationale: tightened S1 rationale after review" in successor.statement


def test_issue_canary_successor_names_removed_and_added_ids():
    prev = issue_canary("2026-07-15")
    # Remove one line and add another → both id lists populated in the successor.
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
    changed = tuple(rl for rl in PERSONAL_RED_LINES if rl.id != "dual-use-ablation") + (new_line,)
    successor = issue_canary("2026-08-01", changed, prev=prev, rationale="reorganized dual-use handling")
    assert "Removed: [dual-use-ablation]" in successor.statement
    assert "Added: [new-line]" in successor.statement


def test_issue_canary_prev_drift_custom_statement_requires_rationale():
    prev = issue_canary("2026-07-15")
    drifted = _drifted_lines()
    custom = "Author-supplied successor note."
    with pytest.raises(ValueError, match="no rationale"):
        issue_canary("2026-08-01", drifted, custom, prev=prev)


def test_issue_canary_custom_successor_preserves_metadata_and_prose():
    prev = issue_canary("2026-07-15")
    drifted = _drifted_lines()
    result = issue_canary(
        "2026-08-01",
        drifted,
        "Author-supplied successor note.",
        prev=prev,
        rationale="tightened the standard after review",
    )
    assert "Supersedes canary" in result.statement
    assert "Rationale: tightened the standard after review" in result.statement
    assert "Author note: Author-supplied successor note." in result.statement
    assert result.registry_digest == registry_hash(drifted)


def test_issue_canary_prev_unchanged_keeps_default_text():
    prev = issue_canary("2026-07-15")
    result = issue_canary("2026-08-01", PERSONAL_RED_LINES, prev=prev)
    assert result.statement == DEFAULT_CANARY_TEXT
    assert result.issued_on == "2026-08-01"


def test_issue_canary_prev_none_is_current_behavior():
    result = issue_canary("2026-07-15", PERSONAL_RED_LINES)
    assert result.statement == DEFAULT_CANARY_TEXT
    assert result.registry_digest == registry_hash()
