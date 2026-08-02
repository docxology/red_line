"""Evidence-gated red-line evaluation logic."""

from __future__ import annotations

from datetime import date

from ..model import (
    ActionAssessment,
    AssessmentReasonCode,
    Classification,
    EvidenceKind,
    ProposedAction,
    RedLine,
    normalize_scope,
)
from ..model.red_line import UNKNOWN_SCOPE_MARKERS
from ..registry import PERSONAL_RED_LINES


def _safe_normalize_scope(
    scope: frozenset[str] | set[str] | tuple[str, ...],
) -> tuple[frozenset[str], tuple[str, ...]]:
    """Normalize hostile input without allowing a malformed token to pass."""

    try:
        return normalize_scope(scope), ()
    except (TypeError, ValueError):
        return frozenset(), ("scope contains a non-canonical or non-ASCII token",)


def _append_code(codes: list[AssessmentReasonCode], code: AssessmentReasonCode) -> None:
    """Keep the structured explanation deterministic and duplicate-free."""

    if code not in codes:
        codes.append(code)


def _intake_issues(
    action: ProposedAction,
    as_of: date,
    normalized_scope: frozenset[str],
    normalization_issues: tuple[str, ...],
) -> tuple[tuple[EvidenceKind, ...], tuple[EvidenceKind, ...], tuple[EvidenceKind, ...], tuple[str, ...]]:
    """Collect blocking intake defects before policy matching begins."""

    missing = action.context.missing_fields(as_of)
    unresolved = action.context.unresolved_evidence(as_of)
    stale = action.context.stale_evidence(as_of)
    unknown_scope = tuple(sorted(normalized_scope & UNKNOWN_SCOPE_MARKERS))
    issues = list(normalization_issues) + list(action.context.unknowns)
    issues.extend(f"unknown scope marker: {token}" for token in unknown_scope)
    if not normalized_scope:
        issues.append("scope declaration is empty")
    if action.ambiguous:
        issues.append("scope or context is explicitly ambiguous")
    return missing, unresolved, stale, tuple(issues)


def evaluate_action(
    action: ProposedAction,
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
    as_of: str | date | None = None,
) -> ActionAssessment:
    """Classify an action only after its required context is evidenced.

    Evaluation is deliberately staged.  A missing or unverified intake cannot
    reach policy matching, and a matching exemption is valid only when its
    typed evidence requirements are verified.  This prevents a free-text
    description or a carve-out keyword from manufacturing a compliant result.
    """

    review_date = (
        date.today() if as_of is None else date.fromisoformat(as_of) if isinstance(as_of, str) else as_of
    )
    normalized_scope, normalization_issues = _safe_normalize_scope(action.scope)
    missing, unresolved, stale, intake_issues = _intake_issues(
        action, review_date, normalized_scope, normalization_issues
    )
    reason_codes: list[AssessmentReasonCode] = []
    if normalization_issues:
        _append_code(reason_codes, AssessmentReasonCode.INVALID_SCOPE)
    if missing:
        _append_code(reason_codes, AssessmentReasonCode.MISSING_EVIDENCE)
    if unresolved:
        _append_code(reason_codes, AssessmentReasonCode.UNRESOLVED_EVIDENCE)
    if stale:
        _append_code(reason_codes, AssessmentReasonCode.STALE_EVIDENCE)
    if action.context.unknowns:
        _append_code(reason_codes, AssessmentReasonCode.UNDECLARED_UNKNOWN)
    unknown_scope = normalized_scope & UNKNOWN_SCOPE_MARKERS
    if unknown_scope:
        _append_code(reason_codes, AssessmentReasonCode.UNKNOWN_SCOPE)
    if not normalized_scope:
        _append_code(reason_codes, AssessmentReasonCode.EMPTY_SCOPE)
    if action.ambiguous:
        _append_code(reason_codes, AssessmentReasonCode.AMBIGUOUS_INTAKE)
    if missing or unresolved or stale or intake_issues:
        _append_code(reason_codes, AssessmentReasonCode.INTAKE_BLOCKED)
        reasons = [
            "intake is incomplete; no compliant result is available until the blocking information is resolved"
        ]
        if missing:
            reasons.append(
                "missing or unsupported required evidence: " + ", ".join(kind.value for kind in missing)
            )
        if unresolved:
            reasons.append(
                "unverified or contradicted evidence: " + ", ".join(kind.value for kind in unresolved)
            )
        if stale:
            reasons.append(
                "stale or future-dated evidence requires refresh: " + ", ".join(kind.value for kind in stale)
            )
        reasons.extend(intake_issues)
        return ActionAssessment(
            action=action,
            classification=Classification.INSUFFICIENT_INFORMATION,
            implicated=(),
            reasons=tuple(reasons),
            missing_evidence=missing,
            unresolved_evidence=unresolved,
            stale_evidence=stale,
            normalized_scope=tuple(sorted(normalized_scope)),
            reason_codes=tuple(reason_codes),
        )

    implicated: list[RedLine] = []
    reasons: list[str] = []
    hard_block = False
    needs_modification = False
    effective_scope = normalized_scope | {action.tier.value}

    for line in lines:
        if not line.covers(effective_scope):
            continue
        implicated.append(line)
        coverage_hits = set(normalize_scope(line.scope)) & set(effective_scope)
        below_floor = action.tier.oversight_rank < line.max_tier.oversight_rank
        tier_reason = (
            f"{line.id}: deployment tier '{action.tier.value}' retains less oversight "
            f"than the line's floor '{line.max_tier.value}'"
        )
        satisfied = line.satisfied_exemptions(effective_scope, action.context, review_date)
        if satisfied:
            if len(coverage_hits) >= 2:
                needs_modification = True
                _append_code(reason_codes, AssessmentReasonCode.MULTIPLE_PROHIBITED_DIMENSIONS)
                reasons.append(
                    f"{line.id}: exemption matched, but multiple prohibited dimensions "
                    f"{sorted(coverage_hits)} are declared — resolved toward coverage"
                )
            else:
                _append_code(reason_codes, AssessmentReasonCode.VERIFIED_EXEMPTION)
                reasons.append(f"{line.id}: implicated and narrowed by verified exemption {satisfied[0].id}")
            if below_floor:
                needs_modification = True
                _append_code(reason_codes, AssessmentReasonCode.BELOW_TIER_FLOOR)
                reasons.append(tier_reason)
            continue

        hard_block = True
        _append_code(reason_codes, AssessmentReasonCode.UNEXEMPTED_LINE)
        reasons.append(f"{line.id}: implicated, not exempted — {line.standard}")
        if below_floor:
            reasons.append(tier_reason)

    if hard_block:
        classification = Classification.NON_COMPLIANT
    elif needs_modification:
        classification = Classification.REQUIRES_MODIFICATION
    elif implicated:
        classification = Classification.COMPLIANT
        _append_code(reason_codes, AssessmentReasonCode.ALL_LINES_NARROWED)
        reasons.append("all implicated lines are satisfied by verified evidence and tier")
    else:
        classification = Classification.OUTSIDE_SCOPE
        _append_code(reason_codes, AssessmentReasonCode.OUTSIDE_SCOPE)
        reasons.append("complete, evidenced intake; no red line implicated")

    return ActionAssessment(
        action=action,
        classification=classification,
        implicated=tuple(implicated),
        reasons=tuple(reasons),
        stale_evidence=stale,
        normalized_scope=tuple(sorted(normalized_scope)),
        reason_codes=tuple(reason_codes),
    )
