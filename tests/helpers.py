"""Reusable complete and incomplete intakes for no-mock tests."""

from __future__ import annotations

from red_line import (
    ActionContext,
    EvidenceKind,
    EvidenceRecord,
    EvidenceStatus,
    ProposedAction,
)
from red_line.model import DeploymentTier
from datetime import date


def complete_context(**overrides: str) -> ActionContext:
    values = {
        "purpose": "test purpose",
        "end_use": "test end use",
        "affected_parties": "none beyond the author",
        "data_provenance": "synthetic test data",
        "legal_basis": "not_applicable",
        "human_control": "author review before use",
        "deployment": "local hosted test",
        "downstream_transfer": "none",
        "capability_scope": "documented test capability",
    }
    values.update(overrides)
    evidence = tuple(
        EvidenceRecord(
            kind=kind,
            reference=f"test://evidence/{kind.value}",
            summary=f"Verified fixture for {kind.value}",
            status=EvidenceStatus.VERIFIED,
            recorded_on=date.today().isoformat(),
        )
        for kind in EvidenceKind
    )
    return ActionContext(**values, evidence=evidence)


def action(
    description: str,
    scope: frozenset[str],
    *,
    tier: DeploymentTier = DeploymentTier.HOSTED,
    ambiguous: bool = False,
    context: ActionContext | None = None,
) -> ProposedAction:
    return ProposedAction(
        description=description,
        scope=scope,
        context=context or complete_context(),
        tier=tier,
        ambiguous=ambiguous,
    )
