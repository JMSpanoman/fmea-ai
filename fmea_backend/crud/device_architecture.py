"""CRUD for Device Architecture (SmartRisk Phase 1)."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from models.device_architecture import DeviceArchitecture, DeviceArchitectureNode, DeviceInterface
from schemas.device_architecture import (
    DeviceArchitectureCreate,
    DeviceArchitectureUpdate,
    DeviceArchitectureNodeCreate,
    DeviceArchitectureNodeUpdate,
    DeviceInterfaceCreate,
    DeviceInterfaceUpdate,
)


def _update_from_schema(obj, schema):
    data = schema.model_dump(exclude_unset=True)
    for field, value in data.items():
        if hasattr(obj, field):
            setattr(obj, field, value)


# ----- DeviceArchitecture -----
def create_architecture(
    db: Session, project_id: str, data: DeviceArchitectureCreate
) -> DeviceArchitecture:
    row = DeviceArchitecture(project_id=project_id, **data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_architecture(db: Session, architecture_id: str) -> Optional[DeviceArchitecture]:
    return db.query(DeviceArchitecture).filter(DeviceArchitecture.id == architecture_id).first()


def list_architectures_by_project(
    db: Session, project_id: str
) -> List[DeviceArchitecture]:
    return (
        db.query(DeviceArchitecture)
        .filter(DeviceArchitecture.project_id == project_id)
        .order_by(DeviceArchitecture.created_at.desc())
        .all()
    )


def update_architecture(
    db: Session, architecture_id: str, data: DeviceArchitectureUpdate
) -> Optional[DeviceArchitecture]:
    row = get_architecture(db, architecture_id)
    if not row:
        return None
    _update_from_schema(row, data)
    db.commit()
    db.refresh(row)
    return row


def delete_architecture(db: Session, architecture_id: str) -> bool:
    row = get_architecture(db, architecture_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


# ----- DeviceArchitectureNode -----
def create_node(
    db: Session, architecture_id: str, data: DeviceArchitectureNodeCreate
) -> Optional[DeviceArchitectureNode]:
    arch = get_architecture(db, architecture_id)
    if not arch:
        return None
    payload = data.model_dump()
    if payload.get("parent_id") and not get_node(db, payload["parent_id"]):
        payload["parent_id"] = None
    row = DeviceArchitectureNode(architecture_id=architecture_id, **payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_node(db: Session, node_id: str) -> Optional[DeviceArchitectureNode]:
    return db.query(DeviceArchitectureNode).filter(DeviceArchitectureNode.id == node_id).first()


def list_nodes_by_architecture(
    db: Session, architecture_id: str, parent_id: Optional[str] = None
) -> List[DeviceArchitectureNode]:
    q = db.query(DeviceArchitectureNode).filter(
        DeviceArchitectureNode.architecture_id == architecture_id
    )
    if parent_id is None:
        q = q.filter(DeviceArchitectureNode.parent_id.is_(None))
    else:
        q = q.filter(DeviceArchitectureNode.parent_id == parent_id)
    return q.order_by(DeviceArchitectureNode.sort_order, DeviceArchitectureNode.name).all()


def list_all_nodes(db: Session, architecture_id: str) -> List[DeviceArchitectureNode]:
    return (
        db.query(DeviceArchitectureNode)
        .filter(DeviceArchitectureNode.architecture_id == architecture_id)
        .order_by(DeviceArchitectureNode.sort_order, DeviceArchitectureNode.name)
        .all()
    )


def update_node(
    db: Session, node_id: str, data: DeviceArchitectureNodeUpdate
) -> Optional[DeviceArchitectureNode]:
    row = get_node(db, node_id)
    if not row:
        return None
    _update_from_schema(row, data)
    db.commit()
    db.refresh(row)
    return row


def delete_node(db: Session, node_id: str) -> bool:
    row = get_node(db, node_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


# ----- DeviceInterface -----
def create_interface(
    db: Session, architecture_id: str, data: DeviceInterfaceCreate
) -> Optional[DeviceInterface]:
    arch = get_architecture(db, architecture_id)
    if not arch:
        return None
    from_ok = get_node(db, data.from_node_id) and get_node(db, data.to_node_id)
    if not from_ok:
        return None
    row = DeviceInterface(architecture_id=architecture_id, **data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_interface(db: Session, interface_id: str) -> Optional[DeviceInterface]:
    return db.query(DeviceInterface).filter(DeviceInterface.id == interface_id).first()


def list_interfaces_by_architecture(
    db: Session, architecture_id: str
) -> List[DeviceInterface]:
    return (
        db.query(DeviceInterface)
        .filter(DeviceInterface.architecture_id == architecture_id)
        .all()
    )


def update_interface(
    db: Session, interface_id: str, data: DeviceInterfaceUpdate
) -> Optional[DeviceInterface]:
    row = get_interface(db, interface_id)
    if not row:
        return None
    _update_from_schema(row, data)
    db.commit()
    db.refresh(row)
    return row


def delete_interface(db: Session, interface_id: str) -> bool:
    row = get_interface(db, interface_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True
