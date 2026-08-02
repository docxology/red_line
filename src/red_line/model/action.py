"""Strict action-intake, evidence, and assessment records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import re

from .enums import AssessmentReasonCode, Classification, DeploymentTier, EvidenceKind, EvidenceStatus
from .red_line import RedLine


REQUIRED_EVIDENCE_KINDS: tuple[EvidenceKind, ...] = tuple(EvidenceKind)
DEFAULT_EVIDENCE_MAX_AGE_DAYS = 180
NOT_APPLICABLE = "not_applicable"
_MISSING_VALUES = frozenset({"", "unknown", "unspecified", "tbd", "unclear"})
_SENSITIVE_REFERENCE_MARKERS = frozenset({"password=", "token=", "secret=", "bearer ", "sk-"})
_RAW_PERSONAL_REFERENCE = re.compile(r"(?:\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|\b\d{3}-\d{2}-\d{4}\b)")


@dataclass(frozen=True)
class EvidenceRecord:
    """A reviewable pointer supporting one intake dimension."""

    kind: EvidenceKind
    reference: str
    summary: str
    status: EvidenceStatus
    recorded_on: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, EvidenceKind) or not isinstance(self.status, EvidenceStatus):
            raise TypeError("evidence kind and status must use the declared enums")
        if not isinstance(self.reference, str) or not isinstance(self.summary, str):
            raise TypeError("evidence reference and summary must be strings")
        if not isinstance(self.recorded_on, str):
            raise TypeError("recorded_on must be an ISO date string")
        if not self.reference.strip() or not self.summary.strip():
            raise ValueError("evidence reference and summary are required")
        if any(marker in self.reference.casefold() for marker in _SENSITIVE_REFERENCE_MARKERS):
            raise ValueError("evidence references must not contain raw secret material")
        if _RAW_PERSONAL_REFERENCE.search(self.reference):
            raise ValueError("evidence references must not contain raw personal identifiers")
        try:
            date.fromisoformat(self.recorded_on)
        except (TypeError, ValueError) as exc:
            raise ValueError("recorded_on must be an ISO date") from exc

    def is_stale(self, as_of: date, max_age_days: int = DEFAULT_EVIDENCE_MAX_AGE_DAYS) -> bool:
        """Return whether this record is future-dated or older than the review window."""

        if not isinstance(as_of, date):
            raise TypeError("as_of must be a date")
        if not isinstance(max_age_days, int) or isinstance(max_age_days, bool) or max_age_days < 0:
            raise ValueError("max_age_days must be a non-negative integer")
        recorded = date.fromisoformat(self.recorded_on)
        return recorded > as_of or (as_of - recorded).days > max_age_days


@dataclass(frozen=True)
class ActionContext:
    """Required context for an evidence-gated action review.

    A value may be ``not_applicable`` only when the corresponding evidence kind
    is still supported by a verified record. Missing or unresolved values are
    intentionally represented rather than silently guessed.
    """

    purpose: str
    end_use: str
    affected_parties: str
    data_provenance: str
    legal_basis: str
    human_control: str
    deployment: str
    downstream_transfer: str
    capability_scope: str
    evidence: tuple[EvidenceRecord, ...] = ()
    unknowns: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        fields = (
            self.purpose,
            self.end_use,
            self.affected_parties,
            self.data_provenance,
            self.legal_basis,
            self.human_control,
            self.deployment,
            self.downstream_transfer,
            self.capability_scope,
        )
        if any(not isinstance(value, str) for value in fields):
            raise TypeError("all ActionContext fields must be strings")
        if not isinstance(self.evidence, (tuple, list)):
            raise TypeError("ActionContext evidence must be a tuple or list")
        if not isinstance(self.unknowns, (tuple, list)):
            raise TypeError("ActionContext unknowns must be a tuple or list")
        if any(not isinstance(record, EvidenceRecord) for record in self.evidence):
            raise TypeError("ActionContext evidence must contain EvidenceRecord values")
        if any(not isinstance(value, str) for value in self.unknowns):
            raise TypeError("ActionContext unknowns must contain strings")
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "unknowns", tuple(self.unknowns))

    def values(self) -> dict[EvidenceKind, str]:
        return {
            EvidenceKind.PURPOSE: self.purpose,
            EvidenceKind.END_USE: self.end_use,
            EvidenceKind.AFFECTED_PARTIES: self.affected_parties,
            EvidenceKind.DATA_PROVENANCE: self.data_provenance,
            EvidenceKind.LEGAL_BASIS: self.legal_basis,
            EvidenceKind.HUMAN_CONTROL: self.human_control,
            EvidenceKind.DEPLOYMENT: self.deployment,
            EvidenceKind.DOWNSTREAM_TRANSFER: self.downstream_transfer,
            EvidenceKind.CAPABILITY_SCOPE: self.capability_scope,
        }

    def evidence_for(self, kind: EvidenceKind) -> tuple[EvidenceRecord, ...]:
        return tuple(record for record in self.evidence if record.kind is kind)

    def has_verified_evidence(
        self,
        kind: EvidenceKind,
        as_of: date | None = None,
        max_age_days: int = DEFAULT_EVIDENCE_MAX_AGE_DAYS,
    ) -> bool:
        if not isinstance(kind, EvidenceKind):
            raise TypeError("evidence kind must use the declared enum")
        if as_of is not None and not isinstance(as_of, date):
            raise TypeError("as_of must be a date")
        return any(
            record.status is EvidenceStatus.VERIFIED
            and (as_of is None or not record.is_stale(as_of, max_age_days))
            for record in self.evidence_for(kind)
        )

    def missing_fields(
        self,
        as_of: date | None = None,
        max_age_days: int = DEFAULT_EVIDENCE_MAX_AGE_DAYS,
    ) -> tuple[EvidenceKind, ...]:
        if as_of is not None and not isinstance(as_of, date):
            raise TypeError("as_of must be a date")
        missing: list[EvidenceKind] = []
        for kind, value in self.values().items():
            normalized = value.strip().casefold() if isinstance(value, str) else ""
            if normalized in _MISSING_VALUES or not self.has_verified_evidence(kind, as_of, max_age_days):
                missing.append(kind)
        return tuple(missing)

    def stale_evidence(
        self,
        as_of: date,
        max_age_days: int = DEFAULT_EVIDENCE_MAX_AGE_DAYS,
    ) -> tuple[EvidenceKind, ...]:
        if not isinstance(as_of, date):
            raise TypeError("as_of must be a date")
        return tuple(
            kind
            for kind in REQUIRED_EVIDENCE_KINDS
            if any(record.is_stale(as_of, max_age_days) for record in self.evidence_for(kind))
        )

    def unresolved_evidence(
        self,
        as_of: date | None = None,
        max_age_days: int = DEFAULT_EVIDENCE_MAX_AGE_DAYS,
    ) -> tuple[EvidenceKind, ...]:
        return tuple(
            kind
            for kind in REQUIRED_EVIDENCE_KINDS
            if any(
                record.status is EvidenceStatus.CONTRADICTED
                or record.status
                in {
                    EvidenceStatus.SELF_ASSERTED,
                    EvidenceStatus.UNVERIFIED,
                }
                for record in self.evidence_for(kind)
            )
            and (
                not self.has_verified_evidence(kind, as_of, max_age_days)
                or any(record.status is EvidenceStatus.CONTRADICTED for record in self.evidence_for(kind))
            )
        )

    def complete(self, as_of: date | None = None) -> bool:
        review_date = date.today() if as_of is None else as_of
        return (
            not self.missing_fields(review_date)
            and not self.unknowns
            and not self.unresolved_evidence(review_date)
        )


@dataclass(frozen=True)
class ProposedAction:
    """A candidate engagement to evaluate against the red lines.

    Attributes:
        description: Free text describing the work.
        scope: Domain/capability keywords describing what the work touches.
        context: Evidence-bearing intake record. It is mandatory; description
            text can never substitute for it.
        tier: The tier at which the work would be deployed.
        ambiguous: If True, the requester could not confirm scope details.
            Ambiguity is an intake defect, so the evaluator stops at
            INSUFFICIENT_INFORMATION before policy matching (resolved
            fail-closed in favor of caution); it never reaches a policy
            verdict such as REQUIRES_MODIFICATION.
    """

    description: str
    scope: frozenset[str]
    context: ActionContext
    tier: DeploymentTier = DeploymentTier.HOSTED
    ambiguous: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.description, str):
            raise TypeError("action description must be a string")
        if not self.description.strip():
            raise ValueError("action description is required")
        if not isinstance(self.scope, (frozenset, set, tuple)):
            raise TypeError("action scope must be a set-like collection of strings")
        if any(not isinstance(token, str) for token in self.scope):
            raise TypeError("action scope tokens must be strings")
        if any(not token.strip() for token in self.scope):
            raise ValueError("action scope tokens must be non-empty")
        if not isinstance(self.context, ActionContext):
            raise TypeError("action context is mandatory and must be an ActionContext")
        if not isinstance(self.tier, DeploymentTier):
            raise TypeError("action tier must use the declared enum")
        if not isinstance(self.ambiguous, bool):
            raise TypeError("ambiguous must be boolean")
        from .red_line import normalize_scope

        object.__setattr__(self, "scope", normalize_scope(frozenset(self.scope)))


@dataclass(frozen=True)
class ActionAssessment:
    """Result of :func:`evaluate_action` (Turner Review-Body finding analog)."""

    action: ProposedAction
    classification: Classification
    implicated: tuple[RedLine, ...]
    reasons: tuple[str, ...] = field(default_factory=tuple)
    missing_evidence: tuple[EvidenceKind, ...] = field(default_factory=tuple)
    unresolved_evidence: tuple[EvidenceKind, ...] = field(default_factory=tuple)
    stale_evidence: tuple[EvidenceKind, ...] = field(default_factory=tuple)
    normalized_scope: tuple[str, ...] = field(default_factory=tuple)
    reason_codes: tuple[AssessmentReasonCode, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.action, ProposedAction):
            raise TypeError("assessment action must be a ProposedAction")
        if not isinstance(self.classification, Classification):
            raise TypeError("assessment classification must use the declared enum")
        if any(not isinstance(line, RedLine) for line in self.implicated):
            raise TypeError("assessment implicated must contain RedLine values")
        for name, values in (
            ("reasons", self.reasons),
            ("missing_evidence", self.missing_evidence),
            ("unresolved_evidence", self.unresolved_evidence),
            ("stale_evidence", self.stale_evidence),
            ("normalized_scope", self.normalized_scope),
            ("reason_codes", self.reason_codes),
        ):
            if not isinstance(values, (tuple, list)):
                raise TypeError(f"assessment {name} must be a tuple or list")
        if any(not isinstance(value, str) for value in tuple(self.reasons) + tuple(self.normalized_scope)):
            raise TypeError("assessment prose and scope values must be strings")
        for values in (self.missing_evidence, self.unresolved_evidence, self.stale_evidence):
            if any(not isinstance(value, EvidenceKind) for value in values):
                raise TypeError("assessment evidence values must use EvidenceKind")
        if any(not isinstance(value, AssessmentReasonCode) for value in self.reason_codes):
            raise TypeError("assessment reason_codes must use AssessmentReasonCode")
        if len(self.reason_codes) != len(set(self.reason_codes)):
            raise ValueError("assessment reason_codes must be unique")
        object.__setattr__(self, "implicated", tuple(self.implicated))
        object.__setattr__(self, "reasons", tuple(self.reasons))
        object.__setattr__(self, "missing_evidence", tuple(self.missing_evidence))
        object.__setattr__(self, "unresolved_evidence", tuple(self.unresolved_evidence))
        object.__setattr__(self, "stale_evidence", tuple(self.stale_evidence))
        object.__setattr__(self, "normalized_scope", tuple(self.normalized_scope))
        object.__setattr__(self, "reason_codes", tuple(self.reason_codes))

    @property
    def outside_scope(self) -> bool:
        """True only when the explicit classification is ``OUTSIDE_SCOPE``."""

        return self.classification is Classification.OUTSIDE_SCOPE
