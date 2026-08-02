"""Tier-monotonicity sweep: exercise the evaluator's strictness lattice.

The manuscript claims the evaluator is *monotonic in danger*: for any fixed
declared scope, reducing retained oversight (``HOSTED`` → ``CONNECTED`` →
``AIR_GAPPED``) can never soften the verdict. This module turns that claim
into an exercised property in the same spirit as
:mod:`red_line.analysis.outcome_coverage`: every scope keyword of every
current red line is run through the real
:func:`~red_line.evaluation.evaluator.evaluate_action` (no stand-ins, no
patched internals) at all three deployment tiers, and the report records the
verdict lattice actually returned.

Design rules, matching the rest of :mod:`red_line.analysis`:

* zero I/O; deterministic ordering (line id, then keyword);
* fail-closed validation — a malformed review date or an off-lattice verdict
  raises instead of being silently coerced;
* no change to registry content, evaluator semantics, or enum vocabulary.

Monotonicity is a consistency property of the local decision procedure. It is
NOT evidence that any tier is safe, that a hosted deployment is reviewed, or
that the lexical scope tokens describe a real capability truthfully.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..evaluation import evaluate_action
from ..model import Classification, DeploymentTier, ProposedAction, RedLine
from ..registry import PERSONAL_RED_LINES
from .outcome_coverage import BATTERY_AS_OF, _verified_context

#: Deployment tiers ordered by descending retained oversight. The sweep runs
#: every keyword at each tier in this order, so a monotone row reads
#: most-oversight → least-oversight with non-decreasing strictness.
TIERS_BY_DESCENDING_OVERSIGHT: tuple[DeploymentTier, ...] = (
    DeploymentTier.HOSTED,
    DeploymentTier.CONNECTED,
    DeploymentTier.AIR_GAPPED,
)

#: Strictness rank of the three policy verdicts a fully evidenced,
#: line-implicating intake can reach. Higher is stricter.
STRICTNESS_ORDER: dict[Classification, int] = {
    Classification.COMPLIANT: 0,
    Classification.REQUIRES_MODIFICATION: 1,
    Classification.NON_COMPLIANT: 2,
}


def strictness_is_monotone(verdicts: tuple[Classification, ...]) -> bool:
    """True when strictness never decreases along a descending-oversight row.

    Fails closed: a verdict outside the policy triple (``COMPLIANT`` /
    ``REQUIRES_MODIFICATION`` / ``NON_COMPLIANT``) raises ``ValueError``
    rather than being ranked arbitrarily, because an intake gate stop or an
    out-of-scope result has no place on the strictness lattice.
    """

    ranks: list[int] = []
    for verdict in verdicts:
        if verdict not in STRICTNESS_ORDER:
            raise ValueError(f"verdict {verdict!r} is outside the policy strictness lattice")
        ranks.append(STRICTNESS_ORDER[verdict])
    return ranks == sorted(ranks)


@dataclass(frozen=True)
class KeywordStrictnessRow:
    """The evaluator's verdicts for one scope keyword across all tiers.

    Attributes:
        line_id: Owning red line's stable id.
        keyword: The canonical scope keyword swept.
        verdicts: Verdicts aligned with
            :data:`TIERS_BY_DESCENDING_OVERSIGHT`.
        monotone: True when strictness never decreases as oversight drops.
    """

    line_id: str
    keyword: str
    verdicts: tuple[Classification, ...]
    monotone: bool


@dataclass(frozen=True)
class MonotonicityReport:
    """Aggregate strictness-lattice report for one sweep.

    Attributes:
        as_of: ISO review date every evaluation used.
        tiers: Tier order shared by every row's ``verdicts``.
        rows: Per-keyword rows sorted by (line id, keyword).
        keyword_count: Number of (line, keyword) *slots* swept (== len(rows)).
            A keyword declared by two lines is swept once per line, so this is
            larger than the vocabulary size whenever lines share a token.
        distinct_keyword_count: Number of distinct canonical tokens swept.
            Equals ``keyword_count`` only when no two lines share a token;
            calling the slot count "keywords" is the drift this field exists
            to make impossible.
        evaluation_count: Real ``evaluate_action`` runs performed.
        inversion_count: Rows where a lower-oversight tier softened the
            verdict; zero on a monotone evaluator.
        monotone: True when ``inversion_count`` is zero and rows exist.
    """

    as_of: str
    tiers: tuple[DeploymentTier, ...]
    rows: tuple[KeywordStrictnessRow, ...]
    keyword_count: int
    distinct_keyword_count: int
    evaluation_count: int
    inversion_count: int
    monotone: bool


def run_monotonicity_sweep(
    lines: tuple[RedLine, ...] = PERSONAL_RED_LINES,
    as_of: str = BATTERY_AS_OF,
) -> MonotonicityReport:
    """Sweep every line's every scope keyword through all deployment tiers.

    Each evaluation uses a fully evidenced fixture intake (the same
    ``_verified_context`` the outcome-coverage battery uses), so the only
    variable across a row is retained oversight. The function analyses the
    real evaluator; a future inversion regression surfaces here as a nonzero
    ``inversion_count`` and ``monotone`` False, never as a silent pass.
    """

    if not isinstance(as_of, str):
        raise TypeError("as_of must be an ISO date string")
    date.fromisoformat(as_of)  # fail closed on malformed review dates
    if not isinstance(lines, (tuple, list)):
        raise TypeError("lines must be a tuple or list of RedLine values")
    for line in lines:
        if not isinstance(line, RedLine):
            raise TypeError("lines must contain only RedLine values")

    rows: list[KeywordStrictnessRow] = []
    evaluation_count = 0
    for line in sorted(lines, key=lambda entry: entry.id):
        for keyword in sorted(line.scope):
            verdicts = []
            for tier in TIERS_BY_DESCENDING_OVERSIGHT:
                action = ProposedAction(
                    description=f"monotonicity sweep fixture for {keyword}",
                    scope=frozenset({keyword}),
                    context=_verified_context(),
                    tier=tier,
                )
                verdicts.append(evaluate_action(action, tuple(lines), as_of=as_of).classification)
                evaluation_count += 1
            verdict_row = tuple(verdicts)
            rows.append(
                KeywordStrictnessRow(
                    line_id=line.id,
                    keyword=keyword,
                    verdicts=verdict_row,
                    monotone=strictness_is_monotone(verdict_row),
                )
            )

    inversion_count = sum(1 for row in rows if not row.monotone)
    return MonotonicityReport(
        as_of=as_of,
        tiers=TIERS_BY_DESCENDING_OVERSIGHT,
        rows=tuple(rows),
        keyword_count=len(rows),
        distinct_keyword_count=len({row.keyword for row in rows}),
        evaluation_count=evaluation_count,
        inversion_count=inversion_count,
        monotone=bool(rows) and inversion_count == 0,
    )
