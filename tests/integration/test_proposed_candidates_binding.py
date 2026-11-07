"""Exercise current non-adoption of the six candidate refusals.

Each candidate token and whole declared scope is outside the live registry
with complete intake. A live-token positive control ensures the real evaluator
can detect a match. This is not a test of hypothetical candidate policy.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from red_line import Classification, evaluate_action
from red_line.model.red_line import normalize_scope
from red_line.registry import PERSONAL_RED_LINES
from tests.helpers import action

ROOT = Path(__file__).resolve().parents[2]

#: Fresh review date so a probe result never depends on a stale fixture
#: recording date: the helper evidence is dated at ``date.today()``, so the
#: probe runs as of now and never trips the freshness window.
PROBE_AS_OF = date.today().isoformat()


def _candidates() -> list[dict]:
    payload = json.loads((ROOT / "data" / "proposed_red_lines.json").read_text(encoding="utf-8"))
    return payload["candidates"]


def _candidate_tokens() -> list[str]:
    return sorted({token for candidate in _candidates() for token in candidate["proposed_scope"]})


def _live_tokens() -> set[str]:
    return {token for line in PERSONAL_RED_LINES for token in normalize_scope(line.scope)}


def _probe(scope: frozenset[str]):
    """Run one fully evidenced probe through the real evaluator."""

    return evaluate_action(
        action("candidate coverage probe", scope),
        PERSONAL_RED_LINES,
        as_of=PROBE_AS_OF,
    )


def test_the_candidate_scan_set_is_not_empty() -> None:
    """A silence claim proved over zero candidates would be vacuous."""

    candidates = _candidates()

    assert len(candidates) == 6
    assert len(_candidate_tokens()) >= 6 * 5


def test_the_probe_can_detect_a_match_positive_control() -> None:
    """The identical helper must be able to return something other than silence.

    Without this, every assertion below would pass on a broken probe.
    """

    live = sorted(_live_tokens())
    assert live, "the live registry declares no scope tokens"

    matched = _probe(frozenset({live[0]}))

    assert matched.classification is not Classification.OUTSIDE_SCOPE
    assert matched.implicated


@pytest.mark.parametrize("token", _candidate_tokens())
def test_every_candidate_token_alone_is_outside_scope(token: str) -> None:
    """One token at a time: no candidate word reaches any live line."""

    result = _probe(frozenset({token}))

    assert result.classification is Classification.OUTSIDE_SCOPE
    assert result.implicated == ()


@pytest.mark.parametrize("candidate", _candidates(), ids=lambda entry: entry["id"])
def test_every_candidate_whole_scope_is_outside_scope(candidate: dict) -> None:
    """The full declared scope of a candidate is equally unreachable."""

    result = _probe(frozenset(candidate["proposed_scope"]))

    assert result.classification is Classification.OUTSIDE_SCOPE
    assert result.implicated == ()


def test_candidate_vocabulary_is_disjoint_from_the_live_vocabulary() -> None:
    """The structural reason the evaluator is silent, stated as a fact.

    Adopting a candidate makes this fail, which is the intended trigger for
    rewriting the document's silence claim.
    """

    overlap = sorted(set(_candidate_tokens()) & _live_tokens())

    assert overlap == []
