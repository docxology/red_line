"""Enum definitions for the red-line framework model."""

from __future__ import annotations

from enum import Enum


class DeploymentTier(Enum):
    """Oversight-retention grade for a work product (Turner Tier 1/2/3 analog).

    Turner keys deployment eligibility to how much runtime oversight The Company
    retains. The personal analog keys what a work product may do to how much the
    author can still observe and withdraw it after release.
    """

    HOSTED = "hosted"  # Tier 1: author-operated; full observation + withdrawal.
    CONNECTED = "connected"  # Tier 2: on client premises but author retains update/suspend.
    AIR_GAPPED = "air_gapped"  # Tier 3: released beyond recall (OSS, handed-off model).

    @property
    def oversight_rank(self) -> int:
        """Higher rank = more retained oversight."""
        return {"air_gapped": 0, "connected": 1, "hosted": 2}[self.value]


class Severity(Enum):
    """Grades a red line by how the author treats a breach.

    ``CANARY`` lines are load-bearing: their removal is itself a reportable
    event (warrant-canary semantics). Others are ordered by escalation.
    """

    CANARY = "canary"
    ABSOLUTE = "absolute"
    STRONG = "strong"


class Classification(Enum):
    """Outcome of evaluating a proposed engagement.

    ``INSUFFICIENT_INFORMATION`` is deliberately distinct from both
    ``NON_COMPLIANT`` and ``OUTSIDE_SCOPE``: a missing or unverifiable context
    is a stop signal, not permission and not a policy violation finding.
    """

    COMPLIANT = "compliant"
    REQUIRES_MODIFICATION = "requires_modification"
    NON_COMPLIANT = "non_compliant"
    OUTSIDE_SCOPE = "outside_scope"
    INSUFFICIENT_INFORMATION = "insufficient_information"


class EvidenceStatus(Enum):
    """Epistemic status of an intake record.

    Only ``VERIFIED`` evidence can satisfy a required field.  The evaluator
    does not decide whether a source is true; it records whether a reviewable
    artifact exists and refuses to treat assertion as verification.
    """

    VERIFIED = "verified"
    SELF_ASSERTED = "self_asserted"
    UNVERIFIED = "unverified"
    CONTRADICTED = "contradicted"


class EvidenceKind(Enum):
    """Required intake dimensions for a strict action review."""

    PURPOSE = "purpose"
    END_USE = "end_use"
    AFFECTED_PARTIES = "affected_parties"
    DATA_PROVENANCE = "data_provenance"
    LEGAL_BASIS = "legal_basis"
    HUMAN_CONTROL = "human_control"
    DEPLOYMENT = "deployment"
    DOWNSTREAM_TRANSFER = "downstream_transfer"
    CAPABILITY_SCOPE = "capability_scope"


class ExemptionMatchMode(Enum):
    """How a typed exemption's trigger scope is evaluated."""

    ANY = "any"
    ALL = "all"


class AssessmentReasonCode(Enum):
    """Stable machine-readable explanations for an action assessment.

    Human-readable ``reasons`` remain the explanatory surface. These codes are
    the durable audit surface: callers can aggregate or regression-test why a
    result was reached without parsing prose that may be edited for clarity.
    """

    INTAKE_BLOCKED = "intake_blocked"
    MISSING_EVIDENCE = "missing_evidence"
    UNRESOLVED_EVIDENCE = "unresolved_evidence"
    STALE_EVIDENCE = "stale_evidence"
    INVALID_SCOPE = "invalid_scope"
    UNDECLARED_UNKNOWN = "undeclared_unknown"
    UNKNOWN_SCOPE = "unknown_scope"
    EMPTY_SCOPE = "empty_scope"
    AMBIGUOUS_INTAKE = "ambiguous_intake"
    VERIFIED_EXEMPTION = "verified_exemption"
    MULTIPLE_PROHIBITED_DIMENSIONS = "multiple_prohibited_dimensions"
    BELOW_TIER_FLOOR = "below_tier_floor"
    UNEXEMPTED_LINE = "unexempted_line"
    ALL_LINES_NARROWED = "all_lines_narrowed"
    OUTSIDE_SCOPE = "outside_scope"
