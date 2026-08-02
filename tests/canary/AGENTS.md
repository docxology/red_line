# canary tests - Test-folder guidance

This folder covers canary hashing, issuance, verification, and the `scripts/build_canary.py` and `scripts/check_canary.py` entrypoints. It does not cover cross-surface beacon or release-document bindings; those live under `tests/integration/`.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_hashing.py](test_hashing.py) | Deterministic registry and line digests, including the committed hash anchor. | 8 |
| [test_scripts.py](test_scripts.py) | CLI build/check behavior, real subprocess execution, and committed fixture parity. | 9 |
| [test_statement.py](test_statement.py) | Issued canary metadata, successor rationale, and added or removed line reporting. | 10 |
| [test_verification.py](test_verification.py) | Freshness, drift detection, aggregate-only statements, and canary-grade escalation. | 16 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `tests.helpers.py` | not imported in this folder | [helpers.py](../helpers.py) | Canary tests construct their own statements and script calls instead of helper-built actions. |
| `tests/fixtures/canary_committed.json` | JSON fixture with `statement`, `issued_on`, `registry_digest`, `line_ids`, and `line_digests` | [canary_committed.json](../fixtures/canary_committed.json) | Pinned canary output used for byte-for-byte fixture parity and committed-statement checks. |

## No-mock policy

Use real canary statements, real fixture bytes, and real subprocesses. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation. The preferred pattern here is [test_scripts.py](test_scripts.py), which calls the real script module and a real subprocess, then compares the `--json` output to [canary_committed.json](../fixtures/canary_committed.json).

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.
