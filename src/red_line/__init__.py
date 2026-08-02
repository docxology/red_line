"""red_line — a versioned personal red-line framework for development work.

A beacon (public, structured articulation of boundaries the author will not
cross) and a canary (a hash-attested statement whose silent modification is
itself a signal). Adapted from and citing Alex Turner's "A Red Line and
Oversight Framework for Government AI Contracts"
(https://turntrout.com/red-line-framework, 2026-07-15) — the org-scale
mechanism, turned into a single practitioner's operating instrument.
"""

from __future__ import annotations

from .canary import (
    CanaryStatement,
    CanaryVerification,
    DEFAULT_CANARY_TEXT,
    DEFAULT_MAX_AGE_DAYS,
    detect_line_removal,
    is_stale,
    issue_canary,
    line_digest,
    registry_hash,
    verify_canary,
)
from .envelope import (
    ENVELOPE_SCHEMA,
    RED_LINE_ID,
    REPORT_SCHEMA,
    ReportEnvelope,
    SCOPE_AND_NONCLAIMS,
    canonical_envelope,
    canonical_report,
    envelope_matches_finding,
    finding_envelope,
    report_digest,
)
from .evaluation import evaluate_action
from .invariants import InvariantResult, all_invariants, invariants_pass
from .model import (
    ActionAssessment,
    ActionContext,
    AssessmentReasonCode,
    Classification,
    DEFAULT_EVIDENCE_MAX_AGE_DAYS,
    DeploymentTier,
    EvidenceKind,
    EvidenceRecord,
    EvidenceStatus,
    ExemptionMatchMode,
    ProposedAction,
    RedLine,
    Severity,
)
from .oversight import (
    ReviewAuthorization,
    ReviewFinding,
    TransparencyReport,
    review_engagement,
    transparency_report,
)
from .registry import (
    PERSONAL_RED_LINES,
    REGISTRY_IS_EXHAUSTIVE,
    SOURCE_DATE,
    SOURCE_FRAMEWORK,
    SOURCE_URL,
)
from .version import PROJECT_VERSION

__version__ = PROJECT_VERSION

__all__ = [
    "__version__",
    "SOURCE_FRAMEWORK",
    "SOURCE_URL",
    "SOURCE_DATE",
    "RedLine",
    "DeploymentTier",
    "Severity",
    "EvidenceKind",
    "EvidenceStatus",
    "ExemptionMatchMode",
    "Classification",
    "ActionContext",
    "AssessmentReasonCode",
    "EvidenceRecord",
    "ProposedAction",
    "ActionAssessment",
    "DEFAULT_EVIDENCE_MAX_AGE_DAYS",
    "PERSONAL_RED_LINES",
    "REGISTRY_IS_EXHAUSTIVE",
    "evaluate_action",
    "ReviewFinding",
    "ReviewAuthorization",
    "TransparencyReport",
    "review_engagement",
    "transparency_report",
    "CanaryStatement",
    "CanaryVerification",
    "DEFAULT_CANARY_TEXT",
    "DEFAULT_MAX_AGE_DAYS",
    "registry_hash",
    "line_digest",
    "issue_canary",
    "verify_canary",
    "detect_line_removal",
    "is_stale",
    "ENVELOPE_SCHEMA",
    "RED_LINE_ID",
    "REPORT_SCHEMA",
    "SCOPE_AND_NONCLAIMS",
    "ReportEnvelope",
    "canonical_report",
    "report_digest",
    "finding_envelope",
    "canonical_envelope",
    "envelope_matches_finding",
    "InvariantResult",
    "all_invariants",
    "invariants_pass",
]
