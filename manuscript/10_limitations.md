# Limitations and negative space {#sec:limitations}

## What this document does not decide

Red Line is deliberately narrow. It does not decide:

- **Legal adjudication:** whether an act is lawful, licensed, contractually
  authorized, or subject to a particular jurisdiction's standard.
- **Truth verification:** whether a cited source, artifact, witness, or evidence
  record is true, complete, current, or free of strategic misrepresentation.
- **Real-world safety:** whether a system will behave safely, whether harm will
  occur, or whether a documented control will work under operational pressure.
- **Institutional authorization:** whether an employer, customer, regulator,
  community, or affected person has granted authority to proceed.
- **Independent external witnessing:** whether anyone outside the author's
  write boundary has received, checked, or attested to the registry or finding.

The instrument can require escalation when these questions cannot be
established, but it cannot answer them by itself.

**Auditability, not enforcement.** The package records a local result. It does
not stop execution, remove access, adjudicate legality, or create an independent
review body. A named authorization is visible but never releases a block.

**Evidence is not truth.** `VERIFIED` means a reviewable artifact or source was
identified. The package does not establish that the artifact is accurate,
complete, current, lawfully obtained, or free of strategic misrepresentation.
Contradicted or unsupported context blocks the result, but a plausible false
record can still pass the local status gate.

**Lexical, not semantic.** Explicit scope aliases are safer than heuristic
stemming, but the evaluator still matches declared tokens. A complete-looking
action can be mislabeled. Description mismatch hints expose one symptom; they
do not solve semantic interpretation.

**False positives and false negatives.** The fail-closed intake is intentionally
biased toward stopping when required information is absent or unresolved. That
can produce a false positive for caution: a legitimate exemption may wait
until its evidence is assembled. The lexical boundary also permits a more
serious residual false negative: a dangerous action can be described with a
benign token set or a complete-looking but misleading evidence packet. The
instrument reduces these risks through explicit scope, negative tests, source
provenance, and independent review; it cannot remove them without semantic and
institutional authority it does not have.

## Adversarial declarations {#sec:adversarial}

Because every input is self-declared, the instrument can be gamed by
construction, and the honest response is to demonstrate the attacks rather
than deny them. Each of the following was executed against the real evaluator.

**Scope-token laundering.** A targeting-component action declares only
`logistics`, `translation`, and `maintenance` — permissible support tokens that
match the `adjacent-force-support` exemption on `s1-human-control-force` —
while omitting `targeting`, `weapons`, or `autonomous_weapon`. The evaluator
matches declared tokens against scope and exemption triggers; the action's
narrowed scope implicates only `s1-human-control-force`, and the verified
exemption returns `COMPLIANT`. The evaluator cannot inspect whether the
declared tokens honestly describe a component that selects and engages
targets.

**Evidence-status fabrication.** An action provides VERIFIED records with
plausible but fabricated references — a purpose statement citing a
non-existent contract, a human-control record pointing to a private repository
that has never been reviewed. The evidence gate requires VERIFIED status for
every dimension the exemption demands; a record whose status field reads
`VERIFIED` satisfies the gate regardless of whether the referenced artifact
exists, is accurate, or was genuinely reviewed. The evaluator records
epistemic status, not ground truth.

**Refresh-date laundering.** The freshness window requires evidence dated
within 180 days of the review date. An action whose evidence records were
last genuinely verified 300 days ago rewrites their dates to the current
review date and returns `COMPLIANT`. The evaluator checks the declared date
against the window; it cannot distinguish a genuine re-verification — a
reviewer re-examining the source — from an edit to a date string.

**Declared-unknown gamesmanship.** An action declares every sensitive
dimension as `not_applicable` and supplies a single VERIFIED record backing
that designation, aiming to minimize the evidence surface while staying within
the gate. The evaluator still demands VERIFIED evidence for each dimension,
and `not_applicable` is a permitted value only when a verified record supports
it — but the evaluator cannot assess whether the dimension is genuinely
inapplicable or merely declared so to shrink the review burden. An action
whose sole remaining required dimension carries a fabricated record passes on
the strength of a single false positive.

These are instances of a well-documented dynamic, not defects unique to this
design. A refusal instrument that certified safety
would make these failure modes catastrophic, because a gamed `COMPLIANT` would
launder a dangerous action into apparent permission. Red Line's design
response is to refuse the certifying role entirely: a classification reports
what the declarer provided and the evaluator computed, so a gamed `COMPLIANT`
overstates nothing but the presence of declared evidence. The attacks also
stay inspectable rather than hidden — the declared scope, the evidence status
records, and the declared dates are the very record a reviewer reads, so a
reviewer who asks "do these tokens describe this work?", "was this evidence
genuinely reviewed?", or "what changed at this refresh?" is asking questions
the declaration itself exposes. The instrument narrows what gaming can
counterfeit; it cannot remove the need for the human judgment those questions
require, and it never converts any classification into a safety
certification, an accreditation, or a permission.

**Registry scope is non-exhaustive.** `OUTSIDE_SCOPE` is not “safe” and
`COMPLIANT` is not “universally acceptable.” Both are bounded by seven personal
lines, their current vocabulary, and the quality of the intake.

**Personal authority remains personal.** The lines are the author's refusals,
not a claim that other people must share them. The global and historical reading
base widens the questions and exposes blind spots; it does not turn the author
into a representative of the traditions cited.

**Scholarship is curated, not representative.** The reading base is not a
systematic review or a substitute for affected-party testimony, local expertise,
or jurisdiction-specific legal analysis. Its purpose is to widen the questions
asked of a personal instrument and to make transfer limits visible.

**A formal statement is not a stronger claim.** The definitions and
propositions in [@sec:formalism] say what the program returns for declared
inputs. Writing that down precisely, and binding each proposition to a test,
removes one failure mode — prose drifting away from the procedure — and adds no
authority. A proposition can be true of the code and useless in the world at the
same time, which is the case [@prop:evidence-conjunction] describes, and the
same is true of [@prop:tier-monotone] and [@prop:outcome-precedence]: the gate is
strict, and strictness is not accuracy.

**Structural analytics describe shape, not strength.** The derived numbers in
[@sec:registry-composition] and the exercised outcome coverage in
[@sec:evaluation] are registry introspection, not measurement of the world.
An exemption that demands three evidence kinds is not thereby "stronger" than
one that demands two, and the demand profile across intake dimensions is not
a risk model; comparing such counts across authors as if they scored rigor
would recreate exactly the safety-score misuse this document disclaims. The
free-pass detector reports on structurally degenerate exemptions only — a
substantively wrong boundary with well-formed structure passes every metric.
Its empty result is bounded to the current registry state, and the
outcome-coverage report is a control-flow reachability pin built on fixture
evidence: a `complete` report shows the evaluator can produce all five
classifications, not that any real engagement was classified correctly.

**Canary dependence.** A same-author repository fixture is a regression anchor,
not an external witness. The hash detects drift only when a prior copy is held
outside the writer's control and checked by someone else. The canary is a
tamper-evidence pattern, not legal protection or prevention.

**Publication pipeline.** Deterministic figures, output validation, and rendered
inspection reduce source-to-artifact risk, but they do not prove that a polished
figure is rhetorically fair. PDF and HTML review remain required.

**Release state.** This work is released as a standalone repository at <https://github.com/docxology/red_line>.
It has no external canary witness, no minted DOI, no independent review body,
and no execution admission control. A public release should not claim those
things until the release evidence bundle in [`docs/claim-register.md`](../docs/claim-register.md)
exists and an independent reader has checked the source, outputs, and prior
statement.
