"""Additional proof-of-detection for the invariant battery."""

from __future__ import annotations

from dataclasses import replace

import pytest

from red_line import EvidenceKind, PERSONAL_RED_LINES, invariants_pass
from red_line.invariants import all_invariants, check_exemption_triggers_disjoint, check_typed_exemptions
from red_line.invariants.checks import check_canonical_scope_tokens, check_provenance
from red_line.model import Exemption

from ._shared import HOMOGLYPH_SURVEILLANCE, _corrupt, _line, _swap


class TestInvariantProofOfDetection:
    def test_exemption_triggers_disjoint_passes_on_real_registry(self):
        result = check_exemption_triggers_disjoint(PERSONAL_RED_LINES)[0]
        assert result.passed is True
        assert result.detail == "ok"

    def test_exemption_triggers_disjoint_registered_in_battery(self):
        names = [r.name for r in all_invariants(PERSONAL_RED_LINES)]
        assert "exemption_triggers_disjoint" in names

    def test_self_exempting_trigger_detected(self):
        """A planted exemption triggered by the line's own prohibited scope fires."""
        line = _line("s2-untargeted-profiling")
        planted = Exemption(
            id="planted-self-exempt",
            description="planted: triggered by the prohibited dimension itself",
            trigger_scope=frozenset({"surveillance"}),
            required_evidence=frozenset({EvidenceKind.PURPOSE}),
        )
        bad = _swap(replace(line, exemptions=line.exemptions + (planted,)))
        result = check_exemption_triggers_disjoint(bad)[0]
        assert result.passed is False
        assert "planted-self-exempt" in result.detail and "surveillance" in result.detail
        assert invariants_pass(bad) is False

    def test_alias_smuggled_self_exemption_detected(self):
        """Detection is normalization-aware: an alias spelling cannot hide overlap."""
        line = _line("s1-human-control-force")
        planted = Exemption(
            id="planted-alias-self-exempt",
            description="planted: alias spelling of a prohibited scope token",
            trigger_scope=frozenset({"weapon"}),  # alias of canonical 'weapons'
            required_evidence=frozenset({EvidenceKind.PURPOSE}),
        )
        bad = _swap(replace(line, exemptions=line.exemptions + (planted,)))
        result = check_exemption_triggers_disjoint(bad)[0]
        assert result.passed is False
        assert "weapons" in result.detail

    def test_invalid_match_mode_detected(self):
        exemption = Exemption(
            id="valid-shape",
            description="valid until corrupted",
            trigger_scope=frozenset({"support"}),
            required_evidence=frozenset({EvidenceKind.PURPOSE}),
        )
        corrupted = _corrupt(exemption, match_mode="any")
        bad = _swap(replace(PERSONAL_RED_LINES[0], exemptions=(corrupted,)))
        result = check_typed_exemptions(bad)[0]
        assert result.passed is False
        assert "invalid match mode" in result.detail
        assert invariants_pass(bad) is False

    @pytest.mark.parametrize("stated_on", ["garbage", None])
    def test_invalid_stated_on_detected(self, stated_on):
        bad = _swap(_corrupt(PERSONAL_RED_LINES[0], stated_on=stated_on))
        result = check_provenance(bad)[0]
        assert result.passed is False
        assert "invalid stated_on" in result.detail
        assert invariants_pass(bad) is False

    @pytest.mark.parametrize("stated_by", ["   ", 42])
    def test_missing_stated_by_detected(self, stated_by):
        bad = _swap(_corrupt(PERSONAL_RED_LINES[0], stated_by=stated_by))
        result = check_provenance(bad)[0]
        assert result.passed is False
        assert "missing stated_by" in result.detail

    def test_non_canonical_scope_spelling_detected(self):
        bad = _swap(_corrupt(PERSONAL_RED_LINES[0], scope=("Weapons",)))
        result = check_canonical_scope_tokens(bad)[0]
        assert result.passed is False
        assert "Weapons" in result.detail
        assert invariants_pass(bad) is False

    @pytest.mark.parametrize("token", [42, HOMOGLYPH_SURVEILLANCE])
    def test_unnormalizable_scope_token_detected(self, token):
        bad = _swap(_corrupt(PERSONAL_RED_LINES[0], scope=(token,)))
        assert check_canonical_scope_tokens(bad)[0].passed is False
        # Disjointness that cannot be computed is never certified (fail closed).
        disjoint = check_exemption_triggers_disjoint(bad)[0]
        assert disjoint.passed is False
        assert "unnormalizable scope" in disjoint.detail
        assert invariants_pass(bad) is False

    @pytest.mark.parametrize("token", [42, HOMOGLYPH_SURVEILLANCE])
    def test_unnormalizable_trigger_token_fails_disjointness_closed(self, token):
        exemption = Exemption(
            id="valid-shape",
            description="valid until corrupted",
            trigger_scope=frozenset({"support"}),
            required_evidence=frozenset({EvidenceKind.PURPOSE}),
        )
        corrupted = _corrupt(exemption, trigger_scope=frozenset({token}))
        bad = _swap(replace(PERSONAL_RED_LINES[0], exemptions=(corrupted,)))
        result = check_exemption_triggers_disjoint(bad)[0]
        assert result.passed is False
        assert "unnormalizable scope" in result.detail
