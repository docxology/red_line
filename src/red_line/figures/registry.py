"""Registry of deterministic figure generators."""

from __future__ import annotations

from .diagrams import (
    canary_trust_boundary,
    evaluation_path,
    governance_architecture,
    improvement_method_loop,
    line_set_compass,
    outcome_precedence,
    tier_ladder,
)
from .plates_analysis import (
    evidence_gate_sensitivity,
    exemption_evidence_matrix_figure,
    exemption_trigger_semantics,
    outcome_coverage_plate,
    registry_composition_profile,
    scope_vocabulary_collisions,
    tier_monotonicity_lattice,
)
from .plates_scholarship import (
    boundary_instrument_plate,
    scholarship_map,
    scholarship_intake_bridge,
    scholarship_transfer_matrix,
)

GENERATORS = {
    "fig:governance-architecture": governance_architecture,
    "fig:oversight-tier-ladder": tier_ladder,
    "fig:evaluation-decision-path": evaluation_path,
    "fig:canary-trust-boundary": canary_trust_boundary,
    "fig:scholarship-reading-map": scholarship_map,
    "fig:line-set-compass": line_set_compass,
    "fig:scholarship-transfer-matrix": scholarship_transfer_matrix,
    "fig:outcome-precedence": outcome_precedence,
    "fig:improvement-method-loop": improvement_method_loop,
    "fig:boundary-instrument-plate": boundary_instrument_plate,
    "fig:scholarship-intake-bridge": scholarship_intake_bridge,
    "fig:exemption-evidence-matrix": exemption_evidence_matrix_figure,
    "fig:outcome-coverage-plate": outcome_coverage_plate,
    "fig:tier-monotonicity-lattice": tier_monotonicity_lattice,
    "fig:registry-composition-profile": registry_composition_profile,
    "fig:scope-vocabulary-collisions": scope_vocabulary_collisions,
    "fig:evidence-gate-sensitivity": evidence_gate_sensitivity,
    "fig:exemption-trigger-semantics": exemption_trigger_semantics,
}
