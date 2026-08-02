"""Registry sanity anchors for the new invariant."""

from __future__ import annotations

from red_line import DeploymentTier, PERSONAL_RED_LINES, Severity


class TestRegistryAnchors:
    def test_registry_still_holds_severity_shape(self):
        canary_ids = {rl.id for rl in PERSONAL_RED_LINES if rl.severity is Severity.CANARY}
        assert canary_ids == {"s1-human-control-force", "s2-untargeted-profiling"}

    def test_every_tier_value_is_a_valid_scope_word(self):
        # Tier values are appended to the effective scope by the evaluator; they
        # must stay canonical or evaluation would silently drop them.
        from red_line.model import normalize_token

        for tier in DeploymentTier:
            assert normalize_token(tier.value) == tier.value
