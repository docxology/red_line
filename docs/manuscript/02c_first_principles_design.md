# First-principles design: what the artifact can actually do {#sec:first-principles}

Before asking whether Red Line resembles another governance framework, ask what
problem the artifact must solve and what information it can actually possess.
One practitioner, deciding alone, before the work starts. That is the whole
situation the artifact is built for, and it fixes what the artifact can know:
whatever the practitioner has written down and whatever he can check locally.
Everything the abstract promises follows from that constraint rather than from
an ambition — and so does everything it refuses to promise, which is universal
morality, verification of the world, and stopping an action by software alone.

## Deconstruction

The project is made of six constituent parts:

| Part | Irreducible job | Evidence in this repository |
|---|---|---|
| Personal commitment | State what this author will not accept, build, tune, release, or knowingly transfer | Seven dated first-person `RedLine` records |
| Intake | Describe an action before its description can be used as a policy shortcut | `ProposedAction` and nine-field `ActionContext` |
| Evidence gate | Refuse a green result when required context is missing, stale, contradicted, or merely asserted | Typed `EvidenceRecord` values and `INSUFFICIENT_INFORMATION` |
| Local decision procedure | Apply declared scope, typed exemptions, and oversight floors consistently | `evaluate_action` and its five classifications (@def:classification) |
| Review and change record | Preserve what was decided and expose registry drift | Frozen `ReviewFinding`, transparency aggregation, and `CanaryStatement` |
| Publication surface | Let a reader compare source, implementation, and rendered artifact | Beacon prose, source ledger, deterministic figures, PDF, and HTML |

The parts are complementary but not interchangeable. A hash cannot replace a
review. A review cannot replace evidence. Evidence cannot become truth merely
because it is labeled `VERIFIED`. A public document cannot become universal
authority merely because it cites sources from many places.

## Fundamental truths

The design begins from facts that survive removal of familiar labels:

1. A personal refusal has authority over the author's own participation, not
   over other people or institutions.
2. A local program receives declarations and pointers to records; it does not,
   by inspecting their labels, know whether the underlying world is true.
3. A lexical scope matcher can apply explicit vocabulary consistently, but it
   cannot infer the actual capability or purpose of arbitrary work.
4. A cryptographic digest can show that current content differs from a prior
   digest. It does not prove authorship, authenticity, semantic adequacy, or
   non-forgeability.
5. A frozen finding records a result; without an external authority or admission
   control it cannot physically prevent execution.
6. If the conditions for a review cannot be established, treating the action as
   compliant would manufacture certainty from absence. This is the classical
   fail-safe-defaults posture: base a decision on demonstrated permission rather
   than on the mere absence of objection.
7. A publication claim is only as strong as the chain connecting its source,
   code, tests, generated assets, and rendered output.

These are not claims that the instrument is safe. They are the reasons its
strongest honest output is often a stop, a limitation, or a request for an
independent witness.

## Constraint analysis

The project also contains choices that should not be mistaken for laws of
nature. The following classification keeps the mechanism revisable:

| Design element | Classification | Why it is kept or challenged |
|---|---|---|
| First-person, dated provenance | Hard requirement of the stated function | Without an accountable author and date, the artifact cannot be a personal commitment. |
| Fail closed on unresolved required context | Hard epistemic consequence | Missing information cannot logically support a positive review result. |
| Nine required intake dimensions | Deliberate policy choice | The fields are a broad audit surface, not a complete ontology; new evidence needs may require revision. |
| Explicit aliases and an ASCII boundary | Deliberate policy choice | They block trivial masquerading without pretending to solve semantic interpretation. |
| Seven current lines | Deliberate scope choice | `REGISTRY_IS_EXHAUSTIVE = False`; absence is not endorsement. |
| 180-day freshness window | Maintenance policy | It is a useful review cadence, not a universal truth about evidence expiry. |
| Turner as the organizing comparison | Removable interpretive choice | The project must stand without importing Turner's authority, institution, or legal claims. |
| External prior canary copy | Hard condition for external change detection | A same-author file can be rewritten together with the registry and therefore cannot witness itself. |
| PDF and HTML validation | Hard requirement of a publication claim | A source that does not reach the reader intact has not been successfully published. |

## Reconstruction: what the ordering has to be

Those truths do not yet give a procedure, but they fix its order. Refusal comes
before optimization, because a boundary consulted after a project has a client
is a boundary that argues with sunk cost. Evidence comes before policy matching,
because a description that can select its own exemption token is not a
description. A result comes before authorization, because an escalation that
can be recorded ahead of a finding is an override wearing a different word. And
a local attestation comes before, without ever substituting for, an independent
witness — a file the author can rewrite cannot testify about the author.

The eight-step form the practitioner actually runs is in [@sec:operating-method];
it is one procedure stated once, not a summary and an expansion.

## Claim classes

The manuscript uses four claim classes so that a polished document does not
make unlike evidence look interchangeable:

| Claim class | What can support it | What cannot upgrade it |
|---|---|---|
| Descriptive | A cited source, edition, and stable locator | A source's existence does not establish the author's interpretation of it |
| Transfer / interpretive | An explicit question, rationale, and stopping point | A broad reading list does not create universal legitimacy |
| Implementation | Source code, tests, generated figures, validation, and inspected output | Green code does not verify the world, the source records, or operational safety |
| Release | A validated source-to-render chain, artifact manifest, and inspected PDF/HTML | A successful build does not provide external certification or real-world outcome evidence |

The adaptation is therefore a bounded construction rather than a conclusion
that the cited traditions, standards, or threat catalogs endorse Red Line. The
artifact is strongest when it says exactly what it did, what it refused to infer,
and where another reviewer must take over.

The resulting operating sequence is made explicit in [@sec:operating-method],
where each claim carries an evidence state and stopping point through the local
decision and publication gates.
