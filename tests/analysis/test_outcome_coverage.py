"""Outcome-coverage harness tests: reachability exercised, not asserted.

No mocks — every case runs through the real ``evaluate_action`` against the
live registry. Includes a negative control (a reduced registry makes
implication-dependent outcomes honestly unreachable), proving the harness CAN
report incompleteness rather than being green by construction.
"""

from __future__ import annotations

import pytest

from red_line.analysis.outcome_coverage import (
    BATTERY_AS_OF,
    CoverageCase,
    canonical_battery,
    run_outcome_coverage,
)
from red_line.model import (
    AssessmentReasonCode,
    Classification,
    DeploymentTier,
    ProposedAction,
)
from red_line.registry import PERSONAL_RED_LINES


class TestCanonicalBattery:
    def test_one_case_per_classification(self) -> None:
        battery = canonical_battery()
        assert len(battery) == len(Classification) == 5
        assert {case.intent for case in battery} == set(Classification)

    def test_case_names_are_unique_and_kebab(self) -> None:
        names = [case.name for case in canonical_battery()]
        assert len(names) == len(set(names))
        assert all(name == name.lower().strip() for name in names)

    def test_battery_is_deterministic(self) -> None:
        first = canonical_battery()
        second = canonical_battery()
        assert [c.name for c in first] == [c.name for c in second]
        assert [c.action.scope for c in first] == [c.action.scope for c in second]

    def test_case_validation_fails_closed(self) -> None:
        action = canonical_battery()[0].action
        with pytest.raises(ValueError):
            CoverageCase(name="  ", intent=Classification.COMPLIANT, action=action)
        with pytest.raises(TypeError):
            CoverageCase(name="x", intent="compliant", action=action)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            CoverageCase(name="x", intent=Classification.COMPLIANT, action="nope")  # type: ignore[arg-type]


class TestOutcomeCoverageOnLiveRegistry:
    def test_all_five_outcomes_are_reachable(self) -> None:
        report = run_outcome_coverage()
        assert report.complete is True
        assert report.unreached == ()
        assert set(report.reached) == set(Classification)

    def test_every_case_reaches_its_intended_outcome(self) -> None:
        report = run_outcome_coverage()
        assert report.all_matched is True
        for result in report.results:
            assert result.reached is result.intent
            assert result.matched is True

    def test_reason_codes_are_recorded_per_case(self) -> None:
        by_name = {result.name: result for result in run_outcome_coverage().results}
        assert AssessmentReasonCode.INTAKE_BLOCKED in by_name["insufficient-information"].reason_codes
        assert AssessmentReasonCode.OUTSIDE_SCOPE in by_name["outside-scope"].reason_codes
        assert AssessmentReasonCode.VERIFIED_EXEMPTION in by_name["compliant"].reason_codes
        assert (
            AssessmentReasonCode.MULTIPLE_PROHIBITED_DIMENSIONS
            in by_name["requires-modification"].reason_codes
        )
        assert AssessmentReasonCode.UNEXEMPTED_LINE in by_name["non-compliant"].reason_codes

    def test_report_is_deterministic(self) -> None:
        assert run_outcome_coverage() == run_outcome_coverage()
        assert run_outcome_coverage().as_of == BATTERY_AS_OF

    def test_reached_uses_enum_definition_order(self) -> None:
        report = run_outcome_coverage()
        order = {classification: index for index, classification in enumerate(Classification)}
        indices = [order[c] for c in report.reached]
        assert indices == sorted(indices)


class TestNegativeControls:
    def test_empty_registry_makes_implication_outcomes_unreachable(self) -> None:
        report = run_outcome_coverage(lines=())
        assert report.complete is False
        assert report.all_matched is False
        assert set(report.unreached) == {
            Classification.COMPLIANT,
            Classification.REQUIRES_MODIFICATION,
            Classification.NON_COMPLIANT,
        }

    def test_single_line_registry_reports_partial_coverage(self) -> None:
        s1_only = tuple(line for line in PERSONAL_RED_LINES if line.id == "s1-human-control-force")
        assert len(s1_only) == 1
        report = run_outcome_coverage(lines=s1_only)
        assert report.complete is False
        by_name = {result.name: result for result in report.results}
        # The targeting case still hard-blocks; the profiling case no longer
        # implicates any line and honestly lands outside scope.
        assert by_name["non-compliant"].reached is Classification.NON_COMPLIANT
        assert by_name["requires-modification"].reached is Classification.OUTSIDE_SCOPE
        assert by_name["requires-modification"].matched is False

    def test_stale_review_date_downgrades_evidence(self) -> None:
        # 181+ days after the fixture evidence date, every VERIFIED record is
        # stale and even the compliant case fails closed to an information stop.
        report = run_outcome_coverage(as_of="2027-07-15")
        by_name = {result.name: result for result in report.results}
        assert by_name["compliant"].reached is Classification.INSUFFICIENT_INFORMATION
        assert report.complete is False


class TestInputValidation:
    def test_malformed_as_of_fails_closed(self) -> None:
        with pytest.raises(ValueError):
            run_outcome_coverage(as_of="not-a-date")
        with pytest.raises(TypeError):
            run_outcome_coverage(as_of=20260715)  # type: ignore[arg-type]

    def test_battery_entries_are_type_checked(self) -> None:
        with pytest.raises(TypeError):
            run_outcome_coverage(battery=("not a case",))  # type: ignore[arg-type]

    def test_custom_battery_is_honoured(self) -> None:
        case = canonical_battery()[1]
        report = run_outcome_coverage(battery=(case,))
        assert len(report.results) == 1
        assert report.results[0].reached is Classification.OUTSIDE_SCOPE
        assert report.complete is False

    def test_battery_actions_are_real_proposed_actions(self) -> None:
        for case in canonical_battery():
            assert isinstance(case.action, ProposedAction)
            assert case.action.tier is DeploymentTier.HOSTED
