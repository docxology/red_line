# Claim register

This register is the publication-facing map from important claims to the
evidence that can support them and the stronger claim that must not be inferred.
The machine-readable counterpart is
[`data/claim_register.json`](../data/claim_register.json), checked by
[`red_line.contracts.claim_register`](../src/red_line/contracts/claim_register.py)
through its `scripts/validate_claim_register.py` CLI. The source ledger in
[`research-method.md`](research-method.md) contains the detailed literature
records, while the tests and output reports contain executable evidence.

Supporting-surface entries name the module that owns the behavior, not the CLI
that invokes it. Figure generation lives in
[`src/red_line/figures/`](../src/red_line/figures/) and the five validators live
in [`src/red_line/contracts/`](../src/red_line/contracts/); everything under
`scripts/` parses arguments and calls one package function.

| ID | Claim made by the project | Claim class | Supporting surface | Verification mode | Verification status | Stopping point |
|---|---|---|---|---|---|---|
| `CLM-001` | The author has seven current, first-person red lines | implementation | `src/red_line/registry/lines.py`, `manuscript/09_red_lines.md`, beacon-binding tests | executable | locally_bound_hash_pinned | Not a universal ethics code and not exhaustive |
| `CLM-002` | Missing or unresolved required context cannot produce COMPLIANT | implementation | `src/red_line/evaluation/evaluator.py`, evaluator tests, `docs/evaluator-semantics.md` | executable | executably_tested | A verified record is still not independently true |
| `CLM-003` | Outside-scope work is distinct from compliance | implementation | `Classification.OUTSIDE_SCOPE`, assessment tests, manuscript section on evaluation | executable | executably_tested | Outside scope means only that this registry did not match |
| `CLM-004` | Less retained oversight narrows the release envelope | implementation | `DeploymentTier`, registry floors, monotonicity tests, tier figure | executable | executably_tested_as_a_local_rule | Oversight retention is not safety, legality, or enforcement |
| `CLM-005` | A named authorization does not release a block | implementation | `ReviewAuthorization`, `ReviewFinding.blocks`, oversight tests | executable | executably_tested | The author remains the sole local enforcer |
| `CLM-006` | Registry changes can be detected against a prior | implementation | canonical hash, per-line digests, `verify_canary`, `docs/VERIFY.md` | external_witness_condition | locally_reproducible_externally_conditional | Same-repository regeneration is self-referential; no signature or non-forgeability |
| `CLM-007` | The scholarship widens the questions asked of the instrument | transfer | `docs/research-method.md`, citations, transfer matrix, scholarship-intake bridge | source_bounded | interpretive_and_source_bounded | It is not a systematic review, global representation, or source endorsement |
| `CLM-008` | The rendered artifact is bound to the source tree for a specific validation run | release | deterministic figures, template validation, PDF/HTML inspection | render_validated | requires_each_render_run_and_render_gate | This is a per-run source-to-render claim; release boundary (repository now publicly released at <https://github.com/docxology/red_line>), renderer boundary, and build-tool trust remain external residual risks |
| `CLM-009` | Structured assessment records preserve why a result blocked or passed | implementation | `ActionAssessment.reason_codes`, `ReviewFinding`, evaluator and oversight tests, `docs/evaluator-semantics.md` | executable | executably_tested | Codes preserve the local decision trace; they do not establish semantic truth or honest input |
| `CLM-010` | Every source-driven figure carries a bounded caption, alt text, and source binding | implementation | `src/red_line/figures/`, `src/red_line/contracts/visual_bindings.py`, `data/source_claims.json`, `docs/visualization-briefs.md`, rendered PDF/HTML | render_validated | executably_tested_and_render_inspected | Caption and source binding constrain interpretation; they do not make the underlying source or action true |

## Reading rule

When a sentence crosses from one row to another, the manuscript must say so.
For example, a source may support a descriptive account of surveillance history;
it cannot by itself prove that a particular intake record is lawful. A green
test may support an implementation claim about a branch of code; it cannot prove
that the action's declared purpose is honest.

## Release evidence bundle

Before publication, retain one small bundle containing:

1. the source revision and current registry hash;
2. the current canary statement plus an independently held prior copy;
3. the test and coverage output;
4. the figure registry and deterministic regeneration check;
5. the template revision and PDF/HTML validation report; and
6. an independent reader's record of unresolved source, semantic, and visual
   concerns.

The bundle is evidence of the release process, not a certification that the
framework is complete or safe.
