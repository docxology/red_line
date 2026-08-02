# Proposed red lines (for the author's adoption)

A `daf-connect-dots` pass over the registry (2026-07-16), reviewed by hand
against the live evaluator's vocabulary, found six candidate coverage gaps.
Nothing below has been run through `evaluate_action`, and nothing below could
be: none of these candidates is in `PERSONAL_RED_LINES`, so the evaluator is
structurally silent on their tokens — `evaluate_action` returns `OUTSIDE_SCOPE`
with an empty implicated set for every one of them. That silence is the only
executable fact here, and
`tests/integration/test_proposed_candidates_binding.py` pins it — probing every
candidate token alone and every candidate's whole scope, with a positive
control on a live registry token so the silence is a measured result rather
than a broken probe.

The current seven
lines all govern **products the author builds and ships** (weapons components,
surveillance tooling, released models, cogsec tools, training data, published
claims, onward transfer). They cannot adjudicate a **role or trust relationship**
the author occupies — and that is exactly where the most vulnerable
counterparties sit (a captive prison classroom, a research participant, an
unnamed collaborator, an unattended agent acting as the author, a nonprofit's
funds).

**These are NOT adopted.** Each red line is the author's own first-person,
dated, revisable commitment; a model must not author them unilaterally. They are
presented here as candidate scopes for review; a future adoption must provide
typed exemptions and verified evidence rather than relying on a carve-out
keyword. They are ready to consider only on explicit assent. Adding
any of them changes the published registry hash and requires a full canary
re-issue (recompute hash → update README + `manuscript/09_red_lines.md` pins +
beacon prose + `manuscript/11_conclusion.md` count + regenerate
`tests/fixtures/canary_committed.json`).

Severity note: `CANARY` grade stays reserved for the two Turner-Standard analogs
(`invariants.STANDARD_ANALOG_IDS`); these extensions are `ABSOLUTE`/`STRONG`.

| id | title | proposed scope (not yet evaluated) | max_tier | severity | priority |
|----|-------|----------------------------------|----------|----------|----------|
| `agent-autonomy-limit` | Human authority over irreversible / self-modifying agent actions | autonomous_agent, agent_action, self_modification, irreversible_action, auto_publish, auto_spend, unattended | CONNECTED | ABSOLUTE | high |
| `authorship-attribution` | Honest authorship, credit, and AI-assistance disclosure | authorship, attribution, credit, plagiarism, collaborators, byline, ai_disclosure, citation | AIR_GAPPED | STRONG | high |
| `human-subjects-ethics` | Consent / review / withdrawal for research on persons | human_subjects, research_participants, participant_enrollment, irb, human_study, cognitive_experiment, participant_intervention | HOSTED | ABSOLUTE | high |
| `student-relationship-data` | No repurposing of student data or the teaching relationship (incl. Pelican Bay captive learners) | student_data, student_records, grade_data, coursework_reuse, student_profiling, carceral_data, ferpa | HOSTED | ABSOLUTE | high |
| `fiduciary-integrity` | AII treasurer stewardship boundary — **requires charter widening the author must confirm** | commingling, self_dealing, undisclosed_conflict, financial_misrepresentation, private_inurement | HOSTED | STRONG | medium |
| `research-organism-welfare` | Welfare / permits in organismal fieldwork | animal_research, field_collection, specimens, organism_welfare, collecting_permit, ecological_harm | AIR_GAPPED | STRONG | low |

Each candidate should be tested so that: (a) the bare domain word (e.g.
`teaching`, `ecology`, routine treasurer work) does NOT hard-block legitimate
activity; (b) the declared capability scope cannot be laundered by description
text; and (c) every adjacent-use exemption names its required evidence kinds.
Full standards, rationales, and carve-out wording are in the workflow synthesis
(`MEMORY/WORK/.../red-line-skill-application`) and can be pasted into
`PERSONAL_RED_LINES` on request.

`fiduciary-integrity` additionally widens the module's stated
software/modeling/cogsec charter to cover nonprofit stewardship — flagged
separately because it is a scope-of-the-instrument decision, not just a new line.

## Current-release decision records

The following records make the non-adoption state explicit. No candidate has
author assent for adoption in version `0.3.0`; each remains a proposal requiring
an affirmative future decision. These records are not registry entries and do
not change `PERSONAL_RED_LINES`. The machine-readable mirror is
`data/proposed_red_lines.json`; the release gate validates its six IDs, decision
state, scope boundaries, future `any`/`all` exemption semantics, evidence
requirements, and evaluator controls, and binds its hash into the release
manifest.

| id | author decision | scope boundary | typed exemptions and required evidence | false-positive controls and evaluator cases |
|---|---|---|---|---|
| `agent-autonomy-limit` | Assent not granted; do not adopt in this release. | Only unattended, self-modifying, irreversible, auto-publishing, or auto-spending agent actions; not ordinary scripted assistance or supervised tooling. | No exemption is adopted. Reconsideration must define human-control, reversibility, and authorization evidence. | Negative: `teaching` or supervised documentation alone does not block. Positive: declared `autonomous_agent` + `irreversible_action` with missing human control blocks; description alone never supplies scope. |
| `authorship-attribution` | Assent not granted; do not adopt in this release. | Attribution, credit, plagiarism, citation, byline, and AI-assistance disclosure in published work; not private drafting or ordinary editing. | No exemption is adopted. Reconsideration must define collaborator consent, provenance, and disclosure records. | Negative: ordinary editing without a publication claim is outside this candidate. Positive: declared `plagiarism` or `ai_disclosure` in a release context requires provenance; a title or description cannot launder an undeclared scope. |
| `human-subjects-ethics` | Assent not granted; do not adopt in this release. | Enrollment, intervention, identifiable participant data, withdrawal, and review of research on persons; not anonymous aggregate or non-human work. | No exemption is adopted. Reconsideration must define consent, review/approval, withdrawal, and data-provenance evidence. | Negative: aggregate research without individualized output stays outside this candidate. Positive: `human_subjects` + `participant_intervention` without verified consent/review is blocking; free text is not evidence. |
| `student-relationship-data` | Assent not granted; do not adopt in this release. | Student records, grades, coursework reuse, profiling, and carceral education relationships; not public teaching materials or de-identified pedagogy. | No exemption is adopted. Reconsideration must define student consent, role authority, purpose limitation, and retention/flow-down evidence. | Negative: `teaching` alone does not block. Positive: `student_records` + `coursework_reuse` without verified authority and consent blocks; description-only mentions are advisory at most. |
| `fiduciary-integrity` | Assent not granted; do not adopt in this release; charter widening requires separate author confirmation. | Treasurer stewardship, commingling, self-dealing, conflicts, private inurement, and financial misrepresentation; not ordinary software work. | No exemption is adopted. Reconsideration must define charter authority, conflict disclosure, approvals, and transaction evidence. | Negative: routine bookkeeping without a declared fiduciary scope does not block. Positive: `self_dealing` + `undisclosed_conflict` with missing disclosure evidence blocks; the candidate cannot be triggered by prose alone. |
| `research-organism-welfare` | Assent not granted; do not adopt in this release. | Organism collection, animal research, specimens, permits, and ecological harm; not ordinary simulations or literature review. | No exemption is adopted. Reconsideration must define permits, welfare review, minimization, and chain-of-custody evidence. | Negative: `ecology` or simulation alone does not block. Positive: `animal_research` + `collecting_permit` without verified welfare/permit evidence blocks; narrative cannot substitute for the declared scope. |

Any future adoption must replace “assent not granted” with an explicit author
assent or rejection, add executable `Exemption` records with conservative
`any`/`all` semantics, add positive and negative tests, and issue a rationaled
successor canary before changing the registry.
