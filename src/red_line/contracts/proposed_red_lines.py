"""Validate the non-adopted candidate decision ledger."""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..model.red_line import normalize_scope
from ..registry import PERSONAL_RED_LINES

EXPECTED_IDS = {
    "agent-autonomy-limit",
    "authorship-attribution",
    "human-subjects-ethics",
    "student-relationship-data",
    "fiduciary-integrity",
    "research-organism-welfare",
}
REQUIRED_FIELDS = (
    "id",
    "title",
    "proposed_scope",
    "author_decision",
    "scope_boundary",
    "typed_exemption_design",
    "required_evidence_on_reconsideration",
    "false_positive_controls",
    "positive_cases",
    "negative_cases",
)


#: Canonical scope tokens declared by the live registry. A candidate token that
#: collides with one of these would already be inside the evaluator's
#: vocabulary, which would make the candidate's "not adopted" state ambiguous.
LIVE_SCOPE_TOKENS = frozenset(
    token for line in PERSONAL_RED_LINES for token in normalize_scope(line.scope)
)


def _proposed_scope_errors(candidate_id: str, scope: object, proposals: str) -> list[str]:
    """Bind a candidate's proposed tokens to the published table and the registry.

    The table column used to be headed "scope (verified non-laundering)", which
    claimed a property nothing computed: the tokens appeared only in prose and
    in this ledger, and no code path ever ran one through ``evaluate_action``.
    What *is* checkable is enforced here — the tokens are canonical, the JSON
    and the document agree, and none of them is already live — and the column
    heading has been downgraded to match.
    """

    if not isinstance(scope, list) or not scope:
        return [f"{candidate_id}: proposed_scope must be a non-empty list"]
    errors: list[str] = []
    if list(scope) != sorted(scope):
        errors.append(f"{candidate_id}: proposed_scope must be sorted for deterministic review")
    for token in scope:
        if not isinstance(token, str) or normalize_scope((token,)) != frozenset({token}):
            errors.append(f"{candidate_id}: proposed scope token is not canonical: {token!r}")
            continue
        if token in LIVE_SCOPE_TOKENS:
            errors.append(
                f"{candidate_id}: proposed scope token {token} is already live in PERSONAL_RED_LINES; "
                "a non-adopted candidate cannot share the adopted vocabulary"
            )
    table_row = next(
        (line for line in proposals.splitlines() if re.match(rf"\| `{re.escape(candidate_id)}` \|.*\| \w+ \|", line)),
        "",
    )
    for token in scope:
        if isinstance(token, str) and f"{token}" not in table_row:
            errors.append(f"{candidate_id}: proposed scope token {token} is absent from its published row")
    return errors


def validate_proposed_red_lines(root: Path) -> list[str]:
    ledger_path = root / "data" / "proposed_red_lines.json"
    proposals_path = root / "docs" / "PROPOSED_RED_LINES.md"
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        proposals = proposals_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"candidate ledger cannot be loaded: {exc}"]

    errors: list[str] = []
    if ledger.get("schema_version") != "1.0":
        errors.append("candidate ledger schema_version must be 1.0")
    if ledger.get("registry_effect") != "none":
        errors.append("candidate ledger must declare registry_effect=none")
    candidates = ledger.get("candidates")
    if not isinstance(candidates, list):
        return errors + ["candidate ledger candidates must be a list"]

    seen: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("candidate ledger entry is not an object")
            continue
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append("candidate ledger entry has no id")
            continue
        if candidate_id in seen:
            errors.append(f"duplicate candidate id: {candidate_id}")
        seen.add(candidate_id)
        for field in REQUIRED_FIELDS:
            value = candidate.get(field)
            valid = isinstance(value, str) and bool(value.strip())
            valid = valid or (
                isinstance(value, list)
                and bool(value)
                and all(isinstance(item, str) and item.strip() for item in value)
            )
            valid = valid or (field == "typed_exemption_design" and isinstance(value, dict))
            if not valid:
                errors.append(f"{candidate_id}: missing or malformed {field}")
        if candidate.get("author_decision") != "no_assent_recorded":
            errors.append(f"{candidate_id}: author_decision must remain no_assent_recorded")
        design = candidate.get("typed_exemption_design")
        if isinstance(design, dict):
            if design.get("status") != "not_defined_until_assent":
                errors.append(f"{candidate_id}: typed exemptions cannot be active before assent")
            if design.get("match_modes") != ["any", "all"]:
                errors.append(f"{candidate_id}: match modes must declare any and all")
            if (
                not isinstance(design.get("required_evidence_policy"), str)
                or not design["required_evidence_policy"].strip()
            ):
                errors.append(f"{candidate_id}: typed exemptions need a required evidence policy")
        if f"| `{candidate_id}` |" not in proposals:
            errors.append(f"{candidate_id}: absent from a current-release decision row")
        if candidate.get("title") not in proposals:
            errors.append(f"{candidate_id}: title is not bound in docs/PROPOSED_RED_LINES.md")
        decision_row = next(
            (
                line
                for line in proposals.splitlines()
                if line.startswith(f"| `{candidate_id}` |") and "Assent not granted" in line
            ),
            "",
        )
        if "Assent not granted" not in decision_row:
            errors.append(f"{candidate_id}: decision row does not record no assent")
        if candidate.get("scope_boundary") not in decision_row:
            errors.append(f"{candidate_id}: scope boundary is not bound in its decision row")
        errors.extend(_proposed_scope_errors(candidate_id, candidate.get("proposed_scope"), proposals))

    if seen != EXPECTED_IDS:
        errors.append(f"candidate ids differ from expected six: {sorted(seen)}")
    return errors
