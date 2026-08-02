"""Exact boundary dates for evidence and canary staleness."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from red_line import (
    Classification,
    DEFAULT_EVIDENCE_MAX_AGE_DAYS,
    DEFAULT_MAX_AGE_DAYS,
    EvidenceKind,
    EvidenceRecord,
    EvidenceStatus,
    evaluate_action,
    is_stale,
    issue_canary,
)

from ..helpers import action


def _record(recorded_on: str) -> EvidenceRecord:
    return EvidenceRecord(
        kind=EvidenceKind.PURPOSE,
        reference="test://evidence/purpose",
        summary="boundary fixture",
        status=EvidenceStatus.VERIFIED,
        recorded_on=recorded_on,
    )


class TestStalenessBoundaries:
    def test_evidence_exactly_at_window_edge_is_fresh(self):
        recorded = date(2026, 1, 1)
        record = _record(recorded.isoformat())
        edge = recorded + timedelta(days=DEFAULT_EVIDENCE_MAX_AGE_DAYS)
        assert record.is_stale(edge) is False
        assert record.is_stale(edge + timedelta(days=1)) is True

    def test_future_dated_evidence_is_stale(self):
        record = _record("2026-01-02")
        assert record.is_stale(date(2026, 1, 1)) is True

    def test_zero_day_window_boundary(self):
        record = _record("2026-01-01")
        assert record.is_stale(date(2026, 1, 1), max_age_days=0) is False
        assert record.is_stale(date(2026, 1, 2), max_age_days=0) is True

    def test_evaluator_honors_exact_evidence_boundary(self):
        # Derive the boundary from the helper's actual recording date rather
        # than pinning a hard-coded literal, so the test stays correct no
        # matter what date the fixture records evidence (it must never
        # silently go stale).
        act = action("teaching materials", frozenset({"teaching"}))
        recorded = date.fromisoformat(act.context.evidence[0].recorded_on)
        at_edge = evaluate_action(act, as_of=recorded + timedelta(days=DEFAULT_EVIDENCE_MAX_AGE_DAYS))
        past_edge = evaluate_action(act, as_of=recorded + timedelta(days=DEFAULT_EVIDENCE_MAX_AGE_DAYS + 1))
        assert at_edge.classification is Classification.OUTSIDE_SCOPE
        assert past_edge.classification is Classification.INSUFFICIENT_INFORMATION
        assert EvidenceKind.PURPOSE in past_edge.stale_evidence

    def test_canary_staleness_exact_boundary(self):
        issued = date(2026, 1, 1)
        canary = issue_canary(issued.isoformat())
        edge = issued + timedelta(days=DEFAULT_MAX_AGE_DAYS)
        assert is_stale(canary, edge.isoformat()) is False
        assert is_stale(canary, (edge + timedelta(days=1)).isoformat()) is True

    def test_future_dated_canary_is_stale(self):
        canary = issue_canary("2026-07-16")
        assert is_stale(canary, "2026-07-15") is True

    @pytest.mark.parametrize("bad_age", [-1, True, "180"])
    def test_canary_is_stale_rejects_invalid_window(self, bad_age):
        canary = issue_canary("2026-07-15")
        with pytest.raises(ValueError):
            is_stale(canary, "2026-07-16", max_age_days=bad_age)

    @pytest.mark.parametrize("bad_age", [-1, True])
    def test_evidence_is_stale_rejects_invalid_window(self, bad_age):
        with pytest.raises(ValueError):
            _record("2026-01-01").is_stale(date(2026, 1, 2), max_age_days=bad_age)

    def test_evidence_is_stale_rejects_non_date(self):
        with pytest.raises(TypeError):
            _record("2026-01-01").is_stale("2026-01-02")
