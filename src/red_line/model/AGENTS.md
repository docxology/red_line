# model — Model editing guidance

This folder defines the core data model: enums, scope normalization, typed exemptions, evidence records, action context, and assessment/result dataclasses.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `EvidenceRecord` | <code>class&nbsp;EvidenceRecord:</code> | A reviewable pointer supporting one intake dimension. | [action.py](action.py) |
| `ActionContext` | <code>class&nbsp;ActionContext:</code> | Required context for an evidence-gated action review. | [action.py](action.py) |
| `ProposedAction` | <code>class&nbsp;ProposedAction:</code> | A candidate engagement to evaluate against the red lines. | [action.py](action.py) |
| `ActionAssessment` | <code>class&nbsp;ActionAssessment:</code> | Result of :func:`evaluate_action` (Turner Review-Body finding analog). | [action.py](action.py) |
| `DeploymentTier` | <code>class&nbsp;DeploymentTier(Enum):</code> | Oversight-retention grade for a work product (Turner Tier 1/2/3 analog). | [enums.py](enums.py) |
| `Severity` | <code>class&nbsp;Severity(Enum):</code> | Grades a red line by how the author treats a breach. | [enums.py](enums.py) |
| `Classification` | <code>class&nbsp;Classification(Enum):</code> | Outcome of evaluating a proposed engagement. | [enums.py](enums.py) |
| `EvidenceStatus` | <code>class&nbsp;EvidenceStatus(Enum):</code> | Epistemic status of an intake record. | [enums.py](enums.py) |
| `EvidenceKind` | <code>class&nbsp;EvidenceKind(Enum):</code> | Required intake dimensions for a strict action review. | [enums.py](enums.py) |
| `ExemptionMatchMode` | <code>class&nbsp;ExemptionMatchMode(Enum):</code> | How a typed exemption's trigger scope is evaluated. | [enums.py](enums.py) |
| `AssessmentReasonCode` | <code>class&nbsp;AssessmentReasonCode(Enum):</code> | Stable machine-readable explanations for an action assessment. | [enums.py](enums.py) |
| `normalize_token` | <code>def&nbsp;normalize_token(token:&nbsp;str)&nbsp;-&gt;&nbsp;str:</code> | Canonicalize one declared scope token without heuristic stemming. | [red_line.py](red_line.py) |
| `normalize_scope` | <code>def&nbsp;normalize_scope(scope:&nbsp;frozenset[str]&nbsp;|&nbsp;set[str]&nbsp;|&nbsp;tuple[str,&nbsp;...])&nbsp;-&gt;&nbsp;frozenset[str]:</code> | Return stable canonical scope tokens. | [red_line.py](red_line.py) |
| `Exemption` | <code>class&nbsp;Exemption:</code> | A named, evidence-bearing narrowing of one red line. | [red_line.py](red_line.py) |
| `RedLine` | <code>class&nbsp;RedLine:</code> | One boundary the author will not cross. | [red_line.py](red_line.py) |

## Import direction

Keep imports inside `model/` acyclic at runtime. `red_line.py` may only refer to `ActionContext` through `TYPE_CHECKING`; do not introduce runtime imports from `model/` into higher layers.

## Invariants

- Normalization stays explicit: aliases are reviewed in `SCOPE_ALIASES`, with no heuristic semantic widening.
- `ProposedAction` always requires a real `ActionContext`; description text never substitutes for structured intake.
- `EvidenceRecord.reference` stays free of raw secrets and raw personal identifiers.

## Tests

Tests for this folder live in:
- [../../../tests/model/test_action.py](../../../tests/model/test_action.py)
- [../../../tests/model/test_enums.py](../../../tests/model/test_enums.py)
- [../../../tests/model/test_red_line.py](../../../tests/model/test_red_line.py)
- [../../../tests/hardening/test_constructor_rejections.py](../../../tests/hardening/test_constructor_rejections.py)
- [../../../tests/hardening/test_scope.py](../../../tests/hardening/test_scope.py)
