# Deployment tiers as oversight-retention grades {#sec:deployment-tiers}

Turner relates deployment eligibility to the oversight retained over a system
after delivery [@turner2026redline]. Red Line reinterprets that mechanism for a
single practitioner:

- `HOSTED` retains author-operated observation and withdrawal;
- `CONNECTED` retains a maintained update or suspension path;
- `AIR_GAPPED` means beyond recall, such as an unrestricted release or handed-off
  model.

The `oversight_rank` values are 2, 1, and 0 respectively. Each registry line
declares a `max_tier`; despite that field name, it is used as a minimum retained-
oversight floor: the least-oversight environment in which a fully evidenced
typed exemption may operate. A tier floor is never a permission by itself: scope,
context, and exemption evidence still govern. [@def:tier] and [@def:tier-floor]
state the rank and the floor test exactly as the code applies them.

The evaluator is monotonic in danger. An unexempted implicated line is
`NON_COMPLIANT` at every tier; reducing retained oversight adds an aggravating
reason but cannot turn a hard block into a softer outcome. A verified exemption
below its line's floor becomes `REQUIRES_MODIFICATION`. [@prop:tier-monotone]
states this as a property and names the test that exercises it. It is a
consistency property of the local decision procedure, not empirical evidence
that a hosted system is safe or that an air-gapped system is dangerous in every
circumstance.

“Air-gapped” is shorthand for beyond the author's practical ability to observe,
update, suspend, or withdraw the work product. It is not a security certification
and does not mean that a released artifact is literally disconnected in every
deployment.

![Less retained oversight narrows the release envelope. The registry-derived matrix marks each line's oversight floor and labels the tiers directly; a filled cell means only that the tier floor is met. It does not mean an action is compliant, safe, or legally permitted. The two CANARY records remain visibly bounded away from AIR_GAPPED release by an executable invariant. Shape, text, and cell state repeat the meaning so the figure remains interpretable in grayscale and on a narrow page.](../output/figures/oversight_tier_ladder.png){#fig:oversight-tier-ladder width=95%}

The monotonicity property itself is exercised, not merely asserted. The
analysis module `red_line.analysis.monotonicity` sweeps all 36 line/keyword
slots (34 distinct tokens) across the seven current lines through the real
`evaluate_action` at each of the three deployment tiers — 108 executed
evaluations with a fully evidenced fixture intake — and records the verdict
lattice the evaluator actually returned, with zero inversions. The slot count
exceeds the vocabulary because `handoff` and `provenance` are each declared by
two lines and are therefore swept once per line.

![Dropping retained oversight never softens a verdict. Executed verdict-strictness lattice computed by `red_line.analysis.monotonicity.run_monotonicity_sweep`: all 36 line/keyword slots (34 distinct tokens) across the seven current lines run through the real `evaluate_action` with a fully evidenced fixture intake at each of the three deployment tiers — 108 executed evaluations — and every chip is the classification actually returned. Read left to right, a row moves from most to least retained oversight and strictness never decreases; the sweep records zero inversions, and its regression test carries a positive control that detects the replicated pre-fix defect. Monotonicity is a consistency property of the local decision procedure exercised with fixture evidence, not a safety measurement or a review of any real engagement.](../output/figures/tier_monotonicity_lattice.png){#fig:tier-monotonicity-lattice width=95%}
