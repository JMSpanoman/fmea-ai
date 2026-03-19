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
from datetime import datetime, timezone


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


def _norm_acceptability(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if not raw or raw == "unknown":
        return "unknown"
    if "unacceptable" in raw:
        return "unacceptable"
    if "benefit" in raw or "needs_benefit_risk" in raw:
        return "needs_benefit_risk"
    if "justification" in raw:
        return "acceptable_with_justification"
    if "acceptable" in raw:
        return "acceptable"
    return "unknown"


def _safe_avg(nums: List[Optional[float]]) -> Optional[float]:
    vals = [float(n) for n in nums if n is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def calculate_data_completeness(rows: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
    total = len(rows)
    total_hazards = sum(1 for r in rows if (r.get("hazard") or "").strip())
    total_haz_situations = sum(1 for r in rows if (r.get("hazardous_situation") or "").strip())
    total_hazards_or_situations = sum(
        1 for r in rows if (r.get("hazard") or "").strip() or (r.get("hazardous_situation") or "").strip()
    )
    missing_counts = {
        "initial_severity": sum(1 for r in rows if r.get("initial_severity") is None),
        "initial_probability": sum(1 for r in rows if r.get("initial_probability") is None),
        "residual_severity": sum(1 for r in rows if r.get("residual_severity") is None),
        "residual_probability": sum(1 for r in rows if r.get("residual_probability_of_harm") is None),
        "linked_controls": sum(1 for r in rows if not r.get("has_linked_controls")),
        "acceptability_decision": sum(1 for r in rows if _norm_acceptability(r.get("residual_acceptability")) == "unknown"),
    }
    required_checks_per_row = 6
    missing_total = sum(missing_counts.values())
    denominator = max(total * required_checks_per_row, 1)
    completeness_score = round(max(0.0, 100.0 * (1.0 - (missing_total / denominator))), 1)

    if total == 0 or total_hazards_or_situations == 0:
        status = "EMPTY"
        interpretation = "Residual risk evaluation cannot be meaningfully performed because no risk data is available."
    elif missing_total == 0:
        status = "COMPLETE"
        interpretation = "Residual risk evaluation can be performed."
    elif completeness_score < 60.0 or missing_counts["residual_probability"] > max(1, total // 2):
        status = "INSUFFICIENT_FOR_EVALUATION"
        interpretation = "Residual risk evaluation is limited by incomplete risk records."
    else:
        status = "PARTIAL"
        interpretation = "Residual risk evaluation is limited by incomplete risk records."

    device_blob = " ".join(
        [
            str(profile.get("device_description") or ""),
            str(profile.get("intended_use") or ""),
            str(profile.get("device_class") or ""),
        ]
    ).lower()
    high_risk_hint = any(k in device_blob for k in ["implant", "life-sustain", "pacemaker", "class iii", "class 3"])
    atypical_warning = None
    if high_risk_hint and total_hazards_or_situations == 0:
        atypical_warning = (
            "This result is atypical for an implantable or life-sustaining medical device and suggests incomplete "
            "hazard analysis data or excluded version scope."
        )

    return {
        "totalRiskItems": total,
        "totalHazards": total_hazards,
        "totalHazardousSituations": total_haz_situations,
        "totalHazardsOrSituations": total_hazards_or_situations,
        "missingFieldCounts": missing_counts,
        "completenessScore": completeness_score,
        "dataQualityStatus": status,
        "interpretation": interpretation,
        "atypicalWarning": atypical_warning,
    }


def summarize_risk_reduction(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    paired = [r for r in rows if r.get("initial_risk_score") is not None and r.get("residual_risk_score") is not None]
    reduced = 0
    unchanged = 0
    worsened = 0
    deltas: List[float] = []
    for r in paired:
        delta = (r.get("initial_risk_score") or 0) - (r.get("residual_risk_score") or 0)
        deltas.append(delta)
        if delta > 0:
            reduced += 1
        elif delta < 0:
            worsened += 1
        else:
            unchanged += 1
    avg_initial = _safe_avg([r.get("initial_risk_score") for r in paired])
    avg_residual = _safe_avg([r.get("residual_risk_score") for r in paired])
    control_breakdown = {
        "inherent_safety_by_design": sum(1 for r in paired if r.get("inherent_safety")),
        "protective_measures": sum(1 for r in paired if r.get("protective_measures")),
        "information_for_safety": sum(1 for r in paired if r.get("information_for_safety")),
    }
    return {
        "pairedCount": len(paired),
        "reducedCount": reduced,
        "unchangedCount": unchanged,
        "worsenedCount": worsened,
        "reducedPercent": round((100.0 * reduced / len(paired)), 1) if paired else None,
        "averageInitialScore": round(avg_initial, 2) if avg_initial is not None else None,
        "averageResidualScore": round(avg_residual, 2) if avg_residual is not None else None,
        "meanRiskReductionDelta": round(_safe_avg(deltas), 2) if deltas else None,
        "controlTypeBreakdown": control_breakdown,
        "hasComparativeData": bool(paired),
    }


def build_traceability_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    fully = 0
    partial = 0
    missing_control = 0
    missing_verification = 0
    for r in rows:
        has_control = bool(r.get("has_linked_controls"))
        has_ver = bool(r.get("verification_refs"))
        if not has_control:
            missing_control += 1
        if not has_ver:
            missing_verification += 1
        if has_control and has_ver:
            fully += 1
        elif has_control or has_ver:
            partial += 1
    return {
        "fullyTraceable": fully,
        "partiallyTraceable": partial,
        "missingControlLinkage": missing_control,
        "missingVerificationLinkage": missing_verification,
    }


def determine_final_residual_risk_decision(
    rows: List[Dict[str, Any]],
    data_quality: Dict[str, Any],
) -> Dict[str, Any]:
    total = len(rows)
    norm = [_norm_acceptability(r.get("residual_acceptability")) for r in rows]
    unacceptable = sum(1 for n in norm if n == "unacceptable")
    benefit = sum(1 for n in norm if n == "needs_benefit_risk")
    with_just = sum(1 for n in norm if n == "acceptable_with_justification")
    acceptable = sum(1 for n in norm if n == "acceptable")
    quality_status = data_quality.get("dataQualityStatus")

    if total == 0:
        det = "NOT EVALUABLE"
        narrative = "An overall residual risk evaluation cannot be concluded because no risk data was available in the selected export scope."
    elif quality_status in {"INSUFFICIENT_FOR_EVALUATION", "EMPTY"}:
        det = "NOT FULLY EVALUABLE"
        narrative = "The overall residual risk evaluation is limited by incomplete risk records and requires data completion before a definitive conclusion."
    elif unacceptable > 0:
        det = "UNACCEPTABLE"
        narrative = "One or more residual risks remain in an unacceptable region and require mitigation before approval."
    elif benefit > 0:
        det = "BENEFIT-RISK REVIEW REQUIRED"
        narrative = "One or more residual risks remain above the acceptable region and require documented benefit-risk justification."
    elif with_just > 0:
        det = "ACCEPTABLE WITH CONDITIONS"
        narrative = "Residual risk is acceptable with conditions, including documented justification and continued monitoring."
    elif acceptable == total and quality_status == "COMPLETE":
        det = "ACCEPTABLE"
        narrative = "Based on the evaluated residual risks, overall residual risk is acceptable for intended use."
    else:
        det = "ACCEPTABLE WITH CONDITIONS"
        narrative = "Residual risk appears acceptable but remains subject to completion of supporting records and formal review."

    requires_review = det in {"NOT FULLY EVALUABLE", "UNACCEPTABLE", "BENEFIT-RISK REVIEW REQUIRED"}
    approval_blocked = det in {"NOT EVALUABLE", "NOT FULLY EVALUABLE", "UNACCEPTABLE"}
    basis = [
        f"Included risk items: {total}",
        f"Data quality: {quality_status}",
        f"Unacceptable residual risks: {unacceptable}",
        f"Benefit-risk review required: {benefit}",
    ]
    limitations = []
    if quality_status != "COMPLETE":
        limitations.append("Risk records are incomplete for one or more required fields.")
    if data_quality.get("missingFieldCounts", {}).get("acceptability_decision", 0) > 0:
        limitations.append("Some acceptability decisions were inferred due to missing explicit fields.")

    return {
        "finalDetermination": det,
        "narrative": narrative,
        "requiresFurtherReview": requires_review,
        "approvalBlocked": approval_blocked,
        "basis": basis,
        "limitations": limitations,
        "benefitRiskRequiredCount": benefit,
        "unacceptableResidualRiskCount": unacceptable,
    }


def determine_report_status(
    data_quality_status: str,
    final_determination: str,
    benefit_risk_required_count: int,
) -> Dict[str, Any]:
    blocking_reason = None
    if data_quality_status in {"EMPTY", "INSUFFICIENT_FOR_EVALUATION"}:
        status = "Approval Blocked"
        blocking_reason = "Approval pending completion of risk records."
    elif final_determination == "UNACCEPTABLE":
        status = "Approval Blocked"
        blocking_reason = "Approval blocked due to unacceptable residual risk."
    elif final_determination == "BENEFIT-RISK REVIEW REQUIRED" and benefit_risk_required_count > 0:
        status = "Ready for Review"
        blocking_reason = "Approval pending documented benefit-risk justification."
    elif final_determination in {"ACCEPTABLE", "ACCEPTABLE WITH CONDITIONS"} and data_quality_status == "COMPLETE":
        status = "Ready for Approval"
    else:
        status = "Draft"
    return {"reportStatus": status, "blockingReason": blocking_reason}


def generate_regulatory_observations(
    rows: List[Dict[str, Any]],
    data_quality: Dict[str, Any],
    traceability: Dict[str, Any],
    final_decision: Dict[str, Any],
    profile: Dict[str, Any],
) -> List[str]:
    obs: List[str] = []
    if data_quality.get("totalHazardsOrSituations", 0) == 0:
        obs.append("No hazard records were present in the selected approved scope.")
    if traceability.get("missingControlLinkage", 0) > 0:
        obs.append("Some risk items lack linked control measures.")
    if traceability.get("missingVerificationLinkage", 0) > 0:
        obs.append("Several risk items lack linked verification evidence for implemented controls.")
    if data_quality.get("missingFieldCounts", {}).get("residual_probability", 0) > 0:
        obs.append("Residual probability is missing for one or more risk items.")
    if data_quality.get("missingFieldCounts", {}).get("acceptability_decision", 0) > 0:
        obs.append("Residual risk acceptability was inferred for some items due to missing explicit acceptability fields.")
    if final_decision.get("benefitRiskRequiredCount", 0) > 0:
        obs.append("One or more residual risks require benefit-risk review before final approval.")
    atypical_warning = data_quality.get("atypicalWarning")
    if atypical_warning:
        obs.append(atypical_warning)
    if not obs:
        obs.append("No major residual risk data-quality concerns were detected in the selected scope.")
    return obs

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
    thresholds_meta = {
        "source": "custom_thresholds" if custom_thresholds else "project_risk_matrix_or_policy",
        "profile": acceptability_profile,
        "revision": "latest",
    }
    
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
    excluded_versions = 0
    missing_field_list = []
    last_approved_update: Optional[str] = None
    
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
                else:
                    excluded_versions += 1
        
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
            has_linked_controls = bool(controls_parts)
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
                "hazardous_situation": (version.hazardous_situation or "").strip() or None,
                "sequence_of_events": (version.sequence_of_events or "").strip() or None,
                "harm": (version.harm or "").strip() or None,
                "initial_severity": initial_severity,
                "initial_probability": initial_probability,
                "initial_risk_score": initial_risk_score,
                "initial_risk_level": initial_risk_level,
                "controls_summary": controls_summary,
                "has_linked_controls": has_linked_controls,
                "inherent_safety": (version.inherent_safety or "").strip() or None,
                "protective_measures": (version.protective_measures or "").strip() or None,
                "information_for_safety": (version.information_for_safety or "").strip() or None,
                "verification_refs": [],
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
            if approval and approval.timestamp:
                ts = approval.timestamp.astimezone(timezone.utc).isoformat()
                if not last_approved_update or ts > last_approved_update:
                    last_approved_update = ts

    # Project profile for device context
    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    profile_data = {}
    if profile:
        profile_data = {
            "device_description": (profile.device_description or "").strip() or None,
            "intended_use": (profile.intended_use or "").strip() or None,
            "user_population": (profile.user_population or "").strip() or None,
            "use_environment": (profile.use_environment or "").strip() or None,
            "device_class": None,
            "implantable": None,
            "life_sustaining": None,
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

    # Data quality and decision intelligence
    data_quality = calculate_data_completeness(residual_risk_rows, profile_data)
    risk_reduction_summary = summarize_risk_reduction(residual_risk_rows)
    traceability_summary = build_traceability_summary(residual_risk_rows)
    final_decision = determine_final_residual_risk_decision(residual_risk_rows, data_quality)
    report_status = determine_report_status(
        data_quality_status=data_quality.get("dataQualityStatus", "EMPTY"),
        final_determination=final_decision.get("finalDetermination", "NOT EVALUABLE"),
        benefit_risk_required_count=int(final_decision.get("benefitRiskRequiredCount", 0)),
    )
    regulatory_observations = generate_regulatory_observations(
        residual_risk_rows, data_quality, traceability_summary, final_decision, profile_data
    )

    generated_utc = datetime.now(timezone.utc)
    generated_local = datetime.now().astimezone()
    version_scope_desc_map = {
        "approved_only": "Approved versions only",
        "current": "Current versions only",
        "all": "All available versions",
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
            "excluded_versions": excluded_versions,
        },
        "metadata": {
            "total_included_versions": versions_included,
            "total_excluded_versions": excluded_versions,
            "version_scope_description": version_scope_desc_map.get(version_scope, version_scope.replace("_", " ")),
            "generated_at_utc": generated_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "generated_at_local": generated_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "last_approved_risk_item_update": last_approved_update,
        },
        "thresholds_meta": thresholds_meta,
        "profile": profile_data,
        "pre_control_summary": pre_control_summary,
        "risk_control_measures": risk_control_measures,
        "post_control_summary": post_control_summary,
        "data_quality": data_quality,
        "risk_reduction_summary": risk_reduction_summary,
        "traceability_summary": traceability_summary,
        "final_decision": final_decision,
        "report_status": report_status,
        "regulatory_observations": regulatory_observations,
        # Machine-readable fields for dashboards/frontend
        "finalDetermination": final_decision.get("finalDetermination"),
        "dataQualityStatus": data_quality.get("dataQualityStatus"),
        "reportStatus": report_status.get("reportStatus"),
        "completenessScore": data_quality.get("completenessScore"),
        "totalRiskItems": data_quality.get("totalRiskItems"),
        "totalHazards": data_quality.get("totalHazards"),
        "missingFieldCounts": data_quality.get("missingFieldCounts"),
        "traceabilitySummary": traceability_summary,
        "riskReductionSummary": risk_reduction_summary,
        "benefitRiskRequiredCount": final_decision.get("benefitRiskRequiredCount"),
        "unacceptableResidualRiskCount": final_decision.get("unacceptableResidualRiskCount"),
        "regulatoryObservations": regulatory_observations,
    }

