"""
Persist rule-engine outputs to FMEA rows and append audit records.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.fmea import FMEARow
from models.project_risk_criteria import RuleEvaluationAudit
from services import risk_rule_engine as engine


def _merge_stored_results(existing: Optional[Dict[str, Any]], key: str, result: Dict[str, Any]) -> Dict[str, Any]:
    base = dict(existing) if isinstance(existing, dict) else {}
    base[key] = {k: result.get(k) for k in result.keys()}
    return base


def recompute_aggregate_flags(row: FMEARow) -> None:
    """Derive row-level booleans from stored initial + residual engine results."""
    j = row.rule_engine_result_json if isinstance(row.rule_engine_result_json, dict) else {}
    ri = j.get("initial") if isinstance(j.get("initial"), dict) else {}
    rr = j.get("residual") if isinstance(j.get("residual"), dict) else {}

    row.benefit_risk_required = bool(ri.get("benefit_risk_required")) or bool(rr.get("benefit_risk_required"))
    row.critical_function_flag = bool(ri.get("critical_function_flag")) or bool(rr.get("critical_function_flag"))
    row.system_level_verification_required = bool(ri.get("system_level_verification_required")) or bool(
        rr.get("system_level_verification_required")
    )
    row.critical_hazard_category_flag = bool(ri.get("critical_hazard_category_match")) or bool(
        rr.get("critical_hazard_category_match")
    )

    blocked = bool(ri.get("approval_blocked")) or bool(rr.get("approval_blocked"))
    row.approval_blocked = blocked

    acceptable = True
    has_eval = False
    for part in (ri, rr):
        if isinstance(part, dict) and part.get("ok") is True:
            has_eval = True
            if part.get("acceptable_for_release") is False:
                acceptable = False
    row.acceptable_for_release = acceptable if has_eval else getattr(row, "acceptable_for_release", True)


def persist_audit_record(
    db: Session,
    *,
    fmea_row_id: str,
    project_id: str,
    criteria_version: int,
    evaluation_type: str,
    inputs: Dict[str, Any],
    result: Dict[str, Any],
) -> RuleEvaluationAudit:
    audit = RuleEvaluationAudit(
        fmea_row_id=fmea_row_id,
        project_id=project_id,
        criteria_version=criteria_version,
        evaluation_type=evaluation_type,
        inputs_json=inputs,
        matched_rules_json=result.get("matched_rules"),
        output_json=result,
        decision_path_text="\n".join(f"- {x}" for x in (result.get("decision_path") or [])),
    )
    db.add(audit)
    return audit


def apply_initial_evaluation(
    db: Session,
    row: FMEARow,
    criteria_version: int,
    result: Dict[str, Any],
    inputs: Dict[str, Any],
) -> None:
    row.initial_risk_classification = result.get("classification")
    row.rule_engine_result_json = _merge_stored_results(row.rule_engine_result_json, "initial", result)
    row.risk_criteria_version_applied = criteria_version
    recompute_aggregate_flags(row)
    persist_audit_record(
        db,
        fmea_row_id=row.id,
        project_id=row.project_id,
        criteria_version=criteria_version,
        evaluation_type="initial",
        inputs=inputs,
        result=result,
    )


def apply_residual_evaluation(
    db: Session,
    row: FMEARow,
    criteria_version: int,
    result: Dict[str, Any],
    inputs: Dict[str, Any],
) -> None:
    row.residual_risk_classification = result.get("classification")
    row.rule_engine_result_json = _merge_stored_results(row.rule_engine_result_json, "residual", result)
    row.risk_criteria_version_applied = criteria_version
    recompute_aggregate_flags(row)
    persist_audit_record(
        db,
        fmea_row_id=row.id,
        project_id=row.project_id,
        criteria_version=criteria_version,
        evaluation_type="residual",
        inputs=inputs,
        result=result,
    )


def evaluation_inputs_snapshot(row: FMEARow, evaluation_type: str) -> Dict[str, Any]:
    d = engine.row_to_dict(row)
    d["evaluation_type"] = evaluation_type
    return d


def resolve_criteria_for_evaluation(db: Session, project_id: str, criteria_id: Optional[str] = None):
    from crud import project_risk_criteria as prc

    if criteria_id:
        c = prc.get_criteria(db, criteria_id, project_id)
        if not c:
            return None, None
        return c, engine.criteria_entity_to_dict(c)
    c = prc.get_latest_approved(db, project_id) or prc.get_latest_any(db, project_id)
    if not c:
        return None, None
    return c, engine.criteria_entity_to_dict(c)
