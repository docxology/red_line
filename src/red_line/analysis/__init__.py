"""Read-only analytics over the red-line registry and evaluator.

Pure-compute summaries (zero I/O, no infrastructure imports, deterministic
output ordering) that describe what the existing structures already contain.
Nothing in this package changes registry content, evaluator semantics, enum
vocabularies, or the canonical canary hash — it only derives inspectable
views over them. None of these functions is a safety score, an accreditation,
or a permission mechanism.
"""

from __future__ import annotations

from .evidence_sensitivity import (
    BASELINE_SCOPE,
    BASELINE_TIER,
    PERTURBATIONS,
    EvidenceSensitivityReport,
    SensitivityCell,
    run_evidence_sensitivity,
)
from .monotonicity import (
    STRICTNESS_ORDER,
    TIERS_BY_DESCENDING_OVERSIGHT,
    KeywordStrictnessRow,
    MonotonicityReport,
    run_monotonicity_sweep,
    strictness_is_monotone,
)
from .outcome_coverage import (
    BATTERY_AS_OF,
    CaseResult,
    CoverageCase,
    OutcomeCoverageReport,
    canonical_battery,
    run_outcome_coverage,
)
from .registry_metrics import (
    ExemptionEvidenceRow,
    LineSummary,
    evidence_kind_demand,
    exemption_evidence_matrix,
    line_summaries,
    scope_token_frequency,
    scope_token_membership,
    severity_distribution,
    tier_floor_distribution,
    unevidenced_exemptions,
)
from .trigger_semantics import (
    PROBE_TIER,
    TriggerProbe,
    TriggerRow,
    TriggerSemanticsReport,
    run_trigger_semantics,
)

__all__ = [
    "BASELINE_SCOPE",
    "BASELINE_TIER",
    "BATTERY_AS_OF",
    "CaseResult",
    "CoverageCase",
    "EvidenceSensitivityReport",
    "ExemptionEvidenceRow",
    "KeywordStrictnessRow",
    "LineSummary",
    "MonotonicityReport",
    "OutcomeCoverageReport",
    "PERTURBATIONS",
    "PROBE_TIER",
    "STRICTNESS_ORDER",
    "SensitivityCell",
    "TIERS_BY_DESCENDING_OVERSIGHT",
    "TriggerProbe",
    "TriggerRow",
    "TriggerSemanticsReport",
    "canonical_battery",
    "evidence_kind_demand",
    "exemption_evidence_matrix",
    "line_summaries",
    "run_evidence_sensitivity",
    "run_monotonicity_sweep",
    "run_outcome_coverage",
    "run_trigger_semantics",
    "scope_token_frequency",
    "scope_token_membership",
    "severity_distribution",
    "strictness_is_monotone",
    "tier_floor_distribution",
    "unevidenced_exemptions",
]
