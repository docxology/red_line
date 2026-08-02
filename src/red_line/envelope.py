"""The common report envelope Red Line exports for co-registration.

A reader holding reports from several independent instruments needs one
uniform way to say "this instrument, about this subject, at this review
moment, said this — and here is the pointer to its complete native report."
The envelope is that data contract and nothing more. It points to the full
canonical review finding by digest instead of copying or reinterpreting its
fields, so this instrument remains authoritative about its own vocabulary,
and it carries the instrument's non-claims with it, so a stored envelope
cannot quietly outgrow what the instrument was allowed to say.

The shared shape is declared per instrument under the schema string
``line.report-envelope/1.0``; sibling instruments that export the same shape
do so by publishing the same schema string, never by importing one another.
``native_status`` is deliberately typed as this line's own vocabulary — for
Red Line, the single :class:`~red_line.model.enums.Classification` value the
evaluator emitted. Selecting the most severe applicable outcome (intake stop
first, hard block over narrowing, narrowing over silence) is the native
evaluator contract, already part of what :func:`review_engagement` records;
the envelope does not flatten anything further. The complete derivation —
the rendered finding prose, the stable reason codes, the evidence-stop
dimensions, the normalized scope, and any named authorization — stays behind
``report_ref`` in full. Envelopes from different lines must not be compared,
ranked, averaged, or merged on ``native_status``. An envelope is a witness
record, not a score.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from collections.abc import Iterable

from .canary import registry_hash
from .model import RedLine
from .oversight import ReviewFinding
from .registry import PERSONAL_RED_LINES
from .version import PROJECT_VERSION

#: Schema string for the complete canonical serialization of one native
#: review finding — the document ``report_ref`` digests.
REPORT_SCHEMA = "red-line.report/1.0"

#: The cross-instrument envelope shape this module exports.
ENVELOPE_SCHEMA = "line.report-envelope/1.0"

#: This instrument's identity inside an envelope.
RED_LINE_ID = "red_line"

#: The non-claims every envelope carries, restating the instrument boundary
#: (README limitations, ``docs/README.md`` honesty boundary, and
#: ``manuscript/10_limitations.md``) in transportable form.
SCOPE_AND_NONCLAIMS: tuple[str, ...] = (
    "classifies one described action against the author's own dated, "
    "first-person, revisable red-line registry at a stated review date",
    "evidence-gated auditability, not enforcement, legal adjudication, "
    "truth verification, real-world safety, or external certification",
    "OUTSIDE_SCOPE is not 'safe' and COMPLIANT is not 'universally "
    "acceptable': both are bounded by the registry's lines, their current "
    "vocabulary, and the quality of the intake",
    "'verified' means a reviewable artifact or source was identified, not "
    "that it is accurate, complete, current, or lawfully obtained",
    "a named authorization is a visible escalation record and never "
    "releases a blocking result",
    "the evaluator is lexical over a declared scope, not semantic over "
    "free text",
    "does not rank, merge, or evaluate the other line instruments",
)


def canonical_report(finding: ReviewFinding) -> str:
    """Serialize a review finding into stable JSON so it can be archived.

    This is the complete derivation, not a summary: the full rendered
    finding prose (verdict, reason bullets, and any advisory hints), the
    stable reason codes, every evidence-stop dimension, the declared and
    normalized scope, the tier, the ambiguity flag, and the authorization
    record — serialized in full when present and as an explicit ``null``
    when absent, so the set-aside arm is part of the canonical document
    rather than an omission. Two identical reviews produce byte-identical
    output, which lets a finding be diffed, digested, and cited.
    """

    if not isinstance(finding, ReviewFinding):
        raise TypeError("canonical_report requires a ReviewFinding")
    authorization = (
        None
        if finding.authorization is None
        else {
            "authorized_by": finding.authorization.authorized_by,
            "authority": finding.authorization.authority,
            "rationale": finding.authorization.rationale,
            "recorded_on": finding.authorization.recorded_on,
        }
    )
    payload = {
        "schema_version": REPORT_SCHEMA,
        "engagement": finding.engagement,
        "classification": finding.classification.value,
        "implicated_ids": list(finding.implicated_ids),
        "finding": finding.finding,
        "reviewed_on": finding.reviewed_on,
        "authorization": authorization,
        "declared_scope": list(finding.declared_scope),
        "tier": finding.tier,
        "ambiguous": finding.ambiguous,
        "reason_codes": list(finding.reason_codes),
        "missing_evidence": list(finding.missing_evidence),
        "unresolved_evidence": list(finding.unresolved_evidence),
        "stale_evidence": list(finding.stale_evidence),
        "normalized_scope": list(finding.normalized_scope),
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def report_digest(finding: ReviewFinding) -> str:
    """SHA-256 over the canonical finding; the pointer an envelope carries."""

    return hashlib.sha256(canonical_report(finding).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReportEnvelope:
    """One instrument's complete review finding, referenced without reinterpretation.

    ``report_ref`` is the SHA-256 of the canonical native finding, which
    contains the full derivation. ``native_status`` is this line's own
    classification word; it is a projection, and the state it projects from
    is behind the reference, not restated here. ``registry_version`` is the
    package version that shipped the registry — the registry has no separate
    version marker, and its content is pinned by ``registry_digest``, the
    same deterministic hash the canary attests. ``source_snapshot_refs`` is
    caller-supplied provenance for the material the review was made about;
    the envelope stores, and does not verify, those references.
    """

    schema_version: str
    line_id: str
    subject_id: str
    review_date: str
    registry_version: str
    registry_digest: str
    native_status: str
    report_ref: str
    source_snapshot_refs: tuple[str, ...]
    scope_and_nonclaims: tuple[str, ...]

    def __post_init__(self) -> None:
        strings = (
            self.schema_version,
            self.line_id,
            self.subject_id,
            self.review_date,
            self.registry_version,
            self.registry_digest,
            self.native_status,
            self.report_ref,
        )
        if any(not isinstance(value, str) for value in strings):
            raise TypeError("envelope scalar fields must be strings")
        for name, values in (
            ("source_snapshot_refs", self.source_snapshot_refs),
            ("scope_and_nonclaims", self.scope_and_nonclaims),
        ):
            if not isinstance(values, (tuple, list)):
                raise TypeError(f"envelope {name} must be a tuple or list")
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"envelope {name} must contain non-blank strings")
            object.__setattr__(self, name, tuple(values))


def finding_envelope(
    finding: ReviewFinding,
    subject_id: str = "",
    source_snapshot_refs: Iterable[str] = (),
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> ReportEnvelope:
    """Wrap a review finding in the common envelope, pointing at — never
    re-reading — its complete canonical form.

    ``subject_id`` names what was reviewed, in the caller's own reference
    scheme; the instrument does not verify it. ``lines`` must be the same
    registry the review was evaluated against (the default is the live
    personal registry that :func:`review_engagement` also defaults to); its
    content is pinned into ``registry_digest``. The envelope's ``report_ref``
    is computed from the exact finding supplied, so an envelope can only
    ever point at the derivation that produced its classification.
    """

    if not isinstance(finding, ReviewFinding):
        raise TypeError("finding_envelope requires a ReviewFinding")
    if not isinstance(subject_id, str):
        raise TypeError("subject_id must be a string")
    if isinstance(source_snapshot_refs, (str, bytes)):
        raise TypeError("source_snapshot_refs must be a collection of strings, not one bare string")
    refs = tuple(source_snapshot_refs)
    if any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        raise ValueError("source_snapshot_refs must contain non-blank strings")
    return ReportEnvelope(
        schema_version=ENVELOPE_SCHEMA,
        line_id=RED_LINE_ID,
        subject_id=subject_id,
        review_date=finding.reviewed_on,
        registry_version=PROJECT_VERSION,
        registry_digest=registry_hash(lines),
        native_status=finding.classification.value,
        report_ref=report_digest(finding),
        source_snapshot_refs=refs,
        scope_and_nonclaims=SCOPE_AND_NONCLAIMS,
    )


def canonical_envelope(envelope: ReportEnvelope) -> str:
    """Serialize an envelope to stable JSON for archiving beside its report.

    Store this string next to the :func:`canonical_report` output it points
    at; the pair is the smallest archive from which a later review can verify
    that the envelope and the derivation still agree.
    """

    payload = {
        "schema_version": envelope.schema_version,
        "line_id": envelope.line_id,
        "subject_id": envelope.subject_id,
        "review_date": envelope.review_date,
        "registry_version": envelope.registry_version,
        "registry_digest": envelope.registry_digest,
        "native_status": envelope.native_status,
        "report_ref": envelope.report_ref,
        "source_snapshot_refs": list(envelope.source_snapshot_refs),
        "scope_and_nonclaims": list(envelope.scope_and_nonclaims),
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def envelope_matches_finding(
    envelope: ReportEnvelope,
    finding: ReviewFinding,
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> bool:
    """Return whether an envelope still points at exactly this finding.

    This is the read-back check for an archived pair: the digest, the review
    date, the classification word, and the registry digest must all agree.
    A mismatch means one of the two was edited after export; the check cannot
    say which, and it says nothing about the truth of either.
    """

    return (
        envelope.report_ref == report_digest(finding)
        and envelope.review_date == finding.reviewed_on
        and envelope.native_status == finding.classification.value
        and envelope.registry_digest == registry_hash(lines)
    )


__all__ = [
    "ENVELOPE_SCHEMA",
    "RED_LINE_ID",
    "REPORT_SCHEMA",
    "ReportEnvelope",
    "SCOPE_AND_NONCLAIMS",
    "canonical_envelope",
    "canonical_report",
    "envelope_matches_finding",
    "finding_envelope",
    "report_digest",
]
