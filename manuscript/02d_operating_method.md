# Operating method: from first principles to a bounded release {#sec:operating-method}

The first-principles reconstruction ([Section @sec:first-principles](#sec:first-principles)) fixes the order; this section gives the procedure.

The first-principles section identifies the artifact's irreducible job: help one
practitioner decline or narrow high-risk development work before commitment,
record the local reason, and disclose what the record cannot establish. This
section turns that reconstruction into a repeatable method. It is a protocol
for producing inspectable evidence, not a claim that the protocol can discover
semantic truth or guarantee a safe outcome.

## The unit of analysis

Keep three objects separate:

| Object | Question | Permitted evidence |
|---|---|---|
| Observation | What was declared, recorded, or rendered? | a typed field, dated record, source locator, test output, or artifact hash |
| Interpretation | What question or limit is being transferred? | an explicit rationale and stopping point attached to a source or claim |
| Action decision | What may this author do within this local registry? | the evidence-gated evaluator result for a declared scope, tier, and review date |

A source can support an interpretation without authorizing an action. A test can
support an implementation claim without verifying the truth of an intake field.
A rendered page can show that a statement reached an artifact without showing
that the statement is correct in the world. This separation is the central
anti-confusion rule.

## The operating loop

1. **Deconstruct the function.** State the concrete decision or release problem
   before importing a label such as governance, security, or safety. Identify
   who can refuse, who may be affected, and what the instrument can actually
   observe.
2. **Challenge the boundary.** List hidden assumptions about authority, scope,
   evidence, freshness, semantic interpretation, and external witnessing. Mark
   each as a hard constraint, a local policy choice, or an open question.
3. **Declare the claim.** Assign a claim class (`descriptive`, `transfer`,
   `implementation`, or `release`), a verification mode, a supporting surface,
   and a stopping point. The machine-readable register in
   `data/claim_register.json` is the publication-facing contract.
4. **Reconstruct the smallest honest rule.** Represent an action with its scope,
   deployment tier, nine context dimensions, evidence records, and explicit
   unknowns. Do not let free-text purpose or an exemption token substitute for
   typed context.
5. **Evaluate fail-closed.** Normalize the scope, check missingness,
   unresolved statuses, freshness, and ambiguity before policy matching. Then
   apply typed exemptions and tier floors. The evaluator's five classifications
   (@def:classification) remain distinct and ordered, from the intake-blocking
   `INSUFFICIENT_INFORMATION` through `OUTSIDE_SCOPE`. 
6. **Freeze the record.** Preserve the classification, implicated lines,
   human-readable reasons, stable reason codes, normalized scope, evidence-stop
   dimensions, review date, and any authorization. An
   authorization may document escalation or remediation; it cannot turn a
   block into permission.
7. **Verify the publication chain.** Rebuild source-driven figures, validate
   bindings, run tests and coverage, render PDF and HTML, and inspect the
   combined artifacts. A source claim is not a release claim until its required
   surface exists and is checked.
8. **Revise or stop.** If a result, source, figure, or rendered artifact fails
   its criterion, record the defect and either amend it with a dated rationale
   or stop. Never replace an unresolved state with a favorable default.

![An evidence-gated improvement loop keeps claim, action, and artifact boundaries aligned. The eight-step schematic moves from deconstruction and challenge through claim declaration, reconstruction, fail-closed evaluation, frozen records, source-to-render verification, and dated revision. The outside panel names semantic truth, legal validity, enforcement, independent witnessing, and real-world safety as claims this local loop cannot establish. It is a reproducible method map, not a measurement of improvement or safety.](../output/figures/improvement_method_loop.png){#fig:improvement-method-loop width=95%}

## Evidence states and stop points

The protocol uses evidence as a condition for a local decision, not as a proxy
for truth. `MISSING` means no usable value or supporting record exists;
`SELF_ASSERTED` means the requester supplied an assertion without an
independent reviewable basis; `UNVERIFIED` means a pointer exists but has not
been checked; `CONTRADICTED` means the available record conflicts with the
declaration; and `STALE` means the record is outside the configured review
window or future-dated. None can narrow a line. `VERIFIED` means only that a
reviewable record was checked for this decision and remains current; it can
narrow a line only through its typed exemption and declared scope.

This vocabulary prevents an important category error. A verified legal-basis
record is evidence that a reviewer checked the supplied record; it is not a
legal opinion generated by Red Line. A verified human-control record is not
proof that people will exercise that control under pressure. The evaluator
therefore refuses to manufacture `COMPLIANT` from an information gap.

The frozen `ReviewFinding` carries stable reason-code values alongside the
display prose. This is a small but important audit distinction: prose can be
clarified without forcing downstream consumers to parse wording, while the
codes make a block such as `STALE_EVIDENCE` or `UNEXEMPTED_LINE` available for
aggregation and regression checks.

## Falsification and negative controls

The method is credible only if it can fail visibly. The release checks should
include negative controls that deliberately attempt to cross the boundary:

- remove a required claim class, stopping point, or verification mode;
- add a duplicate or unknown claim identifier to the prose register;
- describe a stale, self-asserted, or contradicted evidence record as current;
- make the figure registry and visualization brief disagree;
- alter a source-driven figure and test whether byte determinism detects the
  difference; and
- render without a required artifact and verify that the release manifest
  refuses readiness.

These controls test the instrument's refusal behavior. They do not estimate
false-positive or false-negative rates in the world, because this project has
no labeled corpus of real engagements and no independent operational observer.
The appropriate conclusion is narrower: the local gates either detect the
planted defect or they do not.

## Scope of inference

The method can support a statement such as: “given this registry, this typed
intake, this review date, and these recorded evidence statuses, the evaluator
returned this classification.” It cannot support: “the action is safe,” “the
action is lawful,” “the source endorses the framework,” or “the rendered
artifact has been independently certified.” Those stronger conclusions require
different authorities and evidence. The project is most coherent when it keeps
that stopping point attached to every claim, figure, and release record.
