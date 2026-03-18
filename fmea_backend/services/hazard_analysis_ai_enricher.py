"""
Enriches RiskItem current versions with AI-generated hazard analysis fields (failure_mode, sequence_of_events, etc.).
Creates new immutable versions; does not overwrite approved content.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from models.component import Component
from services.hazard_analysis_ai_service import generate_hazard_analysis_item_with_ai, merge_ai_into_item


@dataclass
class EnrichStats:
    processed: int = 0
    enriched: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "processed": self.processed,
            "enriched": self.enriched,
            "skipped": self.skipped,
            "errors": self.errors,
        }


def enrich_hazard_analysis_fields(
    db: Session,
    *,
    project_id: str,
    user_id: str,
    max_items: int = 25,
    only_if_missing: bool = True,
) -> EnrichStats:
    """
    For risk items in the project, if current version has missing failure_mode or sequence_of_events,
    call AI to propose values and create a new version (does not overwrite approved).
    """
    stats = EnrichStats()
    items = (
        db.query(RiskItem)
        .filter(RiskItem.project_id == project_id)
        .limit(max_items)
        .all()
    )
    # Optional: get project profile for intended_use, use_environment
    profile = None
    try:
        from models.project_profile import ProjectProfile
        profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    except Exception:
        pass
    intended_use = getattr(profile, "intended_use", None) if profile else None
    use_environment = getattr(profile, "use_environment", None) if profile else None
    device_desc = getattr(profile, "device_description", None) if profile else None

    for risk_item in items:
        stats.processed += 1
        current = None
        if risk_item.current_version_id:
            current = db.query(RiskItemVersion).filter(
                RiskItemVersion.id == risk_item.current_version_id
            ).first()
        if not current:
            stats.skipped += 1
            continue
        if only_if_missing and (current.failure_mode or current.sequence_of_events):
            stats.skipped += 1
            continue
        component_name = None
        if risk_item.component_id:
            comp = db.query(Component).filter(Component.id == risk_item.component_id).first()
            if comp:
                component_name = comp.name
        if not component_name:
            component_name = risk_item.component_name or "Component"
        existing = {
            "failure_mode": current.failure_mode,
            "sequence_of_events": current.sequence_of_events,
            "hazard": current.hazard,
            "harm": current.harm,
            "hazardous_situation": current.hazardous_situation,
            "approval_status": "approved",
        }
        ai_out = generate_hazard_analysis_item_with_ai(
            device_type=device_desc,
            component_name=component_name,
            intended_use=intended_use,
            use_environment=use_environment,
            fmea_row=None,
        )
        merged = merge_ai_into_item(existing, ai_out, only_blank=True, approved_statuses=[])
        # Create new version: copy current and set enriched fields
        try:
            new_fm = merged.get("failure_mode") or current.failure_mode
            new_seq = merged.get("foreseeable_sequence_of_events") or merged.get("sequence_of_events") or current.sequence_of_events
            new_version = RiskItemVersion(
                risk_item_id=risk_item.id,
                version_number=(current.version_number or 1) + 1,
                failure_mode=new_fm,
                sequence_of_events=new_seq,
                hazard=current.hazard,
                hazardous_situation=current.hazardous_situation,
                harm=current.harm,
                severity=current.severity,
                probability_of_harm=current.probability_of_harm or current.probability,
                occurrence=current.occurrence,
                detection=current.detection,
                probability=current.probability,
                impact=current.impact,
                risk_score=current.risk_score,
                risk_level=current.risk_level,
                inherent_safety=current.inherent_safety,
                protective_measures=current.protective_measures,
                information_for_safety=current.information_for_safety,
                control_measures_summary=current.control_measures_summary,
                residual_severity=current.residual_severity,
                residual_probability_of_harm=current.residual_probability_of_harm,
                residual_risk_score=current.residual_risk_score,
                residual_risk_level=current.residual_risk_level,
                risk_acceptability=current.risk_acceptability,
                created_by=user_id,
            )
            db.add(new_version)
            db.flush()
            risk_item.current_version_id = new_version.id
            db.commit()
            stats.enriched += 1
        except Exception as e:
            stats.errors.append(str(e))
            db.rollback()
    return stats
