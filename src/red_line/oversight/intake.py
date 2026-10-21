"""Restricted intake snapshots, separate from public reports and envelopes."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json

from ..model import ActionContext, EvidenceKind, EvidenceRecord, EvidenceStatus, ProposedAction, DeploymentTier

INTAKE_SCHEMA = "red-line.intake/1.0"
EVALUATOR_ID = "red_line.evaluate_action/2"


def canonical_intake(action: ProposedAction) -> str:
    """Serialize all intake fields; archive under access controls, never in a public envelope."""

    context = asdict(action.context)
    context["evidence"] = [
        {**asdict(record), "kind": record.kind.value, "status": record.status.value}
        for record in action.context.evidence
    ]
    payload = {
        "schema_version": INTAKE_SCHEMA, "description": action.description,
        "scope": sorted(action.scope), "tier": action.tier.value,
        "ambiguous": action.ambiguous, "context": context,
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def intake_digest(snapshot: str) -> str:
    return hashlib.sha256(snapshot.encode("utf-8")).hexdigest()


def action_from_snapshot(snapshot: str) -> ProposedAction:
    """Parse a restricted canonical snapshot; reject unsupported schemas or noncanonical content."""

    payload = json.loads(snapshot)
    if payload["schema_version"] != INTAKE_SCHEMA:
        raise ValueError("unsupported intake schema")
    context = payload["context"]
    evidence = tuple(EvidenceRecord(
        kind=EvidenceKind(record["kind"]), reference=record["reference"], summary=record["summary"],
        status=EvidenceStatus(record["status"]), recorded_on=record["recorded_on"],
    ) for record in context["evidence"])
    candidate = ProposedAction(
        description=payload["description"], scope=frozenset(payload["scope"]),
        tier=DeploymentTier(payload["tier"]), ambiguous=payload["ambiguous"],
        context=ActionContext(**{**context, "evidence": evidence}),
    )
    if canonical_intake(candidate) != snapshot:
        raise ValueError("intake snapshot is not canonical or contains unknown fields")
    return candidate
