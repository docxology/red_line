"""Deterministic registry and line hashing helpers."""

from __future__ import annotations

import hashlib
import json

from ..model import RedLine
from ..registry import PERSONAL_RED_LINES


def _line_payload(rl: RedLine) -> dict:
    """Canonical dict for a single red line — the atom of both registry and line hashes.

    Factored out of :func:`_canonical` so a *single* line can be digested
    identically to how it contributes to the registry digest. The key set and
    value normalization here are load-bearing: any change alters both the
    registry hash and every per-line digest, so this function is frozen.
    """
    return {
        "id": rl.id,
        "title": rl.title,
        "standard": rl.standard,
        "rationale": rl.rationale,
        "scope": sorted(rl.scope),
        "carve_outs": sorted(rl.carve_outs),
        "exemptions": [
            {
                "id": exemption.id,
                "description": exemption.description,
                "trigger_scope": sorted(exemption.trigger_scope),
                "required_evidence": sorted(kind.value for kind in exemption.required_evidence),
                "match_mode": exemption.match_mode.value,
            }
            for exemption in sorted(rl.exemptions, key=lambda item: item.id)
        ],
        "max_tier": rl.max_tier.value,
        "severity": rl.severity.value,
        "stated_by": rl.stated_by,
        "stated_on": rl.stated_on,
    }


def _canonical(lines: tuple[RedLine, ...]) -> str:
    """Canonical JSON of the registry — sorted, stable, environment-free.

    Byte-for-byte identical to the pre-refactor inline construction: the payload
    is the list of :func:`_line_payload` dicts ordered by id, dumped with
    ``sort_keys=True`` (so intra-dict key order is irrelevant).
    """
    payload = [_line_payload(rl) for rl in sorted(lines, key=lambda r: r.id)]
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def registry_hash(lines: tuple[RedLine, ...] = PERSONAL_RED_LINES) -> str:
    """Deterministic sha256 hex digest over the canonicalized registry content."""
    return hashlib.sha256(_canonical(lines).encode("utf-8")).hexdigest()


def line_digest(rl: RedLine) -> str:
    """Deterministic sha256 hex digest over a single red line's canonical content.

    Uses the same :func:`_line_payload` atom as the registry hash, so a line's
    digest changes exactly when its canonical content changes. This lets a canary
    bind the issue-time content of *each* line, not just the aggregate registry
    hash — enabling detection of *which* line was modified (not merely that the
    aggregate drifted).
    """
    return hashlib.sha256(
        json.dumps(_line_payload(rl), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
