# Evidence, ambiguity, and evaluation {#sec:evaluation}

The evaluator is a staged method, not a semantic safety classifier. The first
stage asks whether the action can be reviewed at all. `ActionContext` requires
nine dimensions: purpose, end use, affected parties, data provenance, legal
basis, human control, deployment, downstream transfer, and capability scope.
Each must have a `VERIFIED` evidence record, including an explicit supported
not-applicable value. Self-assertion, unresolved contradiction, unknown scope,
empty scope, or explicit ambiguity returns `INSUFFICIENT_INFORMATION`. The gate
is conjunctive over all nine and it says which one it stopped on;
[@prop:evidence-conjunction] and [@fig:evidence-gate-sensitivity] carry the
executed sweep behind that claim.

The evaluator first attempts canonical normalization of the declared scope;
malformed or non-ASCII tokens stop the intake rather than becoming new
vocabulary. It then checks the evidence gate before matching registry coverage,
applying typed exemptions, checking verified evidence for the exemption, and
enforcing the deployment tier. Normalization is input hygiene, not a policy
verdict. The description is useful for human reading and mismatch hints; it
cannot satisfy the scope or evidence gate.

The distinction matters: `OUTSIDE_SCOPE` means the complete intake implicated no
current line, while `COMPLIANT` means at least one line was implicated and a
verified exemption plus tier requirements satisfied it. A missing legal basis is
neither: it is an information stop. The precedence is
therefore: intake defect first; then an unexempted line; then a verified but
modified or under-tier use; then a fully narrowed implicated line; and only
then outside scope. [@prop:intake-precedence] and [@prop:outcome-precedence]
state the same rule formally, each bound to a test that re-derives the branch
order from the evaluator source rather than restating it.

This ordering is monotone in severity: the intake gate short-circuits before any
policy matching, and the reduction over implicated lines always resolves to the
single most severe applicable classification, so a less severe outcome never
overrides a more severe one. [@fig:outcome-precedence] reads that precedence top
to bottom, from the `INSUFFICIENT_INFORMATION` short circuit down through the
hard block, the modification requirement, the narrowed compliant result, and the
distinct `OUTSIDE_SCOPE` terminal.

![The evaluator returns the single most severe applicable outcome. Outcome-precedence ladder generated from the `evaluate_action` control flow: the intake gate returns `INSUFFICIENT_INFORMATION` before policy matching, after which the reduction over implicated lines resolves to one classification ordered by severity — a hard block dominates a modification requirement, which dominates a compliant result, which dominates `OUTSIDE_SCOPE`. A less severe outcome never overrides a more severe one. The ladder is a control-flow schematic, not empirical evidence that any action was safe, lawful, or correctly described.](../output/figures/outcome_precedence_ladder.png){#fig:outcome-precedence width=95%}

![Normalization and evidence gates precede policy verdicts. This deterministic method map shows the reading path from canonical input normalization through mandatory context, required evidence, line coverage, typed exemption, and tier checks. The `INSUFFICIENT_INFORMATION` branch is deliberately upstream of compliance; `OUTSIDE_SCOPE` is a distinct terminal result. The figure is generated from the evaluator contract, not from observed safety data, and the caption's distinction is essential when the visual is read without the surrounding prose.](../output/figures/evaluation_decision_path.png){#fig:evaluation-decision-path width=95%}

## Exercised outcome coverage

The two figures above are schematics of intended control flow. The five-outcome
claim is separately executed rather than drawn: the harness
`red_line.analysis.outcome_coverage.run_outcome_coverage` runs a deterministic
battery of five `ProposedAction` fixtures — one designed for each
classification — through the real `evaluate_action` against the live registry
at a fixed review date (2026-07-15). In the current registry all five of the
five classifications are reached and every case lands on its intended outcome,
with the evaluator's stable reason codes recorded per case. The same harness
honestly reports partial coverage when it should: run against an empty
registry, the three implication-dependent outcomes (`COMPLIANT`,
`REQUIRES_MODIFICATION`, `NON_COMPLIANT`) become unreachable, and a review
date a year later downgrades every fixture's evidence to stale, collapsing
even the compliant case to an information stop. [@fig:outcome-coverage-plate]
renders the executed report.

The reason codes returned by the executed battery also confirm that each case
reaches the intended terminal by the intended *route*. The unevidenced case
stops with `missing_evidence` and
`intake_blocked` — the short circuit, not a policy verdict. The out-of-scope
case returns the single code `outside_scope`. The compliant case carries both
`verified_exemption` and `all_lines_narrowed`, meaning a line was implicated
and then narrowed rather than never matched. The modification case reports
`multiple_prohibited_dimensions` — a verified exemption undercut by extra
prohibited scope on the same line — and the blocked case reports
`unexempted_line`. A future refactor that preserved the five terminals but
altered the paths to them would surface here as a changed code set.

Reachability is a structural property of the evaluator's control flow. The
battery's evidence records are harness fixtures, so a complete report is a
regression pin on the evaluator — it is not evidence that any real engagement
was reviewed, safe, lawful, or correctly described.

![All five outcomes are exercised through the real evaluator, not asserted. Outcome-coverage plate computed by `red_line.analysis.outcome_coverage.run_outcome_coverage`: each battery case runs through the real `evaluate_action` at the fixed review date, and the chip on the right is the classification actually returned with its stable reason codes. All five classifications are reached and every case matches its intended outcome, upgrading the five-outcome claim from a control-flow assertion to an executed, regression-pinned property. The fixture evidence is not real-world verification, and the plate is not a safety measurement.](../output/figures/outcome_coverage_plate.png){#fig:outcome-coverage-plate width=95%}

## Residual lexical limitation

Explicit aliases close trivial singular/plural and punctuation near-misses, but
they do not infer meaning. A complete-looking action can still misdescribe its
capability or evidence. That is why the manuscript calls the output a local
auditability result and requires independent witness/review before making a
stronger public assurance claim.

The result is also bounded by the current registry vocabulary. A newly named
capability, an unfamiliar deployment pattern, or a misleading but complete
evidence packet can escape the intended semantic category. This is why the
instrument treats `OUTSIDE_SCOPE` as a bounded registry statement and why the
release claim remains auditability rather than safety certification.

That vocabulary is small enough to print in full, and
[@fig:scope-vocabulary-collisions] does. Thirty-four words decide what this
evaluator can see; two of them belong to more than one line. A reader who wants
to know what `OUTSIDE_SCOPE` is bounded by can read the whole boundary off one
grid rather than take the caveat on trust.
