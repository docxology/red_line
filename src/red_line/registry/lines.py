"""Personal red-line registry, model, and action evaluator.

This module is the *beacon*: a structured, versioned articulation of the
boundaries the author will not cross while developing open-source software,
proprietary modeling, and cognitive-security / intelligence products.

It adapts the *mechanism* of Alex Turner's "A Red Line and Oversight Framework
for Government AI Contracts" (https://turntrout.com/red-line-framework,
2026-07-15) from an organization-selling-to-governments to a single
practitioner governing his own work. Turner's two narrow Standards, tiered
deployment architecture, and review classification are the substrate-independent
core reused here; only the subject changes.

Design rule (mirrors the ``template_code_project`` lineage): this package is
infrastructure-independent — it MUST NOT import ``infrastructure.*``. It is pure
domain logic with deterministic behaviour and no I/O.
"""

from __future__ import annotations

from ..model.enums import DeploymentTier, EvidenceKind, ExemptionMatchMode, Severity
from ..model.red_line import Exemption, RedLine

SOURCE_FRAMEWORK = "Alex Turner, A Red Line and Oversight Framework for Government AI Contracts"
SOURCE_URL = "https://turntrout.com/red-line-framework"
SOURCE_DATE = "2026-07-15"

# --------------------------------------------------------------------------- #
# The registry — the author's personal red lines. Versioned and revisable.
#
# PROVENANCE: every line below is Daniel Ari Friedman's first-person, dated,
# revisable commitment (see each RedLine.stated_by / stated_on). None is a moral
# fact asserted by this framework. The set is the author's CURRENT and
# NON-EXHAUSTIVE selection, not a canonical or complete ethics.
#
# Standard-1 analog (S1): human control over harm-capable systems.
# Standard-2 analog (S2): no untargeted profiling / mass surveillance.
# --------------------------------------------------------------------------- #
REGISTRY_IS_EXHAUSTIVE = False  # the author may add lines; absence ≠ endorsement
PERSONAL_RED_LINES: tuple[RedLine, ...] = (
    RedLine(
        id="s1-human-control-force",
        title="Human control over force and harm-capable systems",
        standard=(
            "I will not build, tune, or knowingly supply a component to a system "
            "that selects and engages targets for force without appropriate human "
            "control over each engagement."
        ),
        rationale=(
            "Turner Standard 1: force-application without an identifiable, "
            "accountable human decision-maker removes the moral circuit-breaker. "
            "Applies whether I provide targeting directly or as a component."
        ),
        scope=("targeting", "weapons", "lethality", "force", "kinetic", "autonomous_weapon"),
        carve_outs=(
            "Does not restrict defensive-only alerting with a human in the loop",
            "Does not restrict logistics, translation, maintenance, or research and development",
            "Does not restrict intelligence analysis reviewed by an accountable human",
        ),
        exemptions=(
            Exemption(
                id="defensive-alerting-human-control",
                description="Defensive-only alerting with an accountable human decision-maker",
                trigger_scope=frozenset({"defensive_alerting", "human_in_loop"}),
                required_evidence=frozenset({EvidenceKind.HUMAN_CONTROL, EvidenceKind.END_USE}),
                match_mode=ExemptionMatchMode.ALL,
            ),
            Exemption(
                id="adjacent-force-support",
                description="Logistics, translation, maintenance, research, or intelligence analysis",
                trigger_scope=frozenset(
                    {
                        "logistics",
                        "translation",
                        "maintenance",
                        "research",
                        "research_development",
                        "intelligence_analysis",
                    }
                ),
                required_evidence=frozenset({EvidenceKind.PURPOSE, EvidenceKind.HUMAN_CONTROL}),
            ),
        ),
        max_tier=DeploymentTier.HOSTED,
        severity=Severity.CANARY,
    ),
    RedLine(
        id="s2-untargeted-profiling",
        title="No untargeted profiling or mass surveillance",
        standard=(
            "I will not build tooling whose purpose is to convert bulk data into "
            "individualized intelligence on persons not already identified as "
            "subjects of a specific, lawful, individualized process."
        ),
        rationale=(
            "Turner Standard 2: bulk-to-individual inference on unnamed persons is "
            "the engine of mass surveillance. Demographic-, origin-, or "
            "belief-based initiation is prohibited outright."
        ),
        scope=("surveillance", "profiling", "bulk_data", "biometric_id", "dragnet", "tracking"),
        carve_outs=(
            "Does not restrict aggregate research producing no individualized output",
            "Does not restrict analysis of an already-identified, lawfully specified subject",
            "Does not restrict consented, opt-in personal analytics",
        ),
        exemptions=(
            Exemption(
                id="aggregate-research",
                description="Aggregate research producing no individualized output",
                trigger_scope=frozenset({"aggregate_research", "research"}),
                required_evidence=frozenset(
                    {EvidenceKind.PURPOSE, EvidenceKind.AFFECTED_PARTIES, EvidenceKind.DATA_PROVENANCE}
                ),
            ),
            Exemption(
                id="identified-lawful-subject",
                description="Analysis of an already-identified, lawfully specified subject",
                trigger_scope=frozenset({"identified_subject", "lawful_subject"}),
                required_evidence=frozenset({EvidenceKind.AFFECTED_PARTIES, EvidenceKind.LEGAL_BASIS}),
                match_mode=ExemptionMatchMode.ALL,
            ),
            Exemption(
                id="opt-in-personal-analytics",
                description="Consent-based opt-in personal analytics",
                trigger_scope=frozenset({"opt_in_analytics", "consented_analytics"}),
                required_evidence=frozenset(
                    {EvidenceKind.AFFECTED_PARTIES, EvidenceKind.DATA_PROVENANCE, EvidenceKind.LEGAL_BASIS}
                ),
            ),
        ),
        max_tier=DeploymentTier.CONNECTED,
        severity=Severity.CANARY,
    ),
    RedLine(
        id="dual-use-ablation",
        title="Scoped release of dual-use models",
        standard=(
            "I will not release a proprietary or handed-off model beyond my recall "
            "(air-gapped) while it retains dangerous dual-use capability that has "
            "not been ablated below a repurposing-cost threshold."
        ),
        rationale=(
            "Turner Tier 3: for work released beyond monitoring, the cost of "
            "repurposing a scoped model should exceed the value of doing so."
        ),
        # Scope names the prohibited ACT (release beyond recall), not the mere
        # possession of dual-use capability — hosted/connected dual-use work
        # under retained oversight is not what this line forbids.
        scope=("model_release", "weights", "handoff"),
        carve_outs=(
            "Does not restrict release of task-specific models with capability removed",
            "Does not restrict open publication of methods, papers, or benchmarks",
            "Does not restrict hosted or connected tiers under retained oversight",
        ),
        exemptions=(
            Exemption(
                id="ablated-task-specific",
                description="Task-specific release with dangerous capability removed",
                trigger_scope=frozenset({"task_specific", "ablated"}),
                required_evidence=frozenset({EvidenceKind.CAPABILITY_SCOPE, EvidenceKind.DEPLOYMENT}),
            ),
            Exemption(
                id="methods-not-weights",
                description="Open methods, papers, or benchmark publication without dangerous weights",
                trigger_scope=frozenset({"methods", "paper", "benchmark"}),
                required_evidence=frozenset(
                    {EvidenceKind.CAPABILITY_SCOPE, EvidenceKind.DOWNSTREAM_TRANSFER}
                ),
            ),
            Exemption(
                id="retained-oversight",
                description="Hosted or connected work under retained oversight",
                trigger_scope=frozenset({"hosted", "connected"}),
                required_evidence=frozenset({EvidenceKind.DEPLOYMENT, EvidenceKind.HUMAN_CONTROL}),
            ),
        ),
        max_tier=DeploymentTier.AIR_GAPPED,
        severity=Severity.STRONG,
    ),
    RedLine(
        id="cogsec-integrity",
        title="Cognitive security strengthens, never degrades, the epistemic commons",
        standard=(
            "I will not build cognitive-security tooling whose function is to "
            "manufacture deception, run covert influence operations, or degrade a "
            "population's shared ability to reason."
        ),
        rationale=(
            "My cognitive-security work is defensive by definition: it strengthens "
            "information ecosystems. Weaponized persuasion inverts that mission."
        ),
        scope=("influence_ops", "disinformation", "manipulation", "propaganda", "deception", "cogsec"),
        carve_outs=(
            "Does not restrict detection, red-teaming, or defensive analysis of influence operations",
            "Does not restrict education, media-literacy, or transparency tooling",
        ),
        exemptions=(
            Exemption(
                id="defensive-cognitive-security",
                description="Detection, red-teaming, or defensive analysis",
                trigger_scope=frozenset({"detection", "red_team", "defensive_analysis"}),
                required_evidence=frozenset(
                    {EvidenceKind.PURPOSE, EvidenceKind.END_USE, EvidenceKind.HUMAN_CONTROL}
                ),
            ),
            Exemption(
                id="epistemic-education",
                description="Education, media literacy, or transparency tooling",
                trigger_scope=frozenset({"education", "media_literacy", "transparency"}),
                required_evidence=frozenset({EvidenceKind.PURPOSE, EvidenceKind.AFFECTED_PARTIES}),
            ),
        ),
        max_tier=DeploymentTier.CONNECTED,
        severity=Severity.ABSOLUTE,
    ),
    RedLine(
        id="provenance-and-consent",
        title="Provenance and consent for data and identity",
        standard=(
            "I will not train, evaluate, or ship on data acquired without a lawful "
            "basis and, where persons are involved, without consent or a legitimate "
            "public-interest basis."
        ),
        rationale=(
            "Turner's 'acquisition' clause: any process by which person data enters "
            "my systems is covered regardless of how a source labels it."
        ),
        scope=("data_acquisition", "scraping", "pii", "consent", "provenance"),
        carve_outs=(
            "Does not restrict public-domain, openly-licensed, or synthetic data",
            "Does not restrict my own or explicitly-consented personal data",
        ),
        exemptions=(
            Exemption(
                id="public-open-synthetic-data",
                description="Public-domain, openly licensed, or synthetic data",
                trigger_scope=frozenset({"public_domain", "open_license", "synthetic"}),
                required_evidence=frozenset({EvidenceKind.DATA_PROVENANCE, EvidenceKind.LEGAL_BASIS}),
            ),
            Exemption(
                id="own-consented-data",
                description="Author-owned or explicitly consented personal data",
                trigger_scope=frozenset({"own_data", "explicit_consent", "consented_data"}),
                required_evidence=frozenset(
                    {EvidenceKind.DATA_PROVENANCE, EvidenceKind.LEGAL_BASIS, EvidenceKind.AFFECTED_PARTIES}
                ),
            ),
        ),
        max_tier=DeploymentTier.HOSTED,
        severity=Severity.STRONG,
    ),
    RedLine(
        id="open-science-good-faith",
        title="Open-science claims are honest and reproducible",
        standard=(
            "I will not publish a result, metric, or capability claim I have not "
            "verified against a reproducible artifact, nor let proprietary interest "
            "launder an unverified claim into the public record."
        ),
        rationale=(
            "My public research graph is a beacon only if its claims bind to code "
            "that runs. Overclaiming corrodes the commons I am trying to build."
        ),
        scope=("publication", "benchmark_claim", "metric", "reproducibility", "provenance"),
        carve_outs=(
            "Does not restrict clearly-labeled preliminary, hypothesis, or negative results",
            "Does not restrict withholding proprietary detail while stating what is withheld",
        ),
        exemptions=(
            Exemption(
                id="clearly-labeled-preliminary",
                description="Clearly labeled preliminary, hypothesis, or negative result",
                trigger_scope=frozenset({"preliminary", "hypothesis", "negative_result"}),
                required_evidence=frozenset({EvidenceKind.PURPOSE, EvidenceKind.CAPABILITY_SCOPE}),
            ),
            Exemption(
                id="stated-withholding",
                description="Withheld proprietary detail explicitly identified",
                trigger_scope=frozenset({"withheld_detail", "proprietary_detail"}),
                required_evidence=frozenset(
                    {EvidenceKind.CAPABILITY_SCOPE, EvidenceKind.DOWNSTREAM_TRANSFER}
                ),
            ),
        ),
        max_tier=DeploymentTier.AIR_GAPPED,
        severity=Severity.STRONG,
    ),
    RedLine(
        id="downstream-transfer",
        title="No knowing transfer to a violating end use",
        standard=(
            "I will not sell, license, or hand off work where I know or have "
            "substantial reason to believe it will be re-transferred to an end use "
            "that violates any of these red lines."
        ),
        rationale=(
            "Turner's downstream-transfer and 'knows or has substantial reason to "
            "believe' clauses: flow-down of the substantive boundary, not just the box."
        ),
        scope=("resale", "sublicense", "integration", "downstream", "handoff"),
        carve_outs=(
            "Does not restrict transfer to a vetted end user with a flow-down commitment",
            "Does not restrict fully open-source release under a license that itself binds no end use",
        ),
        exemptions=(
            Exemption(
                id="vetted-flow-down",
                description="Transfer to a vetted end user with a flow-down commitment",
                trigger_scope=frozenset({"vetted_end_user", "flow_down"}),
                required_evidence=frozenset(
                    {
                        EvidenceKind.DOWNSTREAM_TRANSFER,
                        EvidenceKind.LEGAL_BASIS,
                        EvidenceKind.AFFECTED_PARTIES,
                    }
                ),
                match_mode=ExemptionMatchMode.ALL,
            ),
            Exemption(
                id="open-source-no-end-use-binding",
                description="Open-source release whose license does not bind end use",
                trigger_scope=frozenset({"open_source_no_end_use", "open_source"}),
                required_evidence=frozenset(
                    {EvidenceKind.DOWNSTREAM_TRANSFER, EvidenceKind.CAPABILITY_SCOPE}
                ),
            ),
        ),
        max_tier=DeploymentTier.CONNECTED,
        severity=Severity.STRONG,
    ),
)
