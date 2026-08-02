"""Bind the scholarship-ledger prose to the ledger it describes.

Section 02a, `docs/research-method.md`, and `docs/security-threat-model.md` all
state how much of the eleven-field source record actually exists. Before this
module those sentences were unbound, and they were wrong: they claimed genre,
language, and a stable locator for every source while `edition_locator` held
the same self-referential string in all 39 records.

Every number asserted here is recomputed from `data/source_claims.json` and
`docs/research-method.md`, so a backfilled locator or an added source reddens
the prose instead of silently drifting past it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from red_line.contracts.source_claims import LOCATOR_SENTINEL, validate_source_claims

ROOT = Path(__file__).resolve().parents[2]
LEDGER = json.loads((ROOT / "data" / "source_claims.json").read_text(encoding="utf-8"))


def _flat(relative: str) -> str:
    """Read a document with its hard line wraps collapsed to single spaces."""

    return " ".join((ROOT / relative).read_text(encoding="utf-8").split())


METHOD_RAW = (ROOT / "docs" / "research-method.md").read_text(encoding="utf-8")
METHOD = _flat("docs/research-method.md")
SCHOLARSHIP = _flat("manuscript/02a_global_and_historical_scholarship.md")
THREAT_MODEL = _flat("docs/security-threat-model.md")


def _ledger_tables() -> list[list[str]]:
    """Return the source-name column of every pipe table in the method doc."""

    tables: list[list[str]] = []
    lines = METHOD_RAW.splitlines()
    for index, line in enumerate(lines):
        stripped = line.replace("|", "").replace(" ", "")
        if not line.startswith("|") or not stripped or set(stripped) - set("-:"):
            continue
        rows: list[str] = []
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].startswith("|"):
            rows.append(lines[cursor].split("|")[1].strip())
            cursor += 1
        tables.append(rows)
    return tables


def _ledger_table_lines() -> list[list[str]]:
    """Return the whole line of every data row of every pipe table.

    :func:`_ledger_tables` keeps only the first cell, which is enough to key a
    row by its work but loses the URL cell the record set is bound through.
    """

    tables: list[list[str]] = []
    lines = METHOD_RAW.splitlines()
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
    return tables


def _locator_counts() -> tuple[int, int]:
    locators = [record["edition_locator"] for record in LEDGER["records"]]
    not_recorded = sum(1 for locator in locators if locator == LOCATOR_SENTINEL)
    return len(locators) - not_recorded, not_recorded


def test_source_count_in_the_prose_re_derives_from_the_ledger_records() -> None:
    """"39 sources" is the record set, and every record's URL is in a table.

    An earlier revision of this test derived 38 by counting *rows* and calling
    them sources. That is one row short of the record set and one row over the
    distinct-row count at the same time: Kukutai and Taylor occupies two rows,
    and the Cugoano row cites two works. Both corrections are asserted here so
    the arithmetic cannot be split again — the prose states 39 sources in 38
    rows, and each half is recomputed from a different artefact.
    """

    index_table, deep_table = _ledger_tables()[:2]
    index_lines, deep_lines = _ledger_table_lines()[:2]
    rows = [*index_table, *deep_table]
    record_urls = {record["verified_url"] for record in LEDGER["records"]}
    table_urls = {
        url
        for line in (*index_lines, *deep_lines)
        for url in re.findall(r"https?://[^\s)|\]]+", line)
    }

    assert len(index_table) == 23
    assert len(deep_table) == 22
    assert len(rows) == 45, "the two tables carry 45 rows between them"
    assert len(record_urls) == len(LEDGER["records"]) == 45
    assert record_urls <= table_urls, sorted(record_urls - table_urls)
    assert table_urls == record_urls, sorted(table_urls - record_urls)

    def work_key(row: str) -> str:
        """Key a row by its italicized title when it has one, else by the cell."""

        title = re.search(r"\*([^*]+)\*", row)
        return re.sub(r"[^a-z0-9]", "", (title.group(1) if title else row).lower())

    distinct_rows = {work_key(row) for row in rows}
    shared = {work_key(row) for row in index_table} & {work_key(row) for row in deep_table}
    multi_source_rows = [
        line for line in (*index_lines, *deep_lines) if len(re.findall(r"https?://", line)) > 1
    ]

    assert shared == {"indigenousdatasovereignty"}, "exactly one work is listed in both tables"
    assert len(distinct_rows) == 44
    assert len(multi_source_rows) == 1, "exactly one row cites two works"
    assert "cugoano" in multi_source_rows[0].lower()
    # 45 records = 44 distinct rows - 1 (Kukutai's second row is not a new
    # source) + 2 (the Cugoano row is two sources, counted once above).
    assert len(record_urls) == len(distinct_rows) - len(shared) + 2

    assert f"For every one of its {len(record_urls)} sources" in SCHOLARSHIP
    assert f"Those {len(record_urls)} sources sit in {len(distinct_rows)} table rows" in SCHOLARSHIP
    assert f"recorded for all {len(record_urls)} sources" in METHOD


def test_deepened_subset_size_in_the_prose_matches_the_second_table() -> None:
    """The deepened-subset claim equals the row count of the seven-column table."""

    deep_table = _ledger_tables()[1]

    recorded, not_recorded = _locator_counts()

    assert len(deep_table) == recorded
    assert f"the {recorded} sources in the deepened second table" in SCHOLARSHIP
    assert f"remaining {not_recorded} `{LOCATOR_SENTINEL}`" in SCHOLARSHIP


def test_locator_coverage_prose_matches_the_recomputed_ledger_counts() -> None:
    """Every stated locator count is recomputed from the records themselves."""

    recorded, not_recorded = _locator_counts()
    coverage = LEDGER["locator_coverage"]

    assert coverage["recorded"] == recorded
    assert coverage["not_recorded"] == not_recorded
    assert recorded + not_recorded == len(LEDGER["records"])
    assert f"the {recorded} sources in the deepened second table" in SCHOLARSHIP
    assert f"only for the {recorded} sources in the second table below" in METHOD
    assert f"first table's {not_recorded} rows" in METHOD
    assert f"edition and locator fields for the {recorded} deepened sources only" in THREAT_MODEL
    assert f"other {not_recorded} marked `{LOCATOR_SENTINEL}`" in THREAT_MODEL
    # The threat model's own source total sat unbound and had drifted to the
    # row count; it is the record set, and it is recomputed here.
    assert f"transfer limits for all {len(LEDGER['records'])} sources" in THREAT_MODEL


def test_every_recorded_locator_names_a_real_edition_or_section() -> None:
    """A recorded locator must be more than the sentinel or a citation key."""

    recorded = [
        record
        for record in LEDGER["records"]
        if record["edition_locator"] != LOCATOR_SENTINEL
    ]

    assert len(recorded) == 22
    for record in recorded:
        locator = record["edition_locator"]
        assert not locator.startswith("references.bib:"), record["source_id"]
        assert record["source_id"] not in locator.replace(" ", ""), record["source_id"]
        assert locator in METHOD, f"{record['source_id']}: locator is not the one the ledger table records"


def test_no_record_carries_the_old_self_referential_locator() -> None:
    """The exact defect that was shipped must stay impossible to reintroduce."""

    for record in LEDGER["records"]:
        assert record["edition_locator"] != (
            f"references.bib:{record['source_id']}; docs/research-method.md"
        )


# --------------------------------------------------------------------------
# Planted defects: proof the validator fires on the shape it now forbids.
# --------------------------------------------------------------------------


def _synthetic_tree(tmp_path: Path, mutate) -> Path:
    ledger = json.loads(json.dumps(LEDGER))
    mutate(ledger)
    (tmp_path / "data").mkdir(parents=True)
    (tmp_path / "data" / "source_claims.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (tmp_path / "manuscript").mkdir(parents=True)
    (tmp_path / "manuscript" / "references.bib").write_text("", encoding="utf-8")
    (tmp_path / "manuscript" / "01_body.md").write_text("", encoding="utf-8")
    (tmp_path / "docs").mkdir(parents=True)
    # The real method doc, because the row count is derived from its tables and
    # an empty stub would make every row assertion pass for the wrong reason.
    (tmp_path / "docs" / "research-method.md").write_text(METHOD_RAW, encoding="utf-8")
    return tmp_path


def test_validator_rejects_a_locator_that_points_at_its_own_citation_key(tmp_path: Path) -> None:
    def plant(ledger: dict) -> None:
        record = ledger["records"][0]
        record["edition_locator"] = f"references.bib:{record['source_id']}; docs/research-method.md"

    errors = validate_source_claims(_synthetic_tree(tmp_path, plant))

    assert any("points at its own citation key" in error for error in errors)
    assert any("derivable from source_id" in error for error in errors)


def test_validator_rejects_a_backfill_that_leaves_the_counts_stale(tmp_path: Path) -> None:
    """Recording a real locator without updating the published counts fails."""

    def plant(ledger: dict) -> None:
        for record in ledger["records"]:
            if record["edition_locator"] == LOCATOR_SENTINEL:
                record["edition_locator"] = "English monograph; Some Press; chapter 3"
                return
        raise AssertionError("no sentinel record to backfill")

    errors = validate_source_claims(_synthetic_tree(tmp_path, plant))

    assert "source ledger locator_coverage.recorded must be 23" in errors
    assert "source ledger locator_coverage.not_recorded must be 22" in errors


def test_validator_rejects_a_renamed_sentinel(tmp_path: Path) -> None:
    """A sentinel that is not the enumerated one stops being countable."""

    def plant(ledger: dict) -> None:
        ledger["locator_coverage"]["sentinel"] = "n/a"

    errors = validate_source_claims(_synthetic_tree(tmp_path, plant))

    assert any("locator_coverage.sentinel must be" in error for error in errors)


def test_validator_rejects_a_missing_coverage_block(tmp_path: Path) -> None:
    def plant(ledger: dict) -> None:
        del ledger["locator_coverage"]

    errors = validate_source_claims(_synthetic_tree(tmp_path, plant))

    assert "source ledger locator_coverage must be an object" in errors


def test_live_ledger_passes_the_validator_it_is_pinned_against() -> None:
    assert validate_source_claims(ROOT) == []


@pytest.mark.parametrize("document", ["SCHOLARSHIP", "METHOD", "THREAT_MODEL"])
def test_no_document_still_claims_a_locator_for_every_source(document: str) -> None:
    """The refuted universal claim must not reappear in any surface."""

    text = {"SCHOLARSHIP": SCHOLARSHIP, "METHOD": METHOD, "THREAT_MODEL": THREAT_MODEL}[document]

    assert "records place, period, genre, language or translation, stable locator" not in text


def test_record_counts_block_is_recomputed_and_can_reject():
    """The published counts must be derived, and a corrupted pair must fail."""

    counts = LEDGER["record_counts"]

    assert counts["sources"] == len(LEDGER["records"]) == 45
    assert counts["ledger_table_rows"] == 44
    assert validate_source_claims(ROOT) == []


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("sources", 44, "record_counts.sources must be 45"),
        ("ledger_table_rows", 45, "record_counts.ledger_table_rows must be 44"),
    ],
)
def test_a_corrupted_record_count_is_rejected(tmp_path: Path, field: str, value: int, message: str):
    """Planted defect: state one number as the other and require a red result."""

    def corrupt(ledger: dict) -> None:
        ledger["record_counts"][field] = value

    errors = validate_source_claims(_synthetic_tree(tmp_path, corrupt))

    assert any(message in error for error in errors), errors


def test_a_missing_record_counts_block_is_rejected(tmp_path: Path):
    def drop(ledger: dict) -> None:
        del ledger["record_counts"]

    errors = validate_source_claims(_synthetic_tree(tmp_path, drop))

    assert any("record_counts must be an object" in error for error in errors), errors


def test_row_count_derivation_fails_closed_on_a_method_doc_with_no_tables(tmp_path: Path):
    """A method doc that lost its tables must be an error, never a silent zero.

    Without this branch the ledger's row claim would be certified by a file
    that contains nothing to certify it against.
    """

    tree = _synthetic_tree(tmp_path, lambda ledger: None)
    (tree / "docs" / "research-method.md").write_text("# no tables here\n", encoding="utf-8")

    errors = validate_source_claims(tree)

    assert any("row count could not be derived" in error for error in errors), errors
