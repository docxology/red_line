"""Tests for deterministic registry and line hashing."""

from __future__ import annotations

from dataclasses import replace

from red_line.canary import _line_payload, line_digest, registry_hash
from red_line.registry import PERSONAL_RED_LINES

COMMITTED_HASH = "72835fd81d1f7ecf70f47b1e0061cd56c385273dd846879ab639225913f5aad7"


def test_hash_is_deterministic():
    assert registry_hash() == registry_hash()
    assert registry_hash(PERSONAL_RED_LINES) == registry_hash(PERSONAL_RED_LINES)


def test_hash_is_sha256_hex():
    h = registry_hash()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_hash_changes_on_edit():
    edited = (replace(PERSONAL_RED_LINES[0], title="Different title"),) + PERSONAL_RED_LINES[1:]
    assert registry_hash(edited) != registry_hash(PERSONAL_RED_LINES)


def test_hash_changes_on_removal():
    fewer = PERSONAL_RED_LINES[1:]
    assert registry_hash(fewer) != registry_hash(PERSONAL_RED_LINES)


def test_hash_invariant_to_registry_order():
    reordered = tuple(reversed(PERSONAL_RED_LINES))
    assert registry_hash(reordered) == registry_hash(PERSONAL_RED_LINES)


def test_registry_hash_unchanged_after_line_payload_refactor():
    """The pinned committed hash is preserved after factoring out _line_payload."""
    assert registry_hash() == COMMITTED_HASH
    assert registry_hash(PERSONAL_RED_LINES) == COMMITTED_HASH


def test_line_digest_is_sha256_over_line_payload():
    import hashlib
    import json

    rl = PERSONAL_RED_LINES[0]
    expected = hashlib.sha256(
        json.dumps(_line_payload(rl), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert line_digest(rl) == expected
    assert len(line_digest(rl)) == 64


def test_line_digest_changes_on_edit():
    rl = PERSONAL_RED_LINES[0]
    edited = replace(rl, standard="I will use a weakened standard.")
    assert line_digest(edited) != line_digest(rl)
