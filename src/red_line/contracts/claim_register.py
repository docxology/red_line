"""Validate the machine-readable publication claim contract and its prose map."""

from __future__ import annotations

import json
import re
from pathlib import Path

CLAIM_ID = re.compile(r"CLM-[0-9]{3}")


def validate_claim_register(root: Path) -> list[str]:
    claims_path = root / "data" / "claim_register.json"
    doc_path = root / "docs" / "claim-register.md"
    errors: list[str] = []
    try:
        payload = json.loads(claims_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"claim register cannot be read: {exc}"]

    if payload.get("schema_version") != "1.0":
        errors.append("claim register schema_version must be 1.0")
    classes = payload.get("claim_classes")
    modes = payload.get("verification_modes")
    claims = payload.get("claims")
    if not isinstance(classes, list) or not classes or len(set(classes)) != len(classes):
        errors.append("claim_classes must be a non-empty unique list")
        classes = []
    if not isinstance(modes, list) or not modes or len(set(modes)) != len(modes):
        errors.append("verification_modes must be a non-empty unique list")
        modes = []
    if not isinstance(claims, list) or not claims:
        return errors + ["claims must be a non-empty list"]

    ids: list[str] = []
    for index, claim in enumerate(claims):
        prefix = f"claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{prefix} must be an object")
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not CLAIM_ID.fullmatch(claim_id):
            errors.append(f"{prefix}.claim_id must match CLM-NNN")
        elif claim_id in ids:
            errors.append(f"duplicate claim_id: {claim_id}")
        else:
            ids.append(claim_id)
        for field in ("claim", "status", "stopping_point"):
            if not isinstance(claim.get(field), str) or not claim[field].strip():
                errors.append(f"{prefix}.{field} must be non-empty")
        claim_class = claim.get("claim_class")
        if claim_class not in classes:
            errors.append(f"{prefix}.claim_class is not declared: {claim_class!r}")
        mode = claim.get("verification_mode")
        if mode not in modes:
            errors.append(f"{prefix}.verification_mode is not declared: {mode!r}")
        surfaces = claim.get("supporting_surface")
        if (
            not isinstance(surfaces, list)
            or not surfaces
            or any(not isinstance(value, str) for value in surfaces)
        ):
            errors.append(f"{prefix}.supporting_surface must be a non-empty string list")

    try:
        document = doc_path.read_text(encoding="utf-8")
    except OSError as exc:
        return errors + [f"claim register document cannot be read: {exc}"]
    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("claim_id"), str):
            continue
        claim_id = claim["claim_id"]
        rows = [line for line in document.splitlines() if line.startswith(f"| `{claim_id}` |")]
        if len(rows) != 1:
            errors.append(f"{claim_id}: expected exactly one documentation row")
            continue
        row = rows[0]
        if claim["claim_class"] not in row:
            errors.append(f"{claim_id}: claim class is not bound in documentation")
        if claim["verification_mode"] not in row:
            errors.append(f"{claim_id}: verification mode is not bound in documentation")
        if claim["claim"] not in row:
            errors.append(f"{claim_id}: claim text is not bound in documentation")
    documented_ids = set(CLAIM_ID.findall(document))
    unknown = sorted(documented_ids - set(ids))
    if unknown:
        errors.append(f"documentation contains unknown claim IDs: {unknown}")
    return errors
