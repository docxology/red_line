"""Beacon-and-canary instrument (Turner durability / transparency analog).

Turner protects the framework's *durability*: material modifications require
advance notice with rationale, and if the Review Body's capacity is impaired the
impairment is disclosed. The personal analog is cryptographic rather than
procedural:

  * **Beacon** — the red-line registry is public, so anyone can see the standard
    the author holds and align to it.
  * **Canary** — the registry is reduced to a deterministic content hash carried
    in a dated ``CanaryStatement``. Because the statement must be re-issued with a
    fresh date to stay current, the *silent removal or weakening* of a red line, or
    a *stale attestation that stops being re-issued*, becomes a detectable state.
    ``detect_line_removal`` names exactly which lines vanished between two versions.

**Honest naming.** This uses the *pattern* of a warrant canary — absence or
staleness of an affirmative attestation is the signal — NOT the legal instrument.
A warrant canary's force rests on a legal asymmetry (compelled silence is lawful,
compelled affirmative lies are not) that does not apply to a personal framework.
This is a *tamper-evident freshness attestation*: it makes weakening the standard
**visible and auditable**, it does not **prevent** it. Enforcement here is
visibility, not immunity — the author is also the enforcer, and that limitation is
disclosed rather than papered over.

Determinism is the whole point: the content hash is a pure function of
canonicalized registry content, with no timestamps or environment inputs. Freshness
is tracked separately, via the statement's ``issued_on`` date.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re

from ..model import RedLine, Severity
from ..registry import PERSONAL_RED_LINES
from .hashing import line_digest, registry_hash
from .verification import detect_line_removal

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SEVERITY_VALUES = frozenset(severity.value for severity in Severity)


@dataclass(frozen=True)
class CanaryStatement:
    """A dated attestation binding a registry hash to a public statement.

    Attributes:
        statement: The public warrant-canary text.
        issued_on: ISO date the statement was issued.
        registry_digest: The registry hash at issue time.
        line_ids: The ids present in the registry at issue time.
        line_digests: Per-line ``(id, severity_value, digest)`` triples captured
            at issue time. Binding the *issue-time severity* alongside the digest
            lets a later verification escalate on a canary-grade line whose
            severity may since have been weakened in the live registry. Defaults
            to ``()`` so aggregate-only statements — those issued before this field
            existed, including the committed fixture — remain valid and fall back to
            aggregate-hash behavior.
    """

    statement: str
    issued_on: str
    registry_digest: str
    line_ids: tuple[str, ...]
    line_digests: tuple[tuple[str, str, str], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError("canary statement text is required")
        if not isinstance(self.issued_on, str):
            raise TypeError("canary issued_on must be an ISO date string")
        try:
            date.fromisoformat(self.issued_on)
        except ValueError as exc:
            raise ValueError("canary issued_on must be an ISO date") from exc
        if not isinstance(self.registry_digest, str) or not _SHA256.fullmatch(self.registry_digest):
            raise ValueError("canary registry_digest must be a lowercase SHA-256 hex digest")
        if not isinstance(self.line_ids, (tuple, list)):
            raise TypeError("canary line_ids must be a tuple or list")
        if any(not isinstance(line_id, str) or not line_id.strip() for line_id in self.line_ids):
            raise ValueError("canary line_ids must contain non-empty strings")
        if len(self.line_ids) != len(set(self.line_ids)):
            raise ValueError("canary line_ids must be unique")
        if not isinstance(self.line_digests, (tuple, list)):
            raise TypeError("canary line_digests must be a tuple or list")
        triples: list[tuple[str, str, str]] = []
        for item in self.line_digests:
            if not isinstance(item, (tuple, list)) or len(item) != 3:
                raise ValueError("canary line_digests must contain (id, severity, digest) triples")
            line_id, severity, digest = item
            if not isinstance(line_id, str) or not line_id.strip():
                raise ValueError("canary line digest ids must be non-empty strings")
            if severity not in _SEVERITY_VALUES:
                raise ValueError("canary line digest severity is not recognized")
            if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                raise ValueError("canary line digest must be a lowercase SHA-256 hex digest")
            triples.append((line_id, severity, digest))
        if len(triples) != len({item[0] for item in triples}):
            raise ValueError("canary line_digests must not repeat line ids")
        if triples and {item[0] for item in triples} != set(self.line_ids):
            raise ValueError("canary line_digests ids must match line_ids")
        object.__setattr__(self, "line_ids", tuple(self.line_ids))
        object.__setattr__(self, "line_digests", tuple(triples))


DEFAULT_CANARY_TEXT = (
    "As of this date these red lines stand unweakened; none has been removed or "
    "narrowed under pressure. If a line disappears without a dated, rationaled "
    "successor statement, treat that silence as signal."
)


def issue_canary(
    issued_on: str,
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
    statement: str = DEFAULT_CANARY_TEXT,
    *,
    prev: CanaryStatement | None = None,
    rationale: str | None = None,
) -> CanaryStatement:
    """Create a ``CanaryStatement`` for ``lines`` at ``issued_on`` (ISO date).

    Successor guard (Turner's "material modification requires a dated, rationaled
    successor"): when ``prev`` is supplied AND the registry hash has changed since
    ``prev`` was issued, a silent re-issue would erase the tamper-evidence. In
    that case:

      * if the caller left the default statement and gave no ``rationale``, this
        raises ``ValueError`` naming both 8-char digests — silence is refused; the
        author must acknowledge the drift.
      * if a ``rationale`` is given, a derived *successor statement* is emitted
        that names the superseded digest, the removed/added ids, and the rationale
        — a self-describing audit record rather than an opaque re-issue.

    When ``prev`` is ``None`` (guard bypassed) or the hash is unchanged, behavior
    is exactly the historical path: the supplied ``statement`` is used verbatim.
    ``prev=None`` is the explicit bypass; the git-committed prior canary is the
    intended anchor to pass here.
    """
    if not isinstance(issued_on, str):
        raise TypeError("issued_on must be an ISO date string")
    try:
        issued_on = date.fromisoformat(issued_on).isoformat()
    except ValueError as exc:
        raise ValueError("issued_on must be an ISO date") from exc
    if not isinstance(statement, str) or not statement.strip():
        raise ValueError("canary statement text is required")
    current_digest = registry_hash(lines)
    effective_statement = statement

    if prev is not None and current_digest != prev.registry_digest:
        removed = detect_line_removal(prev.line_ids, lines)
        current_ids = {rl.id for rl in lines}
        added = tuple(sorted(current_ids - set(prev.line_ids)))
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(
                "registry hash changed from "
                f"{prev.registry_digest[:8]} to {current_digest[:8]} but no "
                "rationale was supplied for the successor canary; pass "
                "rationale= to emit a dated successor statement, or prev=None to "
                "bypass the guard deliberately"
            )
        removed_str = ", ".join(removed) if removed else "none"
        added_str = ", ".join(added) if added else "none"
        effective_statement = (
            f"Supersedes canary {prev.registry_digest[:8]} ({prev.issued_on}). "
            f"Removed: [{removed_str}] Added: [{added_str}] "
            "(content modified; ids unchanged if both empty). "
            f"Rationale: {rationale.strip()}"
        )
        if statement != DEFAULT_CANARY_TEXT:
            effective_statement += f" Author note: {statement.strip()}"

    return CanaryStatement(
        statement=effective_statement,
        issued_on=issued_on,
        registry_digest=current_digest,
        line_ids=tuple(sorted(rl.id for rl in lines)),
        line_digests=tuple(
            (rl.id, rl.severity.value, line_digest(rl)) for rl in sorted(lines, key=lambda r: r.id)
        ),
    )
