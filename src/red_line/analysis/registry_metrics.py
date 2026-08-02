"""Registry analytics: pure derivations over the personal red-line registry.

Every function here is a read-only summarizer over ``tuple[RedLine, ...]``.
The registry itself remains the single source of truth; these views exist so
the manuscript can state registry composition (exemption evidence demands,
severity and tier-floor distributions, scope-token reuse) as derived numbers
rather than hand-maintained prose.

Design rules, matching :mod:`red_line.invariants.checks`:

* zero I/O and no ``infrastructure.*`` imports;
* deterministic output ordering (sorted by stable identifiers or enum
  definition order);
* fail-closed input validation — a non-``RedLine`` entry raises rather than
  being silently skipped.

None of these summaries is a safety score or a compliance measurement. A
count of required evidence kinds describes the *shape* of a boundary, not the
strength, correctness, or moral standing of the person committing to it.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..model import DeploymentTier, EvidenceKind, ExemptionMatchMode, RedLine, Severity
from ..model.red_line import normalize_scope
from ..registry import PERSONAL_RED_LINES

#: Column order for every evidence matrix: enum definition order, which is the
#: intake-dimension order used by :class:`red_line.model.action.ActionContext`.
EVIDENCE_KIND_COLUMNS: tuple[EvidenceKind, ...] = tuple(EvidenceKind)


def _require_lines(lines: tuple[RedLine, ...]) -> tuple[RedLine, ...]:
    """Validate the input collection fail-closed and return it as a tuple."""

    if not isinstance(lines, (tuple, list)):
        raise TypeError("lines must be a tuple or list of RedLine values")
    for line in lines:
        if not isinstance(line, RedLine):
            raise TypeError("lines must contain only RedLine values")
    return tuple(lines)


@dataclass(frozen=True)
class ExemptionEvidenceRow:
    """One exemption's typed evidence requirements, as a matrix row.

    Attributes:
        line_id: Owning red line's stable id.
        exemption_id: The exemption's stable id (unique across the registry).
        match_mode: ``any`` or ``all`` — how the trigger scope is matched.
        trigger_scope: Canonicalized, sorted trigger tokens.
        required: Per-column booleans aligned with
            :data:`EVIDENCE_KIND_COLUMNS` — True where the exemption requires
            a VERIFIED record of that kind.
    """

    line_id: str
    exemption_id: str
    match_mode: str
    trigger_scope: tuple[str, ...]
    required: tuple[bool, ...]

    @property
    def required_kinds(self) -> tuple[EvidenceKind, ...]:
        """The evidence kinds this exemption requires, in column order."""

        return tuple(kind for kind, needed in zip(EVIDENCE_KIND_COLUMNS, self.required) if needed)

    @property
    def required_count(self) -> int:
        """Number of distinct evidence kinds the exemption requires."""

        return sum(self.required)


def exemption_evidence_matrix(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> tuple[ExemptionEvidenceRow, ...]:
    """Derive the exemption × evidence-kind coverage matrix.

    Rows are every typed exemption in the registry, sorted by
    ``(line_id, exemption_id)``; columns are the nine
    :class:`~red_line.model.enums.EvidenceKind` values in intake order. A True
    cell means the exemption can only narrow its line when a VERIFIED record
    of that kind is present in the action context.
    """

    rows: list[ExemptionEvidenceRow] = []
    for line in _require_lines(lines):
        for exemption in line.exemptions:
            rows.append(
                ExemptionEvidenceRow(
                    line_id=line.id,
                    exemption_id=exemption.id,
                    match_mode=exemption.match_mode.value,
                    trigger_scope=tuple(sorted(normalize_scope(exemption.trigger_scope))),
                    required=tuple(kind in exemption.required_evidence for kind in EVIDENCE_KIND_COLUMNS),
                )
            )
    return tuple(sorted(rows, key=lambda row: (row.line_id, row.exemption_id)))


def evidence_kind_demand(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> dict[EvidenceKind, int]:
    """Count, per evidence kind, how many exemptions require it.

    Every kind appears as a key (zero-demand kinds included) so the result is
    a complete profile of which intake dimensions the registry's exemptions
    actually lean on.
    """

    demand: dict[EvidenceKind, int] = {kind: 0 for kind in EVIDENCE_KIND_COLUMNS}
    for row in exemption_evidence_matrix(lines):
        for kind in row.required_kinds:
            demand[kind] += 1
    return demand


def unevidenced_exemptions(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> tuple[ExemptionEvidenceRow, ...]:
    """Return matrix rows whose exemption requires NO evidence kind at all.

    An exemption with an empty ``required_evidence`` set would be satisfied by
    any matching declaration — a free pass. On the real registry this must be
    empty; a non-empty result is a planted or drifted registry and the
    companion invariant (``check_typed_exemptions``) fails on the same input.
    """

    return tuple(row for row in exemption_evidence_matrix(lines) if row.required_count == 0)


@dataclass(frozen=True)
class LineSummary:
    """Structural composition of a single red line (no prose judgment).

    Attributes:
        line_id: Stable id.
        severity: Severity enum value string (``canary``/``absolute``/``strong``).
        max_tier: Tier-floor enum value string.
        scope_size: Number of canonical scope tokens.
        carve_out_count: Number of narrative carve-out clauses.
        exemption_count: Number of typed executable exemptions.
        any_mode_count: Exemptions matched with ``ANY`` trigger semantics.
        all_mode_count: Exemptions matched with ``ALL`` trigger semantics.
        evidence_kinds_used: Union of evidence kinds across the line's
            exemptions, in intake order.
        stated_on: ISO provenance date of the line.
    """

    line_id: str
    severity: str
    max_tier: str
    scope_size: int
    carve_out_count: int
    exemption_count: int
    any_mode_count: int
    all_mode_count: int
    evidence_kinds_used: tuple[EvidenceKind, ...]
    stated_on: str


def line_summaries(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> tuple[LineSummary, ...]:
    """Summarize each line's structural composition, sorted by line id."""

    summaries: list[LineSummary] = []
    for line in _require_lines(lines):
        used = {kind for exemption in line.exemptions for kind in exemption.required_evidence}
        summaries.append(
            LineSummary(
                line_id=line.id,
                severity=line.severity.value,
                max_tier=line.max_tier.value,
                scope_size=len(normalize_scope(line.scope)),
                carve_out_count=len(line.carve_outs),
                exemption_count=len(line.exemptions),
                any_mode_count=sum(
                    1 for exemption in line.exemptions if exemption.match_mode is ExemptionMatchMode.ANY
                ),
                all_mode_count=sum(
                    1 for exemption in line.exemptions if exemption.match_mode is ExemptionMatchMode.ALL
                ),
                evidence_kinds_used=tuple(kind for kind in EVIDENCE_KIND_COLUMNS if kind in used),
                stated_on=line.stated_on,
            )
        )
    return tuple(sorted(summaries, key=lambda summary: summary.line_id))


def severity_distribution(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> dict[Severity, int]:
    """Count lines per severity grade; every grade appears as a key."""

    distribution: dict[Severity, int] = {severity: 0 for severity in Severity}
    for line in _require_lines(lines):
        distribution[line.severity] += 1
    return distribution


def tier_floor_distribution(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> dict[DeploymentTier, int]:
    """Count lines per tier floor (``max_tier``); every tier appears as a key."""

    distribution: dict[DeploymentTier, int] = {tier: 0 for tier in DeploymentTier}
    for line in _require_lines(lines):
        distribution[line.max_tier] += 1
    return distribution


def scope_token_frequency(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> dict[str, int]:
    """Count, per canonical scope token, how many lines' coverage includes it.

    Tokens shared by two or more lines mark the registry's overlap points:
    an action declaring such a token implicates multiple boundaries at once.
    Keys are sorted canonical tokens for deterministic iteration order.
    """

    frequency: dict[str, int] = {}
    for line in _require_lines(lines):
        for token in normalize_scope(line.scope):
            frequency[token] = frequency.get(token, 0) + 1
    return dict(sorted(frequency.items()))


def scope_token_membership(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Map every canonical scope token to the ids of the lines declaring it.

    :func:`scope_token_frequency` answers *how many* lines share a token;
    this answers *which*, which is the part a reader needs to see the
    consequence. An action declaring a shared token implicates every line in
    its tuple simultaneously, so one line's verified exemption cannot clear
    it — the other line is evaluated on its own terms.

    Ordering is fully sorted (tokens, then ids within each token) so a caller
    can write the result straight into a deterministic artefact without
    re-sorting. No set or dict iteration order reaches the output.
    """

    owners: dict[str, set[str]] = {}
    for line in _require_lines(lines):
        for token in normalize_scope(line.scope):
            owners.setdefault(token, set()).add(line.id)
    return tuple((token, tuple(sorted(ids))) for token, ids in sorted(owners.items()))
