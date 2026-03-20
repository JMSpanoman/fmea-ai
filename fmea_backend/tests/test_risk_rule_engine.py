"""Tests for deterministic risk acceptability rule engine."""

import pytest

from schemas.risk_rule_engine import FmeaRiskEvaluationInput, RiskCriteriaConfig, RiskEvaluationResult
from services import risk_rule_engine as eng
from services.risk_rule_engine_defaults import build_default_criteria_payload

# Attestations for structured benefit–risk workflow when formal B–R pathway applies (death-severity, etc.)
FULL_BRA_ATTESTATIONS = {
    "bra_clinical_benefit_documented": True,
    "bra_benefit_vs_residual_risk_documented": True,
    "bra_state_of_the_art_documented": True,
    "bra_supporting_evidence_addressed": True,
    "bra_approval_clinical_medical_recorded": True,
    "bra_approval_quality_regulatory_recorded": True,
    "bra_approval_design_authority_recorded": True,
}


def test_matrix_s4_p1_alarp(pacemaker_criteria_dict):
    row = {"severity": 10, "probability": 1, "detection": 1, "reviewer_justification": "ok"}
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict, component_name="")
    assert r["ok"] is True
    assert r["classification"] == "ALARP"
    assert r["benefit_risk_required"] is True


def test_matrix_s2_p4_unacceptable(pacemaker_criteria_dict):
    row = {"severity": 6, "probability": 10, "detection": 1, "reviewer_justification": "x"}
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict, component_name="")
    assert r["ok"] is True
    assert r["classification"] == "Unacceptable"
    assert r["approval_blocked"] is True


def test_critical_function_keyword_escalation(pacemaker_criteria_dict):
    row = {
        "severity": 3,
        "probability": 3,
        "detection": 1,
        "failure_mode": "Loss of pacing due to battery depletion",
        "reviewer_justification": "documented",
        "system_level_verification_recorded": True,
    }
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict, component_name="")
    assert r["ok"] is True
    assert r["classification"] == "ALARP"
    assert r["critical_function_flag"] is True
    assert any("critical_function" in x for x in r["matched_rules"])


def test_residual_requires_separate_inputs(pacemaker_criteria_dict):
    row = {
        "severity": 4,
        "probability": 4,
        "residual_severity": 9,
        "residual_probability": 2,
        "residual_detection": 1,
        "reviewer_justification": "Residual rationale documented for S3 band.",
    }
    r = eng.evaluate_residual_risk(row, pacemaker_criteria_dict, component_name="")
    assert r["ok"] is True
    assert r["reviewer_justification_required"] is True


def test_residual_justification_missing_blocks(pacemaker_criteria_dict):
    row = {
        "severity": 4,
        "probability": 4,
        "residual_severity": 9,
        "residual_probability": 2,
        "residual_detection": 1,
        "reviewer_justification": "",
    }
    r = eng.evaluate_residual_risk(row, pacemaker_criteria_dict, component_name="")
    assert r["ok"] is True
    assert r["approval_blocked"] is True


def test_invalid_scale_errors(pacemaker_criteria_dict):
    row = {"severity": None, "probability": 3, "detection": 1}
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict, component_name="")
    assert r["ok"] is False
    assert r["validation_errors"]


def test_incomplete_matrix_rejected():
    bad = build_default_criteria_payload(include_pacemaker_rules=False)
    bad["risk_matrix"] = {"1": {"1": "Acceptable"}}  # incomplete
    row = {"severity": 5, "probability": 5, "detection": 1, "reviewer_justification": "x"}
    r = eng.evaluate_initial_risk(row, bad, component_name="")
    assert r["ok"] is False
    assert r["validation_errors"]


def test_score_method_requires_thresholds():
    crit = build_default_criteria_payload(include_pacemaker_rules=False)
    crit["evaluation_method"] = "score"
    crit["score_thresholds"] = {}
    row = {"severity": 2, "probability": 2, "detection": 2, "reviewer_justification": "x"}
    r = eng.evaluate_initial_risk(row, crit, component_name="")
    assert r["ok"] is False


def test_hybrid_worse_of_matrix_and_score():
    crit = build_default_criteria_payload(include_pacemaker_rules=False)
    crit["evaluation_method"] = "hybrid"
    crit["score_thresholds"] = {
        "acceptable_max_rpn": 8,
        "alarp_max_rpn": 50,
        "fmea_severity_to_matrix_index": {str(i): min(4, max(1, (i + 2) // 3)) for i in range(1, 11)},
        "fmea_occurrence_to_matrix_index": {str(i): min(4, max(1, (i + 2) // 3)) for i in range(1, 11)},
    }
    row = {"severity": 10, "probability": 10, "detection": 10, "reviewer_justification": "x"}
    r = eng.evaluate_initial_risk(row, crit, component_name="")
    assert r["ok"] is True
    assert r["classification"] == "Unacceptable"


def test_global_summary_counts():
    class R:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    rows = [
        R(
            id="1",
            residual_risk_classification="Acceptable",
            benefit_risk_required=False,
            approval_blocked=False,
            critical_function_flag=False,
            residual_rpn=10,
            failure_mode="a",
            effect="b",
        ),
        R(
            id="2",
            residual_risk_classification="Unacceptable",
            benefit_risk_required=True,
            approval_blocked=True,
            critical_function_flag=True,
            residual_rpn=500,
            failure_mode="c",
            effect="d",
        ),
    ]
    s = eng.build_global_residual_summary(
        project_id="p",
        criteria_version=3,
        rows=rows,
        criteria_dict={"special_rules": {"global_residual_acceptability_policy": {"enabled": False}}},
    )
    assert s["total_rows"] == 2
    assert s["residual_summary"]["unacceptable"] == 1
    assert s["approval_blocked_count"] == 1
    assert s["global_residual_acceptability"]["policy_applied"] is False


def test_global_residual_acceptability_requires_unacceptable_escape():
    class R:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    crit = {"special_rules": {}}
    rows = [
        R(
            id="a",
            residual_risk_classification="Unacceptable",
            benefit_risk_analysis_approved=False,
            additional_controls_reduced_risk=False,
            approval_blocked=False,
        )
    ]
    g = eng.evaluate_global_residual_acceptability(
        rows=rows,
        criteria_dict=crit,
        project_attestations={
            "overall_device_benefit_risk_profile_acceptable": True,
            "rmr_overall_residual_risk_conclusion_documented": True,
        },
    )
    assert g["overall_acceptable"] is False
    assert any("Unacceptable" in b for b in g["blockers"])

    rows[0].benefit_risk_analysis_approved = True
    g2 = eng.evaluate_global_residual_acceptability(
        rows=rows,
        criteria_dict=crit,
        project_attestations={
            "overall_device_benefit_risk_profile_acceptable": True,
            "rmr_overall_residual_risk_conclusion_documented": True,
        },
    )
    assert g2["overall_acceptable"] is True


def test_global_residual_acceptability_blocks_release_and_requires_profile_attestations():
    class R:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    crit = {"special_rules": {}}
    rows = [
        R(
            id="b",
            residual_risk_classification="ALARP",
            benefit_risk_analysis_approved=False,
            additional_controls_reduced_risk=False,
            approval_blocked=True,
        )
    ]
    g = eng.evaluate_global_residual_acceptability(
        rows=rows,
        criteria_dict=crit,
        project_attestations={
            "overall_device_benefit_risk_profile_acceptable": True,
            "rmr_overall_residual_risk_conclusion_documented": True,
        },
    )
    assert g["overall_acceptable"] is False

    rows[0].approval_blocked = False
    g2 = eng.evaluate_global_residual_acceptability(rows=rows, criteria_dict=crit, project_attestations={})
    assert g2["overall_acceptable"] is False
    assert any("Project Setup" in b for b in g2["blockers"])


def test_pacemaker_scenarios(pacemaker_criteria_dict):
    scenarios = [
        ("loss of pacing", True),
        ("incorrect pacing waveform", True),
        ("battery depletion alarm", True),
        ("lead fracture detected", True),
        ("sensing failure in channel A", True),
        ("therapy delivery failure post shock", True),
        ("cosmetic label peel", False),
    ]
    for text, want_flag in scenarios:
        row = {
            "severity": 4,
            "probability": 4,
            "detection": 1,
            "failure_mode": text,
            "reviewer_justification": "justified",
            "system_level_verification_recorded": True,
        }
        r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict, component_name="")
        assert r["ok"] is True
        assert r["critical_function_flag"] is want_flag, text


def test_json_fixture_evaluates_same_as_builder(pacemaker_criteria_dict, pacemaker_criteria_from_json_file):
    """JSON uses string keys for nested maps; Python builder may use int keys — behavior must match."""
    row = {"severity": 10, "probability": 1, "detection": 1, "reviewer_justification": "ok"}
    a = eng.evaluate_initial_risk(row, pacemaker_criteria_dict)
    b = eng.evaluate_initial_risk(row, pacemaker_criteria_from_json_file)
    assert a == b


def test_risk_criteria_config_roundtrip(pacemaker_criteria_dict):
    cfg = RiskCriteriaConfig.model_validate(pacemaker_criteria_dict)
    again = cfg.to_engine_dict()
    assert again["evaluation_method"] == pacemaker_criteria_dict["evaluation_method"]
    assert again["risk_matrix"] == pacemaker_criteria_dict["risk_matrix"]


def test_evaluation_to_result_pydantic(pacemaker_criteria_dict):
    row = {"severity": 5, "probability": 5, "detection": 1, "reviewer_justification": "ok"}
    raw = eng.evaluate_initial_risk(row, pacemaker_criteria_dict)
    model = eng.evaluation_to_result(raw)
    assert isinstance(model, RiskEvaluationResult)
    assert model.ok is True
    assert model.classification in ("Acceptable", "ALARP", "Unacceptable")
    assert isinstance(model.matched_rules, list)
    assert len(model.decision_path) >= 1
    assert model.matrix_indices is not None
    assert model.matrix_indices.severity >= 1


def test_evaluate_initial_risk_model(pacemaker_criteria_dict):
    cfg = RiskCriteriaConfig.model_validate(pacemaker_criteria_dict)
    row = FmeaRiskEvaluationInput.model_validate(
        {
            "severity": 10,
            "probability": 1,
            "detection": 1,
            "reviewer_justification": "Documented",
            "benefit_risk_formal_approval_recorded": True,
            "system_level_verification_recorded": True,
            "failure_mode": "sensing failure observed in clinic",
            **FULL_BRA_ATTESTATIONS,
        }
    )
    out = eng.evaluate_initial_risk_model(row, cfg)
    assert out.ok is True
    assert out.benefit_risk_required is True
    assert out.critical_function_flag is True
    assert any("matrix:" in x for x in out.matched_rules)


def test_mandatory_death_fmea_severity_requires_formal_bra(pacemaker_criteria_dict):
    row = {
        "severity": 5,
        "probability": 1,
        "detection": 1,
        "reviewer_justification": "ok",
    }
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict)
    assert r["ok"] is True
    assert r["benefit_risk_formal_approval_required"] is True
    assert r["acceptable_for_release"] is False
    assert r["benefit_risk_structured_workflow_active"] is True
    assert any(
        "benefit" in b.lower() or "clinical" in b.lower() or "formal" in b.lower()
        for b in r["release_blockers"]
    )


def test_mandatory_death_formal_bra_recorded_clears_gate(pacemaker_criteria_dict):
    row = {
        "severity": 5,
        "probability": 1,
        "detection": 1,
        "reviewer_justification": "ok",
        "benefit_risk_formal_approval_recorded": True,
        **FULL_BRA_ATTESTATIONS,
    }
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict)
    assert r["ok"] is True
    assert r["acceptable_for_release"] is True


def test_unacceptable_release_via_approved_benefit_risk(pacemaker_criteria_dict):
    row = {
        "severity": 10,
        "probability": 10,
        "detection": 10,
        "reviewer_justification": "Documented",
        "benefit_risk_formal_approval_recorded": True,
        "benefit_risk_analysis_approved": True,
        **FULL_BRA_ATTESTATIONS,
    }
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict)
    assert r["classification"] == "Unacceptable"
    assert r["acceptable_for_release"] is True


def test_residual_fmea_severity_4_requires_cross_functional_and_release_approval(pacemaker_criteria_dict):
    row = {
        "severity": 3,
        "probability": 3,
        "residual_severity": 4,
        "residual_probability": 1,
        "residual_detection": 1,
        "reviewer_justification": "Residual justification documented.",
    }
    r = eng.evaluate_residual_risk(row, pacemaker_criteria_dict)
    assert r["ok"] is True
    assert r["cross_functional_review_required"] is True
    assert r["formal_release_approval_required"] is True
    assert r["acceptable_for_release"] is False


def test_critical_hazard_forces_minimum_matrix_severity_band(pacemaker_criteria_dict):
    row = {
        "severity": 1,
        "probability": 1,
        "detection": 1,
        "failure_mode": "Loss of pacing",
        "reviewer_justification": "Clinical rationale documented.",
        "system_level_verification_recorded": True,
    }
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict)
    assert r["ok"] is True
    assert r["critical_hazard_category_match"] is True
    assert r["matrix_indices"]["severity"] == 4
    assert r["input_fmea_severity"] == 1
    assert r["evaluated_fmea_severity"] == 1


def test_critical_hazard_risk_eliminated_skips_justification_requirement(pacemaker_criteria_dict):
    row = {
        "severity": 1,
        "probability": 1,
        "detection": 1,
        "failure_mode": "Sensing failure mode",
        "reviewer_justification": "",
        "risk_eliminated": True,
        "system_level_verification_recorded": True,
    }
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict)
    assert r["ok"] is True
    assert r["critical_hazard_category_match"] is True
    assert r["reviewer_justification_required"] is False


def test_critical_hazard_policies_disabled(pacemaker_criteria_dict):
    crit = dict(pacemaker_criteria_dict)
    sr = dict(crit.get("special_rules") or {})
    sr["critical_hazard_policies"] = {"enabled": False}
    crit["special_rules"] = sr
    row = {
        "severity": 1,
        "probability": 1,
        "detection": 1,
        "failure_mode": "loss of pacing",
        "reviewer_justification": "",
    }
    r = eng.evaluate_initial_risk(row, crit)
    assert r["ok"] is True
    assert r["critical_hazard_category_match"] is False
    assert r["matrix_indices"]["severity"] == 1


def test_residual_acceptable_requires_documented_rationale(pacemaker_criteria_dict):
    row = {
        "severity": 1,
        "probability": 1,
        "residual_severity": 1,
        "residual_probability": 1,
        "residual_detection": 1,
        "reviewer_justification": "",
    }
    r = eng.evaluate_residual_risk(row, pacemaker_criteria_dict)
    assert r["ok"] is True
    assert r["classification"] == "Acceptable"
    assert r["residual_acceptable_rationale_required"] is True
    assert r["approval_blocked"] is True


def test_residual_acceptability_policies_disabled_allows_acceptable_without_text(pacemaker_criteria_dict):
    crit = dict(pacemaker_criteria_dict)
    sr = dict(crit.get("special_rules") or {})
    sr["residual_acceptability_policies"] = {"enabled": False}
    crit["special_rules"] = sr
    row = {
        "severity": 1,
        "probability": 1,
        "residual_severity": 1,
        "residual_probability": 1,
        "residual_detection": 1,
        "reviewer_justification": "",
    }
    r = eng.evaluate_residual_risk(row, crit)
    assert r["ok"] is True
    assert r["classification"] == "Acceptable"
    assert r["residual_acceptable_rationale_required"] is False
    assert r["approval_blocked"] is False


def test_residual_alarp_requires_feasibility_attestations_and_formal_release(pacemaker_criteria_dict):
    row = {
        "severity": 5,
        "probability": 5,
        "residual_severity": 1,
        "residual_probability": 7,
        "residual_detection": 1,
        "reviewer_justification": "Feasible controls implemented; further reduction not practicable.",
        "benefit_risk_formal_approval_recorded": True,
        **FULL_BRA_ATTESTATIONS,
        "formal_release_approval_recorded": True,
    }
    r = eng.evaluate_residual_risk(row, pacemaker_criteria_dict)
    assert r["ok"] is True
    assert r["classification"] == "ALARP"
    assert r["residual_alarp_feasibility_attestations_required"] is True
    assert r["formal_release_approval_required"] is True
    assert r["approval_blocked"] is True
    assert any("feasible" in b.lower() for b in r["release_blockers"])


def test_residual_alarp_all_gates_satisfied(pacemaker_criteria_dict):
    row = {
        "severity": 5,
        "probability": 5,
        "residual_severity": 1,
        "residual_probability": 7,
        "residual_detection": 1,
        "reviewer_justification": "Feasible controls implemented; further reduction not practicable.",
        "benefit_risk_formal_approval_recorded": True,
        **FULL_BRA_ATTESTATIONS,
        "residual_all_feasible_controls_implemented": True,
        "residual_further_reduction_not_practicable": True,
        "formal_release_approval_recorded": True,
    }
    r = eng.evaluate_residual_risk(row, pacemaker_criteria_dict)
    assert r["ok"] is True
    assert r["classification"] == "ALARP"
    assert r["acceptable_for_release"] is True


def test_benefit_risk_workflow_missing_documentation_blocks(pacemaker_criteria_dict):
    row = {
        "severity": 5,
        "probability": 1,
        "detection": 1,
        "reviewer_justification": "ok",
        "bra_approval_clinical_medical_recorded": True,
        "bra_approval_quality_regulatory_recorded": True,
        "bra_approval_design_authority_recorded": True,
    }
    r = eng.evaluate_initial_risk(row, pacemaker_criteria_dict)
    assert r["ok"] is True
    assert r["benefit_risk_structured_workflow_active"] is True
    assert r["approval_blocked"] is True
    assert any("clinical benefit" in b.lower() for b in r["release_blockers"])


def test_benefit_risk_workflow_disabled_uses_legacy_single_formal_flag(pacemaker_criteria_dict):
    crit = dict(pacemaker_criteria_dict)
    sr = dict(crit.get("special_rules") or {})
    sr["benefit_risk_workflow_policy"] = {"enabled": False}
    crit["special_rules"] = sr
    row = {
        "severity": 5,
        "probability": 1,
        "detection": 1,
        "reviewer_justification": "ok",
        "benefit_risk_formal_approval_recorded": True,
    }
    r = eng.evaluate_initial_risk(row, crit)
    assert r["ok"] is True
    assert r["benefit_risk_structured_workflow_active"] is False
    assert r["acceptable_for_release"] is True


def test_mandatory_policies_disabled_skips_formal_bra_gate(pacemaker_criteria_dict):
    crit = dict(pacemaker_criteria_dict)
    sr = dict(crit.get("special_rules") or {})
    sr["mandatory_policies"] = {"enabled": False}
    crit["special_rules"] = sr
    row = {
        "severity": 5,
        "probability": 1,
        "detection": 1,
        "reviewer_justification": "ok",
    }
    r = eng.evaluate_initial_risk(row, crit)
    assert r["ok"] is True
    assert r["benefit_risk_formal_approval_required"] is False
    assert r["acceptable_for_release"] is True
