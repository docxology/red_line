# analysis — Analysis editing guidance

This folder provides read-only analytics over the live registry and evaluator. It derives reports and counts from real package APIs without mutating registry content, evaluator semantics, or enum vocabularies.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `strictness_is_monotone` | <code>def&nbsp;strictness_is_monotone(verdicts:&nbsp;tuple[Classification,&nbsp;...])&nbsp;-&gt;&nbsp;bool:</code> | True when strictness never decreases along a descending-oversight row. | [monotonicity.py](monotonicity.py) |
| `KeywordStrictnessRow` | <code>class&nbsp;KeywordStrictnessRow:</code> | The evaluator's verdicts for one scope keyword across all tiers. | [monotonicity.py](monotonicity.py) |
| `MonotonicityReport` | <code>class&nbsp;MonotonicityReport:</code> | Aggregate strictness-lattice report for one sweep. | [monotonicity.py](monotonicity.py) |
| `run_monotonicity_sweep` | <code>def&nbsp;run_monotonicity_sweep(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;as_of:&nbsp;str&nbsp;=&nbsp;BATTERY_AS_OF,</code><br><code>)&nbsp;-&gt;&nbsp;MonotonicityReport:</code> | Sweep every line's every scope keyword through all deployment tiers. | [monotonicity.py](monotonicity.py) |
| `CoverageCase` | <code>class&nbsp;CoverageCase:</code> | One named battery fixture with the outcome it is designed to exercise. | [outcome_coverage.py](outcome_coverage.py) |
| `canonical_battery` | <code>def&nbsp;canonical_battery()&nbsp;-&gt;&nbsp;tuple[CoverageCase,&nbsp;...]:</code> | The five-case deterministic battery, one case per classification. | [outcome_coverage.py](outcome_coverage.py) |
| `CaseResult` | <code>class&nbsp;CaseResult:</code> | The evaluator's actual verdict for one battery case. | [outcome_coverage.py](outcome_coverage.py) |
| `OutcomeCoverageReport` | <code>class&nbsp;OutcomeCoverageReport:</code> | Aggregate reachability report for one battery run. | [outcome_coverage.py](outcome_coverage.py) |
| `run_outcome_coverage` | <code>def&nbsp;run_outcome_coverage(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;as_of:&nbsp;str&nbsp;=&nbsp;BATTERY_AS_OF,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;battery:&nbsp;tuple[CoverageCase,&nbsp;...]&nbsp;|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>)&nbsp;-&gt;&nbsp;OutcomeCoverageReport:</code> | Run the battery through the real evaluator and report reachability. | [outcome_coverage.py](outcome_coverage.py) |
| `ExemptionEvidenceRow` | <code>class&nbsp;ExemptionEvidenceRow:</code> | One exemption's typed evidence requirements, as a matrix row. | [registry_metrics.py](registry_metrics.py) |
| `exemption_evidence_matrix` | <code>def&nbsp;exemption_evidence_matrix(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;tuple[ExemptionEvidenceRow,&nbsp;...]:</code> | Derive the exemption × evidence-kind coverage matrix. | [registry_metrics.py](registry_metrics.py) |
| `evidence_kind_demand` | <code>def&nbsp;evidence_kind_demand(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;dict[EvidenceKind,&nbsp;int]:</code> | Count, per evidence kind, how many exemptions require it. | [registry_metrics.py](registry_metrics.py) |
| `unevidenced_exemptions` | <code>def&nbsp;unevidenced_exemptions(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;tuple[ExemptionEvidenceRow,&nbsp;...]:</code> | Return matrix rows whose exemption requires NO evidence kind at all. | [registry_metrics.py](registry_metrics.py) |
| `LineSummary` | <code>class&nbsp;LineSummary:</code> | Structural composition of a single red line (no prose judgment). | [registry_metrics.py](registry_metrics.py) |
| `line_summaries` | <code>def&nbsp;line_summaries(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;tuple[LineSummary,&nbsp;...]:</code> | Summarize each line's structural composition, sorted by line id. | [registry_metrics.py](registry_metrics.py) |
| `severity_distribution` | <code>def&nbsp;severity_distribution(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;dict[Severity,&nbsp;int]:</code> | Count lines per severity grade; every grade appears as a key. | [registry_metrics.py](registry_metrics.py) |
| `tier_floor_distribution` | <code>def&nbsp;tier_floor_distribution(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;dict[DeploymentTier,&nbsp;int]:</code> | Count lines per tier floor (``max_tier``); every tier appears as a key. | [registry_metrics.py](registry_metrics.py) |
| `scope_token_frequency` | <code>def&nbsp;scope_token_frequency(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;dict[str,&nbsp;int]:</code> | Count, per canonical scope token, how many lines' coverage includes it. | [registry_metrics.py](registry_metrics.py) |
| `scope_token_membership` | <code>def&nbsp;scope_token_membership(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;tuple[tuple[str,&nbsp;tuple[str,&nbsp;...]],&nbsp;...]:</code> | Map every canonical scope token to the ids of the lines declaring it. | [registry_metrics.py](registry_metrics.py) |
| `run_evidence_sensitivity` | <code>def&nbsp;run_evidence_sensitivity(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;as_of:&nbsp;str&nbsp;=&nbsp;BATTERY_AS_OF,</code><br><code>)&nbsp;-&gt;&nbsp;EvidenceSensitivityReport:</code> | Degrade each intake dimension in turn and report what the gate returned. | [evidence_sensitivity.py](evidence_sensitivity.py) |
| `SensitivityCell` | <code>class&nbsp;SensitivityCell:</code> | One executed perturbation of one intake dimension. | [evidence_sensitivity.py](evidence_sensitivity.py) |
| `EvidenceSensitivityReport` | <code>class&nbsp;EvidenceSensitivityReport:</code> | Aggregate report for one single-dimension perturbation sweep. | [evidence_sensitivity.py](evidence_sensitivity.py) |
| `run_trigger_semantics` | <code>def&nbsp;run_trigger_semantics(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;as_of:&nbsp;str&nbsp;=&nbsp;BATTERY_AS_OF,</code><br><code>)&nbsp;-&gt;&nbsp;TriggerSemanticsReport:</code> | Probe every exemption with one trigger token at a time, then with all. | [trigger_semantics.py](trigger_semantics.py) |
| `TriggerProbe` | <code>class&nbsp;TriggerProbe:</code> | One executed probe of one token subset against one exemption. | [trigger_semantics.py](trigger_semantics.py) |
| `TriggerRow` | <code>class&nbsp;TriggerRow:</code> | Structural and executed trigger behaviour for one typed exemption. | [trigger_semantics.py](trigger_semantics.py) |
| `TriggerSemanticsReport` | <code>class&nbsp;TriggerSemanticsReport:</code> | Aggregate report for one trigger-semantics sweep. | [trigger_semantics.py](trigger_semantics.py) |

## Import direction

May import `evaluation`, `model`, `registry`, and sibling analysis modules. Do not import `figures/`, `contracts/`, or any I/O layer here.

## Invariants

- Keep the modules zero-I/O and deterministic in ordering.
- Fail closed on malformed inputs or dates instead of silently coercing them.
- Do not turn these reports into permission, scoring, or policy-changing code.

## Tests

Tests for this folder live in:
- [../../../tests/analysis/test_outcome_coverage.py](../../../tests/analysis/test_outcome_coverage.py)
- [../../../tests/analysis/test_monotonicity_sweep.py](../../../tests/analysis/test_monotonicity_sweep.py)
- [../../../tests/analysis/test_registry_metrics.py](../../../tests/analysis/test_registry_metrics.py)
- [../../../tests/analysis/test_decision_surface.py](../../../tests/analysis/test_decision_surface.py)
- [../../../tests/test_figures.py](../../../tests/test_figures.py)
