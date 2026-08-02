# Defensive security threat model

This is a defensive design record for the red_line repository and its
publication pipeline. Red Line is not a production service, does not accept
network requests, and does not claim resistance to a nation-state operator.
The purpose of this model is narrower: identify how a patient adversary could
alter the local decision record, exfiltrate private source, forge a rendered
publication, or make a green verifier certify the wrong artifact.

The model uses the vocabulary of [MITRE ATT&CK](https://attack.mitre.org/),
the [Diamond Model of Intrusion Analysis](https://www.activeresponse.org/wp-content/uploads/2013/07/diamond.pdf) (Caltagirone, Pendergast & Betz, 2013), and
the [SLSA v1.2 specification](https://slsa.dev/spec/v1.2/) as defensive
implementation context. These frameworks organize threats and controls; they
do not certify this project, establish legal authority, or turn a self-review
into an external audit.

## Scope, crown jewels, and trust boundaries

The crown jewels are:

- the private registry and its seven red lines;
- the action/evidence records and review findings;
- the prior canary statement and its independent future witness copy;
- private scholarship notes, source URLs, and author identity data;
- the source-to-output mapping across this sidecar and the sibling template
  checkout; and
- the generated PDF, HTML, figures, citations, and validation report.

The last item matters: a polished but altered output can change what readers
believe while source code remains unchanged.

Trust boundaries are:

1. sidecar source to sibling template checkout;
2. manuscript, registry, and figure source to generated PDF/HTML;
3. author-writable registry to a witness-held prior canary;
4. action declaration to evidence records;
5. source claim to citation, edition, and stable locator; and
6. local test oracle to real-world semantic judgment.

There is no production runtime, cloud account, database, secret store, or
deployment admission controller in this repository. Runtime hardening,
Kubernetes controls, mTLS, HSM-backed signing, and endpoint telemetry are
therefore out of scope here; presenting them as present would be a false
security claim.

## Adversary profiles

| Profile | Goal | Relevant ATT&CK pressure | Defensive concern |
|---|---|---|---|
| Privileged-account or host compromise | alter the registry, evidence, canary, or private source | Valid Accounts (`T1078`); Stored Data Manipulation (`T1565.001`) | local tests may pass after both source and fixture are rewritten |
| Dependency or development-tool compromise | alter figure generation or rendering without an obvious manuscript diff | Compromise Software Dependencies and Development Tools (`T1195.001`) | a changed renderer can forge a visually persuasive PDF/HTML |
| Template/supply-chain compromise | cross the sidecar/template boundary or leak private material | Compromise Software Supply Chain (`T1195.002`); Exfiltration Over Web Service (`T1567`) | symlinked development paths make write and read boundaries easy to misunderstand |
| Citation or source-manipulation adversary | make an authority appear verified, current, or supportive when it is not | Data Manipulation (`T1565`); External Defacement (`T1491.002`) | scholarship can become authority-washing even when code is green |
| Coercive or social-engineering adversary | obtain a private source, pressure a re-issuance, or impersonate a witness | Valid Accounts (`T1078`); Unsecured Credentials (`T1552.001`) | the canary has force only when the prior copy is outside the author's write reach |

These are capability classes, not an attribution of an incident or a claim
that a named government actor is targeting this project. The model assumes
patience, access to public repository history, and the ability to exploit
human review gaps; it does not assume that a local lexical evaluator can
understand the true purpose of arbitrary code.

## Attack paths and controls

| Path | False certification or impact | Current control | Required residual action |
|---|---|---|---|
| Registry edit → canary fixture edit → green local suite | a red line is weakened while the same-author oracle certifies the replacement | canonical aggregate/per-line hashes, successor rationale, fresh-canary check, external-witness limitation | obtain and compare a prior copy from outside the repository writer's control |
| Confusable/aliased scope → evaluator bypass | a dangerous declaration is normalized into an unrelated token or a synonym is silently widened | explicit aliases, ASCII/NFKC normalization, unknown/empty-scope blocking, negative controls | review every new alias and add a semantic witness review; lexical matching remains insufficient |
| Stale or fabricated evidence → green policy result | an old duplicate, assertion, or contradicted record appears current | typed statuses, 180-day freshness window, stale-duplicate blocking, secret/PII reference rejection | verify the underlying artifact with an independent reviewer; `VERIFIED` is not truth |
| Dependency/renderer change → altered PDF or HTML | source and unit tests pass while the user-facing artifact is forged or incomplete | `uv.lock`, pure-stdlib runtime, sibling-template boundary, figure registry, PDF/HTML validation, visual inspection | add a signed SBOM/provenance record and compare renders from an isolated environment |
| Symlink/write-boundary confusion → private-source disclosure | template hydration or render writes through a path assumed to be public or read-only | explicit render from a template checkout that was actually located — `RED_LINE_TEMPLATE_ROOT`, or an ancestor directory that carries `scripts/pipeline/stage_03_render.py`; no assumed relative path, no copied template engine, no publication in this pass | inspect the resolved path before render; keep sidecar content out of the public template checkout |
| Citation replacement → authority laundering | a stale, wrong, or overbroad source is presented as support | verified URL ledger, edition/locator and transfer boundary, source notes in figures | re-open every URL and edition before release; retain the non-transfer boundary |
| Green tests → false confidence | all executable gates pass but the claim exceeds what they measure | verifier-first review, explicit limitations, long captions, no-safety-certification language | independent critical reading and external witness remain release gates |

## Verifier-first findings

The red-team pass found and repaired three concrete oracle gaps:

1. `src/red_line/model/red_line.py::normalize_token` accepted Unicode confusables as
   new scope tokens, allowing a confusable surveillance declaration to reach
   `OUTSIDE_SCOPE`; non-ASCII tokens now return
   `INSUFFICIENT_INFORMATION` through the evaluator.
2. `src/red_line/oversight/findings.py::ReviewFinding` accepted an invalid
   `reviewed_on` value; review records and authorization dates now require ISO
   dates.
3. `src/red_line/evaluation/evaluator.py::evaluate_action` reported stale evidence but
   did not block when a fresh duplicate existed; any stale record now requires
   resolution, because an unresolved evidence ledger is not a clean intake.

The strongest remaining semantic risk is the gap between a declared label and
the actual work. Red Line fails closed when capability context is missing or
malformed, but a complete-looking evidence packet can still be wrong. The
package therefore describes `COMPLIANT` as “passes this documented local
review,” never as “safe.”

## Nation-state defensive control mapping

The mapping below is intentionally proportionate to a static private artifact.
“Current” means demonstrated by repository code or the acceptance run; it
does not mean independently witnessed.

| Asset | Threat technique | Current evidence | Coverage status |
|---|---|---|---|
| Registry semantics | `T1565.001` | `src/red_line/canary/hashing.py`, `src/red_line/canary/verification.py`, `scripts/check_canary.py`, committed fixture | local integrity and drift detection; not non-forgeability |
| Action intake | `T1078` / evidence laundering | typed records, statuses, freshness, negative controls in `tests/evaluation/` and `tests/model/` | local gate; not source-truth verification |
| Scope normalization | `T1027`-style masquerading pressure | NFKC + ASCII boundary, explicit aliases, normalized snapshots | blocks malformed input; does not infer semantics |
| Figure and manuscript outputs | `T1195.001`, `T1491.002` | deterministic SVG/PNG generation, registry, template validation, PDF/HTML inspection | source-to-output checks; renderer trust remains external |
| Private source boundary | `T1567`, `T1552.001` | no runtime secrets, reference marker/PII rejection, sidecar/template separation | no endpoint telemetry or DLP |
| Scholarship ledger | `T1565` | verified publisher/library/official URLs and transfer limits for all 45 sources; edition and locator fields for the 22 deepened sources only, with the other 23 marked `not recorded` and counted in `locator_coverage` | human source audit still required; a `not recorded` locator carries no per-source integrity signal |

The project does not run ATT&CK emulation, Atomic Red Team, Caldera, or a
production red-team engagement. Those exercises would require a separately
authorized system and crown-jewel scope; they must not be inferred from this
static review.

## Supply-chain and build posture

The project currently has a minimal, honest posture:

- runtime domain logic has no third-party dependencies;
- development dependencies are recorded in `pyproject.toml` and `uv.lock`;
- figures are generated from inspectable SVG source and rasterized locally;
- rendering is explicitly delegated to the sibling template checkout; and
- tests, canary, figure generation, output validation, and visual inspection
  are rerun as one publication gate.

This is not SLSA Level 3 or Level 4. There is no signed provenance, external
SBOM attestation, hermetic isolated builder, two-party release review, or
admission policy in this pass. Before a public release, the minimum supply
chain package should include:

1. a dependency and toolchain SBOM with versions and licenses;
2. provenance identifying source revision, builder, template revision, and
   generated artifact hashes;
3. an isolated render from a clean environment with network access disabled
   after dependencies are resolved;
4. signature or equivalent external timestamp for the release manifest and
   canary; and
5. an independent reviewer who compares source, output, and prior canary.

The [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final),
[NIST Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final),
and [SLSA](https://slsa.dev/spec/v1.2/) are implementation vocabularies for
that future release work. They are not evidence that Red Line is compliant
with a regulation or secure against an advanced persistent threat.

## Response and review cadence

If a source, renderer, dependency, canary, or output is suspected to be
compromised: stop publication; preserve the current source and generated
artifact hashes; isolate the changed checkout; compare against the last
independently held prior; rerun the verifier from a clean environment; and
record the finding before any successor canary is issued. Do not silently
regenerate a green artifact over a disputed one.

Re-review this model when the template checkout, render toolchain, dependency
lockfile, evidence schema, registry, or publication surface changes. A
quarterly review is a useful maintenance target, but an actual incident or
new release boundary takes precedence.
