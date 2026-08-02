"""Determinism of registry and line digests under reordering and change."""

from __future__ import annotations

from dataclasses import replace

from red_line import PERSONAL_RED_LINES, line_digest, registry_hash

from ._shared import _line, _swap


class TestDigestDeterminism:
    def test_registry_hash_is_repeatable_hex(self):
        first, second = registry_hash(), registry_hash()
        assert first == second
        assert len(first) == 64 and set(first) <= set("0123456789abcdef")

    def test_registry_hash_invariant_to_exemption_order_within_a_line(self):
        line = _line("s2-untargeted-profiling")
        shuffled = _swap(replace(line, exemptions=tuple(reversed(line.exemptions))))
        assert registry_hash(shuffled) == registry_hash(PERSONAL_RED_LINES)

    def test_line_digest_matches_exemption_order_invariance(self):
        line = _line("s2-untargeted-profiling")
        assert line_digest(replace(line, exemptions=tuple(reversed(line.exemptions)))) == line_digest(line)

    def test_line_digests_are_distinct_across_lines(self):
        digests = [line_digest(rl) for rl in PERSONAL_RED_LINES]
        assert len(digests) == len(set(digests))

    def test_content_change_moves_both_line_and_registry_digests(self):
        line = PERSONAL_RED_LINES[0]
        tweaked = replace(line, title=line.title + " (edited)")
        assert line_digest(tweaked) != line_digest(line)
        assert registry_hash(_swap(tweaked)) != registry_hash(PERSONAL_RED_LINES)
