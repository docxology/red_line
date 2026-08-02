"""Beacon-to-code binding: the human-readable beacon must equal the registry.

The manuscript beacon (``manuscript/09_red_lines.md``) and the README carry a
pinned registry hash and prose renderings of the red lines. If someone edits a
red line in ``src/red_line/registry/lines.py`` without re-issuing the beacon — or edits the
prose so it no longer matches the code — the standard has silently forked. These
tests make that fork a *build failure*: the canary sings in CI, not just in prose.

No mocks; reads the real files, computes the real hash.
"""

from __future__ import annotations

import re
from pathlib import Path

from red_line.canary import registry_hash
from red_line import PERSONAL_RED_LINES, Severity

ROOT = Path(__file__).resolve().parent.parent.parent
BEACON = ROOT / "manuscript" / "09_red_lines.md"
README = ROOT / "README.md"


def _normalize(text: str) -> str:
    """Collapse markdown quoting/wrapping so prose can be compared to code text."""
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.replace("\u2011", "-").replace("*", " ").split())


def test_beacon_pinned_hash_matches_registry():
    """The full 64-hex hash pinned in the beacon equals the computed hash."""
    body = BEACON.read_text(encoding="utf-8")
    pinned = re.findall(r"\b[0-9a-f]{64}\b", body)
    assert len(pinned) == 1, "beacon must pin exactly one registry hash"
    assert pinned[0] == registry_hash(PERSONAL_RED_LINES)


def test_readme_truncated_hash_matches_registry():
    """README's `first8…last6` truncated hash matches the computed hash."""
    body = README.read_text(encoding="utf-8")
    match = re.search(r"`([0-9a-f]{8})…([0-9a-f]{6})`", body)
    assert match is not None, "README must carry the truncated registry hash"
    digest = registry_hash(PERSONAL_RED_LINES)
    assert match.group(1) == digest[:8]
    assert match.group(2) == digest[-6:]


def test_readme_registry_counts_match():
    """README's '(N lines, M `CANARY`-grade)' claim matches the registry."""
    body = README.read_text(encoding="utf-8")
    match = re.search(r"\((\d+) lines, (\d+) `CANARY`-grade\)", body)
    assert match is not None, "README must state registry line/canary counts"
    canary_count = sum(1 for rl in PERSONAL_RED_LINES if rl.severity is Severity.CANARY)
    assert int(match.group(1)) == len(PERSONAL_RED_LINES)
    assert int(match.group(2)) == canary_count


def test_beacon_contains_every_standard_verbatim():
    """Every red line's standard text appears in the beacon (modulo wrapping)."""
    doc = _normalize(BEACON.read_text(encoding="utf-8"))
    for rl in PERSONAL_RED_LINES:
        assert _normalize(rl.standard) in doc, f"standard text drifted: {rl.id}"


def test_beacon_contains_every_title_verbatim():
    """Every red line's title appears in the beacon (modulo wrapping)."""
    doc = _normalize(BEACON.read_text(encoding="utf-8"))
    for rl in PERSONAL_RED_LINES:
        assert _normalize(rl.title) in doc, f"title drifted: {rl.id}"


def test_beacon_marks_exactly_the_canary_lines():
    """The beacon's `[CANARY]` markers count equals the registry's CANARY lines."""
    body = BEACON.read_text(encoding="utf-8")
    canary_count = sum(1 for rl in PERSONAL_RED_LINES if rl.severity is Severity.CANARY)
    assert body.count("[CANARY]") == canary_count


def test_beacon_section_count_matches_registry():
    """One `## ` section per red line — no missing or phantom beacon entries."""
    body = BEACON.read_text(encoding="utf-8")
    sections = [ln for ln in body.splitlines() if ln.startswith("## ")]
    assert len(sections) == len(PERSONAL_RED_LINES)


def test_beacon_contains_every_carve_out_verbatim():
    """Every carve-out clause body appears in the beacon (modulo wrapping).

    Clauses are prefixed "Does not restrict " in code and rendered after a
    "**Does not restrict:**" label in prose; the clause BODY must match
    verbatim so a carve-out cannot be silently widened in one surface only.
    """
    doc = _normalize(BEACON.read_text(encoding="utf-8"))
    prefix = "Does not restrict "
    for rl in PERSONAL_RED_LINES:
        for clause in rl.carve_outs:
            body = clause[len(prefix) :] if clause.startswith(prefix) else clause
            assert _normalize(body) in doc, f"carve-out drifted: {rl.id}: {body}"


def test_beacon_max_tier_lines_match_registry_in_order():
    """Each beacon section's 'Max tier:' value equals its registry line's tier.

    Sections render in registry order; a Max-tier-only prose edit must not be
    able to drift from the machine registry.
    """
    body = BEACON.read_text(encoding="utf-8")
    sections = body.split("\n## ")[1:]  # one per red line, registry order
    assert len(sections) == len(PERSONAL_RED_LINES)
    label = {"hosted": "hosted", "connected": "connected", "air_gapped": "air-gapped"}
    for rl, section in zip(PERSONAL_RED_LINES, sections):
        norm_section = _normalize(section).lower()
        assert "max tier:" in norm_section, f"no Max tier line: {rl.id}"
        tier_text = norm_section.split("max tier:", 1)[1].strip()
        assert tier_text.startswith(label[rl.max_tier.value]), (
            f"max tier drifted: {rl.id}: beacon says '{tier_text[:20]}…', registry says '{rl.max_tier.value}'"
        )
