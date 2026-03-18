"""
Business Logic for Hazard Analysis Evidence Builder
Builds hazard analysis from hazard_analysis_items (preferred) or from risk_item_versions (fallback).
Returns rows with full ISO 14971-style fields for report and UI.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from models.approval import Approval
from models.component import Component
from models.hazard_analysis_item import HazardAnalysisItem
from sqlalchemy import or_
from business_logic.fmea_to_hazard_analysis import risk_item_version_to_hazard_analysis_dict


def _ha_item_to_row(item: HazardAnalysisItem, component_name: Optional[str] = None) -> Dict[str, Any]:
    """Convert HazardAnalysisItem ORM to full row dict for report/API."""
    name = component_name
    if name is None and item.component_id and item.component:
        name = getattr(item.component, "name", None) or item.component_id
    if not name:
        name = "Unknown"
    approved = (item.approval_status or "").lower() == "approved"
    row = {
        "id": item.id,
        "risk_item_id": item.risk_item_id,
        "risk_item_version_id": item.risk_item_version_id,
        "component_name": name,
        "risk_key": item.risk_key or f"HA-{item.id[:8]}",
        "version_id": item.risk_item_version_id,
        "version_no": item.version_no,
        "hazard_category": item.hazard_category,
        "hazard": item.hazard,
        "foreseeable_sequence_of_events": item.foreseeable_sequence_of_events,
        "hazardous_situation": item.hazardous_situation,
        "harm": item.harm,
        "affected_user": item.affected_user,
        "failure_mode": item.failure_mode,
        "cause_of_failure": item.cause_of_failure,
        "clinical_effect": item.clinical_effect,
        "operating_mode": item.operating_mode,
        "use_environment": item.use_environment,
        "initial_severity": item.initial_severity,
        "initial_probability": item.initial_probability,
        "initial_risk_level": item.initial_risk_level,
        "risk_control_measures": item.risk_control_measures if isinstance(item.risk_control_measures, list) else ([item.risk_control_measures] if item.risk_control_measures else []),
        "risk_control_type": item.risk_control_type if isinstance(item.risk_control_type, list) else ([item.risk_control_type] if item.risk_control_type else []),
        "control_implementation_notes": item.control_implementation_notes,
        "residual_severity": item.residual_severity,
        "residual_probability": item.residual_probability,
        "residual_risk_level": item.residual_risk_level,
        "residual_risk_acceptability": item.residual_risk_acceptability,
        "related_design_input": item.related_design_input or [],
        "related_design_output": item.related_design_output or [],
        "verification_reference": item.verification_reference or [],
        "validation_reference": item.validation_reference or [],
        "requirement_ids": item.requirement_ids or [],
        "approval_status": item.approval_status or "draft",
        "approved": approved,
        "approved_at": item.approved_at.isoformat() if item.approved_at else None,
        "approved_by": item.approved_by,
        "reviewer_comments": item.reviewer_comments,
        "ai_generated": item.ai_generated or False,
        "ai_confidence": item.ai_confidence,
        "source_context": item.source_context,
        "assumptions": item.assumptions if isinstance(item.assumptions, list) else ([item.assumptions] if item.assumptions else []),
        "sequence_of_events": item.foreseeable_sequence_of_events,
        "is_current": True,
    }
    return row


def build_hazard_analysis(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
    version_scope: str = "approved_only",
    include_unapproved: bool = False,
    prefer_ha_items: bool = True,
) -> Dict[str, Any]:
    """
    Build hazard analysis evidence. Prefers hazard_analysis_items when present;
    otherwise builds from risk_item_versions (backward compatible).
    Rows include full ISO 14971-style fields.
    """
    component_ids = []
    component_names = []
    if component_filter:
        for comp in component_filter:
            if comp.get("id"):
                component_ids.append(comp["id"])
            if comp.get("name"):
                component_names.append(comp["name"])

    # Prefer native hazard_analysis_items
    if prefer_ha_items:
        q = db.query(HazardAnalysisItem).filter(HazardAnalysisItem.project_id == project_id)
        if component_ids:
            q = q.filter(HazardAnalysisItem.component_id.in_(component_ids))
        if component_names:
            comps = db.query(Component).filter(Component.name.in_(component_names)).all()
            cids = [c.id for c in comps]
            if cids:
                q = q.filter(HazardAnalysisItem.component_id.in_(cids))
        ha_items = q.order_by(HazardAnalysisItem.risk_key, HazardAnalysisItem.version_no.desc()).all()
        if ha_items:
            rows = []
            for item in ha_items:
                if version_scope == "approved_only" and (item.approval_status or "").lower() != "approved" and not include_unapproved:
                    continue
                rows.append(_ha_item_to_row(item))
            return {
                "project_id": project_id,
                "components": component_filter or [],
                "version_scope": version_scope,
                "include_unapproved": include_unapproved,
                "rows": rows,
                "counts": {
                    "risk_items": len(rows),
                    "versions_included": len(rows),
                    "unapproved_excluded": 0,
                },
                "source": "hazard_analysis_items",
            }
    # Fallback: build from risk_item_versions
    risk_items_query = db.query(RiskItem).filter(RiskItem.project_id == project_id)
    if component_ids or component_names:
        filters = []
        if component_ids:
            filters.append(RiskItem.component_id.in_(component_ids))
        if component_names:
            filters.append(RiskItem.component_name.in_(component_names))
        if filters:
            risk_items_query = risk_items_query.filter(or_(*filters))
    risk_items = risk_items_query.all()

    hazard_analysis_rows = []
    risk_items_included = 0
    versions_included = 0
    unapproved_excluded = 0

    for risk_item in risk_items:
        all_versions = db.query(RiskItemVersion).filter(
            RiskItemVersion.risk_item_id == risk_item.id
        ).order_by(RiskItemVersion.version_number.desc()).all()
        current_version = None
        if risk_item.current_version_id:
            current_version = db.query(RiskItemVersion).filter(
                RiskItemVersion.id == risk_item.current_version_id
            ).first()
        versions_to_include = []
        if version_scope == "approved_only":
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
                    unapproved_excluded += 1
        elif version_scope == "current":
            if current_version:
                approvals = db.query(Approval).filter(
                    Approval.artifact_type == "risk_item_version",
                    Approval.artifact_id == current_version.id,
                    Approval.status == "approved"
                ).all()
                versions_to_include.append((current_version, approvals[0] if approvals else None))
        elif version_scope == "all":
            for version in all_versions:
                approvals = db.query(Approval).filter(
                    Approval.artifact_type == "risk_item_version",
                    Approval.artifact_id == version.id,
                    Approval.status == "approved"
                ).all()
                versions_to_include.append((version, approvals[0] if approvals else None))

        component_name = None
        if risk_item.component_id:
            comp = db.query(Component).filter(Component.id == risk_item.component_id).first()
            if comp:
                component_name = comp.name
        if not component_name:
            component_name = risk_item.component_name or "Unknown"

        for version, approval in versions_to_include:
            row = risk_item_version_to_hazard_analysis_dict(version, risk_item, component_name=component_name)
            row["risk_item_id"] = risk_item.id
            row["version_id"] = version.id
            row["sequence_of_events"] = row.get("foreseeable_sequence_of_events") or row.get("sequence_of_events")
            row["approved"] = approval is not None
            row["approved_at"] = approval.timestamp.isoformat() if approval and approval.timestamp else None
            row["approved_by"] = approval.approver_id if approval else None
            row["is_current"] = version.id == (current_version.id if current_version else None)
            hazard_analysis_rows.append(row)
            versions_included += 1
        if versions_to_include:
            risk_items_included += 1

    return {
        "project_id": project_id,
        "components": component_filter or [],
        "version_scope": version_scope,
        "include_unapproved": include_unapproved,
        "rows": hazard_analysis_rows,
        "counts": {
            "risk_items": risk_items_included,
            "versions_included": versions_included,
            "unapproved_excluded": unapproved_excluded
        },
        "source": "risk_item_versions",
    }
