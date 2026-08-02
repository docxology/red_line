"""Tests for red-line model enums."""

from __future__ import annotations

from red_line.model import DeploymentTier


def test_deployment_tier_oversight_rank_ordering():
    assert DeploymentTier.HOSTED.oversight_rank > DeploymentTier.CONNECTED.oversight_rank
    assert DeploymentTier.CONNECTED.oversight_rank > DeploymentTier.AIR_GAPPED.oversight_rank
