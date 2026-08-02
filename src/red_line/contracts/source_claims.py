"""Validate the machine-readable source/claim ledger against citations."""

from __future__ import annotations

import json
import re
from pathlib import Path


#: The one value ``edition_locator`` may take when no page, section, chapter,
#: or edition has been recorded for a source. An explicit, enumerated sentinel
#: keeps the gap countable; free-form filler and self-referential pointers do
#: not, which is how every record once carried
#: ``references.bib:<id>; docs/research-method.md`` — a string derivable from
#: ``source_id`` alone and therefore content-free.
LOCATOR_SENTINEL = "not recorded"


def _locator_errors(source_id: str, locator: str) -> list[str]:
    """Reject a locator that carries no information beyond the citation key."""

    errors: list[str] = []
    if locator == LOCATOR_SENTINEL:
        return errors
    if locator.startswith("references.bib:"):
        errors.append(
            f"{source_id}: edition_locator points at its own citation key; record a real "
            f"edition and locator or the {LOCATOR_SENTINEL!r} sentinel"
        )
    if source_id in locator.replace(" ", ""):
        errors.append(f"{source_id}: edition_locator is derivable from source_id")
    return errors


def _coverage_errors(coverage: object, records: list) -> list[str]:
    """Re-derive the declared locator coverage from the records themselves.

    The published counts are a claim about the ledger; ``records`` is the
    ledger. Recomputing here means the gap cannot be narrated smaller than it
    is, and a backfilled locator that leaves the counts untouched fails.
    """

    if not isinstance(coverage, dict):
        return ["source ledger locator_coverage must be an object"]
    errors: list[str] = []
    if coverage.get("sentinel") != LOCATOR_SENTINEL:
        errors.append(f"source ledger locator_coverage.sentinel must be {LOCATOR_SENTINEL!r}")
    locators = [
        record.get("edition_locator")
        for record in records
        if isinstance(record, dict) and isinstance(record.get("edition_locator"), str)
    ]
    not_recorded = sum(1 for locator in locators if locator.strip() == LOCATOR_SENTINEL)
    recorded = len(locators) - not_recorded
    if coverage.get("recorded") != recorded:
        errors.append(f"source ledger locator_coverage.recorded must be {recorded}")
    if coverage.get("not_recorded") != not_recorded:
        errors.append(f"source ledger locator_coverage.not_recorded must be {not_recorded}")
    return errors


def _distinct_ledger_rows(method: str) -> int:
    """Count distinct works across the two ledger tables in the method doc.

    Rows are keyed by their italicized title when they have one, so the work
    listed in both tables collides into one. This is deliberately *not* the
    source count: one row cites two works, so the record set is larger than the
    row set. Recomputing both here keeps the manuscript from restating either
    number as the other, which is exactly the drift that shipped once.
    """

    lines = method.splitlines()
    tables: list[list[str]] = []
    for index, line in enumerate(lines):
        stripped = line.replace("|", "").replace(" ", "")
        if not line.startswith("|") or not stripped or set(stripped) - set("-:"):
            continue
        rows: list[str] = []
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].startswith("|"):
            rows.append(lines[cursor])
            cursor += 1
        tables.append(rows)
    if len(tables) < 2:
        return 0
    keys = set()
    for row in (*tables[0], *tables[1]):
        cell = row.split("|")[1].strip()
        title = re.search(r"\*([^*]+)\*", cell)
        keys.add(re.sub(r"[^a-z0-9]", "", (title.group(1) if title else cell).lower()))
    return len(keys)


def _record_count_errors(counts: object, records: list, method: str) -> list[str]:
    """Re-derive the published source and row counts from the artefacts.

    The manuscript states both numbers; if they were only stored here, a
    hand-edit could make the ledger agree with a wrong sentence.
    """

    if not isinstance(counts, dict):
        return ["source ledger record_counts must be an object"]
    errors: list[str] = []
    if counts.get("sources") != len(records):
        errors.append(f"source ledger record_counts.sources must be {len(records)}")
    rows = _distinct_ledger_rows(method)
    if not rows:
        errors.append("source ledger row count could not be derived from docs/research-method.md")
    elif counts.get("ledger_table_rows") != rows:
        errors.append(f"source ledger record_counts.ledger_table_rows must be {rows}")
    return errors


def _bibliography_for(path: Path) -> dict[str, str | None]:
    text = path.read_text(encoding="utf-8")
    records: dict[str, str] = {}
    for match in re.finditer(r"@\w+\{([^,]+),(.*?)(?=\n@\w+\{|\Z)", text, re.DOTALL):
        key, body = match.groups()
        url_match = re.search(r"\burl\s*=\s*\{([^}]+)\}", body)
        records[key] = "".join(url_match.group(1).split()) if url_match else None
    return records


def validate_source_claims(root: Path) -> list[str]:
    ledger_path = root / "data" / "source_claims.json"
    bib_path = root / "manuscript" / "references.bib"
    method_path = root / "docs" / "research-method.md"
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        bibliography = _bibliography_for(bib_path)
        method = method_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"source ledger cannot be loaded: {exc}"]
    errors: list[str] = []
    if ledger.get("schema_version") != "1.0":
        errors.append("source ledger schema_version must be 1.0")
    records = ledger.get("records")
    if not isinstance(records, list):
        return errors + ["source ledger records must be a list"]
    errors.extend(_record_count_errors(ledger.get("record_counts"), records, method))
    by_id: dict[str, dict] = {}
    for record in records:
        if not isinstance(record, dict):
            errors.append("source ledger record is not an object")
            continue
        source_id = record.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append("source ledger record has no source_id")
            continue
        if source_id in by_id:
            errors.append(f"duplicate source_id: {source_id}")
        by_id[source_id] = record
        for field in (
            "edition_locator",
            "verified_url",
            "claim_class",
            "transferred_question",
            "stopping_boundary",
        ):
            if not isinstance(record.get(field), str) or not record[field].strip():
                errors.append(f"{source_id}: missing {field}")
        locator = record.get("edition_locator")
        if isinstance(locator, str) and locator.strip():
            errors.extend(_locator_errors(source_id, locator.strip()))
        if not isinstance(record.get("uses"), list) or not record["uses"]:
            errors.append(f"{source_id}: uses must be a non-empty list")
        if source_id in bibliography and record.get("verified_url") != bibliography[source_id]:
            errors.append(f"{source_id}: verified_url differs from references.bib")
        if source_id in bibliography and bibliography[source_id] and bibliography[source_id] not in method:
            errors.append(f"{source_id}: verified_url is absent from docs/research-method.md")
    figure_bindings = ledger.get("figure_bindings", {})
    if not isinstance(figure_bindings, dict):
        errors.append("source ledger figure_bindings must be an object")
    else:
        for figure_label, bound_ids in figure_bindings.items():
            if not isinstance(figure_label, str) or not figure_label.strip():
                errors.append("source ledger figure binding has no figure label")
                continue
            if not isinstance(bound_ids, list) or not bound_ids:
                errors.append(f"{figure_label}: figure binding must be a non-empty list")
                continue
            if any(not isinstance(source_id, str) or not source_id.strip() for source_id in bound_ids):
                errors.append(f"{figure_label}: figure binding source ids must be non-empty strings")
            if all(isinstance(source_id, str) for source_id in bound_ids) and len(bound_ids) != len(
                set(bound_ids)
            ):
                errors.append(f"{figure_label}: figure binding contains duplicate source ids")
            for source_id in bound_ids:
                if source_id not in by_id:
                    errors.append(f"{figure_label}: figure binding references unknown source id {source_id}")
    errors.extend(_coverage_errors(ledger.get("locator_coverage"), records))
    tokens = set(
        re.findall(
            r"@([A-Za-z0-9_:-]+)",
            "\n".join(path.read_text(encoding="utf-8") for path in (root / "manuscript").glob("*.md")),
        )
    )
    # pandoc-crossref prefixes plus the formalism-block prefixes consumed by
    # ``infrastructure/rendering/formalism.lua`` in the render engine. A
    # ``[@def:x]`` or ``[@prop:x]`` is a cross-reference resolved from a label,
    # never a bibliography key, so treating one as a citation would report the
    # whole formalism section as citing unknown sources.
    cross_reference_prefixes = {
        "ax",
        "claim",
        "cor",
        "def",
        "eq",
        "ex",
        "fig",
        "lem",
        "lst",
        "prop",
        "rem",
        "sec",
        "tbl",
        "thm",
    }
    cited = {token for token in tokens if token.split(":", 1)[0] not in cross_reference_prefixes}
    unknown = sorted(cited - set(bibliography))
    if unknown:
        errors.append(f"manuscript cites unknown bibliography keys: {unknown}")
    for source_id in sorted(cited & set(bibliography)):
        if not bibliography[source_id]:
            errors.append(f"{source_id}: cited bibliography entry has no verified URL")
    missing = sorted(cited - set(by_id))
    if missing:
        errors.append(f"cited sources missing from ledger: {missing}")
    extra = sorted(set(by_id) - set(bibliography))
    if extra:
        errors.append(f"ledger sources missing from bibliography: {extra}")
    return errors
