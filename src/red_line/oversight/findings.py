"""Self-review records with non-bypassable escalation metadata."""

from __future__ import annotations

from dataclasses import dataclass
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

    def __post_init__(self) -> None:
        if not isinstance(self.engagement, str) or not isinstance(self.finding, str):
            raise TypeError("review finding text fields must be strings")
        if not isinstance(self.reviewed_on, str):
            raise TypeError("reviewed_on must be an ISO date string")
        if not self.engagement.strip() or not self.finding.strip():
            raise ValueError("review findings require engagement and finding text")
        if not isinstance(self.classification, Classification):
            raise TypeError("classification must use the declared enum")
        if not isinstance(self.implicated_ids, (tuple, list)):
            raise TypeError("implicated_ids must be a tuple or list")
        if any(
            not isinstance(identifier, str) or not identifier.strip() for identifier in self.implicated_ids
        ):
            raise ValueError("implicated_ids must contain non-empty strings")
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
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must not contain duplicates")
        try:
            date.fromisoformat(self.reviewed_on)
        except (TypeError, ValueError) as exc:
            raise ValueError("reviewed_on must be an ISO date") from exc
        object.__setattr__(self, "implicated_ids", tuple(self.implicated_ids))
        object.__setattr__(
            self, "declared_scope", tuple(sorted(normalize_scope(frozenset(self.declared_scope))))
        )
        object.__setattr__(self, "reason_codes", tuple(self.reason_codes))
        object.__setattr__(self, "missing_evidence", tuple(self.missing_evidence))
        object.__setattr__(self, "unresolved_evidence", tuple(self.unresolved_evidence))
        object.__setattr__(self, "stale_evidence", tuple(self.stale_evidence))
        object.__setattr__(self, "normalized_scope", tuple(self.normalized_scope))

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
    try:
        date.fromisoformat(on)
    except (TypeError, ValueError) as exc:
        raise ValueError("reviewed_on must be an ISO date") from exc
    # Bind evidence freshness to the date printed on the finding. Without this
    # explicit as_of, a backdated record could silently be evaluated against a
    # different day than the record claims.
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
    )


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
