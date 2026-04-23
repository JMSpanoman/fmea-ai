from sqlalchemy.orm import Session
from models.fmea import FMEARow
from models.fmea_version import FMEAVersion
from schemas.fmea import FMEARowCreate, FMEARowUpdate
from typing import List, Optional, Dict, Any
import uuid
import json

def _calculate_rpn(severity: Optional[int], probability: Optional[int], detection: Optional[int]) -> Optional[int]:
    """Calculate RPN from severity, probability, and detection"""
    if severity is not None and probability is not None and detection is not None:
        return severity * probability * detection
    return None

def _calculate_diff(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate diff between old and new FMEA row data"""
    diff = {}
    for key in set(old_data.keys()) | set(new_data.keys()):
        old_val = old_data.get(key)
        new_val = new_data.get(key)
        if old_val != new_val:
            diff[key] = {"old": old_val, "new": new_val}
    return diff

def _serialize_for_diff(row: FMEARow) -> Dict[str, Any]:
    """Serialize FMEA row for diff calculation"""
    return {
        "device_function": getattr(row, "device_function", None),
        "failure_mode": row.failure_mode,
        "effect": row.effect,
        "cause": row.cause,
        "hazard": getattr(row, "hazard", None),
        "harm": getattr(row, "harm", None),
        "severity": row.severity,
        "probability": row.probability,
        "detection": row.detection,
        "rpn": row.rpn,
        "mitigation": row.mitigation,
        "action_taken": getattr(row, "action_taken", None),
        "residual_severity": row.residual_severity,
        "residual_probability": row.residual_probability,
        "residual_detection": row.residual_detection,
        "residual_rpn": row.residual_rpn,
        "financial_impact": float(row.financial_impact) if row.financial_impact else None,
        "component_id": row.component_id,
        "hazard_library_id": getattr(row, "hazard_library_id", None),
        "harm_library_id": getattr(row, "harm_library_id", None),
        "risk_control_library_id": getattr(row, "risk_control_library_id", None),
        "verification_library_id": getattr(row, "verification_library_id", None),
        "initial_risk_classification": getattr(row, "initial_risk_classification", None),
        "residual_risk_classification": getattr(row, "residual_risk_classification", None),
        "benefit_risk_required": getattr(row, "benefit_risk_required", None),
        "reviewer_justification": getattr(row, "reviewer_justification", None),
        "reviewer_name": getattr(row, "reviewer_name", None),
        "reviewer_date": getattr(row, "reviewer_date", None),
        "critical_function_flag": getattr(row, "critical_function_flag", None),
        "approval_blocked": getattr(row, "approval_blocked", None),
        "acceptable_for_release": getattr(row, "acceptable_for_release", None),
        "benefit_risk_formal_approval_recorded": getattr(row, "benefit_risk_formal_approval_recorded", None),
        "bra_clinical_benefit_documented": getattr(row, "bra_clinical_benefit_documented", None),
        "bra_benefit_vs_residual_risk_documented": getattr(row, "bra_benefit_vs_residual_risk_documented", None),
        "bra_state_of_the_art_documented": getattr(row, "bra_state_of_the_art_documented", None),
        "bra_supporting_evidence_addressed": getattr(row, "bra_supporting_evidence_addressed", None),
        "bra_approval_clinical_medical_recorded": getattr(row, "bra_approval_clinical_medical_recorded", None),
        "bra_approval_quality_regulatory_recorded": getattr(row, "bra_approval_quality_regulatory_recorded", None),
        "bra_approval_design_authority_recorded": getattr(row, "bra_approval_design_authority_recorded", None),
        "cross_functional_review_completed": getattr(row, "cross_functional_review_completed", None),
        "formal_release_approval_recorded": getattr(row, "formal_release_approval_recorded", None),
        "additional_controls_reduced_risk": getattr(row, "additional_controls_reduced_risk", None),
        "benefit_risk_analysis_approved": getattr(row, "benefit_risk_analysis_approved", None),
        "critical_hazard_severity_floor_waived": getattr(row, "critical_hazard_severity_floor_waived", None),
        "risk_eliminated": getattr(row, "risk_eliminated", None),
        "system_level_verification_recorded": getattr(row, "system_level_verification_recorded", None),
        "critical_hazard_category_flag": getattr(row, "critical_hazard_category_flag", None),
        "system_level_verification_required": getattr(row, "system_level_verification_required", None),
        "residual_all_feasible_controls_implemented": getattr(
            row, "residual_all_feasible_controls_implemented", None
        ),
        "residual_further_reduction_not_practicable": getattr(
            row, "residual_further_reduction_not_practicable", None
        ),
        "rule_engine_result_json": getattr(row, "rule_engine_result_json", None),
        "ai_suggested_values_json": getattr(row, "ai_suggested_values_json", None),
        "risk_criteria_version_applied": getattr(row, "risk_criteria_version_applied", None),
        "evidence_source": getattr(row, "evidence_source", None),
        "postmarket_review_status": getattr(row, "postmarket_review_status", None),
        "postmarket_evidence_summary": getattr(row, "postmarket_evidence_summary", None),
    }

def create_fmea_row(db: Session, fmea_row: FMEARowCreate) -> FMEARow:
    """Create a new FMEA row with auto-calculated RPN"""
    db_row = FMEARow(
        id=str(uuid.uuid4()),
        project_id=fmea_row.project_id,
        component_id=fmea_row.component_id,
        device_function=getattr(fmea_row, "device_function", None),
        failure_mode=fmea_row.failure_mode,
        effect=fmea_row.effect,
        cause=fmea_row.cause,
        hazard=getattr(fmea_row, "hazard", None),
        harm=getattr(fmea_row, "harm", None),
        severity=fmea_row.severity,
        probability=fmea_row.probability,
        detection=fmea_row.detection,
        mitigation=fmea_row.mitigation,
        action_taken=getattr(fmea_row, "action_taken", None),
        residual_severity=fmea_row.residual_severity,
        residual_probability=fmea_row.residual_probability,
        residual_detection=fmea_row.residual_detection,
        financial_impact=fmea_row.financial_impact,
        ai_metadata=fmea_row.ai_metadata,
        evidence_source=getattr(fmea_row, "evidence_source", None),
        postmarket_review_status=getattr(fmea_row, "postmarket_review_status", None),
        postmarket_evidence_summary=getattr(fmea_row, "postmarket_evidence_summary", None),
        hazard_library_id=getattr(fmea_row, "hazard_library_id", None),
        harm_library_id=getattr(fmea_row, "harm_library_id", None),
        risk_control_library_id=getattr(fmea_row, "risk_control_library_id", None),
        verification_library_id=getattr(fmea_row, "verification_library_id", None),
        initial_risk_classification=getattr(fmea_row, "initial_risk_classification", None),
        residual_risk_classification=getattr(fmea_row, "residual_risk_classification", None),
        benefit_risk_required=bool(getattr(fmea_row, "benefit_risk_required", False)),
        reviewer_justification=getattr(fmea_row, "reviewer_justification", None),
        reviewer_name=getattr(fmea_row, "reviewer_name", None),
        reviewer_date=getattr(fmea_row, "reviewer_date", None),
        critical_function_flag=bool(getattr(fmea_row, "critical_function_flag", False)),
        approval_blocked=bool(getattr(fmea_row, "approval_blocked", False)),
        acceptable_for_release=bool(getattr(fmea_row, "acceptable_for_release", True)),
        benefit_risk_formal_approval_recorded=bool(
            getattr(fmea_row, "benefit_risk_formal_approval_recorded", False)
        ),
        bra_clinical_benefit_documented=bool(getattr(fmea_row, "bra_clinical_benefit_documented", False)),
        bra_benefit_vs_residual_risk_documented=bool(
            getattr(fmea_row, "bra_benefit_vs_residual_risk_documented", False)
        ),
        bra_state_of_the_art_documented=bool(getattr(fmea_row, "bra_state_of_the_art_documented", False)),
        bra_supporting_evidence_addressed=bool(getattr(fmea_row, "bra_supporting_evidence_addressed", False)),
        bra_approval_clinical_medical_recorded=bool(
            getattr(fmea_row, "bra_approval_clinical_medical_recorded", False)
        ),
        bra_approval_quality_regulatory_recorded=bool(
            getattr(fmea_row, "bra_approval_quality_regulatory_recorded", False)
        ),
        bra_approval_design_authority_recorded=bool(
            getattr(fmea_row, "bra_approval_design_authority_recorded", False)
        ),
        cross_functional_review_completed=bool(getattr(fmea_row, "cross_functional_review_completed", False)),
        formal_release_approval_recorded=bool(getattr(fmea_row, "formal_release_approval_recorded", False)),
        additional_controls_reduced_risk=bool(getattr(fmea_row, "additional_controls_reduced_risk", False)),
        benefit_risk_analysis_approved=bool(getattr(fmea_row, "benefit_risk_analysis_approved", False)),
        critical_hazard_severity_floor_waived=bool(
            getattr(fmea_row, "critical_hazard_severity_floor_waived", False)
        ),
        risk_eliminated=bool(getattr(fmea_row, "risk_eliminated", False)),
        system_level_verification_recorded=bool(getattr(fmea_row, "system_level_verification_recorded", False)),
        critical_hazard_category_flag=bool(getattr(fmea_row, "critical_hazard_category_flag", False)),
        system_level_verification_required=bool(getattr(fmea_row, "system_level_verification_required", False)),
        residual_all_feasible_controls_implemented=bool(
            getattr(fmea_row, "residual_all_feasible_controls_implemented", False)
        ),
        residual_further_reduction_not_practicable=bool(
            getattr(fmea_row, "residual_further_reduction_not_practicable", False)
        ),
        rule_engine_result_json=getattr(fmea_row, "rule_engine_result_json", None),
        ai_suggested_values_json=getattr(fmea_row, "ai_suggested_values_json", None),
        risk_criteria_version_applied=getattr(fmea_row, "risk_criteria_version_applied", None),
        version=1
    )
    
    # Auto-calculate RPN
    db_row.rpn = _calculate_rpn(db_row.severity, db_row.probability, db_row.detection)
    db_row.residual_rpn = _calculate_rpn(
        db_row.residual_severity, 
        db_row.residual_probability, 
        db_row.residual_detection
    )
    
    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row

def get_fmea_rows_by_project(db: Session, project_id: str) -> List[FMEARow]:
    """Get all FMEA rows for a project"""
    return db.query(FMEARow).filter(FMEARow.project_id == project_id).all()

def get_fmea_row(db: Session, fmea_row_id: str, project_id: str) -> Optional[FMEARow]:
    """Get a specific FMEA row by ID"""
    return db.query(FMEARow).filter(
        FMEARow.id == fmea_row_id,
        FMEARow.project_id == project_id
    ).first()

def update_fmea_row(db: Session, fmea_row_id: str, fmea_row: FMEARowUpdate, project_id: str) -> Optional[FMEARow]:
    """Update an FMEA row with versioning"""
    db_row = get_fmea_row(db, fmea_row_id, project_id)
    if not db_row:
        return None
    
    # Store old data for diff
    old_data = _serialize_for_diff(db_row)
    
    # Update fields
    # Pydantic v2 compatibility
    if hasattr(fmea_row, 'model_dump'):
        update_data = fmea_row.model_dump(exclude_unset=True)
    else:
        update_data = fmea_row.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_row, field, value)
    
    # Auto-calculate RPN
    db_row.rpn = _calculate_rpn(db_row.severity, db_row.probability, db_row.detection)
    db_row.residual_rpn = _calculate_rpn(
        db_row.residual_severity,
        db_row.residual_probability,
        db_row.residual_detection
    )
    
    # Create version entry with diff
    new_data = _serialize_for_diff(db_row)
    diff = _calculate_diff(old_data, new_data)
    
    if diff:  # Only create version if there are changes
        db_row.version += 1
        version_entry = FMEAVersion(
            id=str(uuid.uuid4()),
            fmea_row_id=db_row.id,
            version=db_row.version,
            diff=diff
        )
        db.add(version_entry)
    
    db.commit()
    db.refresh(db_row)
    return db_row

def delete_fmea_row(db: Session, fmea_row_id: str, project_id: str) -> bool:
    """Delete an FMEA row"""
    db_row = get_fmea_row(db, fmea_row_id, project_id)
    if not db_row:
        return False
    
    db.delete(db_row)
    db.commit()
    return True

def get_fmea_version_history(db: Session, fmea_row_id: str, project_id: str) -> List[FMEAVersion]:
    """Get version history for an FMEA row"""
    # Verify the row belongs to the project
    row = get_fmea_row(db, fmea_row_id, project_id)
    if not row:
        return []
    
    return db.query(FMEAVersion).filter(
        FMEAVersion.fmea_row_id == fmea_row_id
    ).order_by(FMEAVersion.version.desc()).all()
