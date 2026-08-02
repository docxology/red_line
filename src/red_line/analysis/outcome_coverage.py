"""Outcome-space coverage harness for the real evaluator.

The manuscript claims the evaluator can reach five distinct classifications.
This module turns that claim from an assertion into an exercised property: a
curated, deterministic battery of :class:`~red_line.model.action.ProposedAction`
fixtures is run through the real :func:`~red_line.evaluation.evaluator.evaluate_action`
(no stand-ins, no patched internals), and the report records which
:class:`~red_line.model.enums.Classification` each case actually reached.

The harness analyses the existing public API; it does not alter evaluator
semantics, the registry, or any enum vocabulary. Reachability of an outcome is
a structural property of the evaluator's control flow — it is NOT evidence
that any real engagement was safe, lawful, or correctly described, and a
``complete`` report is not a safety score.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

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
from ..registry import PERSONAL_RED_LINES

#: Fixed review date for the canonical battery. Matching the registry's
#: ``stated_on`` date keeps every fixture's evidence fresh (age zero days)
#: and makes the whole harness deterministic — no ``date.today()`` leakage.
BATTERY_AS_OF = "2026-07-15"

#: Classification order used for reports: enum definition order.
_CLASSIFICATION_ORDER: tuple[Classification, ...] = tuple(Classification)


def _verified_context(recorded_on: str = BATTERY_AS_OF) -> ActionContext:
    """A complete intake with a VERIFIED record for all nine dimensions.

    The references are explicit fixture URIs — reviewable pointers in shape,
    fixtures in substance. They exercise the evaluator's evidence gate; they
    do not assert that any real-world evidence exists.
    """

    return ActionContext(
        purpose="coverage-harness fixture purpose",
        end_use="coverage-harness fixture end use",
        affected_parties="none beyond the author",
        data_provenance="synthetic fixture data",
        legal_basis="not_applicable",
        human_control="author review before any use",
        deployment="local hosted harness run",
        downstream_transfer="none",
        capability_scope="documented harness capability",
        evidence=tuple(
            EvidenceRecord(
                kind=kind,
                reference=f"fixture://outcome-coverage/{kind.value}",
                summary=f"Deterministic harness fixture for {kind.value}",
                status=EvidenceStatus.VERIFIED,
                recorded_on=recorded_on,
            )
            for kind in EvidenceKind
        ),
    )


def _unevidenced_context() -> ActionContext:
    """A fully described intake carrying no evidence records at all.

    Every field has prose, so the only defect is the evidence gate — the
    cleanest way to exercise the ``INSUFFICIENT_INFORMATION`` short circuit.
    """

    return ActionContext(
        purpose="described but unevidenced purpose",
        end_use="described but unevidenced end use",
        affected_parties="described but unevidenced parties",
        data_provenance="described but unevidenced provenance",
        legal_basis="described but unevidenced basis",
        human_control="described but unevidenced control",
        deployment="described but unevidenced deployment",
        downstream_transfer="described but unevidenced transfer",
        capability_scope="described but unevidenced capability",
        evidence=(),
    )


@dataclass(frozen=True)
class CoverageCase:
    """One named battery fixture with the outcome it is designed to exercise.

    ``intent`` is the classification the case targets; the harness still runs
    the real evaluator and records what was actually reached, so a drifted
    evaluator surfaces as a mismatch instead of being papered over.
    """

    name: str
    intent: Classification
    action: ProposedAction

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("coverage case name is required")
        if not isinstance(self.intent, Classification):
            raise TypeError("coverage case intent must be a Classification")
        if not isinstance(self.action, ProposedAction):
            raise TypeError("coverage case action must be a ProposedAction")


def canonical_battery() -> tuple[CoverageCase, ...]:
    """The five-case deterministic battery, one case per classification.

    Each case is built against the live registry vocabulary:

    * ``insufficient-information`` — complete prose, zero evidence records;
    * ``outside-scope`` — evidenced intake whose scope matches no line;
    * ``compliant`` — one implicated line narrowed by a verified exemption;
    * ``requires-modification`` — a verified exemption undercut by two
      declared prohibited dimensions on the same line;
    * ``non-compliant`` — an implicated line with no matching exemption.
    """

    return (
        CoverageCase(
            name="insufficient-information",
            intent=Classification.INSUFFICIENT_INFORMATION,
            action=ProposedAction(
                description="Described engagement with no reviewable evidence",
                scope=frozenset({"publication"}),
                context=_unevidenced_context(),
                tier=DeploymentTier.HOSTED,
            ),
        ),
        CoverageCase(
            name="outside-scope",
            intent=Classification.OUTSIDE_SCOPE,
            action=ProposedAction(
                description="Static documentation tooling outside every declared boundary",
                scope=frozenset({"static_documentation"}),
                context=_verified_context(),
                tier=DeploymentTier.HOSTED,
            ),
        ),
        CoverageCase(
            name="compliant",
            intent=Classification.COMPLIANT,
            action=ProposedAction(
                description="Media-literacy education work inside the cogsec boundary",
                scope=frozenset({"cogsec", "education"}),
                context=_verified_context(),
                tier=DeploymentTier.HOSTED,
            ),
        ),
        CoverageCase(
            name="requires-modification",
            intent=Classification.REQUIRES_MODIFICATION,
            action=ProposedAction(
                description="Aggregate research declaring two prohibited profiling dimensions",
                scope=frozenset({"surveillance", "profiling", "aggregate_research"}),
                context=_verified_context(),
                tier=DeploymentTier.HOSTED,
            ),
        ),
        CoverageCase(
            name="non-compliant",
            intent=Classification.NON_COMPLIANT,
            action=ProposedAction(
                description="Targeting component with no adjacent-use narrowing",
                scope=frozenset({"targeting"}),
                context=_verified_context(),
                tier=DeploymentTier.HOSTED,
            ),
        ),
    )


@dataclass(frozen=True)
class CaseResult:
    """The evaluator's actual verdict for one battery case."""

    name: str
    intent: Classification
    reached: Classification
    matched: bool
    reason_codes: tuple[AssessmentReasonCode, ...]


@dataclass(frozen=True)
class OutcomeCoverageReport:
    """Aggregate reachability report for one battery run.

    Attributes:
        as_of: ISO review date the battery was evaluated at.
        results: Per-case results in battery order.
        reached: Classifications actually reached, in enum order.
        unreached: Classifications no case reached, in enum order.
        complete: True when every classification was reached.
        all_matched: True when every case reached its intended outcome.
    """

    as_of: str
    results: tuple[CaseResult, ...]
    reached: tuple[Classification, ...]
    unreached: tuple[Classification, ...]
    complete: bool
    all_matched: bool


def run_outcome_coverage(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
    as_of: str = BATTERY_AS_OF,
    battery: tuple[CoverageCase, ...] | None = None,
) -> OutcomeCoverageReport:
    """Run the battery through the real evaluator and report reachability.

    ``lines`` defaults to the live registry; passing a reduced registry is the
    harness's own negative control — outcomes that depend on implication
    become unreachable and the report honestly says so (``complete`` False).
    ``as_of`` must be an ISO date string; it defaults to the deterministic
    battery date rather than today so repeated runs are byte-identical.
    """

    if not isinstance(as_of, str):
        raise TypeError("as_of must be an ISO date string")
    date.fromisoformat(as_of)  # fail closed on malformed review dates
    cases = canonical_battery() if battery is None else battery
    for case in cases:
        if not isinstance(case, CoverageCase):
            raise TypeError("battery must contain CoverageCase values")

    results: list[CaseResult] = []
    for case in cases:
        assessment = evaluate_action(case.action, lines, as_of=as_of)
        results.append(
            CaseResult(
                name=case.name,
                intent=case.intent,
                reached=assessment.classification,
                matched=assessment.classification is case.intent,
                reason_codes=assessment.reason_codes,
            )
        )

    reached_set = {result.reached for result in results}
    reached = tuple(c for c in _CLASSIFICATION_ORDER if c in reached_set)
    unreached = tuple(c for c in _CLASSIFICATION_ORDER if c not in reached_set)
    return OutcomeCoverageReport(
        as_of=as_of,
        results=tuple(results),
        reached=reached,
        unreached=unreached,
        complete=not unreached,
        all_matched=all(result.matched for result in results),
    )
