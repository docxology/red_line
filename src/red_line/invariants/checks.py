"""Structural invariants over the red-line registry.

Pure-compute checks (zero I/O, no infrastructure imports) that validate the
*shape* of the registry rather than any single action. These are the pinned
invariants from the ISA ``## Constraints`` — the properties the beacon must hold
for the framework to be coherent.

Each ``check_*`` returns a list of :class:`InvariantResult`; ``all_invariants``
runs the full battery. The companion test suite asserts they all pass on the
real registry AND fail on a planted-bad registry (proof-of-detection).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json

from ..model import (
    DeploymentTier,
    EvidenceKind,
    ExemptionMatchMode,
    RedLine,
    Severity,
    normalize_scope,
    normalize_token,
)
from ..model.red_line import _tokens
from ..registry import PERSONAL_RED_LINES


@dataclass(frozen=True)
class InvariantResult:
    """One structural check outcome."""

    name: str
    passed: bool
    detail: str


def check_unique_ids(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    ids = [rl.id for rl in lines]
    ok = len(ids) == len(set(ids))
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    return [InvariantResult("unique_ids", ok, "ok" if ok else f"duplicate ids: {dupes}")]


def check_each_has_carve_out(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    # Narrative clauses remain required for human readability, while executable
    # exemptions are separately typed and evidence-bearing.
    missing = [
        rl.id
        for rl in lines
        if len(rl.carve_outs) < 1 or any(not _tokens(clause) for clause in rl.carve_outs)
    ]
    ok = not missing
    return [
        InvariantResult("each_has_carve_out", ok, "ok" if ok else f"no content-bearing carve-out: {missing}")
    ]


def check_typed_exemptions(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    bad: list[str] = []
    for line in lines:
        if not line.exemptions:
            bad.append(f"{line.id}:<none>")
            continue
        for exemption in line.exemptions:
            if not exemption.id.strip() or not exemption.description.strip():
                bad.append(f"{line.id}:{exemption.id or '<blank>'}")
            elif not normalize_scope(exemption.trigger_scope) or not exemption.required_evidence:
                bad.append(f"{line.id}:{exemption.id}")
            elif not exemption.required_evidence.issubset(set(EvidenceKind)):
                bad.append(f"{line.id}:{exemption.id}:invalid evidence kind")
            elif not isinstance(exemption.match_mode, ExemptionMatchMode):
                bad.append(f"{line.id}:{exemption.id}:invalid match mode")
    ok = not bad and all(line.exemptions for line in lines)
    return [InvariantResult("typed_exemptions", ok, "ok" if ok else f"invalid exemptions: {bad}")]


def check_nonempty_scope(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    """Every line must have ≥1 scope keyword — a zero-scope line is unreachable.

    Gutting a line's scope to ``()`` makes ``evaluate_action`` never implicate
    it: a maximal silent weakening the rest of the battery would certify as
    healthy. This closes that blind spot.
    """
    empty = [rl.id for rl in lines if len(rl.scope) < 1]
    ok = not empty
    return [InvariantResult("nonempty_scope", ok, "ok" if ok else f"zero-scope (unreachable) lines: {empty}")]


def check_standard_analogs_not_air_gapped(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    """CANARY-grade (Standard-1/2 analog) lines may never permit air-gapped release."""
    offenders = [
        rl.id for rl in lines if rl.severity is Severity.CANARY and rl.max_tier is DeploymentTier.AIR_GAPPED
    ]
    ok = not offenders
    detail = "ok" if ok else f"canary lines allow air-gap: {offenders}"
    return [InvariantResult("canary_not_air_gapped", ok, detail)]


STANDARD_ANALOG_IDS: frozenset[str] = frozenset({"s1-human-control-force", "s2-untargeted-profiling"})


def check_has_both_standards(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    """At least one Standard-1 analog (force) and one Standard-2 analog (profiling)."""
    ids = {rl.id for rl in lines}
    has_s1 = "s1-human-control-force" in ids
    has_s2 = "s2-untargeted-profiling" in ids
    ok = has_s1 and has_s2
    detail = "ok" if ok else f"missing standard analog: s1={has_s1} s2={has_s2}"
    return [InvariantResult("has_both_standards", ok, detail)]


def check_standard_analogs_are_canary(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    """The Standard-analog lines must keep CANARY severity — demotion is drift.

    Silently downgrading s1/s2 from CANARY to a lesser grade would strip their
    removal of warrant-canary semantics while leaving the ids present, which
    the presence check alone cannot see.
    """
    demoted = [rl.id for rl in lines if rl.id in STANDARD_ANALOG_IDS and rl.severity is not Severity.CANARY]
    ok = not demoted
    detail = "ok" if ok else f"standard analog demoted from CANARY: {demoted}"
    return [InvariantResult("standard_analogs_are_canary", ok, detail)]


def check_enum_field_types(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    """max_tier / severity must be real enum members — dataclasses don't type-check.

    ``dataclasses.replace(rl, max_tier="garbage")`` succeeds silently; a
    string would then fail comparisons in unpredictable ways downstream.
    """
    bad = [
        rl.id
        for rl in lines
        if not isinstance(rl.max_tier, DeploymentTier) or not isinstance(rl.severity, Severity)
    ]
    ok = not bad
    detail = "ok" if ok else f"invalid enum field types: {bad}"
    return [InvariantResult("enum_field_types", ok, detail)]


def check_nonempty_standard_text(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    empty = [rl.id for rl in lines if not rl.standard.strip() or not rl.rationale.strip()]
    ok = not empty
    return [InvariantResult("nonempty_text", ok, "ok" if ok else f"empty standard/rationale: {empty}")]


def check_provenance(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    """Provenance dates and first-person commitments must remain explicit."""

    bad: list[str] = []
    for line in lines:
        try:
            date.fromisoformat(line.stated_on)
        except (TypeError, ValueError):
            bad.append(f"{line.id}:invalid stated_on")
        if not isinstance(line.stated_by, str) or not line.stated_by.strip():
            bad.append(f"{line.id}:missing stated_by")
        if not isinstance(line.standard, str) or not line.standard.lstrip().startswith("I "):
            bad.append(f"{line.id}:standard is not first-person")
    return [InvariantResult("provenance", not bad, "ok" if not bad else f"invalid provenance: {bad}")]


def check_unique_exemption_ids(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    ids = [exemption.id for line in lines for exemption in line.exemptions]
    duplicates = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    return [
        InvariantResult(
            "unique_exemption_ids",
            not duplicates,
            "ok" if not duplicates else f"duplicate exemption ids: {duplicates}",
        )
    ]


def check_canonical_scope_tokens(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    """Registry and exemption scopes must use reviewed canonical spellings."""

    bad: list[str] = []
    for line in lines:
        for token in (*line.scope, *(token for ex in line.exemptions for token in ex.trigger_scope)):
            try:
                if normalize_token(token) != token:
                    bad.append(f"{line.id}:{token}")
            except (TypeError, ValueError):
                bad.append(f"{line.id}:{token}")
    return [
        InvariantResult(
            "canonical_scope_tokens",
            not bad,
            "ok" if not bad else f"non-canonical scope tokens: {bad}",
        )
    ]


def check_exemption_triggers_disjoint(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    """No exemption trigger token may repeat its own line's prohibited scope.

    An exemption whose ``trigger_scope`` shares a token with the line's own
    ``scope`` is self-exempting: declaring the prohibited dimension itself would
    (once evidence is verified) satisfy the exemption trigger, silently narrowing
    the line for exactly the activity it prohibits. The rest of the battery
    cannot see this — ids, evidence kinds, and match modes all remain valid.
    A scope or trigger that cannot be normalized (non-string or non-ASCII
    tokens — :func:`check_canonical_scope_tokens` names the offending token)
    fails closed here too: disjointness that cannot be computed is never
    certified.
    """

    bad: list[str] = []
    for line in lines:
        try:
            line_scope = normalize_scope(line.scope)
            for exemption in line.exemptions:
                overlap = normalize_scope(exemption.trigger_scope) & line_scope
                bad.extend(f"{line.id}:{exemption.id}:{token}" for token in sorted(overlap))
        except (TypeError, ValueError) as exc:
            bad.append(f"{line.id}:unnormalizable scope: {exc}")
    ok = not bad
    return [
        InvariantResult(
            "exemption_triggers_disjoint",
            ok,
            "ok" if ok else f"self-exempting trigger tokens: {bad}",
        )
    ]


def check_registry_serialization(lines: tuple[RedLine, ...]) -> list[InvariantResult]:
    """Canonical serialization must remain valid and JSON-stable."""

    try:
        payload = []
        for line in sorted(lines, key=lambda item: item.id):
            payload.append(
                {
                    "id": line.id,
                    "title": line.title,
                    "standard": line.standard,
                    "rationale": line.rationale,
                    "scope": sorted(line.scope),
                    "carve_outs": sorted(line.carve_outs),
                    "exemptions": [
                        {
                            "id": exemption.id,
                            "description": exemption.description,
                            "trigger_scope": sorted(exemption.trigger_scope),
                            "required_evidence": sorted(kind.value for kind in exemption.required_evidence),
                            "match_mode": exemption.match_mode.value,
                        }
                        for exemption in sorted(line.exemptions, key=lambda item: item.id)
                    ],
                    "max_tier": line.max_tier.value,
                    "severity": line.severity.value,
                    "stated_by": line.stated_by,
                    "stated_on": line.stated_on,
                }
            )
        json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    except (AttributeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return [InvariantResult("registry_serialization", False, f"invalid registry serialization: {exc}")]
    return [InvariantResult("registry_serialization", True, "ok")]


def all_invariants(lines: tuple[RedLine, ...] = PERSONAL_RED_LINES) -> list[InvariantResult]:
    """Run every structural check and return the flattened result list."""
    results: list[InvariantResult] = []
    results.extend(check_unique_ids(lines))
    results.extend(check_each_has_carve_out(lines))
    results.extend(check_typed_exemptions(lines))
    results.extend(check_nonempty_scope(lines))
    results.extend(check_standard_analogs_not_air_gapped(lines))
    results.extend(check_has_both_standards(lines))
    results.extend(check_standard_analogs_are_canary(lines))
    results.extend(check_enum_field_types(lines))
    results.extend(check_nonempty_standard_text(lines))
    results.extend(check_provenance(lines))
    results.extend(check_unique_exemption_ids(lines))
    results.extend(check_canonical_scope_tokens(lines))
    results.extend(check_exemption_triggers_disjoint(lines))
    results.extend(check_registry_serialization(lines))
    return results


def invariants_pass(lines: tuple[RedLine, ...] = PERSONAL_RED_LINES) -> bool:
    """True iff every structural invariant passes on ``lines``."""
    return all(r.passed for r in all_invariants(lines))
