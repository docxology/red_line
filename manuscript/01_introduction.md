# Introduction {#sec:introduction}

Some work becomes harder to refuse once it has acquired a client, a deadline,
or a sunk-cost narrative. Red Line places the refusal earlier. It is the
author's personal security boundary and explicit **No document**: a dated,
revisable statement of work he will not accept, build, tune, release, or
knowingly transfer.

This is not a complete ethics system, a legal opinion, or an enforcement
service. Black Line concerns constructive practice; Golden Line concerns
direction; White Line concerns absence, omission, and epistemic restraint. Red
Line is narrower because a boundary must be usable at the moment of decision.
It answers three practical questions: what is refused, what context must be
established before a near-boundary action can be considered, and what the
instrument cannot establish.

## Four propositions

1. **Red Line is a security boundary.** Its seven first-person lines identify
   work that this author will not pursue or knowingly enable.
2. **Red Line is an explicit No document.** It is a personal commitment, not a
   universal moral authority and not a statement made by an AI system on the
   author's behalf.
3. **Red Line is an evidence-gated auditability aid.** It makes a local review
   inspectable and reproducible; it does not prove safety, legality, or truth.
4. **Red Line escalates when context cannot be established.** Missing or
   unverified evidence is `INSUFFICIENT_INFORMATION`, not permission.

## What this paper can establish

| Evidence layer | It can establish here | It cannot establish |
|---|---|---|
| Personal commitment | what this author currently refuses | universal moral authority or another person's consent |
| Local implementation | what the code and tests return for declared inputs | semantic truth, honest input, or operational safety |
| Scholarship transfer | which questions a source prompts | source endorsement, consensus, or public authorization |
| Render and release | that a specific validation run connected source to artifact | external certification or publication readiness without clean and independent witness gates |

## What the artifact is for

At the decision moment the instrument is a triage card rather than an essay:
read the beacon, name the concrete capability and deployment tier, resolve the
nine context dimensions with evidence instead of assertion, run the local
evaluator, preserve the finding with its stable reason codes, and either narrow
the work or stop. Maintaining a prior canary outside the author's write boundary
is the one step that runs on a different clock. [@sec:operating-method] states
the sequence in full; the operator version is in
[`docs/decision-protocol.md`](../docs/decision-protocol.md), and day to day the
instrument is run through the `daf-red-line` skill in the author's private
daf-skills toolchain, so this paper is the theory and the skill is the practice.
The point is relevance to a real decision under time pressure. A polished
boundary that does not change what the practitioner records, asks, or refuses is
only decoration. [@fig:boundary-instrument-plate]

The design puts refusal before optimization and evidence before policy
matching. It also separates four kinds of statement: a source may support a
descriptive claim; an interpretation may transfer a question with an explicit
stopping point; an implementation claim must be supported by code, tests,
generated artifacts, validation, or inspected output; and a release claim must
be tied to a validated source-to-render chain for a particular artifact. None of
these surfaces can silently upgrade another.

![A boundary is an instrument: declare, evidence, stop, witness. This editorial plate turns the live registry, nine-field intake, five evaluator classifications, and external-prior condition into a single decision-time field. Its paper texture, traces, and red mark are visual rhetoric, not empirical data; the caption and alt text preserve the non-claims if the image is unavailable.](../output/figures/boundary_instrument_plate.png){#fig:boundary-instrument-plate width=100%}

## Beacon, evaluator, canary

The registry is a **beacon**: collaborators can read the boundary before a
request becomes a project. The evaluator is a narrow policy instrument, not a
semantic judge. It requires a typed `ActionContext`, verified evidence for each
required dimension, normalized scope, and a structured exemption before it can
return `COMPLIANT`. A complete action that touches no registered line is
`OUTSIDE_SCOPE`, which is deliberately not collapsed into compliance.

The canary is a dated attestation over canonical registry content. It can expose
drift when a prior copy is held beyond the author's write boundary; it cannot
prevent a rewrite, prove authorship, enforce a finding, or independently
establish that a source record is true. A review authorization records
escalation but never unblocks a non-compliant or evidence-insufficient result.

## A bounded comparison

Alex Turner's *A Red Line and Oversight Framework for Government AI Contracts*
[@turner2026redline] is the mechanism source for this project's architecture
(@sec:turner-background). Its organization-to-government setting, standing
Review Body, legal context, and specific scope are not imported as authority.
The adaptation keeps only a carefully marked pattern — precommitment, retained
oversight, review classifications, and durability — and changes the subject
to one practitioner's own work.

The manuscript therefore keeps two questions separate: what the sources make
visible, and what this author commits to. The scholarship widens the questions
asked of the registry—who bears the cost of a false positive, what legibility
can conceal, whose knowledge is being organized—but it does not convert a
plural reading list into universal legitimacy. The claim register makes this
stopping rule auditable.

The paper proceeds as follows. [@sec:turner-background] records the mechanism source. [Section @sec:formalism](#sec:formalism) states the instrument as formal definitions and propositions. The red-line registry is composed in [Section @sec:red-lines](#sec:red-lines), and [Section @sec:limitations](#sec:limitations) closes with the instrument's limitations and negative space.
