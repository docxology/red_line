"""Release-input snapshots built from real ledger files and the live analysis APIs."""

from __future__ import annotations

import json

from red_line.release import analysis_metrics, build_snapshot, write_snapshot

SOURCE_LEDGER_NAMES = ("claim_register.json", "source_claims.json", "proposed_red_lines.json")


def _ledgers(root, names=SOURCE_LEDGER_NAMES):
    (root / "data").mkdir(exist_ok=True)
    for name in names:
        (root / "data" / name).write_text("{}\n", encoding="utf-8")


def _figure_registry(root, payload):
    directory = root / "output" / "figures"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "figure_registry.json").write_text(json.dumps(payload), encoding="utf-8")


class TestAnalysisMetrics:
    def test_metrics_are_deterministic_across_calls(self):
        assert analysis_metrics() == analysis_metrics()

    def test_metrics_report_the_live_registry_shape(self):
        metrics = analysis_metrics()
        assert metrics["registry_line_count"] == 7
        assert metrics["monotonicity"]["evaluation_count"] == 108
        assert metrics["scope_token_disjoint_count"] == 32
        assert metrics["outcome_coverage"]["complete"] is True


class TestBuildSnapshot:
    def test_binds_every_present_ledger_and_the_figure_registry(self, tmp_path):
        _ledgers(tmp_path)
        _figure_registry(tmp_path, {"figure_count": 2, "figures": [{}, {}]})

        first = build_snapshot(tmp_path)
        second = build_snapshot(tmp_path)

        assert first == second
        assert first["schema_version"] == "1.1"
        assert set(first["source_hashes"]) == {
            "data/claim_register.json",
            "data/source_claims.json",
            "data/proposed_red_lines.json",
        }
        assert first["figure_registry"]["figure_count"] == 2
        assert len(first["figure_registry"]["sha256"]) == 64

    def test_figure_count_falls_back_to_the_figure_list_length(self, tmp_path):
        _ledgers(tmp_path)
        _figure_registry(tmp_path, {"figures": [{}, {}, {}]})
        assert build_snapshot(tmp_path)["figure_registry"]["figure_count"] == 3

    def test_absent_figure_registry_is_reported_as_empty(self, tmp_path):
        _ledgers(tmp_path)
        registry = build_snapshot(tmp_path)["figure_registry"]
        assert registry["sha256"] is None
        assert registry["figure_count"] == 0
        assert registry["path"] == "output/figures/figure_registry.json"

    def test_absent_ledgers_are_omitted_rather_than_nulled(self, tmp_path):
        _ledgers(tmp_path, names=("source_claims.json",))
        assert set(build_snapshot(tmp_path)["source_hashes"]) == {"data/source_claims.json"}

    def test_snapshot_states_its_trust_boundary(self, tmp_path):
        _ledgers(tmp_path)
        assert "does not" in build_snapshot(tmp_path)["trust_boundary"]


class TestWriteSnapshot:
    def test_writes_the_snapshot_and_creates_its_parent_directory(self, tmp_path):
        _ledgers(tmp_path)
        destination = write_snapshot(tmp_path)

        assert destination == tmp_path / "output" / "data" / "release_inputs.json"
        assert destination.is_file()
        written = json.loads(destination.read_text(encoding="utf-8"))
        assert written == build_snapshot(tmp_path)
        assert destination.read_text(encoding="utf-8").endswith("\n")
