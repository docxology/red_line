"""Fail-closed validation of hand-crafted canary metadata."""

from __future__ import annotations

import pytest

from red_line import PERSONAL_RED_LINES, issue_canary, registry_hash, verify_canary
from red_line.canary import CanaryStatement

from ._shared import SHA_A, SHA_B, _corrupt


class TestCanaryStatementValidation:
    def _kwargs(self, **overrides):
        base = dict(
            statement="attestation",
            issued_on="2026-07-15",
            registry_digest=registry_hash(),
            line_ids=("a-line",),
            line_digests=(("a-line", "strong", SHA_A),),
        )
        base.update(overrides)
        return base

    @pytest.mark.parametrize(
        ("overrides", "exc"),
        [
            ({"statement": "   "}, ValueError),
            ({"issued_on": 20260715}, TypeError),
            ({"issued_on": "July 15"}, ValueError),
            ({"registry_digest": "beef"}, ValueError),
            ({"registry_digest": ("a" * 64).upper()}, ValueError),
            ({"line_ids": "a-line"}, TypeError),
            ({"line_ids": ("  ",), "line_digests": ()}, ValueError),
            ({"line_ids": ("a", "a"), "line_digests": ()}, ValueError),
            ({"line_digests": "digest"}, TypeError),
            ({"line_digests": (("a-line", "strong"),)}, ValueError),
            ({"line_digests": (("  ", "strong", SHA_A),)}, ValueError),
            ({"line_digests": (("a-line", "mega", SHA_A),)}, ValueError),
            ({"line_digests": (("a-line", "strong", "zz"),)}, ValueError),
            (
                {
                    "line_ids": ("a-line", "b-line"),
                    "line_digests": (("a-line", "strong", SHA_A), ("a-line", "strong", SHA_B)),
                },
                ValueError,
            ),
            ({"line_ids": ("a-line", "b-line"), "line_digests": (("a-line", "strong", SHA_A),)}, ValueError),
        ],
    )
    def test_malformed_statement_rejected(self, overrides, exc):
        with pytest.raises(exc):
            CanaryStatement(**self._kwargs(**overrides))

    @pytest.mark.parametrize(
        ("issued_on", "exc"),
        [(20260715, TypeError), ("July 15", ValueError)],
    )
    def test_issue_canary_rejects_bad_dates(self, issued_on, exc):
        with pytest.raises(exc):
            issue_canary(issued_on)

    def test_issue_canary_rejects_blank_statement(self):
        with pytest.raises(ValueError):
            issue_canary("2026-07-15", statement="   ")


class TestCanaryVerificationFailClosed:
    def test_missing_canary_is_a_signal_not_a_pass(self):
        verification = verify_canary(None, as_of="2026-07-16")
        assert verification.intact is False
        assert verification.stale is True
        assert verification.drift is False
        assert verification.added_ids == tuple(sorted(rl.id for rl in PERSONAL_RED_LINES))
        assert "no prior canary" in verification.detail

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("statement", "   "),
            ("issued_on", 20260715),
            ("registry_digest", "beef"),
            ("line_ids", "s1"),
            ("line_ids", ("  ",)),
            ("line_ids", ("a", "a")),
            ("line_digests", "digest"),
            ("line_digests", (("a", "strong"),)),
            ("line_digests", (("  ", "strong", SHA_A),)),
            ("line_digests", (("a", "mega", SHA_A),)),
            ("line_digests", (("a", "strong", "zz"),)),
        ],
    )
    def test_corrupted_metadata_never_verifies_intact(self, field, value):
        canary = issue_canary("2026-07-15")
        corrupted = _corrupt(canary, **{field: value})
        verification = verify_canary(corrupted, as_of="2026-07-16")
        assert verification.intact is False
        assert verification.stale is True
        assert verification.detail.startswith("canary metadata invalid")

    def test_unparseable_issued_on_reads_as_invalid_metadata(self):
        corrupted = _corrupt(issue_canary("2026-07-15"), issued_on="not-a-date")
        verification = verify_canary(corrupted, as_of="2026-07-16")
        assert verification.intact is False
        assert verification.detail.startswith("canary metadata invalid")
