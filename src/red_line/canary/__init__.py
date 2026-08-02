"""Public canary issuance, hashing, and verification APIs."""

from __future__ import annotations

from .hashing import _line_payload, line_digest, registry_hash
from .statement import CanaryStatement, DEFAULT_CANARY_TEXT, issue_canary
from .verification import (
    CanaryVerification,
    DEFAULT_MAX_AGE_DAYS,
    detect_line_removal,
    is_stale,
    verify_canary,
)

__all__ = [
    "_line_payload",
    "CanaryStatement",
    "CanaryVerification",
    "DEFAULT_CANARY_TEXT",
    "DEFAULT_MAX_AGE_DAYS",
    "registry_hash",
    "line_digest",
    "issue_canary",
    "verify_canary",
    "detect_line_removal",
    "is_stale",
]
