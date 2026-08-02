"""Single-dimension evidence perturbation sweep over the real evaluator.

The manuscript claims the intake gate is *conjunctive*: all nine intake
dimensions must carry a fresh ``VERIFIED`` record, so degrading any one of them
is enough to withdraw a policy result. This module turns that claim into an
exercised property in the same spirit as
:mod:`red_line.analysis.outcome_coverage` and
:mod:`red_line.analysis.monotonicity`.

A baseline action that the live registry classifies ``COMPLIANT`` is perturbed
one dimension at a time. Each perturbation replaces exactly one evidence record
with a degraded form — absent, self-asserted, unverified, contradicted, or
stale — and the whole action is re-run through the real
:func:`~red_line.evaluation.evaluator.evaluate_action`. Nothing else changes:
same scope, same tier, same review date, same eight other records.

Two things are recorded per cell, because they answer different questions. The
returned classification says *whether* the gate withdrew the result. The
dimensions the assessment names as blocking say *whether the gate blamed the
right field* — a gate that stops on any perturbation while naming the wrong
dimension would be uninformative in exactly the way a stop signal must not be.

Design rules, matching the rest of :mod:`red_line.analysis`:

* zero I/O; deterministic ordering (evidence-kind enum order, then the
  perturbation order declared below);
* fail-closed validation — a malformed review date or a baseline that is not
  ``COMPLIANT`` raises rather than producing a sweep nobody can interpret;
* no change to registry content, evaluator semantics, or enum vocabulary.

Sensitivity is a property of the local decision procedure. It is NOT evidence
that the recorded evidence is true, that a real intake was reviewed, or that a
dimension the gate names is the dimension that actually matters in the world.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta

from ..evaluation import evaluate_action
from ..model import (
    ActionContext,
    AssessmentReasonCode,
    Classification,
    DeploymentTier,
    EvidenceKind,
    EvidenceRecord,
    EvidenceStatus,
    ProposedAction,
    RedLine,
)
from ..model.action import DEFAULT_EVIDENCE_MAX_AGE_DAYS
from ..registry import PERSONAL_RED_LINES
from .outcome_coverage import BATTERY_AS_OF, _verified_context

#: Declared scope of the baseline action. Chosen because the live registry
#: classifies it ``COMPLIANT``: ``cogsec`` implicates ``cogsec-integrity`` and
#: ``education`` triggers that line's ``epistemic-education`` exemption. A
#: baseline that were already blocked would make every perturbation vacuous, so
#: :func:`run_evidence_sensitivity` asserts the baseline verdict rather than
#: assuming it.
BASELINE_SCOPE: frozenset[str] = frozenset({"cogsec", "education"})

#: Tier the baseline and every perturbation run at. Held fixed so the only
#: variable in the sweep is the evidence record.
BASELINE_TIER: DeploymentTier = DeploymentTier.HOSTED

#: The five ways one dimension's evidence is degraded, in sweep column order.
#: ``absent`` removes the record; the three status labels replace it with a
#: non-``VERIFIED`` status; ``stale`` keeps ``VERIFIED`` and moves the record
#: outside the freshness window instead.
PERTURBATIONS: tuple[str, ...] = (
    "absent",
    "self_asserted",
    "unverified",
    "contradicted",
    "stale",
)

_STATUS_BY_PERTURBATION: dict[str, EvidenceStatus] = {
    "self_asserted": EvidenceStatus.SELF_ASSERTED,
    "unverified": EvidenceStatus.UNVERIFIED,
    "contradicted": EvidenceStatus.CONTRADICTED,
}


def _degraded_context(
    context: ActionContext,
    kind: EvidenceKind,
    perturbation: str,
    as_of: date,
) -> ActionContext:
    """Return ``context`` with exactly one dimension's record degraded.

    Every other record is carried across unchanged, so a cell that blocks can
    only be blocking because of ``kind``.
    """

    if perturbation not in PERTURBATIONS:
        raise ValueError(f"unknown perturbation {perturbation!r}")
    records: list[EvidenceRecord] = []
    for record in context.evidence:
        if record.kind is not kind:
            records.append(record)
            continue
        if perturbation == "absent":
            continue
        if perturbation == "stale":
            expired = as_of - timedelta(days=DEFAULT_EVIDENCE_MAX_AGE_DAYS + 1)
            records.append(replace(record, recorded_on=expired.isoformat()))
            continue
        records.append(replace(record, status=_STATUS_BY_PERTURBATION[perturbation]))
    return replace(context, evidence=tuple(records))


@dataclass(frozen=True)
class SensitivityCell:
    """One executed perturbation of one intake dimension.

    Attributes:
        kind: The single evidence dimension that was degraded.
        perturbation: Which degradation was applied, from :data:`PERTURBATIONS`.
        reached: The classification the real evaluator returned.
        blocked: True when the verdict left the baseline ``COMPLIANT``.
        blocking_kinds: The evidence kinds the assessment named as missing,
            unresolved, or stale, sorted in enum order.
        localized: True when ``blocking_kinds`` is exactly ``(kind,)`` — the
            gate withdrew the result and blamed only the degraded dimension.
        reason_codes: The assessment's stable reason codes, in returned order.
    """

    kind: EvidenceKind
    perturbation: str
    reached: Classification
    blocked: bool
    blocking_kinds: tuple[EvidenceKind, ...]
    localized: bool
    reason_codes: tuple[AssessmentReasonCode, ...]


@dataclass(frozen=True)
class EvidenceSensitivityReport:
    """Aggregate report for one single-dimension perturbation sweep.

    Attributes:
        as_of: ISO review date every evaluation used.
        baseline: The classification of the unperturbed action.
        scope: The baseline's declared scope, sorted.
        tier: The tier every evaluation ran at.
        perturbations: Column order shared by every row.
        cells: Every executed cell, in (enum order, column order).
        evaluation_count: Real ``evaluate_action`` runs, excluding the baseline.
        blocked_count: Cells that left the baseline verdict.
        localized_count: Cells that blamed only the degraded dimension.
        conjunctive: True when every cell blocked and every block was
            localized — the property the manuscript states.
    """

    as_of: str
    baseline: Classification
    scope: tuple[str, ...]
    tier: DeploymentTier
    perturbations: tuple[str, ...]
    cells: tuple[SensitivityCell, ...]
    evaluation_count: int
    blocked_count: int
    localized_count: int
    conjunctive: bool

    def cell(self, kind: EvidenceKind, perturbation: str) -> SensitivityCell:
        """Return one cell by coordinates, raising when it was not swept."""

        for entry in self.cells:
            if entry.kind is kind and entry.perturbation == perturbation:
                return entry
        raise KeyError(f"no swept cell for {kind.value}/{perturbation}")


def run_evidence_sensitivity(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
    as_of: str = BATTERY_AS_OF,
) -> EvidenceSensitivityReport:
    """Degrade each intake dimension in turn and report what the gate returned.

    The baseline must classify ``COMPLIANT`` against ``lines``; otherwise the
    sweep would compare perturbed blocks against a block and prove nothing, so
    a non-compliant baseline raises ``ValueError`` rather than returning a
    report whose zeros mean the opposite of what they appear to mean.
    """

    if not isinstance(as_of, str):
        raise TypeError("as_of must be an ISO date string")
    review_date = date.fromisoformat(as_of)  # fail closed on malformed dates
    if not isinstance(lines, (tuple, list)):
        raise TypeError("lines must be a tuple or list of RedLine values")
    for line in lines:
        if not isinstance(line, RedLine):
            raise TypeError("lines must contain only RedLine values")

    context = _verified_context(as_of)
    baseline_action = ProposedAction(
        description="evidence-sensitivity baseline",
        scope=BASELINE_SCOPE,
        context=context,
        tier=BASELINE_TIER,
    )
    baseline = evaluate_action(baseline_action, tuple(lines), as_of=as_of).classification
    if baseline is not Classification.COMPLIANT:
        raise ValueError(
            f"evidence-sensitivity baseline must be COMPLIANT, not {baseline.value}; "
            "a blocked baseline makes every perturbation vacuous"
        )

    cells: list[SensitivityCell] = []
    for kind in EvidenceKind:
        for perturbation in PERTURBATIONS:
            action = ProposedAction(
                description=f"evidence-sensitivity probe: {kind.value} {perturbation}",
                scope=BASELINE_SCOPE,
                context=_degraded_context(context, kind, perturbation, review_date),
                tier=BASELINE_TIER,
            )
            assessment = evaluate_action(action, tuple(lines), as_of=as_of)
            named = set(assessment.missing_evidence) | set(assessment.unresolved_evidence)
            named |= set(assessment.stale_evidence)
            blocking = tuple(entry for entry in EvidenceKind if entry in named)
            cells.append(
                SensitivityCell(
                    kind=kind,
                    perturbation=perturbation,
                    reached=assessment.classification,
                    blocked=assessment.classification is not baseline,
                    blocking_kinds=blocking,
                    localized=blocking == (kind,),
                    reason_codes=assessment.reason_codes,
                )
            )

    blocked_count = sum(1 for cell in cells if cell.blocked)
    localized_count = sum(1 for cell in cells if cell.localized)
    return EvidenceSensitivityReport(
        as_of=as_of,
        baseline=baseline,
        scope=tuple(sorted(baseline_action.scope)),
        tier=BASELINE_TIER,
        perturbations=PERTURBATIONS,
        cells=tuple(cells),
        evaluation_count=len(cells),
        blocked_count=blocked_count,
        localized_count=localized_count,
        conjunctive=bool(cells) and blocked_count == len(cells) == localized_count,
    )
