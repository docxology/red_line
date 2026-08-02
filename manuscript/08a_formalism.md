# The instrument stated formally {#sec:formalism}

The preceding sections describe the evaluator in prose. Prose about a decision
procedure drifts from the procedure, and the reader has no way to see the drift.
This section restates the same objects and the same decision rule as numbered
definitions and propositions taken from the shipped code, and binds each
proposition to a named test that fails if the two disagree. Nothing here is new
policy. It is the existing instrument written so that a mismatch is a red test
rather than an unnoticed sentence.

Two limits carry through every result below. Each is a statement about a local
program's behaviour on declared inputs, never about the world those inputs
describe; and each is scoped to the registry version pinned by the digest in
[@sec:red-lines], because these are properties of a decision procedure applied
to particular content.

## The domain objects

::: {.definition #def:tier title="Deployment tier and oversight rank"}
The deployment tiers are $T = \{\mathtt{hosted}, \mathtt{connected},
\mathtt{air\_gapped}\}$, ordered by a retained-oversight rank
$\rho: T \to \{0,1,2\}$ with $\rho(\mathtt{air\_gapped}) = 0$,
$\rho(\mathtt{connected}) = 1$, and $\rho(\mathtt{hosted}) = 2$. A higher rank
means more oversight the author still holds after release: the ability to
observe the work product, update it, suspend it, or withdraw it.
:::

::: {.definition #def:severity title="Severity grade"}
The severity grades are $\{\mathtt{canary}, \mathtt{absolute},
\mathtt{strong}\}$. The grade records how a change to the line itself is
treated, not how bad a breach would be: a `canary` line's removal or demotion
is itself the reportable event.
:::

::: {.definition #def:evidence-status title="Evidence status"}
The evidence statuses are $\{\mathtt{VERIFIED}, \mathtt{SELF\_ASSERTED},
\mathtt{UNVERIFIED}, \mathtt{CONTRADICTED}\}$. Only `VERIFIED` can support a
required dimension. The evaluator does not decide whether a source is true; it
records whether a reviewable artifact was checked.
:::

::: {.definition #def:evidence-kind title="Intake dimension"}
The intake dimensions are the nine-element set $K$:

$$\begin{aligned}
K = \{\ &\mathtt{purpose},\ \mathtt{end\_use},\ \mathtt{affected\_parties},\
\mathtt{data\_provenance},\ \mathtt{legal\_basis},\\
&\mathtt{human\_control},\ \mathtt{deployment},\ \mathtt{downstream\_transfer},\
\mathtt{capability\_scope}\ \}
\end{aligned}$$

Their enum order is the intake order, and it is the column order of every
derived matrix in this paper.
:::

::: {.definition #def:evidence-record title="Evidence record and staleness"}
An evidence record is a tuple $(k, r, s, \sigma, d)$ of a kind $k \in K$, a
reference $r$, a summary $s$, a status $\sigma$, and an ISO date $d$. Given a
review date $a$ and a window $w$ (default $w = 180$ days), the record is
*stale* when $d > a$ or $a - d > w$. A future-dated record is therefore stale
in the same way an expired one is.
:::

::: {.proposition #prop:staleness-boundary title="The staleness boundary is exclusive"}
Staleness uses the strict comparison $a - d > w$ of [@def:evidence-record],
so a verified record dated exactly $w$ days before the review date is fresh,
and a record dated $w + 1$ days before is stale. The boundary is the same
strict-exclusive semantics as black\_line's currentness boundary and
golden\_line's temporal boundary: the window's last fresh day is age $w$,
and the first stale day is $w + 1$. The threshold $w$ is a review-cadence
choice, not a decay law, and a future-dated record is stale regardless of
the window.
:::

::: {.definition #def:context title="Action context"}
An action context $C$ assigns a string to each of the nine dimensions of
[@def:evidence-kind], and carries a finite tuple of evidence records in the sense of [@def:evidence-record] and a
finite tuple of declared unknowns. $C$ *supports* a dimension $k$ at review
date $a$ when it holds a record of kind $k$ whose status is `VERIFIED` and
which is not stale. A dimension whose assigned string is empty or one of
`unknown`, `unspecified`, `tbd`, `unclear` is unsupported whatever its
records say; `not_applicable` is a permitted value, but it is still only
supported when a verified record backs it.
:::

::: {.definition #def:normalization title="Scope normalization"}
A declared token is canonicalized by NFKC normalization, case folding, an ASCII
check that raises on anything else, replacement of every non-alphanumeric
character by an underscore, collapse of repeated underscores, stripping of
leading and trailing underscores, and a final lookup in a reviewed alias table.
There is no stemming: a new synonym must be added to the table by hand.
$\mathcal{N}(S)$ denotes the canonical token set of a declared scope $S$.
:::

::: {.definition #def:exemption title="Typed exemption"}
An exemption is a tuple $e = (\mathrm{id}, \mathrm{description}, T_e, R_e,
m_e)$ where $T_e$ is a non-empty trigger scope, $R_e \subseteq K$ is the
required evidence, and $m_e \in \{\mathtt{any}, \mathtt{all}\}$ is the match
mode. For a declared scope $S$, with $\mathcal{N}$ the normalization of [@def:normalization],

$$\mathrm{matches}_e(S) \;=\;
\begin{cases}
\mathcal{N}(T_e) \subseteq \mathcal{N}(S) & m_e = \mathtt{all}\\[2pt]
\mathcal{N}(T_e) \cap \mathcal{N}(S) \neq \emptyset & m_e = \mathtt{any}
\end{cases}$$

and $e$ is *satisfied* by a context $C$ at review date $a$ when $C$ supports
every $k \in R_e$. Matching is a declaration; satisfaction is the condition
that can narrow a line.
:::

::: {.definition #def:red-line title="Red line"}
A red line is an eleven-field record: a slug id, a title, a first-person
standard beginning `I `, a rationale, a coverage scope, narrative carve-out
clauses, a tier floor `max_tier`, a severity of [@def:severity], the person stating it, the ISO
date it was stated, and a tuple of typed exemptions. A line $\ell$ *covers* a
declared scope $S$ when $\mathcal{N}(\mathrm{scope}_\ell) \cap \mathcal{N}(S)
\neq \emptyset$. The carve-out clauses are prose for a reader; only the typed
exemptions execute.
:::

::: {.definition #def:action title="Proposed action and effective scope"}
A proposed action is a tuple $(\mathrm{description}, S, C, t, \mathrm{amb})$ of
free text, a declared scope, a context, a tier $t \in T$ as ranked in [@def:tier], and an ambiguity flag.
Coverage and exemption matching both run against the *effective* scope
$E = \mathcal{N}(S) \cup \{t\}$: the tier value is itself a token, so a line or
exemption may name a tier in its scope. The description is never part of $E$.
:::

::: {.definition #def:classification title="Classification"}
The classifications are the five-element set $C$:

$$\begin{aligned}
C = \{\ &\mathtt{COMPLIANT},\ \mathtt{REQUIRES\_MODIFICATION},\
\mathtt{NON\_COMPLIANT},\\
&\mathtt{OUTSIDE\_SCOPE},\ \mathtt{INSUFFICIENT\_INFORMATION}\ \}
\end{aligned}$$

`OUTSIDE_SCOPE` is a finding of absence after a complete inspection;
`INSUFFICIENT_INFORMATION` is a refusal to inspect. Neither is permission.
:::

::: {.definition #def:intake-defect title="Intake defect"}
An action has an intake defect at review date $a$ when any of the following
holds: a declared token fails normalization; some dimension is unsupported in
the sense of [@def:context]; some dimension holds a record that is unresolved
(self-asserted, unverified, or contradicted in the sense of [@def:evidence-status], with no verified record standing
in its place) or stale; the context declares an unknown; the normalized scope
is empty or contains one of the markers `unknown`, `unspecified`, `tbd`,
`unclear`; or the ambiguity flag is set.
:::

::: {.definition #def:tier-floor title="Tier floor"}
Each line declares a floor `max_tier`. An action at tier $t$ is *below the
floor* of line $\ell$ when $\rho(t) < \rho(\mathrm{max\_tier}_\ell)$, with $\rho$ the rank function of [@def:tier] — it
retains strictly less oversight than the line requires. The field name reads as
a ceiling and behaves as a floor on retained oversight; the code, not the name,
is the definition.
:::

::: {.definition #def:strictness title="Strictness order"}
On the three verdicts a fully evidenced, line-implicating intake can reach,
strictness is ranked $\mathtt{COMPLIANT} < \mathtt{REQUIRES\_MODIFICATION} <
\mathtt{NON\_COMPLIANT}$. The two remaining classifications carry no strictness
rank: an intake stop is upstream of policy and an out-of-scope result implicates
nothing, so ranking either against these three would be arbitrary. The
implementing predicate raises rather than ranking them.
:::

## The decision rule

::: {.proposition #prop:intake-precedence title="The intake gate precedes policy"}
If an action has an intake defect in the sense of [@def:intake-defect] at review date $a$, then for every registry —
including the empty one — the result is `INSUFFICIENT_INFORMATION`, the
implicated-line tuple is empty, and the reason codes include `intake_blocked`.
No line is consulted, so no registry content can change the outcome. An action
is a proposed action in the sense of [@def:action]; the intake gate inspects
its context and evidence, not its description.
:::

::: {.proposition #prop:evidence-conjunction title="The intake gate is conjunctive over all nine dimensions"}
Take a baseline action the live registry classifies `COMPLIANT` with a fresh
`VERIFIED` record for each of the nine dimensions. Degrading exactly one record
— removing it, or setting its status to self-asserted, unverified, or
contradicted, or dating it outside the freshness window — withdraws that result.
Across the nine dimensions and the five degradations, all forty-five executed
evaluations return `INSUFFICIENT_INFORMATION`, and each of the forty-five names
exactly the degraded dimension and no other as blocking. No dimension is
decorative, and the stop signal identifies the field it stopped on.
:::

::: {.proposition #prop:outcome-precedence title="One verdict, most severe first"}
Given a defect-free intake, the evaluator reduces over the lines that cover the
effective scope and returns exactly one classification, determined in this
order: if any covering line has no satisfied exemption in the sense of [@def:exemption], `NON_COMPLIANT`; else if
any satisfied exemption sits below its line's tier floor of [@def:tier-floor] or coincides with two
or more coverage hits on the same line, `REQUIRES_MODIFICATION`; else if any
line was covered, `COMPLIANT`; else `OUTSIDE_SCOPE`. The four cases are
exhaustive and mutually exclusive, and a less severe outcome never displaces a
more severe one. A line is a red line in the sense of [@def:red-line]; its
coverage scope, tier floor, and typed exemptions are the fields this rule reads.
:::

::: {.proposition #prop:outcome-reachability title="All five classifications are reachable"}
Each of the five classifications of [@def:classification] is returned by at
least one action against the live registry at a fixed review date. Reachability
is a property of the control flow, not evidence that any real engagement was
classified correctly; the same harness reports partial coverage honestly when
run against an empty registry, where the three implication-dependent outcomes
become unreachable.
:::

::: {.proposition #prop:exemption-evidence title="No exemption narrows a line without verified evidence"}
An exemption narrows its line only when it both matches the effective scope and
is satisfied by the context. On the live registry every one of the sixteen
typed exemptions requires at least two evidence kinds, so no matching
declaration alone can clear a line. The detector that would report a
zero-evidence exemption returns nothing on the live registry and fires on a
planted one, which is what makes the empty result informative rather than
merely absent.
:::

::: {.proposition #prop:trigger-mode title="ALL-mode triggers cannot be reached by one token"}
For an `any`-mode exemption every single trigger token matches; for an
`all`-mode exemption with more than one trigger token, no single token matches
and only the full trigger set does. The live registry carries thirteen
`any`-mode and three `all`-mode exemptions, and every `all`-mode exemption has
exactly two trigger tokens. Run through the real evaluator against an anchor
from the exemption's own line, each `all`-mode exemption's line is
`NON_COMPLIANT` when one trigger token is declared and `COMPLIANT` when both
are — fifty-eight executed evaluations, every row behaving as its mode
requires.
:::

::: {.proposition #prop:tier-monotone title="Reducing oversight never softens a verdict"}
Fix a declared scope and a fully evidenced context, and vary only the tier along
$\mathtt{hosted} \to \mathtt{connected} \to \mathtt{air\_gapped}$. Strictness in
the sense of [@def:strictness] never decreases. Every scope keyword of every
current line at all three tiers is one hundred and eight executed evaluations
with zero inversions. An unexempted covering line is `NON_COMPLIANT` at every
tier; a satisfied exemption below its floor is `REQUIRES_MODIFICATION` rather
than `COMPLIANT`.
:::

::: {.proposition #prop:normalization-closure title="Normalization is closed, and failure stops at two layers"}
$\mathcal{N}$ is idempotent: $\mathcal{N}(\mathcal{N}(S)) = \mathcal{N}(S)$ for
every scope it accepts. A token that is not ASCII after NFKC normalization is
rejected rather than canonicalized, and the rejection is enforced twice. The
action constructor raises, so an ordinary caller cannot build the action at all.
Should such a token be written into the frozen record past the constructor, the
evaluator normalizes defensively a second time and returns
`INSUFFICIENT_INFORMATION` with an `invalid_scope` reason code and an empty
normalized scope. A homoglyph or full-width spelling therefore cannot enter the
vocabulary as a new token, and cannot pass as an unmatched one either.
:::

::: {.proposition #prop:reason-codes title="Reason codes are a stable, duplicate-free audit surface"}
Every assessment carries reason codes drawn from a closed vocabulary, appended
in evaluation order and never repeated; the assessment record rejects a
duplicated code at construction. Human-readable reasons can be reworded without
changing the codes, which is what lets a downstream consumer regression-test the
*route* to a verdict rather than the terminal alone.
:::

## The report envelope

A classification word is the *last* step of a review, not the whole of it.
`COMPLIANT` is a projection of a derivation that also holds the reasons
trail, the matched exemption if any, the evidence sweep, and the
authorization arm — and a word that travels without its derivation is
exactly the safe-looking projection this instrument must not let harden into
the state. The envelope is the transport contract that keeps the two
attached: the word travels only alongside a digest pointer to the complete
native finding, and the instrument's non-claims travel inside the same
record.

::: {.definition #def:report-envelope title="Report envelope"}
The report envelope is the frozen record $v = (\mathrm{schema\_version},\
\mathrm{line\_id},\ \mathrm{subject\_id},\ \mathrm{review\_date},\
\mathrm{registry\_version},\ \mathrm{registry\_digest},\
\mathrm{native\_status},\ \mathrm{report\_ref},\
\mathrm{source\_snapshot\_refs},\ \mathrm{scope\_and\_nonclaims})$ with
exactly those ten fields, in order, exported under the schema string
`line.report-envelope/1.0`. $\mathrm{native\_status}$ is this line's own
classification word from [@def:classification]; it is one instrument's word
in that instrument's vocabulary, never to be compared, ranked, averaged, or
merged across lines. $\mathrm{report\_ref}$ is the SHA-256 of the canonical
native finding (`red-line.report/1.0`), which serializes the complete
derivation — including the authorization arm as an explicit `null` when it
is absent, so an unreviewed arm is distinguishable from an empty one.
Sibling instruments export the same shape by publishing the same schema
string, never by importing one another.
:::

::: {.proposition #prop:envelope-pointer title="The envelope points, never reinterprets"}
For every finding $f$ the evaluator returns, `finding_envelope(f)` produces the [@def:report-envelope] and satisfies
`envelope_matches_finding(envelope, f)`: the digest pointer, the review
date, the registry digest, and the classification word all agree with the
finding they were exported from, and editing any checked field afterwards
makes the check return false. The envelope adds nothing the finding does not
determine except the caller-supplied subject and snapshot references, which
are stored, not verified. A matching envelope attests that an archived pair
is unedited; it does not certify the finding true, the action safe, or the
review well aimed.
:::

## What binds each proposition

Every row names a test in `tests/integration/test_formalism_bindings.py` that
re-derives the proposition's content from the code and then asserts the
manuscript states it. Corrupting the sentence reddens the row; corrupting the
code reddens the derivation inside it.

| Proposition | Claim in one line | Verifying test |
|---|---|---|
| [@prop:staleness-boundary] | staleness uses strict comparison; the window edge is exclusive | `test_staleness_exclusive_boundary_is_derived_from_the_code` |
| [@prop:intake-precedence] | a defect stops the evaluation before any line is read | `test_intake_precedence_holds_against_every_registry` |
| [@prop:evidence-conjunction] | all nine dimensions are load-bearing and the stop is localized | `test_evidence_conjunction_matches_the_executed_sweep` |
| [@prop:outcome-precedence] | one verdict, resolved most-severe-first | `test_outcome_precedence_is_exhaustive_and_ordered` |
| [@prop:outcome-reachability] | all five classifications are reached | `test_outcome_reachability_matches_the_executed_battery` |
| [@prop:exemption-evidence] | a matching trigger alone never narrows a line | `test_exemption_evidence_floor_is_derived_from_the_registry` |
| [@prop:trigger-mode] | ALL-mode needs every trigger token | `test_trigger_mode_counts_match_the_executed_probe` |
| [@prop:tier-monotone] | dropping oversight never softens a verdict | `test_tier_monotonicity_numbers_match_the_executed_sweep` |
| [@prop:normalization-closure] | normalization is idempotent and fails closed | `test_normalization_closure_is_executed_not_asserted` |
| [@prop:reason-codes] | codes are closed, ordered, and duplicate-free | `test_reason_code_vocabulary_is_closed_and_duplicate_free` |
| [@prop:envelope-pointer] | the envelope agrees with its finding, and any edit is visible | `test_envelope_pointer_agreement_is_executed_not_asserted` |

The two propositions that are hardest to see from the code alone have their own
plates. [@fig:evidence-gate-sensitivity] renders the forty-five perturbations
behind [@prop:evidence-conjunction], and [@fig:exemption-trigger-semantics]
renders the fifty-eight probes behind [@prop:trigger-mode].

![Degrade one intake dimension and the compliant result is withdrawn. Single-dimension perturbation sweep computed by `red_line.analysis.evidence_sensitivity.run_evidence_sensitivity`: a compliant baseline is re-run through the real `evaluate_action` with exactly one of its nine verified records removed, downgraded, or aged past the freshness window. Every cell reports the classification actually returned and the reason codes it raised, and the trailing column confirms the gate named only the degraded dimension. Conjunctive behaviour is a property of the local gate — not evidence that a verified record is true, that these are the right nine dimensions, or that any real intake was reviewed.](../output/figures/evidence_gate_sensitivity.png){#fig:evidence-gate-sensitivity width=95%}

![One convenient word cannot reach an ALL-mode exemption. Trigger-semantics probe computed by `red_line.analysis.trigger_semantics.run_trigger_semantics`: every typed exemption is run through the real `evaluate_action` twice, once declaring a single trigger token beside an anchor from its own line's coverage scope and once declaring the whole trigger set. ANY-mode rows match on every single token; ALL-mode rows match on none and clear their line only when every trigger token is present. A matched trigger is a declaration and never proof — the typed evidence must still be verified, and the plate reports match semantics rather than whether a declaration describes the work honestly.](../output/figures/exemption_trigger_semantics.png){#fig:exemption-trigger-semantics width=95%}

## What the formalism does not establish

A proposition here says what the program returns for declared inputs. It does
not say that the declaration is honest, that the verified record is true, that
the nine dimensions exhaust what matters, or that the registry names the right
boundaries. [@prop:tier-monotone] is a consistency property of a decision procedure,
not a claim that a hosted deployment is safe. [@prop:evidence-conjunction]
shows that the gate is strict, which is a different thing from showing that
strictness is well aimed: an action can satisfy all nine dimensions with
plausible false records and reach `COMPLIANT`, and the formalism has nothing to
say about that case. Those limits are developed in [@sec:limitations].
