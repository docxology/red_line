"""Hostile scope declarations reaching ``evaluate_action``."""

from __future__ import annotations

from datetime import date

import pytest

from red_line import Classification, evaluate_action

from ..helpers import action
from ._shared import HOMOGLYPH_SURVEILLANCE, _corrupt


class TestHostileScope:
    def test_smuggled_homoglyph_scope_fails_closed(self):
        """A non-ASCII homoglyph smuggled past the constructor never reaches policy."""
        act = action("routine analysis", frozenset({"teaching"}))
        hostile = _corrupt(act, scope=frozenset({HOMOGLYPH_SURVEILLANCE}))
        assessment = evaluate_action(hostile, as_of=date.today().isoformat())
        assert assessment.classification is Classification.INSUFFICIENT_INFORMATION
        assert assessment.normalized_scope == ()
        assert any("non-canonical or non-ASCII token" in reason for reason in assessment.reasons)

    def test_smuggled_non_string_scope_token_fails_closed(self):
        act = action("routine analysis", frozenset({"teaching"}))
        hostile = _corrupt(act, scope=frozenset({42}))
        assessment = evaluate_action(hostile, as_of=date.today().isoformat())
        assert assessment.classification is Classification.INSUFFICIENT_INFORMATION
        assert any("non-canonical or non-ASCII token" in reason for reason in assessment.reasons)

    def test_normalization_vanishing_tokens_yield_empty_scope_stop(self):
        """Punctuation-only tokens survive the constructor but normalize to nothing."""
        act = action("routine analysis", frozenset({"__", "!!!"}))
        assessment = evaluate_action(act, as_of=date.today().isoformat())
        assert assessment.classification is Classification.INSUFFICIENT_INFORMATION
        assert any("scope declaration is empty" in reason for reason in assessment.reasons)

    @pytest.mark.parametrize("marker", ["unknown", "unspecified", "tbd", "unclear"])
    def test_unknown_scope_markers_block_even_with_real_scope(self, marker):
        act = action("bulk data work", frozenset({marker, "surveillance"}))
        assessment = evaluate_action(act, as_of=date.today().isoformat())
        assert assessment.classification is Classification.INSUFFICIENT_INFORMATION
        assert any(f"unknown scope marker: {marker}" in reason for reason in assessment.reasons)

    def test_fullwidth_unicode_scope_folds_to_canonical_coverage(self):
        """NFKC folding means a full-width spelling cannot dodge a red line."""
        fullwidth = "ｓｕｒｖｅｉｌｌａｎｃｅ"
        act = action("bulk inference tooling", frozenset({fullwidth}))
        assessment = evaluate_action(act, as_of=date.today().isoformat())
        assert "surveillance" in assessment.normalized_scope
        assert any(rl.id == "s2-untargeted-profiling" for rl in assessment.implicated)

    def test_ambiguous_intake_is_a_stop_signal(self):
        act = action("maybe surveillance-ish", frozenset({"surveillance"}), ambiguous=True)
        assessment = evaluate_action(act, as_of=date.today().isoformat())
        assert assessment.classification is Classification.INSUFFICIENT_INFORMATION
        assert any("explicitly ambiguous" in reason for reason in assessment.reasons)

    def test_declaring_only_the_prohibited_dimension_cannot_self_exempt(self):
        """No line's exemption triggers overlap its own scope, so a bare prohibited
        declaration with complete evidence is still NON_COMPLIANT."""
        act = action("bulk-to-individual inference", frozenset({"surveillance"}))
        assessment = evaluate_action(act, as_of=date.today().isoformat())
        assert assessment.classification is Classification.NON_COMPLIANT

    def test_as_of_accepts_str_and_date_identically(self):
        act = action("teaching materials", frozenset({"teaching"}))
        via_str = evaluate_action(act, as_of=date.today().isoformat())
        via_date = evaluate_action(act, as_of=date.today())
        assert via_str.classification is via_date.classification is Classification.OUTSIDE_SCOPE
