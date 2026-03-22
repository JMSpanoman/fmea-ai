from sqlalchemy.orm import Session, selectinload
from models.capa import CAPA
from models.capa_evidence import CAPAEvidence
from schemas.capa import CAPACreate, CAPAUpdate, CAPAEvidenceCreate, CAPAFullOut, CAPAEvidenceOut
from schemas.capa_workflow import CAPAWorkflowPayload, default_workflow_payload
from services.capa_workflow_service import (
    coerce_payload,
    default_approval_scaffold,
    legacy_to_payload,
    payload_to_legacy_fields,
    validate_payload_for_state,
)
from typing import List, Optional, Set
import uuid


def _ensure_action_ids(payload: CAPAWorkflowPayload) -> None:
    for a in payload.corrective_actions:
        if not str(a.id or "").strip():
            a.id = str(uuid.uuid4())
    for a in payload.preventive.items:
        if not str(a.id or "").strip():
            a.id = str(uuid.uuid4())


def create_capa(db: Session, capa: CAPACreate) -> CAPA:
    """Create a new CAPA with workflow payload defaults."""
    payload_dict = capa.payload
    if payload_dict is not None:
        p = CAPAWorkflowPayload.model_validate(payload_dict)
    else:
        p = CAPAWorkflowPayload.model_validate(default_workflow_payload())
        if not p.approvals:
            p.approvals = default_approval_scaffold()
    _ensure_action_ids(p)
    # Merge explicit create fields into payload (risk_items / PMS integrations pass text here).
    if capa.root_cause:
        p.rca.root_cause_summary = capa.root_cause
    if capa.capa_plan:
        p.voe_plan.success_criteria = capa.capa_plan
    # Legacy field maps to VoE *plan* text, not effectiveness results (evidence-gated).
    if capa.effectiveness_check:
        p.voe_plan.method = capa.effectiveness_check
    if capa.linked_risk_ids:
        p.risk_linkage.related_fmea_row_ids = list(capa.linked_risk_ids)

    root, plan, eff, risks = payload_to_legacy_fields(p)

    db_capa = CAPA(
        id=str(uuid.uuid4()),
        project_id=capa.project_id,
        root_cause=capa.root_cause or root,
        capa_plan=capa.capa_plan or plan,
        effectiveness_check=capa.effectiveness_check,
        linked_risk_ids=capa.linked_risk_ids or risks or [],
        ai_metadata=capa.ai_metadata,
        workflow_state=capa.workflow_state or "draft",
        payload=p.model_dump(mode="json"),
    )
    db.add(db_capa)
    db.commit()
    db.refresh(db_capa)
    return db_capa


def get_capas_by_project(db: Session, project_id: str) -> List[CAPA]:
    return (
        db.query(CAPA)
        .filter(CAPA.project_id == project_id)
        .order_by(CAPA.created_at.desc())
        .all()
    )


def get_capa(db: Session, capa_id: str, project_id: str) -> Optional[CAPA]:
    return (
        db.query(CAPA)
        .options(selectinload(CAPA.evidences))
        .filter(CAPA.id == capa_id, CAPA.project_id == project_id)
        .first()
    )


def capa_to_full_out(db: Session, row: CAPA) -> CAPAFullOut:
    """Build CAPAFullOut with payload coercion from legacy columns if needed."""
    if row.payload:
        payload = coerce_payload(row.payload)
    else:
        payload = legacy_to_payload(
            row.root_cause or "",
            row.capa_plan or "",
            row.effectiveness_check,
            row.linked_risk_ids or [],
        )
    evs = row.evidences if hasattr(row, "evidences") and row.evidences else []
    if not evs:
        evs = (
            db.query(CAPAEvidence).filter(CAPAEvidence.capa_id == row.id).all()
        )
    ev_out = [CAPAEvidenceOut.model_validate(e) for e in evs]
    return CAPAFullOut(
        id=row.id,
        project_id=row.project_id,
        created_at=row.created_at,
        updated_at=getattr(row, "updated_at", None),
        workflow_state=row.workflow_state or "draft",
        root_cause=row.root_cause,
        capa_plan=row.capa_plan,
        effectiveness_check=row.effectiveness_check,
        linked_risk_ids=row.linked_risk_ids,
        ai_metadata=row.ai_metadata,
        payload=payload,
        evidences=ev_out,
    )


def update_capa(
    db: Session,
    capa_id: str,
    capa: CAPAUpdate,
    project_id: str,
    *,
    strict_validation: bool = True,
) -> Optional[CAPA]:
    """Update CAPA; validates workflow when payload or workflow_state changes."""
    db_capa = get_capa(db, capa_id, project_id)
    if not db_capa:
        return None

    update_data = capa.model_dump(exclude_unset=True) if hasattr(capa, "model_dump") else capa.dict(exclude_unset=True)

    evidence_rows = (
        db.query(CAPAEvidence).filter(CAPAEvidence.capa_id == capa_id).all()
    )
    eids: Set[str] = {e.id for e in evidence_rows}

    if "payload" in update_data and update_data["payload"] is not None:
        payload = CAPAWorkflowPayload.model_validate(update_data["payload"])
        _ensure_action_ids(payload)
        wf = str(update_data.get("workflow_state") or db_capa.workflow_state or "draft")
        if strict_validation:
            validate_payload_for_state(wf, payload, len(evidence_rows), eids)
        root, plan, eff, risks = payload_to_legacy_fields(payload)
        db_capa.root_cause = update_data.get("root_cause", root)
        db_capa.capa_plan = update_data.get("capa_plan", plan)
        db_capa.effectiveness_check = update_data.get("effectiveness_check", eff)
        db_capa.linked_risk_ids = update_data.get("linked_risk_ids", risks)
        db_capa.payload = payload.model_dump(mode="json")
        if "workflow_state" in update_data:
            db_capa.workflow_state = update_data["workflow_state"]
    elif "workflow_state" in update_data:
        payload = coerce_payload(db_capa.payload) if db_capa.payload else legacy_to_payload(
            db_capa.root_cause or "",
            db_capa.capa_plan or "",
            db_capa.effectiveness_check,
            db_capa.linked_risk_ids or [],
        )
        wf = str(update_data["workflow_state"])
        if strict_validation:
            validate_payload_for_state(wf, payload, len(evidence_rows), eids)
        db_capa.workflow_state = wf
    else:
        for field, value in update_data.items():
            if field == "payload":
                continue
            if hasattr(db_capa, field):
                setattr(db_capa, field, value)

    if "ai_metadata" in update_data:
        db_capa.ai_metadata = update_data["ai_metadata"]

    db.add(db_capa)
    db.commit()
    db.refresh(db_capa)
    return db_capa


def add_evidence(
    db: Session,
    capa_id: str,
    project_id: str,
    body: CAPAEvidenceCreate,
) -> Optional[CAPAEvidence]:
    capa = get_capa(db, capa_id, project_id)
    if not capa:
        return None
    ev = CAPAEvidence(
        id=str(uuid.uuid4()),
        capa_id=capa_id,
        category=body.category,
        title=body.title,
        reference_uri=body.reference_uri,
        notes=body.notes,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def delete_capa(db: Session, capa_id: str, project_id: str) -> bool:
    """Delete CAPA and cascaded evidences."""
    db_capa = get_capa(db, capa_id, project_id)
    if not db_capa:
        return False
    db.delete(db_capa)
    db.commit()
    return True


def delete_evidence(
    db: Session,
    capa_id: str,
    project_id: str,
    evidence_id: str,
) -> bool:
    capa = get_capa(db, capa_id, project_id)
    if not capa:
        return False
    ev = (
        db.query(CAPAEvidence)
        .filter(CAPAEvidence.id == evidence_id, CAPAEvidence.capa_id == capa_id)
        .first()
    )
    if not ev:
        return False
    db.delete(ev)
    db.commit()
    return True
