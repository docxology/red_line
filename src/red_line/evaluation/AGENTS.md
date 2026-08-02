# evaluation — Evaluation editing guidance

This folder holds the evidence-gated decision procedure. It turns a fully typed `ProposedAction` plus the live registry into one `ActionAssessment` classification.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `evaluate_action` | <code>def&nbsp;evaluate_action(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;action:&nbsp;ProposedAction,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;as_of:&nbsp;str&nbsp;|&nbsp;date&nbsp;|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>)&nbsp;-&gt;&nbsp;ActionAssessment:</code> | Classify an action only after its required context is evidenced. | [evaluator.py](evaluator.py) |

## Import direction

May import `model` and `registry` only. Do not import `oversight/`, `analysis/`, `figures/`, or `contracts/` into the evaluator.

## Invariants

- The intake gate runs before policy matching; missing, unresolved, stale, malformed, or ambiguous inputs stop at `INSUFFICIENT_INFORMATION`.
- Only typed exemptions with verified evidence may narrow an implicated line.
- Classification precedence remains fail-closed: hard block over modification, modification over compliant, compliant over outside-scope.

## Tests

Tests for this folder live in:
- [../../../tests/evaluation/test_evaluator.py](../../../tests/evaluation/test_evaluator.py)
- [../../../tests/evaluation/test_monotonicity.py](../../../tests/evaluation/test_monotonicity.py)
- [../../../tests/analysis/test_outcome_coverage.py](../../../tests/analysis/test_outcome_coverage.py)
