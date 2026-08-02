"""Tests for transparency report aggregation."""

from __future__ import annotations

from datetime import date

from red_line import ReviewAuthorization, review_engagement, transparency_report
from tests.helpers import action


def test_transparency_report_aggregates():
    outside = review_engagement(
        action("Open-source docs", frozenset({"documentation"})), reviewed_on=date.today().isoformat()
    )
    blocking = review_engagement(
        action("Autonomous targeting", frozenset({"targeting"})), reviewed_on=date.today().isoformat()
    )
    authorized = review_engagement(
        action("Autonomous targeting", frozenset({"targeting"})),
        reviewed_on=date.today().isoformat(),
        authorization=ReviewAuthorization("reviewer", "red-line review", "record escalation", "2026-07-15"),
    )
    report = transparency_report((outside, blocking, authorized), period="2026-Q3")
    assert report.total == 3
    assert report.by_classification["non_compliant"] == 2
    assert report.by_classification["outside_scope"] == 1
    assert report.authorizations == 1
    assert report.blocked == 2
    assert "2026-Q3" in report.render()


def test_transparency_report_default_period():
    report = transparency_report(())
    assert report.total == 0
    assert "as of" in report.period
    assert all(value == 0 for value in report.by_classification.values())
