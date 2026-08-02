"""The canonical review-finding serialization and the common report envelope.

The 2026-07-29 design review of the line set proposed one common report
envelope per line: a record that points at the complete native report by
digest, carries the line's own status word in the line's own vocabulary, and
transports the instrument's non-claims with it. These tests exercise Red
Line's export of that contract against real findings produced by the real
``review_engagement`` over the live registry — including the analysis
subpackage's canonical five-case battery, so every classification the
evaluator can emit passes through the envelope.
"""

from __future__ import annotations

import dataclasses
import json
from datetime import date

import pytest

from red_line import (
    ENVELOPE_SCHEMA,
    PERSONAL_RED_LINES,
    RED_LINE_ID,
    REPORT_SCHEMA,
    SCOPE_AND_NONCLAIMS,
    Classification,
    ReportEnvelope,
    ReviewAuthorization,
    ReviewFinding,
    __version__,
    canonical_envelope,
    canonical_report,
    envelope_matches_finding,
    finding_envelope,
    registry_hash,
    report_digest,
    review_engagement,
)
from red_line.analysis import canonical_battery
from red_line.analysis.outcome_coverage import BATTERY_AS_OF

from tests.helpers import action

#: Fresh review date for helper-built findings: the helper's evidence is dated
#: at ``date.today()``, so evaluating as of now keeps it non-stale forever.
#: The analysis battery below is evaluated at its own fixed ``BATTERY_AS_OF``
#: (its fixture evidence is dated there for deterministic figures/prose), so a
#: single review date can never silently go stale for either source.
AS_OF = date.today().isoformat()

ENVELOPE_FIELDS = (
    "schema_version",
    "line_id",
    "subject_id",
    "review_date",
    "registry_version",
    "registry_digest",
    "native_status",
    "report_ref",
    "source_snapshot_refs",
    "scope_and_nonclaims",
)


def _blocking_finding() -> ReviewFinding:
    """A real NON_COMPLIANT finding from the live evaluator."""

    return review_engagement(
        action(
            "Targeting component with no adjacent-use narrowing",
            frozenset({"targeting"}),
        ),
        reviewed_on=AS_OF,
    )


def _authorized_finding() -> ReviewFinding:
    """A blocking finding carrying a named escalation record."""

    return review_engagement(
        action(
            "Targeting component with no adjacent-use narrowing",
            frozenset({"targeting"}),
        ),
        reviewed_on=AS_OF,
        authorization=ReviewAuthorization(
            authorized_by="Daniel Ari Friedman",
            authority="author",
            rationale="escalation record for the archive-pair tests",
            recorded_on=AS_OF,
        ),
    )


# ---------------------------------------------------------------------------
# The canonical native report.
# ---------------------------------------------------------------------------


def test_canonical_report_is_deterministic() -> None:
    """Two identical reviews serialize to byte-identical canonical strings."""

    first = canonical_report(_blocking_finding())
    second = canonical_report(_blocking_finding())
    assert first == second
    assert report_digest(_blocking_finding()) == report_digest(_blocking_finding())


def test_canonical_report_carries_every_finding_field() -> None:
    """The serialization is the complete derivation, bound to the dataclass
    roster, so a field added to ``ReviewFinding`` cannot silently stay out."""

    payload = json.loads(canonical_report(_blocking_finding()))
    assert payload["schema_version"] == REPORT_SCHEMA
    roster = {field.name for field in dataclasses.fields(ReviewFinding)}
    assert set(payload) == roster | {"schema_version"}


def test_canonical_report_serializes_the_set_aside_authorization_arm() -> None:
    """An absent authorization is an explicit ``null``, not an omission, and
    a present one serializes in full."""

    without = json.loads(canonical_report(_blocking_finding()))
    assert without["authorization"] is None

    with_record = json.loads(canonical_report(_authorized_finding()))
    assert with_record["authorization"] == {
        "authorized_by": "Daniel Ari Friedman",
        "authority": "author",
        "rationale": "escalation record for the archive-pair tests",
        "recorded_on": AS_OF,
    }


def test_canonical_report_keeps_the_full_reason_trail_and_verdict_prose() -> None:
    """The complete rendered finding — verdict, reason codes, and reason
    bullets — travels inside the canonical report, not a summary of it."""

    finding = _blocking_finding()
    payload = json.loads(canonical_report(finding))
    assert payload["finding"] == finding.finding
    assert "NON-COMPLIANT — may not proceed." in payload["finding"]
    assert payload["reason_codes"] == list(finding.reason_codes)
    assert payload["classification"] == Classification.NON_COMPLIANT.value


def test_report_digest_changes_when_any_recorded_field_changes() -> None:
    """The digest binds the whole derivation, not just the verdict word."""

    finding = _blocking_finding()
    baseline = report_digest(finding)
    for tamper in (
        {"reviewed_on": "2026-01-01"},
        {"finding": finding.finding + "\nappended after export"},
        {"classification": Classification.REQUIRES_MODIFICATION},
        {"reason_codes": ()},
        {"tier": "air_gapped"},
        {"ambiguous": True},
    ):
        assert report_digest(dataclasses.replace(finding, **tamper)) != baseline, tamper


def test_canonical_report_rejects_a_non_finding() -> None:
    with pytest.raises(TypeError, match="requires a ReviewFinding"):
        canonical_report("not a finding")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# The common report envelope.
# ---------------------------------------------------------------------------


def test_the_envelope_points_at_the_native_report_without_reinterpreting_it() -> None:
    finding = _blocking_finding()
    envelope = finding_envelope(
        finding, subject_id="worked-example", source_snapshot_refs=("snapshot-1",)
    )
    assert envelope.schema_version == ENVELOPE_SCHEMA
    assert envelope.line_id == RED_LINE_ID
    assert envelope.subject_id == "worked-example"
    assert envelope.review_date == finding.reviewed_on == AS_OF
    assert envelope.registry_version == __version__
    assert envelope.registry_digest == registry_hash()
    assert envelope.native_status == finding.classification.value
    assert envelope.report_ref == report_digest(finding)
    assert envelope.source_snapshot_refs == ("snapshot-1",)
    assert envelope.scope_and_nonclaims == SCOPE_AND_NONCLAIMS


def test_native_status_is_the_projection_and_the_derivation_stays_behind_the_ref() -> None:
    """The envelope carries one classification word; the reason trail, the
    evidence stops, and the finding prose stay behind ``report_ref``."""

    envelope = finding_envelope(_blocking_finding())
    payload = json.loads(canonical_envelope(envelope))
    assert set(payload) == set(ENVELOPE_FIELDS)
    assert payload["native_status"] == Classification.NON_COMPLIANT.value
    assert "reason_codes" not in payload
    assert "finding" not in payload
    assert "implicated_ids" not in payload


def test_every_classification_projects_through_the_envelope() -> None:
    """The live evaluator's whole outcome vocabulary survives the envelope
    unchanged — the battery reaches all five classifications, and each
    envelope's status word is exactly the native one."""

    statuses = set()
    for case in canonical_battery():
        finding = review_engagement(case.action, reviewed_on=BATTERY_AS_OF)
        envelope = finding_envelope(finding, subject_id=case.name)
        assert envelope.native_status == finding.classification.value, case.name
        assert envelope_matches_finding(envelope, finding), case.name
        statuses.add(envelope.native_status)
    assert statuses == {classification.value for classification in Classification}


def test_canonical_envelope_is_deterministic() -> None:
    finding = _blocking_finding()
    first = canonical_envelope(finding_envelope(finding, subject_id="s"))
    second = canonical_envelope(finding_envelope(finding, subject_id="s"))
    assert first == second


def test_the_nonclaims_travel_inside_the_envelope() -> None:
    """The instrument boundary is part of the record, so a stored envelope
    cannot quietly outgrow what the instrument was allowed to say."""

    envelope = finding_envelope(_blocking_finding())
    assert envelope.scope_and_nonclaims == SCOPE_AND_NONCLAIMS
    assert any("not enforcement" in claim for claim in envelope.scope_and_nonclaims)
    assert any("never" in claim and "releases a blocking result" in claim
               for claim in envelope.scope_and_nonclaims)
    assert any("lexical over a declared scope" in claim for claim in envelope.scope_and_nonclaims)
    assert any("does not rank, merge, or evaluate" in claim
               for claim in envelope.scope_and_nonclaims)
    archived = json.loads(canonical_envelope(envelope))
    assert archived["scope_and_nonclaims"] == list(SCOPE_AND_NONCLAIMS)


def test_envelope_matches_finding_verifies_an_archived_pair() -> None:
    finding = _blocking_finding()
    envelope = finding_envelope(finding, subject_id="worked-example")
    assert envelope_matches_finding(envelope, finding)

    other = review_engagement(
        action("Static documentation tooling", frozenset({"static_documentation"})),
        reviewed_on=AS_OF,
    )
    assert not envelope_matches_finding(envelope, other)


def test_a_tampered_envelope_field_is_detected() -> None:
    """Each checked field breaks the read-back match when edited alone."""

    finding = _blocking_finding()
    envelope = finding_envelope(finding)
    for tamper in (
        {"report_ref": "0" * 64},
        {"review_date": "2020-01-01"},
        {"native_status": "compliant"},
        {"registry_digest": "0" * 64},
    ):
        assert not envelope_matches_finding(
            dataclasses.replace(envelope, **tamper), finding
        ), tamper


def test_the_registry_digest_binds_the_envelope_to_registry_content() -> None:
    """A modified registry — one line's standard edited — no longer matches
    an envelope exported against the live one."""

    finding = _blocking_finding()
    envelope = finding_envelope(finding)
    edited = dataclasses.replace(
        PERSONAL_RED_LINES[0], standard=PERSONAL_RED_LINES[0].standard + " (weakened)"
    )
    planted = (edited,) + PERSONAL_RED_LINES[1:]
    assert envelope.registry_digest != registry_hash(planted)
    assert not envelope_matches_finding(envelope, finding, lines=planted)
    assert envelope_matches_finding(envelope, finding, lines=PERSONAL_RED_LINES)


def test_envelope_input_validation_fails_closed() -> None:
    finding = _blocking_finding()
    with pytest.raises(TypeError, match="requires a ReviewFinding"):
        finding_envelope("not a finding")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="subject_id must be a string"):
        finding_envelope(finding, subject_id=7)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="not one bare string"):
        finding_envelope(finding, source_snapshot_refs="snapshot-1")
    with pytest.raises(ValueError, match="non-blank strings"):
        finding_envelope(finding, source_snapshot_refs=("",))
    with pytest.raises(ValueError, match="non-blank strings"):
        finding_envelope(finding, source_snapshot_refs=(42,))  # type: ignore[arg-type]


def test_envelope_dataclass_rejects_malformed_state() -> None:
    """The frozen record itself fails closed, matching the house contract."""

    envelope = finding_envelope(_blocking_finding())
    with pytest.raises(TypeError, match="scalar fields must be strings"):
        dataclasses.replace(envelope, subject_id=7)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="must be a tuple or list"):
        dataclasses.replace(envelope, source_snapshot_refs="bare")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="non-blank strings"):
        dataclasses.replace(envelope, scope_and_nonclaims=("ok", " "))
    coerced = ReportEnvelope(
        schema_version=envelope.schema_version,
        line_id=envelope.line_id,
        subject_id=envelope.subject_id,
        review_date=envelope.review_date,
        registry_version=envelope.registry_version,
        registry_digest=envelope.registry_digest,
        native_status=envelope.native_status,
        report_ref=envelope.report_ref,
        source_snapshot_refs=["ref-as-list"],
        scope_and_nonclaims=list(SCOPE_AND_NONCLAIMS),
    )
    assert coerced.source_snapshot_refs == ("ref-as-list",)
    assert coerced.scope_and_nonclaims == SCOPE_AND_NONCLAIMS


def test_the_authorization_arm_travels_behind_the_ref_not_in_the_envelope() -> None:
    """A named escalation changes the digest — it is part of the derivation —
    but never surfaces as an envelope field of its own."""

    plain = _blocking_finding()
    authorized = _authorized_finding()
    assert report_digest(plain) != report_digest(authorized)
    payload = json.loads(canonical_envelope(finding_envelope(authorized)))
    assert "authorization" not in payload
    assert finding_envelope(authorized).native_status == plain.classification.value
