"""Transparency-report aggregation for review findings."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Mapping

from ..model import Classification
from .findings import ReviewFinding


@dataclass(frozen=True)
class TransparencyReport:
    """Aggregate of findings (Turner annual transparency-report analog)."""

    period: str
    total: int
    by_classification: Mapping[str, int]
    authorizations: int
    blocked: int

    def __post_init__(self) -> None:
        if not isinstance(self.period, str) or not self.period.strip():
            raise ValueError("transparency report period is required")
        if not isinstance(self.total, int) or self.total < 0:
            raise ValueError("transparency report total must be a non-negative integer")
        if not isinstance(self.by_classification, Mapping):
            raise TypeError("by_classification must be a mapping")
        if any(
            not isinstance(key, str) or not isinstance(value, int) or value < 0
            for key, value in self.by_classification.items()
        ):
            raise TypeError("classification counts must map strings to non-negative integers")
        if not isinstance(self.authorizations, int) or self.authorizations < 0:
            raise ValueError("authorizations must be a non-negative integer")
        if not isinstance(self.blocked, int) or self.blocked < 0:
            raise ValueError("blocked must be a non-negative integer")
        object.__setattr__(self, "by_classification", MappingProxyType(dict(self.by_classification)))

    def render(self) -> str:
        lines = [f"Red-line transparency report — {self.period}", f"Total reviewed: {self.total}"]
        for name, count in sorted(self.by_classification.items()):
            lines.append(f"  {name}: {count}")
        lines.append(f"Authorizations recorded on blocking findings: {self.authorizations}")
        lines.append(f"Blocked engagements: {self.blocked}")
        return "\n".join(lines)


def transparency_report(
    findings: tuple[ReviewFinding, ...],
    period: str | None = None,
) -> TransparencyReport:
    """Aggregate ``findings`` into classifications, authorizations, and blocks."""
    if not isinstance(findings, (tuple, list)):
        raise TypeError("findings must be a tuple or list")
    if any(not isinstance(finding, ReviewFinding) for finding in findings):
        raise TypeError("findings must contain ReviewFinding values")
    counts = Counter(f.classification.value for f in findings)
    by_classification = {c.value: counts.get(c.value, 0) for c in Classification}
    # Count named authorizations only on blocking findings. An authorization
    # documents escalation; it never unblocks.
    authorizations = sum(1 for f in findings if f.authorization is not None and f.blocks)
    blocked = sum(1 for f in findings if f.blocks)
    return TransparencyReport(
        period=period or f"as of {date.today().isoformat()}",
        total=len(findings),
        by_classification=by_classification,
        authorizations=authorizations,
        blocked=blocked,
    )
