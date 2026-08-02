# Decision protocol

This is the concise operator sequence for using the Red Line instrument. It
does not replace the full [evaluator semantics](evaluator-semantics.md),
[amendment runbook](amendment-runbook.md), or [third-party canary runbook](VERIFY.md).
The publication claim vocabulary is maintained in
[`../data/claim_register.json`](../data/claim_register.json) and checked by
`scripts/validate_claim_register.py`.

## Epistemic states

The protocol separates a declared value from evidence about that value. These
states are intentionally not a truth oracle:

| State | Meaning in this instrument | Can narrow a line? |
|---|---|---:|
| `MISSING` | no usable value or no supporting record | no |
| `SELF_ASSERTED` | the requester supplied an assertion without an independent reviewable basis | no |
| `UNVERIFIED` | a pointer exists, but the reviewer has not verified it | no |
| `CONTRADICTED` | the available record conflicts with the declared value | no |
| `STALE` | a record is outside the configured review window or future-dated | no |
| `VERIFIED` | a reviewable record was checked for this local decision and is current | only within the typed exemption and declared scope |

`MISSING` and `STALE` are derived intake conditions; the code's
`EvidenceStatus` enum records the status supplied for a record, while the
evaluator derives freshness from `recorded_on` and the review date. `VERIFIED`
means “verified for this review record,” not “independently true,” “lawful,” or
“safe.”

## Intake

1. Read [`manuscript/09_red_lines.md`](../manuscript/09_red_lines.md) and stop
   if the work is plainly inside a refusal.
2. Create a `ProposedAction` with a declared scope and deployment tier.
3. Complete all nine `ActionContext` values:
   `purpose`, `end_use`, `affected_parties`, `data_provenance`, `legal_basis`,
   `human_control`, `deployment`, `downstream_transfer`, and `capability_scope`.
4. Attach one or more reviewable `EvidenceRecord` values to every dimension.
   Use `SELF_ASSERTED`, `UNVERIFIED`, `CONTRADICTED`, or `unknowns` to preserve
   uncertainty; never fill a gap with a convenient assumption.
5. Run `evaluate_action(action, as_of=...)` with a stated review date.

The operational invariant is: no evidence gate, exemption, or prose shortcut
may move an action from an information stop to a narrowing result without a
current `VERIFIED` record for every required dimension. The evaluator is
lexical and deterministic; semantic truthfulness remains a human and external
governance question.

## Result precedence

The first applicable stop controls the result:

| Priority | Condition | Result | Next action |
|---:|---|---|---|
| 1 | Missing, ambiguous, malformed, unknown, stale, self-asserted, unverified, or contradicted intake | `INSUFFICIENT_INFORMATION` | Resolve the evidence or stop |
| 2 | An implicated line has no satisfied typed exemption | `NON_COMPLIANT` | Do not proceed |
| 3 | A verified exemption remains below the line's oversight floor or spans multiple prohibited dimensions | `REQUIRES_MODIFICATION` | Narrow or redesign the action |
| 4 | Every implicated line is narrowed by verified evidence and tier | `COMPLIANT` | Proceed only within the documented scope and limits |
| 5 | Complete intake but no current line is implicated | `OUTSIDE_SCOPE` | Do not read this as a safety result; assess other obligations |

`OUTSIDE_SCOPE` and `COMPLIANT` are deliberately different. The former says
the current registry did not match. The latter says a current line was matched
and locally narrowed. Neither says that the world is safe.

The same distinction applies to release work. A passing test supports an
implementation claim about an exercised branch. A populated source ledger
supports a source-bounded research record. A validated render supports a
particular generated artifact. None of these is a substitute for an independent
witness, domain authority, or real-world outcome.

## Record and escalate

Call `review_engagement` and retain the resulting frozen `ReviewFinding` with
the action's evidence references. The finding includes stable reason codes,
normalized scope, and evidence-stop dimensions in addition to display prose.
A `ReviewAuthorization` may name an escalation, authority, rationale, and date.
It cannot change a blocking classification or turn self-review into third-party
authorization.

## Maintain and publish

After a registry change, use the successor-canary workflow and update every
prose/hash pin. Before an external assurance claim, place a prior statement on
an independently held surface. Before a publication release, regenerate figures,
run the project gate, render from the sibling template checkout, validate the
outputs, and inspect the combined PDF and HTML.
