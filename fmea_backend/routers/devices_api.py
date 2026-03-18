"""
Device-scoped risk outputs API.

GET /api/devices/:id/fmea
GET /api/devices/:id/hazard-analysis
GET /api/devices/:id/risk-traceability
GET /api/devices/:id/residual-risk
POST /api/devices/:id/generate-report
"""
from __future__ import annotations

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from models.device import Device
from models.generated_document import GeneratedDocument
from crud import project as project_crud
from services import project_risk_outputs_service as outputs

router = APIRouter(
    prefix="/api/devices",
    tags=["Devices API"],
    dependencies=[Depends(require_pro)],
)


def _get_device_and_ensure_access(
    db: Session, device_id: str, user_id: str
) -> Device:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if not project_crud.get_project(db, device.project_id, user_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return device


@router.get("/{device_id}/fmea")
def get_device_fmea(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FMEA table for risk items belonging to this device."""
    device = _get_device_and_ensure_access(db, device_id, current_user.id)
    return {"rows": outputs.build_fmea_table(db, device.project_id, device_id=device_id)}


@router.get("/{device_id}/hazard-analysis")
def get_device_hazard_analysis(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Hazard analysis table for this device."""
    device = _get_device_and_ensure_access(db, device_id, current_user.id)
    return {
        "rows": outputs.build_hazard_analysis_table(
            db, device.project_id, device_id=device_id
        )
    }


@router.get("/{device_id}/risk-traceability")
def get_device_risk_traceability(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Risk control traceability table for this device."""
    device = _get_device_and_ensure_access(db, device_id, current_user.id)
    return {
        "rows": outputs.build_risk_control_traceability_table(
            db, device.project_id, device_id=device_id
        )
    }


@router.get("/{device_id}/residual-risk")
def get_device_residual_risk(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Residual risk evaluation table for this device."""
    device = _get_device_and_ensure_access(db, device_id, current_user.id)
    return {
        "rows": outputs.build_residual_risk_evaluation_table(
            db, device.project_id, device_id=device_id
        )
    }


@router.post("/{device_id}/generate-report")
def generate_device_report(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a risk report for the device and store it as a generated document. Returns the document."""
    device = _get_device_and_ensure_access(db, device_id, current_user.id)
    content = outputs.build_device_report_content(
        db, device.project_id, device_id
    )
    title = f"Risk Report — {device.name or device_id[:8]}"
    # Store JSON as string in DB
    content_json_str = json.dumps(content["content_json"]) if content.get("content_json") else None
    doc = GeneratedDocument(
        device_id=device_id,
        document_type="risk_report",
        title=title,
        content_json=content_json_str,
        content_markdown=content.get("content_markdown") or "",
        version=1,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {
        "id": doc.id,
        "device_id": doc.device_id,
        "document_type": doc.document_type,
        "title": doc.title,
        "version": doc.version,
        "created_at": doc.created_at,
    }
