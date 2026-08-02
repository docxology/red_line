# oversight — Oversight editing guidance

This folder holds the self-review layer above the evaluator: frozen findings, non-bypassable authorization metadata, and transparency-report aggregation.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `ReviewAuthorization` | <code>class&nbsp;ReviewAuthorization:</code> | A named escalation or remediation record, never a compliance bypass. | [findings.py](findings.py) |
| `ReviewFinding` | <code>class&nbsp;ReviewFinding:</code> | A durable, citable record of one evidence-gated self-review. | [findings.py](findings.py) |
| `review_engagement` | <code>def&nbsp;review_engagement(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;action:&nbsp;ProposedAction,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;reviewed_on:&nbsp;str&nbsp;|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;authorization:&nbsp;ReviewAuthorization&nbsp;|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>)&nbsp;-&gt;&nbsp;ReviewFinding:</code> | Produce a written finding; authorization never releases a blocking result. | [findings.py](findings.py) |
| `TransparencyReport` | <code>class&nbsp;TransparencyReport:</code> | Aggregate of findings (Turner annual transparency-report analog). | [transparency.py](transparency.py) |
| `transparency_report` | <code>def&nbsp;transparency_report(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;findings:&nbsp;tuple[ReviewFinding,&nbsp;...],</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;period:&nbsp;str&nbsp;|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>)&nbsp;-&gt;&nbsp;TransparencyReport:</code> | Aggregate ``findings`` into classifications, authorizations, and blocks. | [transparency.py](transparency.py) |

## Import direction

May import `evaluation`, `model`, `registry`, and sibling oversight modules. `evaluation/` must not import `oversight/` back.

## Invariants

- Authorization stays an audit record only; it never converts a blocking result into a pass.
- Review findings preserve evaluator reason codes, missing evidence, and normalized scope for downstream auditability.
- Description/scope hints remain advisory text layered on top of the evaluator, not policy inputs.

## Tests

Tests for this folder live in:
- [../../../tests/oversight/test_findings.py](../../../tests/oversight/test_findings.py)
- [../../../tests/oversight/test_transparency.py](../../../tests/oversight/test_transparency.py)
- [../../../tests/hardening/test_constructor_rejections.py](../../../tests/hardening/test_constructor_rejections.py)
