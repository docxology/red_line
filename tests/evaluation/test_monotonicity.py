"""Tests for evaluation monotonicity across deployment tiers."""

from __future__ import annotations

from red_line import Classification, DeploymentTier, PERSONAL_RED_LINES, evaluate_action
from tests.helpers import action as make_action


def test_tier_below_floor_requires_modification():
    # dual-use-ablation permits air-gap; but a CANARY line (s2, max CONNECTED)
    # deployed air-gapped retains too little oversight.
    action = make_action(
        description="Ship a profiling-capable model beyond recall",
        scope=frozenset({"profiling"}),
        tier=DeploymentTier.AIR_GAPPED,
    )
    result = evaluate_action(action)
    assert result.classification in {
        Classification.REQUIRES_MODIFICATION,
        Classification.NON_COMPLIANT,
    }


def test_uncarved_violation_is_hard_block_at_any_tier():
    for tier in (DeploymentTier.HOSTED, DeploymentTier.CONNECTED, DeploymentTier.AIR_GAPPED):
        result = evaluate_action(make_action("targeting work", frozenset({"targeting"}), tier=tier))
        assert result.classification is Classification.NON_COMPLIANT, tier


def test_below_floor_tier_never_softens_hard_block():
    # s1 floor is HOSTED (strictest); at AIR_GAPPED it must stay NON_COMPLIANT
    # and additionally record the tier shortfall as an aggravating reason.
    result = evaluate_action(
        make_action("targeting beyond recall", frozenset({"targeting"}), tier=DeploymentTier.AIR_GAPPED)
    )
    assert result.classification is Classification.NON_COMPLIANT
    assert any("retains less oversight" in r for r in result.reasons)


def test_carve_out_does_not_launder_the_tier_floor():
    # s2 (max_tier CONNECTED) implicated via 'surveillance' but carved by
    # 'research'; at AIR_GAPPED (below CONNECTED floor) the carve-out excuses
    # the scope contact but NOT the oversight deficit → REQUIRES_MODIFICATION.
    result = evaluate_action(
        make_action(
            "surveillance research beyond recall",
            frozenset({"surveillance", "research"}),
            tier=DeploymentTier.AIR_GAPPED,
        )
    )
    assert result.classification is Classification.REQUIRES_MODIFICATION
    assert any("floor" in r and "s2-untargeted-profiling" in r for r in result.reasons)


def test_verdict_strictness_monotonic_in_tier_danger():
    """For every line's every scope keyword, a lower-oversight tier must yield a
    verdict at least as strict as a higher-oversight tier (no inversions)."""
    order = {
        Classification.COMPLIANT: 0,
        Classification.REQUIRES_MODIFICATION: 1,
        Classification.NON_COMPLIANT: 2,
    }
    tiers_desc = [DeploymentTier.HOSTED, DeploymentTier.CONNECTED, DeploymentTier.AIR_GAPPED]
    for line in PERSONAL_RED_LINES:
        for kw in line.scope:
            strictness = [
                order[evaluate_action(make_action("x", frozenset({kw}), tier=t)).classification]
                for t in tiers_desc
            ]
            # HOSTED (most oversight) first → AIR_GAPPED (least) last; strictness
            # must be non-decreasing as oversight drops.
            assert strictness == sorted(strictness), (line.id, kw, strictness)


def test_monotonicity_sweep_is_exhaustive_and_has_a_positive_control():
    """The sweep must (a) examine the FULL keyword lattice and (b) actually go
    red on the known-bad pre-fix logic — else it is green-by-construction.

    Advisor-required (2026-07-16): a regression test authored alongside its fix
    is unproven until watched failing on the defect it guards.
    """
    order = {
        Classification.COMPLIANT: 0,
        Classification.REQUIRES_MODIFICATION: 1,
        Classification.NON_COMPLIANT: 2,
    }
    tiers = [DeploymentTier.HOSTED, DeploymentTier.CONNECTED, DeploymentTier.AIR_GAPPED]

    def _prefix_verdict(action):
        # The exact pre-fix bug: a below-floor tier on an uncarved implicated
        # line sets needs_mod and `continue`s, SKIPPING the hard block.
        hard_block = needs_mod = False
        effective = action.scope | {action.tier.value}
        for line in PERSONAL_RED_LINES:
            if not line.covers(effective):
                continue
            if line.carved_out(effective):
                continue
            if action.tier.oversight_rank < line.max_tier.oversight_rank:
                needs_mod = True
                continue
            hard_block = True
        if hard_block:
            return Classification.NON_COMPLIANT
        return Classification.REQUIRES_MODIFICATION if needs_mod else Classification.COMPLIANT

    total_keywords = sum(len(rl.scope) for rl in PERSONAL_RED_LINES)
    examined = 0
    prefix_inversions = 0
    fixed_inversions = 0
    for line in PERSONAL_RED_LINES:
        for kw in line.scope:
            examined += 1
            actions = [make_action("x", frozenset({kw}), tier=t) for t in tiers]
            pre = [order[_prefix_verdict(a)] for a in actions]
            fixed = [order[evaluate_action(a).classification] for a in actions]
            if pre != sorted(pre):
                prefix_inversions += 1
            if fixed != sorted(fixed):
                fixed_inversions += 1

    assert examined == total_keywords > 0  # exhaustive over the lattice, non-vacuous
    assert prefix_inversions > 0  # positive control: the sweep CAN detect the bug
    assert fixed_inversions == 0  # the fix eliminates every inversion
