"""Executed probe of ANY versus ALL exemption trigger matching.

:class:`~red_line.model.enums.ExemptionMatchMode` is the smallest piece of
policy in the registry and the easiest to state wrongly in prose: an ``ANY``
exemption fires when *one* declared trigger token is present, an ``ALL``
exemption only when *every* one is. The difference decides whether a narrowing
condition can be reached by naming a single convenient word.

This module runs that difference rather than asserting it. For every typed
exemption in the registry it evaluates two things:

* the structural predicate :meth:`~red_line.model.red_line.Exemption.matches`
  against each trigger token alone and against the full trigger set; and
* the real :func:`~red_line.evaluation.evaluator.evaluate_action` on an action
  that declares an *anchor* — one of the owning line's own scope tokens, so the
  line is genuinely implicated — plus that same token subset.

The anchor is chosen deterministically as the line's alphabetically first scope
token declared by no other line, falling back to its first token overall. The
fallback is recorded on the row: a shared anchor implicates a second line whose
exemptions are evaluated on their own terms, so the executed verdict for such a
row reports the pair, not the exemption under test.

Design rules, matching the rest of :mod:`red_line.analysis`: zero I/O,
deterministic ordering, fail-closed validation, and no change to registry
content, evaluator semantics, or enum vocabulary.

Trigger semantics are a property of the local decision procedure. A matched
trigger is a declaration, never proof: the exemption still cannot narrow its
line until its typed evidence requirements are verified.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..evaluation import evaluate_action
from ..model import (
    Classification,
    DeploymentTier,
    Exemption,
    ExemptionMatchMode,
    ProposedAction,
    RedLine,
)
from ..model.red_line import normalize_scope
from ..registry import PERSONAL_RED_LINES
from .outcome_coverage import BATTERY_AS_OF, _verified_context
from .registry_metrics import scope_token_membership

#: Tier every probe runs at. Held fixed at the most-oversight tier so a tier
#: floor never becomes the reason a row's verdict changed.
PROBE_TIER: DeploymentTier = DeploymentTier.HOSTED


def _anchor_for(line: RedLine, owners: dict[str, tuple[str, ...]]) -> tuple[str, bool]:
    """Pick the scope token used to implicate ``line``, and say if it is shared."""

    tokens = sorted(normalize_scope(line.scope))
    if not tokens:
        raise ValueError(f"{line.id}: a zero-scope line cannot be implicated by any probe")
    solo = [token for token in tokens if len(owners.get(token, (line.id,))) == 1]
    if solo:
        return solo[0], False
    return tokens[0], True


@dataclass(frozen=True)
class TriggerProbe:
    """One executed probe of one token subset against one exemption.

    Attributes:
        tokens: The trigger tokens declared alongside the anchor, sorted.
        matched: What :meth:`Exemption.matches` returned for those tokens.
        reached: The classification the real evaluator returned.
    """

    tokens: tuple[str, ...]
    matched: bool
    reached: Classification


@dataclass(frozen=True)
class TriggerRow:
    """Structural and executed trigger behaviour for one typed exemption.

    Attributes:
        line_id: Owning red line's stable id.
        exemption_id: The exemption's stable id.
        match_mode: ``any`` or ``all``.
        trigger_scope: Canonical trigger tokens, sorted.
        anchor: The owning line's scope token the probes declare.
        anchor_shared: True when that anchor is also declared by another line.
        singles: One probe per trigger token declared alone.
        full: The probe declaring every trigger token at once.
        single_match_count: How many single-token probes the predicate matched.
        mode_consistent: True when the row behaves as its mode requires — an
            ``ANY`` row matches on every single token, an ``ALL`` row on none of
            them when it has more than one token, and every row matches on the
            full set.
    """

    line_id: str
    exemption_id: str
    match_mode: str
    trigger_scope: tuple[str, ...]
    anchor: str
    anchor_shared: bool
    singles: tuple[TriggerProbe, ...]
    full: TriggerProbe
    single_match_count: int
    mode_consistent: bool


@dataclass(frozen=True)
class TriggerSemanticsReport:
    """Aggregate report for one trigger-semantics sweep.

    Attributes:
        as_of: ISO review date every evaluation used.
        tier: The tier every probe ran at.
        rows: Per-exemption rows sorted by (line id, exemption id).
        any_mode_count: Rows whose exemption matches with ``ANY`` semantics.
        all_mode_count: Rows whose exemption requires ``ALL`` trigger tokens.
        evaluation_count: Real ``evaluate_action`` runs performed.
        consistent: True when every row is mode-consistent and rows exist.
    """

    as_of: str
    tier: DeploymentTier
    rows: tuple[TriggerRow, ...]
    any_mode_count: int
    all_mode_count: int
    evaluation_count: int
    consistent: bool


def _probe(
    exemption: Exemption,
    anchor: str,
    tokens: tuple[str, ...],
    lines: tuple[RedLine, ...],
    as_of: str,
) -> TriggerProbe:
    """Run one token subset through both the predicate and the real evaluator."""

    declared = frozenset(tokens)
    action = ProposedAction(
        description=f"trigger-semantics probe for {exemption.id}",
        scope=frozenset({anchor}) | declared,
        context=_verified_context(as_of),
        tier=PROBE_TIER,
    )
    return TriggerProbe(
        tokens=tuple(sorted(tokens)),
        matched=exemption.matches(declared),
        reached=evaluate_action(action, lines, as_of=as_of).classification,
    )


def run_trigger_semantics(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
    as_of: str = BATTERY_AS_OF,
) -> TriggerSemanticsReport:
    """Probe every exemption with one trigger token at a time, then with all.

    Each probe uses a fully evidenced fixture intake, so the only variable is
    which trigger tokens the action declares. A future change that let a single
    token satisfy an ``ALL``-mode exemption surfaces here as a row with
    ``mode_consistent`` False, never as a silent pass.
    """

    if not isinstance(as_of, str):
        raise TypeError("as_of must be an ISO date string")
    date.fromisoformat(as_of)  # fail closed on malformed review dates
    if not isinstance(lines, (tuple, list)):
        raise TypeError("lines must be a tuple or list of RedLine values")
    for line in lines:
        if not isinstance(line, RedLine):
            raise TypeError("lines must contain only RedLine values")

    registry = tuple(lines)
    owners = dict(scope_token_membership(registry))
    rows: list[TriggerRow] = []
    evaluation_count = 0
    for line in sorted(registry, key=lambda entry: entry.id):
        anchor, anchor_shared = _anchor_for(line, owners)
        for exemption in sorted(line.exemptions, key=lambda entry: entry.id):
            trigger = tuple(sorted(normalize_scope(exemption.trigger_scope)))
            singles = tuple(
                _probe(exemption, anchor, (token,), registry, as_of) for token in trigger
            )
            full = _probe(exemption, anchor, trigger, registry, as_of)
            evaluation_count += len(singles) + 1
            single_matches = sum(1 for probe in singles if probe.matched)
            if exemption.match_mode is ExemptionMatchMode.ALL:
                expected_singles = len(trigger) if len(trigger) == 1 else 0
            else:
                expected_singles = len(trigger)
            rows.append(
                TriggerRow(
                    line_id=line.id,
                    exemption_id=exemption.id,
                    match_mode=exemption.match_mode.value,
                    trigger_scope=trigger,
                    anchor=anchor,
                    anchor_shared=anchor_shared,
                    singles=singles,
                    full=full,
                    single_match_count=single_matches,
                    mode_consistent=single_matches == expected_singles and full.matched,
                )
            )

    rows.sort(key=lambda row: (row.line_id, row.exemption_id))
    return TriggerSemanticsReport(
        as_of=as_of,
        tier=PROBE_TIER,
        rows=tuple(rows),
        any_mode_count=sum(1 for row in rows if row.match_mode == ExemptionMatchMode.ANY.value),
        all_mode_count=sum(1 for row in rows if row.match_mode == ExemptionMatchMode.ALL.value),
        evaluation_count=evaluation_count,
        consistent=bool(rows) and all(row.mode_consistent for row in rows),
    )
