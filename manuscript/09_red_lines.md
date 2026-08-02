# The red-line registry {#sec:red-lines}

This is the beacon: the author's personal security boundary and explicit No
document at version `0.3.0`. The registry is first-person, dated, revisable,
and non-exhaustive. It is not a universal ethics code and not a claim made by
any AI system that assisted with its preparation.

The current registry contains seven lines, including two CANARY-grade lines
(formalized as [@def:red-line] and [@def:exemption]).
The canonical registry digest is:

`72835fd81d1f7ecf70f47b1e0061cd56c385273dd846879ab639225913f5aad7`

Each line has a human-readable standard, rationale, coverage dimensions,
narrowing clauses, structured exemptions, required evidence, a tier floor,
severity, author, and date. The narrative clauses explain the boundary to a
reader; the typed exemptions are the only executable narrowing conditions.
Adding a token such as `vetted` or `consented` cannot establish vetting or
consent.

The authoritative machine-readable source is `src/red_line/registry/lines.py`. The
canary includes exemption semantics in its canonical payload, so changing an
exemption or its evidence requirement is a detectable registry change and must
be accompanied by a successor rationale.

Because the registry is enumerable data, its narrowing structure can be stated
as derived numbers rather than described qualitatively. The analysis module
`red_line.analysis.registry_metrics` computes the full exemption ×
evidence-kind coverage matrix from the live registry: the seven lines carry 16
typed exemptions that together declare 37 evidence requirements across the
nine intake dimensions. Affected parties is the most-demanded dimension (six
exemptions require it), followed by purpose, legal basis, and capability scope
(five each); end use and deployment are the least demanded (two each). Thirteen
exemptions match their trigger scope with `ANY` semantics and three require
`ALL` trigger tokens to be declared. [@fig:exemption-evidence-matrix] renders
that matrix directly from the analysis code; every filled cell is a
precondition for narrowing, not proof that the required evidence is true. The
fuller structural profile — severity and tier-floor distributions, scope
overlap points, and per-line composition — is derived in
[@sec:registry-composition].

![Every narrowing of a line names the evidence that must be verified first. Registry-derived exemption evidence-requirement matrix computed by `red_line.analysis.registry_metrics.exemption_evidence_matrix`: each row is one typed exemption grouped under its red line, each column one of the nine intake dimensions, and a filled cell means the exemption can narrow its line only when a `VERIFIED` record of that kind is present. The bottom row counts how many exemptions demand each dimension. The matrix describes the structural shape of the author's boundaries, not their moral weight; a satisfied requirement is a locally recorded condition, not independent truth or a safety score.](../output/figures/exemption_evidence_matrix.png){#fig:exemption-evidence-matrix width=95%}

## s1-human-control-force — Human control over force and <span style="white-space: nowrap; overflow-wrap: normal;">harm-capable</span> systems

**[CANARY]**

**Standard:** I will not build, tune, or knowingly supply a component to a system that selects and engages targets for force without appropriate human control over each engagement.

**Rationale:** Turner Standard 1: force-application without an identifiable, accountable human decision-maker removes the moral circuit-breaker. Applies whether I provide targeting directly or as a component.

**Coverage dimensions:** `targeting`, `weapons`, `lethality`, `force`, `kinetic`, `autonomous_weapon`

**Does not restrict:** defensive-only alerting with a human in the loop

**Does not restrict:** logistics, translation, maintenance, or research and development

**Does not restrict:** intelligence analysis reviewed by an accountable human

**Typed exemptions and required evidence:**

- `defensive-alerting-human-control`: Defensive-only alerting with an accountable human decision-maker; `human_control`, `end_use`.
- `adjacent-force-support`: Logistics, translation, maintenance, research, or intelligence analysis; `purpose`, `human_control`.

**Max tier:** hosted  
**Severity:** CANARY  
**Stated by:** Daniel Ari Friedman  
**Stated on:** 2026-07-15

## s2-untargeted-profiling — No untargeted profiling or mass surveillance

**[CANARY]**

**Standard:** I will not build tooling whose purpose is to convert bulk data into individualized intelligence on persons not already identified as subjects of a specific, lawful, individualized process.

**Rationale:** Turner Standard 2: bulk-to-individual inference on unnamed persons is the engine of mass surveillance. Demographic-, origin-, or belief-based initiation is prohibited outright.

**Coverage dimensions:** `surveillance`, `profiling`, `bulk_data`, `biometric_id`, `dragnet`, `tracking`

**Does not restrict:** aggregate research producing no individualized output

**Does not restrict:** analysis of an already-identified, lawfully specified subject

**Does not restrict:** consented, opt-in personal analytics

**Typed exemptions and required evidence:**

- `aggregate-research`: Aggregate research producing no individualized output; `purpose`, `affected_parties`, `data_provenance`.
- `identified-lawful-subject`: Analysis of an already-identified, lawfully specified subject; `affected_parties`, `legal_basis`.
- `opt-in-personal-analytics`: Consent-based opt-in personal analytics; `affected_parties`, `data_provenance`, `legal_basis`.

**Max tier:** connected  
**Severity:** CANARY  
**Stated by:** Daniel Ari Friedman  
**Stated on:** 2026-07-15

## dual-use-ablation — Scoped release of dual-use models

**Standard:** I will not release a proprietary or handed-off model beyond my recall (air-gapped) while it retains dangerous dual-use capability that has not been ablated below a repurposing-cost threshold.

**Rationale:** Turner Tier 3: for work released beyond monitoring, the cost of repurposing a scoped model should exceed the value of doing so.

**Coverage dimensions:** `model_release`, `weights`, `handoff`

**Does not restrict:** release of task-specific models with capability removed

**Does not restrict:** open publication of methods, papers, or benchmarks

**Does not restrict:** hosted or connected tiers under retained oversight

**Typed exemptions and required evidence:**

- `ablated-task-specific`: Task-specific release with dangerous capability removed;  
  required evidence: `capability_scope`, `deployment`.
- `methods-not-weights`: Open methods, papers, or benchmark publication without dangerous weights;  
  required evidence: `capability_scope`, `downstream_transfer`.
- `retained-oversight`: Hosted or connected work under retained oversight;  
  required evidence: `deployment`, `human_control`.

**Max tier:** air-gapped  
**Severity:** STRONG  
**Stated by:** Daniel Ari Friedman  
**Stated on:** 2026-07-15

## cogsec-integrity — Cognitive security strengthens, never degrades, the epistemic commons

**Standard:** I will not build cognitive-security tooling whose function is to manufacture deception, run covert influence operations, or degrade a population's shared ability to reason.

**Rationale:** My cognitive-security work is defensive by definition: it strengthens information ecosystems. Weaponized persuasion inverts that mission.

**Coverage dimensions:** `influence_ops`, `disinformation`, `manipulation`, `propaganda`, `deception`, `cogsec`

**Does not restrict:** detection, red-teaming, or defensive analysis of influence operations

**Does not restrict:** education, media-literacy, or transparency tooling

**Typed exemptions and required evidence:**

- `defensive-cognitive-security`: Detection, red-teaming, or defensive analysis; `purpose`, `end_use`, `human_control`.
- `epistemic-education`: Education, media literacy, or transparency tooling; `purpose`, `affected_parties`.

**Max tier:** connected  
**Severity:** ABSOLUTE  
**Stated by:** Daniel Ari Friedman  
**Stated on:** 2026-07-15

## provenance-and-consent — Provenance and consent for data and identity

**Standard:** I will not train, evaluate, or ship on data acquired without a lawful basis and, where persons are involved, without consent or a legitimate public-interest basis.

**Rationale:** Turner's 'acquisition' clause: any process by which person data enters my systems is covered regardless of how a source labels it.

**Coverage dimensions:** `data_acquisition`, `scraping`, `pii`, `consent`, `provenance`

**Does not restrict:** public-domain, openly-licensed, or synthetic data

**Does not restrict:** my own or explicitly-consented personal data

**Typed exemptions and required evidence:**

- `public-open-synthetic-data`: Public-domain, openly licensed, or synthetic data; `data_provenance`, `legal_basis`.
- `own-consented-data`: Author-owned or explicitly consented personal data; `data_provenance`, `legal_basis`, `affected_parties`.

**Max tier:** hosted  
**Severity:** STRONG  
**Stated by:** Daniel Ari Friedman  
**Stated on:** 2026-07-15

## open-science-good-faith — Open-science claims are honest and reproducible

**Standard:** I will not publish a result, metric, or capability claim I have not verified against a reproducible artifact, nor let proprietary interest launder an unverified claim into the public record.

**Rationale:** My public research graph is a beacon only if its claims bind to code that runs. Overclaiming corrodes the commons I am trying to build.

**Coverage dimensions:** `publication`, `benchmark_claim`, `metric`, `reproducibility`, `provenance`

**Does not restrict:** clearly-labeled preliminary, hypothesis, or negative results

**Does not restrict:** withholding proprietary detail while stating what is withheld

**Typed exemptions and required evidence:**

- `clearly-labeled-preliminary`: Clearly labeled preliminary, hypothesis, or negative result;  
  required evidence: `purpose`, `capability_scope`.
- `stated-withholding`: Withheld proprietary detail explicitly identified;  
  required evidence: `capability_scope`, `downstream_transfer`.

**Max tier:** air-gapped  
**Severity:** STRONG  
**Stated by:** Daniel Ari Friedman  
**Stated on:** 2026-07-15

## downstream-transfer — No knowing transfer to a violating end use

**Standard:** I will not sell, license, or hand off work where I know or have substantial reason to believe it will be re-transferred to an end use that violates any of these red lines.

**Rationale:** Turner's downstream-transfer and 'knows or has substantial reason to believe' clauses: flow-down of the substantive boundary, not just the box.

**Coverage dimensions:** `resale`, `sublicense`, `integration`, `downstream`, `handoff`

**Does not restrict:** transfer to a vetted end user with a flow-down commitment

**Does not restrict:** fully open-source release under a license that itself binds no end use

**Typed exemptions and required evidence:**

- `vetted-flow-down`: Transfer to a vetted end user with a flow-down commitment;  
  required evidence: `downstream_transfer`, `legal_basis`, `affected_parties`.
- `open-source-no-end-use-binding`: Open-source release whose license does not bind end use;  
  required evidence: `downstream_transfer`, `capability_scope`.

**Max tier:** connected  
**Severity:** STRONG  
**Stated by:** Daniel Ari Friedman  
**Stated on:** 2026-07-15

The executable records, rather than this prose alone, determine whether an
exemption is satisfied. A complete intake can still be `NON_COMPLIANT`, and a
complete action with no matching line is `OUTSIDE_SCOPE`, not a safety finding.
