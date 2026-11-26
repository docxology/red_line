# Background — Turner as a bounded mechanism source {#sec:turner-background}

Alex Turner's *A Red Line and Oversight Framework for Government AI Contracts*
is the principal comparative source for this project's architecture
[@turner2026redline]. Turner writes at organization-to-government scale. The
framework combines bright-line standards, retained-oversight tiers, a standing
Review Body, review classifications, durability provisions, and transparency.
This section records the source before describing the personal adaptation.

Turner's formulation of appropriate human control is more demanding than a
checkbox saying “human in the loop.” It asks whether an identifiable person is
accountable, whether that person can exercise independent judgment, whether the
system's operational design permits meaningful evaluation, and whether legal
and operational transparency are available [@turner2026redline]. It also
recognizes that speed, volume, and complexity can make nominal human review
ineffective. Red Line carries these as questions for the intake; it does not
pretend that a text field or token can establish them.

Turner's surveillance standard similarly distinguishes individualized,
particularized analysis from inference based only on a category, population, or
bulk dataset. The existence of data about a person is not, by itself, permission
to generate an individualized assessment. Those details matter here because
they show why Red Line's `human_control`, `affected_parties`, `purpose`, and
`data_provenance` fields must be evidenced rather than asserted.

Turner also describes scope-specific carve-outs, oversight thresholds, and
durability procedures. Ambiguity resolves toward coverage in the source
framework [@turner2026redline]. Red Line preserves that conservative direction
but implements a stronger local first gate: unresolved context becomes
`INSUFFICIENT_INFORMATION` before the registry can return a policy result.

## What is and is not transferred

Transferred as a question: can a bright-line commitment be made inspectable,
reviewed before action, and made harder to weaken silently? Not transferred as
authority: Turner's legal setting, government contracting relationship,
seven-member institution, leadership powers, or claims about external
enforcement. Red Line is a personal, self-authored instrument with an explicit
external-witness limitation.

The implementation mapping appears in the next section. The important boundary
is that an analogy to a governance mechanism is not evidence that the personal
instrument has the institution's powers.

The source framework also contains organizational, contractual, legal, and
operational machinery that this project does not possess: a company, government
counterparties, a standing Review Body, neutral-auditor access, safety-stack
controls, and service suspension. Those omissions are not hidden implementation
debt. They are the reason the local artifact claims auditability rather than
institutional enforcement.

## Provenance labels for the adaptation

The manuscript uses three labels so that resemblance does not become false
attribution:

| Element | Label | Exact boundary |
|---|---|---|
| Human control for harm-capable action | **source-derived** question; **adapted** intake | Turner supplies the accountable-human problem; Red Line adds fields and evidence, not Turner's authority. |
| Individualized and proportionate scrutiny | **source-derived** distinction; **adapted** refusal | Turner supplies particularization; Red Line applies it to S2, not to a complete proportionality theory. |
| Bright lines, tiers, review, and durability | **source-derived** mechanism; **adapted** architecture | The local registry, evidence gate, five classifications, self-review, and canary are this project's implementation. |
| Personal No document and strict evidence gate | **independently authored** | Personal design decisions, not Turner quotations, legal standards, or universal conclusions. |
