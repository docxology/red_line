"""Self-review records with non-bypassable escalation metadata."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date

from ..evaluation import evaluate_action
from ..model import (
    ActionAssessment,
    Classification,
    DeploymentTier,
    ProposedAction,
    RedLine,
    normalize_scope,
    normalize_token,
)
from ..registry import PERSONAL_RED_LINES
from ..canary import registry_hash
from ..version import PROJECT_VERSION
from .intake import EVALUATOR_ID, canonical_intake, intake_digest, action_from_snapshot
from ..model.action import LineDecision
from ..model.red_line import _require_scalar_strings


def _validate_review_date(value: str) -> None:
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError("noncanonical date")
    except (TypeError, ValueError) as exc:
        raise ValueError("reviewed_on must be an ISO date in ASCII YYYY-MM-DD calendar form") from exc


@dataclass(frozen=True)
class ReviewAuthorization:
    """A named escalation or remediation record, never a compliance bypass."""

    authorized_by: str
    authority: str
    rationale: str
    recorded_on: str

    def __post_init__(self) -> None:
        fields = (self.authorized_by, self.authority, self.rationale)
        if any(not isinstance(value, str) for value in fields):
            raise TypeError("authorization fields must be strings")
        if not isinstance(self.recorded_on, str):
            raise TypeError("authorization recorded_on must be an ISO date string")
        _require_scalar_strings((*fields, self.recorded_on))
        if not all(value.strip() for value in fields):
            raise ValueError("authorization requires reviewer, authority, and rationale")
        try:
            date.fromisoformat(self.recorded_on)
        except (TypeError, ValueError) as exc:
            raise ValueError("authorization recorded_on must be an ISO date") from exc


@dataclass(frozen=True)
class ReviewFinding:
    """A durable, citable record of one evidence-gated self-review."""

    engagement: str
    classification: Classification
    implicated_ids: tuple[str, ...]
    finding: str
    reviewed_on: str
    authorization: ReviewAuthorization | None = None
    declared_scope: tuple[str, ...] = ()
    tier: str = ""
    ambiguous: bool = False
    reason_codes: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    unresolved_evidence: tuple[str, ...] = ()
    stale_evidence: tuple[str, ...] = ()
    normalized_scope: tuple[str, ...] = ()
    registry_digest: str = ""
    evaluator_version: str = ""
    evaluator_id: str = ""
    intake_digest: str = ""
    decision_trace: tuple[LineDecision, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.engagement, str) or not isinstance(self.finding, str):
            raise TypeError("review finding text fields must be strings")
        if not isinstance(self.reviewed_on, str):
            raise TypeError("reviewed_on must be an ISO date string")
        if not self.engagement.strip() or not self.finding.strip():
            raise ValueError("review findings require engagement and finding text")
        _require_scalar_strings((self.engagement, self.finding))
        if not isinstance(self.classification, Classification):
            raise TypeError("classification must use the declared enum")
        if not isinstance(self.implicated_ids, (tuple, list)):
            raise TypeError("implicated_ids must be a tuple or list")
        if any(
            not isinstance(identifier, str) or not identifier.strip() for identifier in self.implicated_ids
        ):
            raise ValueError("implicated_ids must contain non-empty strings")
        _require_scalar_strings(tuple(self.implicated_ids))
        if len(self.implicated_ids) != len(set(self.implicated_ids)):
            raise ValueError("implicated_ids must be unique")
        if self.authorization is not None and not isinstance(self.authorization, ReviewAuthorization):
            raise TypeError("authorization must be a ReviewAuthorization or None")
        if self.authorization is not None and self.classification in {
            Classification.COMPLIANT,
            Classification.OUTSIDE_SCOPE,
        }:
            raise ValueError("authorization is only valid on blocking findings")
        if not isinstance(self.declared_scope, (tuple, list, set, frozenset)):
            raise TypeError("declared_scope must be a scope collection")
        if any(not isinstance(token, str) for token in self.declared_scope):
            raise TypeError("declared_scope tokens must be strings")
        _require_scalar_strings(tuple(self.declared_scope))
        if not isinstance(self.tier, str):
            raise TypeError("tier must be a string")
        if self.tier and self.tier not in {tier.value for tier in DeploymentTier}:
            raise ValueError("tier must be a declared deployment tier")
        if not isinstance(self.ambiguous, bool):
            raise TypeError("ambiguous must be boolean")
        for name, values in (
            ("reason_codes", self.reason_codes),
            ("missing_evidence", self.missing_evidence),
            ("unresolved_evidence", self.unresolved_evidence),
            ("stale_evidence", self.stale_evidence),
            ("normalized_scope", self.normalized_scope),
        ):
            if not isinstance(values, (tuple, list)):
                raise TypeError(f"{name} must be a tuple or list")
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{name} must contain non-empty strings")
            _require_scalar_strings(tuple(values))
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must not contain duplicates")
        _validate_review_date(self.reviewed_on)
        object.__setattr__(self, "implicated_ids", tuple(self.implicated_ids))
        object.__setattr__(
            self, "declared_scope", tuple(sorted(normalize_scope(frozenset(self.declared_scope))))
            if self.registry_digest else tuple(self.declared_scope)
        )
        object.__setattr__(self, "reason_codes", tuple(self.reason_codes))
        object.__setattr__(self, "missing_evidence", tuple(self.missing_evidence))
        object.__setattr__(self, "unresolved_evidence", tuple(self.unresolved_evidence))
        object.__setattr__(self, "stale_evidence", tuple(self.stale_evidence))
        object.__setattr__(self, "normalized_scope", tuple(self.normalized_scope))
        bindings = (self.registry_digest, self.evaluator_version, self.evaluator_id, self.intake_digest)
        if any(not isinstance(value, str) for value in bindings):
            raise TypeError("review provenance bindings must be strings")
        _require_scalar_strings(bindings)
        if any(bindings) and not all(bindings):
            raise ValueError("review provenance bindings must be all present or all absent (unbound)")
        for digest in (self.registry_digest, self.intake_digest):
            if digest and (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)):
                raise ValueError("review provenance requires SHA-256 digests")
        if not isinstance(self.decision_trace, (tuple, list)) or any(
            not isinstance(entry, LineDecision) for entry in self.decision_trace
        ):
            raise TypeError("finding decision_trace requires LineDecision values")
        if self.decision_trace and not self.registry_digest:
            raise ValueError("unbound findings cannot carry a current decision_trace")
        object.__setattr__(self, "decision_trace", tuple(self.decision_trace))

    @property
    def blocks(self) -> bool:
        """True for every result other than compliant or explicitly outside scope."""

        return self.classification not in {
            Classification.COMPLIANT,
            Classification.OUTSIDE_SCOPE,
        }


def review_engagement(
    action: ProposedAction,
    reviewed_on: str | None = None,
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
    authorization: ReviewAuthorization | None = None,
) -> ReviewFinding:
    """Produce a written finding; authorization never releases a blocking result."""

    on = reviewed_on if reviewed_on is not None else date.today().isoformat()
    _validate_review_date(on)
    # Bind evidence freshness to the date printed on the finding. Without this
    # explicit as_of, a backdated record could silently be evaluated against a
    # different day than the record claims.
    lines = tuple(sorted(
        (replace(line, scope=tuple(sorted(line.scope)), exemptions=tuple(sorted(line.exemptions, key=lambda ex: ex.id)))
         for line in lines), key=lambda line: line.id,
    ))
    assessment = evaluate_action(action, lines, as_of=on)
    finding = _render_finding(assessment)
    hints = _undeclared_scope_hints(action, lines)
    if hints:
        finding = "\n".join([finding, *hints])
    return ReviewFinding(
        engagement=action.description,
        classification=assessment.classification,
        implicated_ids=tuple(rl.id for rl in assessment.implicated),
        finding=finding,
        reviewed_on=on,
        authorization=authorization,
        declared_scope=tuple(sorted(action.scope)),
        tier=action.tier.value,
        ambiguous=action.ambiguous,
        reason_codes=tuple(code.value for code in assessment.reason_codes),
        missing_evidence=tuple(kind.value for kind in assessment.missing_evidence),
        unresolved_evidence=tuple(kind.value for kind in assessment.unresolved_evidence),
        stale_evidence=tuple(kind.value for kind in assessment.stale_evidence),
        normalized_scope=assessment.normalized_scope,
        registry_digest=registry_hash(lines),
        evaluator_version=PROJECT_VERSION,
        evaluator_id=EVALUATOR_ID,
        intake_digest=intake_digest(canonical_intake(action)),
        decision_trace=assessment.decision_trace,
    )


def replay_finding(
    finding: ReviewFinding, snapshot: str | None, lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> tuple[str, ...]:
    """Report unavailable provenance or replay disagreement; local replay does not verify facts."""

    issues = []
    if not finding.registry_digest:
        issues.append("unbound report has unbound provenance")
    if snapshot is None:
        issues.append("intake snapshot unavailable")
    elif intake_digest(snapshot) != finding.intake_digest:
        issues.append("intake digest disagreement")
    if registry_hash(lines) != finding.registry_digest:
        issues.append("registry digest disagreement")
    if (finding.evaluator_version, finding.evaluator_id) != (PROJECT_VERSION, EVALUATOR_ID):
        issues.append("evaluator identity unavailable in this runtime")
    if issues:
        return tuple(issues)
    candidate = action_from_snapshot(snapshot)
    replayed = review_engagement(candidate, finding.reviewed_on, lines, finding.authorization)
    return () if replayed == finding else ("replayed finding disagreement",)


def _stem(word: str) -> str:
    """Strip a light suffix for advisory description hints only."""

    for suffix in ("ing", "ed", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _description_stems(description: str) -> set[str]:
    cleaned = "".join(c.lower() if c.isalnum() else " " for c in description)
    return {_stem(tok) for tok in cleaned.split()}


def _keyword_mentioned(keyword: str, desc_stems: set[str]) -> bool:
    return all(len(stem := _stem(part)) >= 3 and stem in desc_stems for part in keyword.split("_"))


def _undeclared_scope_hints(action: ProposedAction, lines: tuple[RedLine, ...]) -> list[str]:
    """Surface description/scope disagreement without letting text decide policy."""

    desc_stems = _description_stems(action.description)
    hints: list[str] = []
    declared = normalize_scope(action.scope)
    for line in lines:
        for keyword in line.scope:
            canonical_keyword = normalize_token(keyword)
            if canonical_keyword in declared:
                continue
            if _keyword_mentioned(canonical_keyword, desc_stems):
                hints.append(
                    f"undeclared-scope hint: description mentions '{keyword}' "
                    f"({line.id}) but scope does not declare it"
                )
    return hints


def _render_finding(assessment: ActionAssessment) -> str:
    verdict = {
        Classification.COMPLIANT: "COMPLIANT — may proceed.",
        Classification.OUTSIDE_SCOPE: "OUTSIDE SCOPE — reviewed, but no red line is implicated.",
        Classification.INSUFFICIENT_INFORMATION: "INSUFFICIENT INFORMATION — may not proceed until evidence is resolved.",
        Classification.REQUIRES_MODIFICATION: "REQUIRES MODIFICATION — may not proceed until corrected.",
        Classification.NON_COMPLIANT: "NON-COMPLIANT — may not proceed.",
    }[assessment.classification]
    lines = [f"Engagement: {assessment.action.description}", verdict]
    if assessment.reason_codes:
        lines.append("Reason codes: " + ", ".join(code.value for code in assessment.reason_codes))
    lines.extend(f"  - {reason}" for reason in assessment.reasons)
    return "\n".join(lines)
