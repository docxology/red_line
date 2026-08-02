"""Bind the abstract's stemming sentence to where stemming actually happens.

The abstract used to say, flatly, that "explicit aliases replace heuristic
stemming". That is true of scope normalization and false of the advisory
description hint, where ``red_line.oversight.findings._stem`` still strips
``ing``/``ed``/``s``. The sentence is now qualified, and these tests hold both
halves of the qualification to the code:

* ``normalize_token`` must *not* stem — a suffixed spelling of a live scope
  token must stay a different token, so a policy match is never manufactured
  by a suffix rule;
* the stemmer must still be live on the advisory path — a description that
  mentions a prohibited keyword in a suffixed form must produce a hint;
* and that hint must not move the classification, which is what makes the
  survival of the stemmer honest rather than a hidden policy input.

The third assertion is the load-bearing one: it is a differential test with
the description as the only varied input.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from red_line import Classification
from red_line.model.red_line import normalize_token
from red_line.oversight import review_engagement
from red_line.oversight.findings import _stem
from red_line.registry import PERSONAL_RED_LINES
from tests.helpers import action

ROOT = Path(__file__).resolve().parents[2]

REVIEWED_ON = date.today().isoformat()

#: A live prohibited token and a suffixed spelling of it. Chosen from the
#: registry at import time so a scope edit that drops the token fails loudly.
_PROFILING_TOKENS = frozenset(
    token for line in PERSONAL_RED_LINES for token in line.scope if token == "profiling"
)


def _abstract() -> str:
    return " ".join((ROOT / "manuscript" / "00_abstract.md").read_text(encoding="utf-8").split())


def test_the_abstract_qualifies_the_stemming_claim_to_scope_normalization() -> None:
    """The blanket form of the sentence must not come back."""

    body = _abstract()

    assert "explicit aliases replace heuristic stemming in scope normalization" in body
    assert "never reaches a classification" in body


def test_the_token_the_qualification_talks_about_is_still_in_the_registry() -> None:
    """A vacuous version of these tests would pass on an empty scan set."""

    assert _PROFILING_TOKENS == {"profiling"}


def test_normalize_token_does_not_stem_a_suffixed_spelling() -> None:
    """Scope normalization is alias-driven, so a suffix is not folded away."""

    assert normalize_token("profiling") == "profiling"
    assert normalize_token("profiled") == "profiled"
    assert normalize_token("profiles") == "profiles"
    assert normalize_token("profiled") != normalize_token("profiling")


def test_the_advisory_stemmer_is_still_live_on_the_hint_path() -> None:
    """The surviving stemmer is real: assert it, rather than assuming it."""

    assert _stem("profiling") == "profil"
    assert _stem("profiled") == "profil"

    hinted = review_engagement(
        action("We will be profiling residents at scale", frozenset({"documentation"})),
        reviewed_on=REVIEWED_ON,
    )

    assert "undeclared-scope hint" in hinted.finding
    assert "description mentions 'profiling'" in hinted.finding
    assert "s2-untargeted-profiling" in hinted.finding


def test_the_description_hint_never_moves_the_classification() -> None:
    """Differential control: only the description differs between the two runs.

    If the stemmer ever reached a verdict, the hinted run would classify
    differently from the neutral run on the same declared scope.
    """

    neutral = review_engagement(
        action("Publish a plain project README", frozenset({"documentation"})),
        reviewed_on=REVIEWED_ON,
    )
    hinted = review_engagement(
        action("We will be profiling residents at scale", frozenset({"documentation"})),
        reviewed_on=REVIEWED_ON,
    )

    assert neutral.classification is Classification.OUTSIDE_SCOPE
    assert hinted.classification is neutral.classification
    assert hinted.implicated_ids == neutral.implicated_ids == ()
    assert hinted.blocks is neutral.blocks is False
    assert hinted.reason_codes == neutral.reason_codes == ("outside_scope",)
    # The hint is the only observable difference, which is the whole claim.
    assert "undeclared-scope hint" in hinted.finding
    assert "undeclared-scope hint" not in neutral.finding
