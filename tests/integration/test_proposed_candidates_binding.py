"""Pin the one executable fact about the six non-adopted candidates.

``docs/PROPOSED_RED_LINES.md`` once said the candidate scopes had been
"adversarially verified against the live evaluator" and labelled the table
column "scope (verified non-laundering)". Nothing in the tree ran a candidate
scope through ``evaluate_action``, and nothing could: a candidate is not in
``PERSONAL_RED_LINES``, so the evaluator has no line to implicate and returns
``OUTSIDE_SCOPE`` with an empty implicated set no matter what the scope says.
A non-laundering property cannot be established against an evaluator that is
structurally silent.

The document now claims only that silence. This module executes it, so the
weaker claim is bound rather than merely weaker:

* every candidate token, probed alone, is ``OUTSIDE_SCOPE`` with no implicated
  line, and so is every candidate's whole declared scope;
* a positive control probes a *live* registry token through the identical
  helper and asserts it is not outside scope, proving the probe can detect a
  match and this green is not green-by-construction;
* the candidate vocabulary is disjoint from the live vocabulary, which is the
  structural reason for the silence;
* the document carries no re-adoption of the withdrawn verification wording.

If the author ever adopts a candidate, its tokens enter ``PERSONAL_RED_LINES``,
the disjointness assertion goes red, and the silence claim in the document has
to be rewritten before the suite is green again.
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


def test_the_document_claims_only_the_silence_it_can_demonstrate() -> None:
    """The withdrawn verification wording must not return."""

    body = " ".join((ROOT / "docs" / "PROPOSED_RED_LINES.md").read_text(encoding="utf-8").split())

    assert "adversarially verified against the live evaluator" not in body
    assert "scope (verified non-laundering)" not in body
    assert "reviewed by hand against the live evaluator's vocabulary" in body
    assert "proposed scope (not yet evaluated)" in body
    assert "tests/integration/test_proposed_candidates_binding.py" in body
