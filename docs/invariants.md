# Structural Invariants

This document describes every structural invariant in
[`src/red_line/invariants/checks.py`](../src/red_line/invariants/checks.py). These are pure-compute
checks (zero I/O, no `infrastructure.*` imports) that validate the *shape* of the
red-line registry rather than any single proposed action. They answer one
question: is the registry still coherent enough to be trusted as a beacon?

Each check exists to catch a specific **silent weakening** — a change that leaves
the registry looking healthy (ids present, tests green, hash recomputable) while
having quietly gutted a line's force. A registry can be weakened without deleting
anything: emptying a scope, blanking a carve-out, downgrading a severity, or
stuffing a non-enum value into a field. The presence of a line id proves nothing
about whether that line still bites.

## Honest scope of these checks

The invariants verify **internal consistency**, not correctness of the author's
choices. They cannot tell you whether the seven red lines are the *right* lines,
whether they are morally complete (they are not — `REGISTRY_IS_EXHAUSTIVE = False`),
or whether the author will honor them. Each red line is
[Daniel Ari Friedman's](../src/red_line/registry/lines.py) dated, first-person, revisable
commitment, not a universal moral claim and not authored by any AI. The registry
is released (<https://github.com/docxology/red_line>): there is no external verifier;
review authorizations are self-reported and never bypass a blocking result.
These checks provide **auditability, not enforcement**.

## Contract

Every check has the signature `check_*(lines) -> list[InvariantResult]`, where
`InvariantResult` is a frozen dataclass of `(name, passed, detail)`.
[`all_invariants(lines=PERSONAL_RED_LINES)`](../src/red_line/invariants/checks.py) runs the
full battery and returns the flattened list;
[`invariants_pass(lines)`](../src/red_line/invariants/checks.py) is `True` iff every result
passed. Both default to the real `PERSONAL_RED_LINES` registry but accept any
`tuple[RedLine, ...]`, which is what makes proof-of-detection testing possible.

## Proof of detection

Every invariant below has a companion test that asserts two things: the check
**passes** on the real registry, and the check **fails** on a planted-bad
registry constructed by mutating one line (typically via
`dataclasses.replace`). A check that can only ever pass is worthless — it would
certify a gutted registry as healthy. The planted-defect test proves each check
actually fires on the weakening it claims to prevent. An invariant with no
failing test is treated as unverified.

## The `STANDARD_ANALOG_IDS` set

```python
STANDARD_ANALOG_IDS: frozenset[str] = frozenset(
    {"s1-human-control-force", "s2-untargeted-profiling"}
)
```

Turner's framework rests on two narrow Standards: **Standard 1** (human control
over harm-capable / force-applying systems) and **Standard 2** (no untargeted
profiling or mass surveillance). This registry reuses that substrate. The two
lines whose ids appear in `STANDARD_ANALOG_IDS` are the direct analogs of those
Standards, and they are the **only** two lines carrying `Severity.CANARY`. CANARY
grade is reserved for them because they are the load-bearing pair the entire
warrant-canary mechanism watches: their removal or alteration is what
`verify_canary` escalates to `"CANARY-GRADE LINE ALTERED"`. The other five lines
(dual-use ablation, cogsec integrity, provenance/consent, open-science good faith,
downstream transfer) carry `ABSOLUTE` or `STRONG` severity — real commitments, but
not the two Standards the canary is built to protect. Reserving CANARY for exactly
the Turner-Standard analogs keeps the canary signal from being diluted across
every line.

## The invariants

### 1. `unique_ids` — `check_unique_ids`

**Enforces:** No two red lines share an `id`. Reports the sorted set of any
duplicated ids.

**Why it matters:** Line ids are the stable keys everything else binds to — the
canary statement's per-line `(id, severity, digest)` triples, `detect_line_removal`,
and `STANDARD_ANALOG_IDS` membership all key on id. A duplicate id lets one line
masquerade as another: a canary check keyed on id could match the wrong line, and
removal detection could be fooled into thinking a deleted line is still present
because a colliding id remains. Uniqueness is the precondition that makes id-keyed
auditing meaningful.

### 2. `each_has_carve_out` — `check_each_has_carve_out`

**Enforces:** Every line has at least one carve-out clause **and** every carve-out
clause carries content tokens (checked with `_tokens`). A line fails if it has zero
carve-outs, or if any of its carve-out clauses is empty or pure boilerplate
(`""`, `"does not"`) that tokenizes to nothing.

**Why it matters:** A carve-out is what keeps a red line from over-firing on
legitimate work — it is the explicit boundary between the prohibited act and the
permitted neighbor (defensive alerting, aggregate research, open publication). An
empty or boilerplate carve-out is a carve-out *in name only*: the id and the field
are present, so a shallow presence check passes, but the line now has no articulated
excuse surface. Requiring content tokens prevents a carve-out from being silently
blanked while still counting as "having" one.

### 3. `typed_exemptions` — `check_typed_exemptions`

**Enforces:** Every line has at least one structured `Exemption`; each exemption
has an id, description, canonical trigger scope, and only valid `EvidenceKind`
requirements.

**Why it matters:** A prose carve-out is not an executable permission. Without a
typed exemption record, a reviewer could treat an adjacent-use sentence as a
free-form release token and silently widen a prohibition. This check makes the
exemption surface explicit and lets the evaluator require evidence for the
specific conditions that narrow a line.

### 4. `nonempty_scope` — `check_nonempty_scope`

**Enforces:** Every line has at least one scope keyword. Reports any zero-scope
lines.

**Why it matters:** This is the most dangerous silent weakening the battery
guards against. `evaluate_action` implicates a line only when the action's scope
**intersects** the line's scope. Gutting a line's `scope` to `()` makes the
intersection always empty, so the line can never be implicated by any action — it
becomes unreachable while still appearing in the registry, still carrying its
severity, still counted by every other check. A zero-scope line is a red line that
has been turned off without being removed. This check is the one that closes that
blind spot; without it, the rest of the battery would certify a maximally weakened
registry as healthy.

### 5. `canary_not_air_gapped` — `check_standard_analogs_not_air_gapped`

**Enforces:** No `Severity.CANARY` line has `max_tier == DeploymentTier.AIR_GAPPED`.
Reports any CANARY line that permits air-gapped release.

**Why it matters:** `AIR_GAPPED` is the tier beyond the author's recall and
monitoring — work released past oversight. The two CANARY lines are the Turner
Standards (human control over force; no mass surveillance); allowing either to
reach the air-gapped tier would mean the most serious boundaries could be shipped
into exactly the deployment context where no oversight remains. The function name
says "standard analogs," but the implemented test keys on `Severity.CANARY`,
which — given `standard_analogs_are_canary` — is precisely the two Standard lines.
This caps the two most serious lines at monitored tiers.

### 6. `has_both_standards` — `check_has_both_standards`

**Enforces:** Both `s1-human-control-force` and `s2-untargeted-profiling` are
present in the registry. Reports which analog is missing.

**Why it matters:** The framework's claim to adapt Turner's mechanism depends on
both Standards being represented. Deleting either one — the force Standard or the
profiling Standard — would collapse the framework to a partial imitation while the
remaining lines still look like a full registry. This is the presence half of the
Standard protection. Note its limit: presence alone cannot see a line that is
present but demoted or gutted, which is why it is paired with the next two checks.

### 7. `standard_analogs_are_canary` — `check_standard_analogs_are_canary`

**Enforces:** Every line whose id is in `STANDARD_ANALOG_IDS` still carries
`Severity.CANARY`. Reports any Standard analog demoted to a lesser grade.

**Why it matters:** `has_both_standards` proves the ids exist; this proves they
still carry the grade that gives them warrant-canary semantics. Silently
downgrading `s1`/`s2` from CANARY to STRONG would strip their removal or
modification of the `"CANARY-GRADE LINE ALTERED"` escalation in `verify_canary`,
while leaving the ids present so the presence check stays green. A demoted Standard
is a Standard whose alteration no longer trips the loudest alarm. This closes the
gap the presence check cannot see.

### 8. `enum_field_types` — `check_enum_field_types`

**Enforces:** Every line's `max_tier` is a real `DeploymentTier` member and its
`severity` is a real `Severity` member. Reports any line with a non-enum value in
either field.

**Why it matters:** `RedLine` is a plain dataclass, and dataclasses do not
type-check their fields at construction or under `dataclasses.replace`.
`dataclasses.replace(rl, max_tier="garbage")` succeeds silently, producing a line
whose tier is a string. That string would then fail — or worse, misbehave — in the
tier comparisons `evaluate_action` and `canary_not_air_gapped` rely on, in
unpredictable ways. This check restores the type guarantee the dataclass does not
give, so every downstream comparison is over genuine enum members.

### 9. `nonempty_text` — `check_nonempty_standard_text`

**Enforces:** Every line has non-empty (non-whitespace) `standard` **and**
`rationale` text. Reports any line with a blank standard or rationale.

**Why it matters:** The `standard` is the actual commitment prose — the sentence
the author is bound by — and the `rationale` is the recorded reason. Blanking
either leaves a line that is structurally valid (id, scope, severity, carve-outs
all intact) but semantically hollow: a red line with no stated prohibition, or a
prohibition with no recorded reason. Since the registry's force is auditability,
an unstated commitment cannot be audited. This keeps every line's human-readable
core populated.

### 10. `provenance` — `check_provenance`

**Enforces:** Every line's `stated_on` parses as an ISO date, `stated_by` is a
non-empty string, and `standard` still begins with `I ` — the first-person
form. All three are checked per line and the failures are reported together.

**Why it matters:** The registry's whole legitimacy claim is that each entry is
one named person's dated, revisable commitment rather than a universal moral
assertion or an AI-authored rule. Blanking `stated_by`, corrupting a date, or
rewriting a standard into the third person (`Developers must not…`) would leave
every other check passing while converting a personal precommitment into an
anonymous ruleset — the exact reading the manuscript spends its limitations
section refusing.

### 11. `unique_exemption_ids` — `check_unique_exemption_ids`

**Enforces:** No two typed exemptions share an `id`, anywhere in the registry —
the uniqueness scope is global, not per line.

**Why it matters:** Exemption ids are how a review record names *which*
narrowing was applied. `check_unique_ids` protects line ids only; a duplicate
exemption id one level down would let two different evidence requirements
answer to the same name in a finding, so a transparency record could not be
replayed against the registry that produced it.

### 12. `canonical_scope_tokens` — `check_canonical_scope_tokens`

**Enforces:** Every token in a line's `scope` and in every exemption's
`trigger_scope` is already in canonical form — `normalize_token(token) == token`
— and a token that cannot be normalized at all fails the check closed.

**Why it matters:** The evaluator matches an action's *normalized* scope against
the registry. A registry token that is not itself canonical (`Surveillance`,
`hand-offs`, a full-width spelling) still resolves through the alias table at
match time, so nothing visibly breaks; but the registry then contains a
spelling no reader can grep for, and the alias table silently becomes
load-bearing for coverage. Requiring the reviewed canonical spelling in the
source keeps the vocabulary in the file the author edits.

### 13. `exemption_triggers_disjoint` — `check_exemption_triggers_disjoint`

**Enforces:** No exemption's `trigger_scope` shares a token (after
normalization, so alias spellings cannot hide the overlap) with its own line's
`scope`. A scope or trigger that cannot be normalized fails the check closed —
disjointness that cannot be computed is never certified.

**Why it matters:** An exemption triggered by the line's own prohibited scope is
*self-exempting*: declaring the prohibited dimension itself would, once the
required evidence is verified, satisfy the exemption trigger and narrow the line
for exactly the activity it prohibits. Every other check in the battery would
still pass — the exemption's id, description, evidence kinds, and match mode all
remain valid — so this silent-weakening channel needed its own invariant. On the
real registry every trigger names an *adjacent* permitted use (defensive
alerting, aggregate research, methods publication), never the prohibited
dimension itself; this check pins that property.

### 14. `registry_serialization` — `check_registry_serialization`

**Enforces:** The canonical payload the registry reduces to — lines sorted by
`id`, scopes and carve-outs sorted, exemptions sorted with sorted evidence-kind
values — still builds and still round-trips through `json.dumps` with sorted
keys, ASCII output, and stable separators.

**Why it matters:** This is the exact payload `registry_hash` digests, so it is
the canary's own input. A field that stops being sortable, an enum replaced by a
raw object, or a non-ASCII value entering a serialized field would make the
digest either uncomputable or unstable across runs, and the failure would first
appear as a canary that will not verify rather than as a registry defect. This
check names the defect at its source.

## Summary table

| Invariant | Check function | Silent weakening it prevents |
| --- | --- | --- |
| `unique_ids` | `check_unique_ids` | Colliding ids let one line masquerade as another under id-keyed auditing |
| `each_has_carve_out` | `check_each_has_carve_out` | Carve-out blanked to boilerplate — a carve-out in name only |
| `typed_exemptions` | `check_typed_exemptions` | Prose-only exemption surface that can be widened without evidence |
| `nonempty_scope` | `check_nonempty_scope` | Scope gutted to `()` — line unreachable, never implicated, still listed |
| `canary_not_air_gapped` | `check_standard_analogs_not_air_gapped` | A CANARY Standard permitted past oversight into the air-gapped tier |
| `has_both_standards` | `check_has_both_standards` | Either Turner Standard analog deleted from the registry |
| `standard_analogs_are_canary` | `check_standard_analogs_are_canary` | Standard analog demoted from CANARY, losing warrant-canary semantics |
| `enum_field_types` | `check_enum_field_types` | Non-enum value stuffed into `max_tier`/`severity` via `replace` |
| `nonempty_text` | `check_nonempty_standard_text` | `standard` or `rationale` blanked — a structurally valid, hollow line |
| `provenance` | `check_provenance` | Author, date, or first-person form stripped — a personal commitment reread as an anonymous rule |
| `unique_exemption_ids` | `check_unique_exemption_ids` | Two narrowings answering to one id, so a finding cannot be replayed |
| `canonical_scope_tokens` | `check_canonical_scope_tokens` | Non-canonical registry spelling that only matches through the alias table |
| `exemption_triggers_disjoint` | `check_exemption_triggers_disjoint` | Exemption trigger overlapping its own line's scope — a self-exempting line |
| `registry_serialization` | `check_registry_serialization` | Canonical payload that stops building or stops being stable — the canary's own input |

The table lists fourteen rows because `all_invariants` runs fourteen checks.
It listed ten for several releases while the code ran fourteen; the four
undocumented checks (`provenance`, `unique_exemption_ids`,
`canonical_scope_tokens`, `registry_serialization`) are the ones added above.
`tests/invariants/test_checks.py::test_documented_invariants_are_exactly_the_live_battery`
now recomputes both the numbered sections and this table from `all_invariants()`,
so the two cannot separate again.

Every row has a proof-of-detection test that fires on a planted defect of exactly
this kind. Passing the battery means the registry is internally coherent; it does
not, and cannot, mean the commitments are complete, correct, or externally
enforced.
