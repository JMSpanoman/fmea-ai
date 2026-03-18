"""
Device-scoped API: list devices, get device, device components, and risk outputs.

GET /api/devices — list devices (user's projects)
GET /api/devices/:id — get one device
GET /api/devices/:id/components — list components for this device
GET /api/devices/:id/components/:componentId — get one component
GET /api/devices/:id/fmea, hazard-analysis, risk-traceability, residual-risk
POST /api/devices/:id/generate-report
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from models.device import Device
from models.component import Component
from models.generated_document import GeneratedDocument
from models.project_risk_item import ProjectRiskItem
from crud import project as project_crud
from services import project_risk_outputs_service as outputs

# Prefix /devices (Vite proxy strips /api, so backend receives /devices not /api/devices)
router = APIRouter(
    prefix="/devices",
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


def _device_to_dict(d: Device) -> Dict[str, Any]:
    return {
        "id": d.id,
        "project_id": d.project_id,
        "name": d.name or "",
        "description": d.description or "",
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
    }


def _component_type_from_tags(tags: Any) -> str:
    """Derive component_type from Component.tags (e.g. type or component_type)."""
    if not tags or not isinstance(tags, dict):
        return ""
    return str(tags.get("type") or tags.get("component_type") or "").strip()


def _critical_to_essential_from_tags(tags: Any) -> str:
    """Derive critical_to_essential_performance from Component.tags."""
    if not tags or not isinstance(tags, dict):
        return ""
    return str(tags.get("critical_to_essential_performance") or "").strip()


# Reserved tag keys not included in generic "attributes"
_RESERVED_TAG_KEYS = frozenset(("type", "component_type", "critical_to_essential_performance", "functions", "interfaces", "attributes"))


def _attributes_from_tags(tags: Any) -> Dict[str, Any]:
    """Build attributes dict from Component.tags (e.g. patient_contact, software_controlled)."""
    if not tags or not isinstance(tags, dict):
        return {}
    if "attributes" in tags and isinstance(tags["attributes"], dict):
        return dict(tags["attributes"])
    return {k: v for k, v in tags.items() if k not in _RESERVED_TAG_KEYS and v is not None}


def _functions_from_tags(tags: Any) -> List[Any]:
    """Functions list from Component.tags."""
    if not tags or not isinstance(tags, dict):
        return []
    f = tags.get("functions")
    return list(f) if isinstance(f, list) else []


def _interfaces_from_tags(tags: Any) -> List[Any]:
    """Interfaces list from Component.tags (each item can be str or dict)."""
    if not tags or not isinstance(tags, dict):
        return []
    i = tags.get("interfaces")
    return list(i) if isinstance(i, list) else []


def _component_to_device_dict(c: Component, risk_count: int = 0) -> Dict[str, Any]:
    tags = c.tags or {}
    return {
        "id": c.id,
        "project_id": c.project_id,
        "component_name": c.name or "",
        "component_type": _component_type_from_tags(tags),
        "critical_to_essential_performance": _critical_to_essential_from_tags(tags),
        "risk_items_count": risk_count,
    }


def _component_to_detail_dict(c: Component, risk_count: int = 0) -> Dict[str, Any]:
    """Full detail for device component: name, type, attributes, functions, interfaces."""
    tags = c.tags or {}
    return {
        "id": c.id,
        "project_id": c.project_id,
        "component_name": c.name or "",
        "component_type": _component_type_from_tags(tags),
        "critical_to_essential_performance": _critical_to_essential_from_tags(tags),
        "risk_items_count": risk_count,
        "attributes": _attributes_from_tags(tags),
        "functions": _functions_from_tags(tags),
        "interfaces": _interfaces_from_tags(tags),
    }


class CreateDeviceBody(BaseModel):
    project_id: str
    name: Optional[str] = None
    description: Optional[str] = None


@router.get("", response_model=List[Dict[str, Any]])
def list_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all devices from projects the current user has access to."""
    projects = project_crud.get_projects_by_user(db, current_user.id)
    project_ids = [p.id for p in projects]
    devices = db.query(Device).filter(Device.project_id.in_(project_ids)).order_by(Device.created_at.desc()).all()
    return [_device_to_dict(d) for d in devices]


@router.post("", response_model=Dict[str, Any], status_code=201)
def create_device(
    body: CreateDeviceBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a device for a project the user has access to."""
    project = project_crud.get_project(db, body.project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    device = Device(
        project_id=body.project_id,
        name=body.name or (project.name + " Device" if getattr(project, "name", None) else "Device"),
        description=body.description,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return _device_to_dict(device)


@router.get("/{device_id}", response_model=Dict[str, Any])
def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one device by ID."""
    device = _get_device_and_ensure_access(db, device_id, current_user.id)
    return _device_to_dict(device)


@router.get("/{device_id}/components", response_model=List[Dict[str, Any]])
def list_device_components(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all components for the device's project, with risk item count for this device."""
    device = _get_device_and_ensure_access(db, device_id, current_user.id)
    components = (
        db.query(Component)
        .filter(Component.project_id == device.project_id)
        .order_by(Component.name)
        .all()
    )
    count_q = (
        db.query(ProjectRiskItem.component_id, func.count(ProjectRiskItem.id).label("cnt"))
        .filter(ProjectRiskItem.device_id == device_id)
        .group_by(ProjectRiskItem.component_id)
    )
    count_by_cid = {row.component_id: row.cnt for row in count_q}
    return [
        _component_to_device_dict(c, risk_count=count_by_cid.get(c.id, 0))
        for c in components
    ]


@router.get("/{device_id}/components/{component_id}", response_model=Dict[str, Any])
def get_device_component(
    device_id: str,
    component_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one component for this device (must belong to device's project and have risk items for this device)."""
    device = _get_device_and_ensure_access(db, device_id, current_user.id)
    component = (
        db.query(Component)
        .filter(
            Component.id == component_id,
            Component.project_id == device.project_id,
        )
        .first()
    )
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    risk_count = (
        db.query(ProjectRiskItem)
        .filter(
            ProjectRiskItem.device_id == device_id,
            ProjectRiskItem.component_id == component_id,
        )
        .count()
    )
    return _component_to_detail_dict(component, risk_count=risk_count)


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
