"""Canary freshness and drift verification."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import TYPE_CHECKING

from ..model import RedLine
from ..registry import PERSONAL_RED_LINES
from .hashing import line_digest, registry_hash

if TYPE_CHECKING:
    from .statement import CanaryStatement


@dataclass(frozen=True)
class CanaryVerification:
    """Result of comparing a prior canary against the current registry.

    ``intact`` requires an unchanged content hash, a fresh (non-stale)
    attestation, and internally consistent binding metadata — a stale or
    malformed canary is a signal, not a silent pass. ``stale`` and ``drift``
    are reported independently so the caller can tell *how* the canary failed.
    ``metadata_consistent`` reports whether the prior ids and optional per-line
    digests describe the complete live registry. ``canary_altered_ids`` is the
    issue-time CANARY-severity subset of removed or modified ids, kept separate
    from the human-readable detail string for machine consumers.
    """

    intact: bool
    drift: bool
    stale: bool
    removed_ids: tuple[str, ...]
    added_ids: tuple[str, ...]
    detail: str
    modified_ids: tuple[str, ...] = ()
    metadata_consistent: bool = True
    canary_altered_ids: tuple[str, ...] = ()


# Default freshness window: a canary must be re-issued at least this often, or the
# absence of a fresh attestation is itself treated as signal.
DEFAULT_MAX_AGE_DAYS = 180
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def detect_line_removal(prev_ids: tuple[str, ...], lines: tuple[RedLine, ...]) -> tuple[str, ...]:
    """Return ids present in ``prev_ids`` but absent from ``lines`` — removals."""
    current = {rl.id for rl in lines}
    return tuple(sorted(set(prev_ids) - current))


def _days_between(start_iso: str, end_iso: str) -> int:
    """Whole days from ``start_iso`` to ``end_iso`` (both ISO ``YYYY-MM-DD``)."""
    return (date.fromisoformat(end_iso) - date.fromisoformat(start_iso)).days


def is_stale(
    prev: CanaryStatement | None,
    as_of: str | None = None,
    max_age_days: int = DEFAULT_MAX_AGE_DAYS,
) -> bool:
    """True if there is no fresh attestation as of ``as_of`` (default: today).

    A *missing* canary (``prev is None``) is stale by definition — absence is the
    signal. An existing canary is stale once it is older than ``max_age_days``. A
    *future-dated* attestation is also stale (fail closed): an issue date after
    the check date cannot affirm freshness, only forge it. An unparseable
    ``issued_on``/``as_of`` date likewise reads as stale (fail closed): freshness
    that cannot be verified is never silently certified. When ``as_of`` is
    omitted, today's date is used — freshness is always evaluated, never skipped.
    """
    if prev is None:
        return True
    if not isinstance(max_age_days, int) or isinstance(max_age_days, bool) or max_age_days < 0:
        raise ValueError("max_age_days must be a non-negative integer")
    if as_of is None:
        as_of = date.today().isoformat()
    try:
        age = _days_between(prev.issued_on, as_of)
    except ValueError:
        # An unparseable issue/as-of date means freshness cannot be affirmed.
        # Fail closed: treat unverifiable freshness as stale (a signal), never as
        # a silent pass that would falsely certify the canary as fresh.
        return True
    if age < 0:
        return True
    return age > max_age_days


def verify_canary(
    prev: CanaryStatement | None,
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
    as_of: str | None = None,
    max_age_days: int = DEFAULT_MAX_AGE_DAYS,
) -> CanaryVerification:
    """Compare a prior ``CanaryStatement`` to the current registry.

    ``intact`` is True only when the registry hash is unchanged, the attestation
    is fresh, and the statement's binding metadata is consistent with the live
    registry. Freshness is ALWAYS evaluated: when ``as_of`` is omitted, today's
    date is used — an old-but-matching canary is never silently certified as
    intact (fail closed). Any hash change is ``drift``; removals are surfaced
    explicitly; an over-age, future-dated, or unparseable attestation sets
    ``stale``. Pass an explicit ``as_of`` for deterministic checks (tests,
    reproducible audits).
    """
    if prev is None:
        return CanaryVerification(
            intact=False,
            drift=False,
            stale=True,
            removed_ids=(),
            added_ids=tuple(sorted(rl.id for rl in lines)),
            detail="canary metadata invalid — no prior canary was supplied",
            metadata_consistent=False,
        )
    try:
        _validate_metadata_shape(prev)
    except (TypeError, ValueError) as exc:
        return CanaryVerification(
            intact=False,
            drift=False,
            stale=True,
            removed_ids=(),
            added_ids=(),
            detail=f"canary metadata invalid — {exc}",
            metadata_consistent=False,
        )
    current_digest = registry_hash(lines)
    removed = detect_line_removal(prev.line_ids, lines)
    current_ids = {rl.id for rl in lines}
    added = tuple(sorted(current_ids - set(prev.line_ids)))
    drift = current_digest != prev.registry_digest
    if as_of is None:
        as_of = date.today().isoformat()
    stale = is_stale(prev, as_of, max_age_days)

    # Per-line modification detection. Only possible when the prior canary carried
    # issue-time per-line digests (an aggregate-only statement with line_digests=()
    # falls back to aggregate-hash behavior: modified stays () and detail keeps the
    # aggregate shape). A line is "modified" when it is present in both the prior
    # digests and the current registry but its canonical digest differs.
    prev_digests = {lid: digest for (lid, _sev, digest) in prev.line_digests}
    prev_severity = {lid: sev for (lid, sev, _digest) in prev.line_digests}
    current_digest_by_id = {rl.id: line_digest(rl) for rl in lines}
    modified = tuple(
        sorted(
            lid
            for lid, digest in prev_digests.items()
            if lid in current_digest_by_id and current_digest_by_id[lid] != digest
        )
    )
    # Escalation keyed on ISSUE-TIME severity: a removed OR modified line whose
    # prior severity was CANARY-grade is the load-bearing signal — surface it above
    # any lower-severity change.
    canary_altered = tuple(
        sorted(lid for lid in set(removed) | set(modified) if prev_severity.get(lid) == "canary")
    )

    # A hand-crafted statement whose digest matches but whose binding metadata is
    # malformed is internally inconsistent — never certify it intact. Empty
    # line_digests preserves compatibility with pre-field statements; populated
    # metadata must be a complete, duplicate-free snapshot of the current lines.
    ids_consistent = len(prev.line_ids) == len(set(prev.line_ids)) and set(prev.line_ids) == current_ids
    expected_digests = tuple(
        (rl.id, rl.severity.value, current_digest_by_id[rl.id]) for rl in sorted(lines, key=lambda r: r.id)
    )
    digest_metadata_consistent = not prev.line_digests or (
        len(prev.line_digests) == len(set(prev.line_digests))
        and tuple(sorted(prev.line_digests)) == expected_digests
    )
    metadata_consistent = ids_consistent and digest_metadata_consistent
    intact = not drift and not stale and not removed and not added and not modified and metadata_consistent

    if canary_altered:
        detail = f"CANARY-GRADE LINE ALTERED: {', '.join(canary_altered)}"
    elif removed:
        detail = f"CANARY TRIPPED (pattern) — removed lines: {', '.join(removed)}"
    elif modified:
        detail = f"registry changed — modified lines: {', '.join(modified)}"
    elif drift:
        detail = "registry changed (no removals) — review the diff and re-issue the canary"
    elif not metadata_consistent:
        detail = "canary metadata inconsistent — line ids or per-line digests do not match the registry"
    elif stale:
        detail = f"canary stale — last issued {prev.issued_on}, older than {max_age_days} days as of {as_of}"
    else:
        detail = "registry hash unchanged and attestation fresh — canary intact"

    return CanaryVerification(
        intact=intact,
        drift=drift,
        stale=stale,
        removed_ids=removed,
        added_ids=added,
        detail=detail,
        modified_ids=modified,
        metadata_consistent=metadata_consistent,
        canary_altered_ids=canary_altered,
    )


def _validate_metadata_shape(prev: CanaryStatement) -> None:
    """Defensively validate hand-crafted or aggregate-only statements before verification."""

    if not isinstance(prev.statement, str) or not prev.statement.strip():
        raise ValueError("statement is empty")
    if not isinstance(prev.issued_on, str):
        raise TypeError("issued_on is not a string")
    date.fromisoformat(prev.issued_on)
    if not isinstance(prev.registry_digest, str) or not _SHA256.fullmatch(prev.registry_digest):
        raise ValueError("registry_digest is not a SHA-256 digest")
    if not isinstance(prev.line_ids, (tuple, list)):
        raise TypeError("line_ids is not a collection")
    if any(not isinstance(line_id, str) or not line_id.strip() for line_id in prev.line_ids):
        raise ValueError("line_ids contains an invalid identifier")
    if len(prev.line_ids) != len(set(prev.line_ids)):
        raise ValueError("line_ids contains duplicates")
    if not isinstance(prev.line_digests, (tuple, list)):
        raise TypeError("line_digests is not a collection")
    for item in prev.line_digests:
        if not isinstance(item, (tuple, list)) or len(item) != 3:
            raise ValueError("line_digests contains a malformed triple")
        line_id, severity, digest = item
        if not isinstance(line_id, str) or not line_id.strip():
            raise ValueError("line_digests contains an invalid identifier")
        if severity not in {"canary", "absolute", "strong"}:
            raise ValueError("line_digests contains an invalid severity")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError("line_digests contains an invalid digest")
