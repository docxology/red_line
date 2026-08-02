# Registry composition as derived data {#sec:registry-composition}

The registry chapter above states what each line refuses; this section states
what the registry *is*, structurally, using only numbers computed from the
live registry object. Prose descriptions of a versioned artifact drift; a
count computed at read time from `src/red_line/registry/lines.py` cannot. The
analysis subpackage `red_line.analysis.registry_metrics` exists for exactly
this purpose: every function in it is a pure, zero-I/O summarizer over the
same in-memory `RedLine` tuple the evaluator consumes, with deterministic
sorted output and fail-closed input validation. None of its outputs is a
safety score. A count describes the shape of a boundary — how many tokens it
covers, how many conditions narrow it, what evidence those conditions demand —
not the strength, correctness, or moral standing of the person committing to
it.

## Severity and tier floors

The seven lines divide by severity into two `CANARY` lines, one `ABSOLUTE`
line, and four `STRONG` lines (`severity_distribution`). Their deployment-tier
floors divide into two lines whose floor is `hosted`, three at `connected`,
and two at `air_gapped` (`tier_floor_distribution`). The two gradings are
deliberately orthogonal: severity records how much process a change to the
line itself requires, while the tier floor records the most permissive
deployment tier at which the line's exemptions can operate at all. The
registry exhibits that orthogonality directly — the two `CANARY` lines sit at
different tier floors (`hosted` and `connected`), and the two `air_gapped`
floors belong to `STRONG` lines, not to the most change-protected ones.

## Scope vocabulary and overlap points

The seven lines declare 36 scope-token slots over 34 distinct canonical
tokens (`scope_token_frequency`). Exactly two tokens are shared between
lines, each by two lines: `handoff` (declared by both `dual-use-ablation` and
`downstream-transfer`) and `provenance` (declared by both
`provenance-and-consent` and `open-science-good-faith`). These are the
registry's only structural overlap points: an action whose declared scope
includes one of them implicates two boundaries in a single evaluation, and
the severity-monotone reduction described in [@sec:evaluation] then resolves
the pair to the single most severe applicable classification. The near-total
disjointness of the remaining 32 tokens is a design consequence of the
standalone lines, not an accident — each line names its own coverage rather
than inheriting a shared taxonomy.

[@fig:scope-vocabulary-collisions] draws that vocabulary in full — every token
against every line — so the overlap is visible as a property of the whole grid
rather than as two names in a sentence. The figure also reads out what the
evaluator actually returns for each shared token, which is the part that
matters operationally: `handoff` is declared by `dual-use-ablation`, whose
`retained-oversight` exemption is satisfied by the sweep's fully evidenced
hosted intake, and by `downstream-transfer`, whose exemptions are not — and the
returned verdict is `NON_COMPLIANT`. One line's verified exemption does not
clear a token the other line also claims.

The exemption named there is the one the evaluator reports applying, not the
one a reader might expect from the line's carve-out prose: a scope of exactly
`handoff` triggers no methods-publication exemption, because that exemption's
trigger tokens are `methods`, `paper`, and `benchmark`. The distinction is the
whole point of typed triggers, so the id in the sentence above is re-derived
from the assessment's own reason strings by
`tests/integration/test_manuscript_composition_binding.py` rather than read off
the carve-out list.

![Where two boundaries share a word. Presence grid computed by `red_line.analysis.registry_metrics.scope_token_membership`: every one of the 34 distinct canonical scope tokens against each of the seven lines, with a filled mark where the line declares the token and a count column repeating each row in text. Two tokens — `handoff` and `provenance` — are declared by two lines; the other 32 belong to one line each. The footer prints the verdict the real evaluator returned for each shared token during the tier-monotonicity sweep, so the consequence is executed rather than asserted. Implementation fact: this is the registry's declared vocabulary. Interpretation, stated as a limit: matching remains lexical over a declared scope and is not a semantic classifier, so the grid shows which words can implicate two boundaries, never whether an action truly does.](../output/figures/scope_vocabulary_collisions.png){#fig:scope-vocabulary-collisions width=95%}

## Per-line structure

The table below is computed by
`red_line.analysis.registry_metrics.line_summaries` from the live registry.
Scope is the count of canonical coverage tokens; carve-outs are narrative
clauses; exemptions are the typed, executable narrowing conditions, split by
trigger match mode.

| Line | Severity | Tier floor | Scope | Carve-outs | Exemptions | ANY / ALL |
|---|---|---|---|---|---|---|
| `cogsec-integrity` | absolute | connected | 6 | 2 | 2 | 2 / 0 |
| `downstream-transfer` | strong | connected | 5 | 2 | 2 | 1 / 1 |
| `dual-use-ablation` | strong | air_gapped | 3 | 3 | 3 | 3 / 0 |
| `open-science-good-faith` | strong | air_gapped | 5 | 2 | 2 | 2 / 0 |
| `provenance-and-consent` | strong | hosted | 5 | 2 | 2 | 2 / 0 |
| `s1-human-control-force` | canary | hosted | 6 | 3 | 2 | 1 / 1 |
| `s2-untargeted-profiling` | canary | connected | 6 | 3 | 3 | 2 / 1 |

The ranges are narrow by construction: scope sizes run from three to six
tokens, every line carries two or three narrative carve-outs, and every line
carries two or three typed exemptions. No line is an outlier that concentrates
most of the registry's narrowing surface, and no line is a bare prohibition
with no stated exemption path. The three `ALL`-mode exemptions sit on
`s1-human-control-force`, `s2-untargeted-profiling`, and
`downstream-transfer` — one each — where the exemption's trigger matches only
when *all* of its tokens are declared rather than any single one.

## Evidence depth and the free-pass check

The 16 typed exemptions distribute their 37 evidence requirements narrowly:
eleven exemptions require exactly two evidence kinds and five require exactly
three (`exemption_evidence_matrix`; the minimum across all rows is two, the
maximum three). Trigger scopes are similarly small — nine exemptions trigger
on two tokens, six on three, and one on six.

Trigger scope and evidence are separate gates, and the difference is worth
seeing rather than reading: [@prop:trigger-mode] and
[@fig:exemption-trigger-semantics] probe every exemption with one trigger token
and then with all of them, and the three `ALL`-mode rows stay blocked until
every token is declared.

The floor of two is the registry's most important structural property, so it
is checked rather than assumed. `unevidenced_exemptions` returns every matrix
row whose exemption requires *no* evidence kind at all — an exemption that any
matching declaration would satisfy, which is to say a free pass through its
line. On the current registry the function returns an empty tuple. That empty
result is meaningful only because the detector is proven able to fire: the
test suite constructs a planted registry containing a deliberate zero-evidence
exemption and asserts both that `unevidenced_exemptions` reports it and that
the registry invariant suite fails on the same input. Absence of a finding
from a detector that has demonstrated detection is evidence about the current
registry version; absence of a finding alone would be no evidence at all.

[@fig:registry-composition-profile] puts the two preceding sections on one
plate: the per-line table as four bars on a shared scale, the severity and
tier-floor splits as a footer strip, and the free-pass count as a band that is
drawn whether or not it is zero. Rendering the zero matters. A panel that
appeared only when a free pass existed would make today's clean registry
indistinguishable from a figure set that had quietly stopped checking; a band
reading `EXEMPTIONS REQUIRING NO EVIDENCE AT ALL: 0` is a result. The
regression test for this figure injects one synthetic evidence-free exemption
into a copy of the registry and asserts the band changes, so the zero is
falsifiable in the plate as well as in the analysis module.

![The shape of the boundary, line by line. Per-line structural profile computed by `red_line.analysis.registry_metrics.line_summaries`, `severity_distribution`, `tier_floor_distribution`, and `unevidenced_exemptions`. Each row is one of the seven lines in id order with its severity grade and oversight floor as text-labelled chips, and four counts on one shared bar scale: declared scope tokens, narrative carve-outs, typed exemptions, and distinct evidence kinds used. Every bar carries its number, so the plate reads without colour. The bottom band renders the count of typed exemptions requiring no evidence at all, currently zero. Implementation fact: these are counts over registry fields. Interpretation, stated as a limit: a longer bar is a wider declared surface, not a stronger commitment, a safer practice, or a basis for comparing this author's boundary with anyone else's.](../output/figures/registry_composition_profile.png){#fig:registry-composition-profile width=95%}

These numbers travel with the version. All of them describe the registry
state pinned by the canonical digest in [@sec:red-lines]; a future
amendment that adds a line, widens a scope, or relaxes an evidence
requirement changes the derived numbers, the canary payload, and this
section's claims together. That coupling is intentional: composition claims
that are recomputed from source cannot silently outlive the registry state
they describe.
