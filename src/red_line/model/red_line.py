"""Red-line records, typed exemptions, and deterministic scope helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import TYPE_CHECKING
import unicodedata

from .enums import DeploymentTier, EvidenceKind, ExemptionMatchMode, Severity

if TYPE_CHECKING:
    from .action import ActionContext


SCOPE_ALIASES: dict[str, str] = {
    "weapon": "weapons",
    "weapon_system": "weapons",
    "weapon_systems": "weapons",
    "autonomous-weapons": "autonomous_weapon",
    "autonomous_weapons": "autonomous_weapon",
    "bulk-data": "bulk_data",
    "bulkdata": "bulk_data",
    "biometric-id": "biometric_id",
    "research-and-development": "research_development",
    "research_development": "research_development",
    "red-team": "red_team",
    "redteams": "red_team",
    "hand-offs": "handoff",
    "handoffs": "handoff",
    "open-source": "open_source",
    "opt-in": "opt_in",
    "opt-in-analytics": "opt_in_analytics",
    "vetted": "vetted_end_user",
    "not-applicable": "not_applicable",
}

UNKNOWN_SCOPE_MARKERS = frozenset({"unknown", "unspecified", "tbd", "unclear"})
_IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def normalize_token(token: str) -> str:
    """Canonicalize one declared scope token without heuristic stemming."""

    if not isinstance(token, str):
        raise TypeError("scope tokens must be strings")
    # NFKC folds full-width spellings, while the ASCII boundary rejects
    # homoglyphs that could otherwise make a dangerous declaration look like a
    # harmless new token (for example Cyrillic ``е`` in ``surveillancе``).
    canonical = unicodedata.normalize("NFKC", token).casefold()
    if not canonical.isascii():
        raise ValueError("scope tokens must be ASCII after Unicode normalization")
    cleaned = "".join(c if c.isalnum() else "_" for c in canonical).strip("_")
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return SCOPE_ALIASES.get(cleaned, cleaned)


def normalize_scope(scope: frozenset[str] | set[str] | tuple[str, ...]) -> frozenset[str]:
    """Return stable canonical scope tokens."""

    normalized: set[str] = set()
    for token in scope:
        canonical = normalize_token(token)
        if canonical:
            normalized.add(canonical)
    return frozenset(normalized)


@dataclass(frozen=True)
class Exemption:
    """A named, evidence-bearing narrowing of one red line.

    ``trigger_scope`` describes the explicit adjacent-use declaration.  It is
    never itself proof of the exemption; every kind in ``required_evidence``
    must have a ``VERIFIED`` record in the action context.
    """

    id: str
    description: str
    trigger_scope: frozenset[str]
    required_evidence: frozenset[EvidenceKind]
    match_mode: ExemptionMatchMode = ExemptionMatchMode.ANY

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("exemption id is required")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("exemption description is required")
        if not isinstance(self.trigger_scope, (frozenset, set, tuple)):
            raise TypeError("exemption trigger_scope must be a set-like collection")
        if not isinstance(self.required_evidence, (frozenset, set, tuple)):
            raise TypeError("exemption required_evidence must be a set-like collection")
        if any(not isinstance(token, str) for token in self.trigger_scope):
            raise TypeError("exemption trigger_scope tokens must be strings")
        if any(not isinstance(kind, EvidenceKind) for kind in self.required_evidence):
            raise TypeError("exemption required_evidence must contain EvidenceKind values")
        if not isinstance(self.match_mode, ExemptionMatchMode):
            raise TypeError("exemption match_mode must use ExemptionMatchMode")
        if not normalize_scope(frozenset(self.trigger_scope)):
            raise ValueError("exemption trigger_scope must contain a non-empty token")
        object.__setattr__(self, "trigger_scope", frozenset(self.trigger_scope))
        object.__setattr__(self, "required_evidence", frozenset(self.required_evidence))

    def matches(self, action_scope: frozenset[str]) -> bool:
        trigger = normalize_scope(self.trigger_scope)
        action = normalize_scope(action_scope)
        if self.match_mode is ExemptionMatchMode.ALL:
            return trigger <= action
        return bool(trigger & action)

    def satisfied(self, context: "ActionContext | None", as_of: date | None = None) -> bool:
        if context is None:
            return False
        return all(context.has_verified_evidence(kind, as_of) for kind in self.required_evidence)


@dataclass(frozen=True)
class RedLine:
    """One boundary the author will not cross.

    Attributes:
        id: Stable slug; unique within the registry.
        title: Short human-readable name.
        standard: The boundary itself — what MUST NOT happen.
        rationale: Why the line exists.
        scope: Keywords/domains the line covers (used by the evaluator).
        carve_outs: Explicit "does not restrict …" clauses (Turner's narrowing).
        max_tier: The most-released (least-oversight) tier at which work
            implicating this line may still be deployed. ``HOSTED`` is the
            strictest floor (never beyond the author's recall); ``AIR_GAPPED``
            means even release beyond recall is permitted.
        severity: How a breach is treated.
        stated_by: The person committing to this line — its provenance. A red line
            here is that author's revisable, first-person commitment, NOT a moral
            fact asserted by this framework or by any AI that helped author it.
        stated_on: ISO date the line was stated/last revised.
    """

    id: str
    title: str
    standard: str
    rationale: str
    scope: tuple[str, ...]
    carve_outs: tuple[str, ...]
    max_tier: DeploymentTier
    severity: Severity
    stated_by: str = "Daniel Ari Friedman"
    stated_on: str = "2026-07-15"
    exemptions: tuple[Exemption, ...] = ()

    def __post_init__(self) -> None:
        text_fields = (self.id, self.title, self.standard, self.rationale, self.stated_by, self.stated_on)
        if any(not isinstance(value, str) for value in text_fields):
            raise TypeError("red-line identifiers, prose, and provenance must be strings")
        if not self.id.strip() or not _IDENTIFIER.fullmatch(self.id):
            raise ValueError("red-line id must be a non-empty lowercase hyphenated identifier")
        if any(not value.strip() for value in (self.title, self.standard, self.rationale, self.stated_by)):
            raise ValueError("red-line title, standard, rationale, and stated_by are required")
        if not self.standard.lstrip().startswith("I "):
            raise ValueError("red-line standard must be a first-person commitment beginning with 'I '")
        try:
            date.fromisoformat(self.stated_on)
        except ValueError as exc:
            raise ValueError("red-line stated_on must be an ISO date") from exc
        if not isinstance(self.scope, (tuple, list, set, frozenset)):
            raise TypeError("red-line scope must be a collection of strings")
        if not isinstance(self.carve_outs, (tuple, list, set, frozenset)):
            raise TypeError("red-line carve_outs must be a collection of strings")
        if not isinstance(self.exemptions, (tuple, list, set, frozenset)):
            raise TypeError("red-line exemptions must be a collection of Exemption values")
        if any(not isinstance(token, str) or not normalize_token(token) for token in self.scope):
            raise ValueError("red-line scope must contain non-empty string tokens")
        if any(not isinstance(clause, str) or not clause.strip() for clause in self.carve_outs):
            raise ValueError("red-line carve_outs must contain non-empty strings")
        if any(not isinstance(exemption, Exemption) for exemption in self.exemptions):
            raise TypeError("red-line exemptions must contain Exemption values")
        if not isinstance(self.max_tier, DeploymentTier) or not isinstance(self.severity, Severity):
            raise TypeError("red-line max_tier and severity must use their declared enums")
        object.__setattr__(self, "scope", tuple(self.scope))
        object.__setattr__(self, "carve_outs", tuple(self.carve_outs))
        object.__setattr__(self, "exemptions", tuple(self.exemptions))

    def covers(self, action_scope: frozenset[str]) -> bool:
        """True if any of this line's scope keywords appears in an action's scope.

        Matching uses explicit canonical tokens and aliases. There is no
        heuristic plural or suffix stripping: a new synonym must be added to
        the reviewed alias table rather than silently widening a boundary.
        """
        return bool(normalize_scope(self.scope) & normalize_scope(action_scope))

    def matching_exemptions(self, action_scope: frozenset[str]) -> tuple[Exemption, ...]:
        """Return explicitly declared exemptions whose trigger is present."""

        return tuple(ex for ex in self.exemptions if ex.matches(action_scope))

    def satisfied_exemptions(
        self,
        action_scope: frozenset[str],
        context: "ActionContext | None",
        as_of: date | None = None,
    ) -> tuple[Exemption, ...]:
        """Return matching exemptions whose required evidence is verified."""

        return tuple(ex for ex in self.matching_exemptions(action_scope) if ex.satisfied(context, as_of))

    def carved_out(
        self,
        action_scope: frozenset[str],
        context: "ActionContext | None" = None,
    ) -> bool:
        """Compatibility helper: true only for an evidence-satisfied exemption."""

        return bool(self.satisfied_exemptions(action_scope, context))


# Function words that appear in carve-out *boilerplate* — every carve-out clause
# begins "Does not restrict …" — or as generic connectives. They carry no domain
# meaning, so they must never count as carve-out keywords: otherwise an action
# whose scope incidentally contains one (e.g. "not") would be silently treated as
# exempt from an implicated red line, a false-negative on the core evaluator.
_STOPWORDS: frozenset[str] = frozenset(
    {
        "does",
        "not",
        "restrict",
        "the",
        "and",
        "for",
        "nor",
        "but",
        "with",
        "own",
        "any",
        "all",
        "are",
        "was",
        "its",
        "this",
        "that",
        "who",
        "you",
        "your",
        "our",
        "per",
        "via",
        "may",
        "can",
        "will",
        "into",
        "from",
        "under",
        "over",
        "out",
        "has",
        "had",
        "have",
        "been",
        "being",
        "than",
    }
)


def _tokens(text: str) -> frozenset[str]:
    """Lowercased content tokens for documentation/invariant checks.

    Tokens of length ≤ 2 and common function words (:data:`_STOPWORDS`) are
    dropped so carve-out boilerplate ("Does not restrict …") and connectives
    cannot be mistaken for domain carve-out keywords.
    """
    cleaned = "".join(c.lower() if c.isalnum() else " " for c in text)
    return frozenset(t for t in cleaned.split() if len(t) > 2 and t not in _STOPWORDS)
