"""
Business Logic for Residual Risk Evaluation Evidence Builder
Builds residual risk evaluation data from SmartQS risk_item_versions.
Produces evidence for a complete, audit-ready Residual Risk Evaluation report (ISO 14971).
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from models.approval import Approval
from models.component import Component
from models.risk_management_plan import RiskManagementPlan
from models.project_profile import ProjectProfile
from sqlalchemy import or_
import json


def _initial_risk_level(score: Optional[int], thresholds: Dict[str, Any]) -> str:
    """Classify initial risk score as High, Medium, or Low for summary distribution."""
    if score is None:
        return "Unknown"
    for level in ["Critical", "High", "Medium", "Low"]:
        t = thresholds.get(level, {})
        lo, hi = t.get("min", 0), t.get("max", 100)
        if lo <= score <= hi:
            return level
    return "Unknown"

def get_acceptability_thresholds(
    db: Session,
    project_id: str,
    custom_thresholds: Optional[Dict[str, Any]] = None,
    acceptability_profile: str = "default_med_device"
) -> Dict[str, Any]:
    """
    Get acceptability thresholds from custom, RMP, or defaults
    
    Priority:
    1. custom_thresholds from request
    2. RMP stored thresholds
    3. Default system thresholds
    """
    if custom_thresholds:
        return custom_thresholds
    
    # Try to get from RMP
    rmp = db.query(RiskManagementPlan).filter(
        RiskManagementPlan.project_id == project_id
    ).order_by(RiskManagementPlan.created_at.desc()).first()
    
    if rmp:
        try:
            criteria = json.loads(rmp.acceptability_criteria_json)
            thresholds = criteria.get("thresholds", {})
            if thresholds:
                return thresholds
        except:
            pass
    
    # Default thresholds
    return {
        "Low": {"min": 1, "max": 7, "acceptability": "acceptable"},
        "Medium": {"min": 8, "max": 19, "acceptability": "acceptable_with_justification"},
        "High": {"min": 20, "max": 59, "acceptability": "needs_benefit_risk"},
        "Critical": {"min": 60, "max": 100, "acceptability": "unacceptable"}
    }

def infer_residual_acceptability(
    residual_risk_score: Optional[int],
    thresholds: Dict[str, Any]
) -> tuple[str, str]:
    """
    Infer residual acceptability from score using thresholds
    
    Returns:
        (acceptability_level, acceptability_value)
    """
    if residual_risk_score is None:
        return ("unknown", "unknown")
    
    # Check thresholds in order: Critical, High, Medium, Low
    for level in ["Critical", "High", "Medium", "Low"]:
        threshold = thresholds.get(level, {})
        min_score = threshold.get("min", 0)
        max_score = threshold.get("max", 100)
        if min_score <= residual_risk_score <= max_score:
            return (level.lower(), threshold.get("acceptability", "unknown"))
    
    return ("unknown", "unknown")

def build_residual_risk_evidence(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
    version_scope: str = "approved_only",
    include_unapproved: bool = False,
    custom_thresholds: Optional[Dict[str, Any]] = None,
    acceptability_profile: str = "default_med_device"
) -> Dict[str, Any]:
    """
    Build residual risk evaluation evidence from SmartQS risk_item_versions
    
    Args:
        db: Database session
        project_id: Project ID
        component_filter: List of component filters [{"id": "...", "name": "..."}]
        version_scope: "approved_only", "current", or "all"
        include_unapproved: If True, include unapproved versions even when version_scope is approved_only
        custom_thresholds: Custom acceptability thresholds
        acceptability_profile: Profile name for thresholds
    
    Returns:
        Dictionary with residual risk evaluation data
    """
    # Get acceptability thresholds
    thresholds = get_acceptability_thresholds(db, project_id, custom_thresholds, acceptability_profile)
    
    # Extract component IDs and names from filter
    component_ids = []
    component_names = []
    if component_filter:
        for comp in component_filter:
            if comp.get("id"):
                component_ids.append(comp["id"])
            if comp.get("name"):
                component_names.append(comp["name"])
    
    # Query risk items filtered by components
    risk_items_query = db.query(RiskItem).filter(RiskItem.project_id == project_id)
    
    if component_ids or component_names:
        # Filter by component_id or component_name
        filters = []
        if component_ids:
            filters.append(RiskItem.component_id.in_(component_ids))
        if component_names:
            filters.append(RiskItem.component_name.in_(component_names))
        if filters:
            risk_items_query = risk_items_query.filter(or_(*filters))
    
    risk_items = risk_items_query.all()
    
    # Build residual risk rows
    residual_risk_rows = []
    versions_included = 0
    missing_residual_fields = 0
    missing_field_list = []
    
    for risk_item in risk_items:
        # Get all versions
        all_versions = db.query(RiskItemVersion).filter(
            RiskItemVersion.risk_item_id == risk_item.id
        ).order_by(RiskItemVersion.version_number.desc()).all()
        
        # Get current version
        current_version = None
        if risk_item.current_version_id:
            current_version = db.query(RiskItemVersion).filter(
                RiskItemVersion.id == risk_item.current_version_id
            ).first()
        
        # Determine which versions to include
        versions_to_include = []
        
        if version_scope == "approved_only":
            # Get approved versions
            for version in all_versions:
                approvals = db.query(Approval).filter(
                    Approval.artifact_type == "risk_item_version",
                    Approval.artifact_id == version.id,
                    Approval.status == "approved"
                ).all()
                if approvals:
                    versions_to_include.append((version, approvals[0]))
                elif include_unapproved:
                    versions_to_include.append((version, None))
        
        elif version_scope == "current":
            if current_version:
                # Check if current version is approved
                approvals = db.query(Approval).filter(
                    Approval.artifact_type == "risk_item_version",
                    Approval.artifact_id == current_version.id,
                    Approval.status == "approved"
                ).all()
                versions_to_include.append((current_version, approvals[0] if approvals else None))
        
        elif version_scope == "all":
            # Include all versions
            for version in all_versions:
                approvals = db.query(Approval).filter(
                    Approval.artifact_type == "risk_item_version",
                    Approval.artifact_id == version.id,
                    Approval.status == "approved"
                ).all()
                versions_to_include.append((version, approvals[0] if approvals else None))
        
        # Build residual risk rows for included versions
        for version, approval in versions_to_include:
            # Get component name
            component_name = None
            if risk_item.component_id:
                component = db.query(Component).filter(Component.id == risk_item.component_id).first()
                if component:
                    component_name = component.name
            if not component_name:
                component_name = risk_item.component_name or "Unknown"
            
            # Extract residual fields
            residual_severity = version.residual_severity
            residual_probability = version.residual_probability_of_harm
            residual_risk_score = version.residual_risk_score
            
            # Compute residual_risk_score if missing but severity/probability exist
            if residual_risk_score is None and residual_severity is not None and residual_probability is not None:
                residual_risk_score = residual_severity * residual_probability
            
            # Check for missing fields
            has_missing_fields = (
                residual_severity is None or
                residual_probability is None or
                residual_risk_score is None
            )
            
            if has_missing_fields:
                missing_residual_fields += 1
                missing_field_list.append({
                    "risk_key": risk_item.risk_key or f"R-{risk_item.id[:8]}",
                    "version_id": version.id,
                    "version_no": version.version_number
                })
            
            # Initial risk (pre-control)
            initial_severity = version.severity
            initial_probability = version.probability_of_harm
            initial_risk_score = version.risk_score
            if initial_risk_score is None and initial_severity is not None and initial_probability is not None:
                initial_risk_score = initial_severity * initial_probability
            initial_risk_level = _initial_risk_level(initial_risk_score, thresholds)
            hazard_text = (version.hazard or "").strip() or (version.harm or "").strip() or "Hazard (see Hazard Analysis)"
            controls_parts = []
            if (version.inherent_safety or "").strip():
                controls_parts.append(version.inherent_safety.strip())
            if (version.protective_measures or "").strip():
                controls_parts.append(version.protective_measures.strip())
            if (version.information_for_safety or "").strip():
                controls_parts.append(version.information_for_safety.strip())
            controls_summary = " | ".join(controls_parts) if controls_parts else "See risk control documentation"
            residual_risk_display = (
                f"S{residual_severity or '—'} × P{residual_probability or '—'} = {residual_risk_score or '—'}"
                if (residual_severity is not None or residual_probability is not None or residual_risk_score is not None)
                else "—"
            )

            # Determine residual acceptability
            residual_acceptability_stored = getattr(version, "risk_acceptability", None)
            acceptability_source = "inferred"
            if residual_acceptability_stored:
                residual_acceptability = residual_acceptability_stored
                acceptability_source = "stored"
            else:
                level, value = infer_residual_acceptability(residual_risk_score, thresholds)
                residual_acceptability = value
                acceptability_source = "inferred"

            row = {
                "risk_item_id": risk_item.id,
                "risk_key": risk_item.risk_key or f"R-{risk_item.id[:8]}",
                "version_id": version.id,
                "version_no": version.version_number,
                "component_name": component_name,
                "hazard": hazard_text,
                "initial_severity": initial_severity,
                "initial_probability": initial_probability,
                "initial_risk_score": initial_risk_score,
                "initial_risk_level": initial_risk_level,
                "controls_summary": controls_summary,
                "inherent_safety": (version.inherent_safety or "").strip() or None,
                "protective_measures": (version.protective_measures or "").strip() or None,
                "information_for_safety": (version.information_for_safety or "").strip() or None,
                "residual_severity": residual_severity,
                "residual_probability_of_harm": residual_probability,
                "residual_risk_score": residual_risk_score,
                "residual_risk_display": residual_risk_display,
                "residual_acceptability": residual_acceptability,
                "acceptability_source": acceptability_source,
                "approved": approval is not None,
                "approved_at": approval.timestamp.isoformat() if approval and approval.timestamp else None,
                "approved_by": approval.approver_id if approval else None,
                "is_current": version.id == (current_version.id if current_version else None),
            }
            residual_risk_rows.append(row)
            versions_included += 1

    # Project profile for device context
    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    profile_data = {}
    if profile:
        profile_data = {
            "device_description": (profile.device_description or "").strip() or None,
            "intended_use": (profile.intended_use or "").strip() or None,
            "user_population": (profile.user_population or "").strip() or None,
            "use_environment": (profile.use_environment or "").strip() or None,
        }

    # Pre-control summary
    hazard_count = len(residual_risk_rows)
    initial_high = sum(1 for r in residual_risk_rows if r.get("initial_risk_level") in ("Critical", "High"))
    initial_medium = sum(1 for r in residual_risk_rows if r.get("initial_risk_level") == "Medium")
    initial_low = sum(1 for r in residual_risk_rows if r.get("initial_risk_level") == "Low")
    initial_unknown = sum(1 for r in residual_risk_rows if r.get("initial_risk_level") not in ("Critical", "High", "Medium", "Low"))
    sorted_by_initial = sorted(
        [r for r in residual_risk_rows if r.get("initial_risk_score") is not None],
        key=lambda x: (x.get("initial_risk_score") or 0),
        reverse=True,
    )
    highest_risks = sorted_by_initial[:5]
    pre_control_summary = {
        "number_of_hazards": hazard_count,
        "initial_risk_distribution": {
            "high": initial_high,
            "medium": initial_medium,
            "low": initial_low,
            "unknown": initial_unknown,
        },
        "highest_risks": [
            {"risk_key": r.get("risk_key"), "hazard": (r.get("hazard") or "")[:80], "initial_score": r.get("initial_risk_score"), "initial_level": r.get("initial_risk_level")}
            for r in highest_risks
        ],
        "methodology": "Risk estimation uses severity of harm (1–5 or 1–10) and probability of occurrence of harm. Risk score = severity × probability. Thresholds align with project Risk Acceptability Criteria (ISO 14971).",
    }

    # Risk control measures implemented (aggregated)
    design_controls = []
    protective_list = []
    information_safety = []
    for r in residual_risk_rows:
        if r.get("inherent_safety"):
            design_controls.append(r["inherent_safety"])
        if r.get("protective_measures"):
            protective_list.append(r["protective_measures"])
        if r.get("information_for_safety"):
            information_safety.append(r["information_for_safety"])
    risk_control_measures = {
        "design_controls": list(dict.fromkeys(design_controls)),
        "protective_measures": list(dict.fromkeys(protective_list)),
        "information_for_safety": list(dict.fromkeys(information_safety)),
        "linked_to_risk_reduction": True,
    }

    # Post-control (residual) summary
    res_high = sum(1 for r in residual_risk_rows if (r.get("residual_risk_score") or 0) >= 20)
    res_medium = sum(1 for r in residual_risk_rows if 8 <= (r.get("residual_risk_score") or 0) < 20)
    res_low = sum(1 for r in residual_risk_rows if (r.get("residual_risk_score") or 0) < 8 and r.get("residual_risk_score") is not None)
    res_unknown = sum(1 for r in residual_risk_rows if r.get("residual_risk_score") is None)
    remaining_significant = [r for r in residual_risk_rows if (r.get("residual_risk_score") or 0) >= 12]
    post_control_summary = {
        "residual_risk_distribution": {"high": res_high, "medium": res_medium, "low": res_low, "unknown": res_unknown},
        "effectiveness_narrative": f"After application of risk controls, {len(residual_risk_rows) - len(remaining_significant)} of {len(residual_risk_rows)} risks were reduced to acceptable or ALARP levels." if residual_risk_rows else "No risk data to evaluate.",
        "remaining_significant_risks": [
            {"risk_key": r.get("risk_key"), "hazard": (r.get("hazard") or "")[:60], "residual_score": r.get("residual_risk_score"), "acceptability": r.get("residual_acceptability")}
            for r in remaining_significant[:10]
        ],
    }

    return {
        "project_id": project_id,
        "project_name": None,
        "components": component_filter or [],
        "version_scope": version_scope,
        "include_unapproved": include_unapproved,
        "thresholds": thresholds,
        "rows": residual_risk_rows,
        "missing_field_list": missing_field_list,
        "counts": {
            "versions_included": versions_included,
            "missing_residual_fields": missing_residual_fields,
        },
        "profile": profile_data,
        "pre_control_summary": pre_control_summary,
        "risk_control_measures": risk_control_measures,
        "post_control_summary": post_control_summary,
    }

