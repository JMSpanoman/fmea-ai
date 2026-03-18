"""
Hazard Generation Service (SmartRisk Phase 2).
Walks device architecture (nodes + interfaces), applies rules, returns suggested hazards.
"""
from __future__ import annotations

from typing import List, Optional, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session

from models.device_architecture import DeviceArchitectureNode, DeviceInterface
from models.hazard_generation_rule import HazardGenerationRule
from models.hazard_library import HazardLibrary
from crud import device_architecture as da_crud
from crud import hazard_generation_rule as rule_crud


@dataclass
class SuggestedHazard:
    """One suggested hazard from the rules engine."""
    source_type: str  # "node" | "interface"
    source_id: str
    source_name: str
    rule_id: str
    hazard_library_id: str
    source_extra: Optional[str] = None  # e.g. component_type or interface_type
    hazard_code: Optional[str] = None
    hazard_name: Optional[str] = None
    hazard_description: Optional[str] = None


def _normalize(s: Optional[str]) -> str:
    if s is None:
        return ""
    return s.strip().lower()


def _rule_matches_node(rule: HazardGenerationRule, node: DeviceArchitectureNode) -> bool:
    if rule.trigger_type != "component":
        return False
    if rule.node_type and _normalize(rule.node_type) != _normalize(node.node_type):
        return False
    if rule.component_type and _normalize(rule.component_type) != _normalize(node.component_type or ""):
        return False
    return True


def _rule_matches_interface(rule: HazardGenerationRule, iface: DeviceInterface) -> bool:
    if rule.trigger_type != "interface":
        return False
    if rule.interface_type and _normalize(rule.interface_type) != _normalize(iface.interface_type or ""):
        return False
    return True


def generate_hazards_from_architecture(
    db: Session,
    architecture_id: str,
    only_active_rules: bool = True,
) -> List[SuggestedHazard]:
    """
    For a given device architecture, walk all nodes and interfaces,
    apply hazard generation rules, and return suggested hazards with traceability.
    """
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch:
        return []

    nodes = da_crud.list_all_nodes(db, architecture_id)
    interfaces = da_crud.list_interfaces_by_architecture(db, architecture_id)
    rules: List[HazardGenerationRule] = rule_crud.list_rules(
        db, is_active=only_active_rules, limit=1000
    )

    # Preload hazard library for names
    hazard_ids = {r.hazard_library_id for r in rules}
    hazards_map: dict[str, HazardLibrary] = {}
    if hazard_ids:
        for hid in hazard_ids:
            h = db.query(HazardLibrary).filter(HazardLibrary.id == hid).first()
            if h:
                hazards_map[hid] = h

    result: List[SuggestedHazard] = []

    for node in nodes:
        for rule in rules:
            if not _rule_matches_node(rule, node):
                continue
            h = hazards_map.get(rule.hazard_library_id)
            result.append(
                SuggestedHazard(
                    source_type="node",
                    source_id=node.id,
                    source_name=node.name,
                    source_extra=node.component_type,
                    rule_id=rule.id,
                    hazard_library_id=rule.hazard_library_id,
                    hazard_code=h.hazard_id if h else None,
                    hazard_name=h.hazard_name if h else None,
                    hazard_description=h.description if h else None,
                )
            )

    for iface in interfaces:
        for rule in rules:
            if not _rule_matches_interface(rule, iface):
                continue
            h = hazards_map.get(rule.hazard_library_id)
            name = iface.name or f"{iface.from_node_id[:8]} → {iface.to_node_id[:8]}"
            result.append(
                SuggestedHazard(
                    source_type="interface",
                    source_id=iface.id,
                    source_name=name,
                    source_extra=iface.interface_type,
                    rule_id=rule.id,
                    hazard_library_id=rule.hazard_library_id,
                    hazard_code=h.hazard_id if h else None,
                    hazard_name=h.hazard_name if h else None,
                    hazard_description=h.description if h else None,
                )
            )

    return result


def create_risk_items_from_suggestions(
    db: Session,
    project_id: str,
    suggestions: List[SuggestedHazard],
    created_by: Optional[str] = None,
) -> List[Any]:
    """
    Phase 3: Create risk items from suggested hazards; each gets a new version
    with hazard_library_id set for traceable library linking.
    Returns list of created RiskItem ids.
    """
    from crud import risk_item as risk_item_crud
    from crud import risk_item_version as version_crud
    from schemas.risk_item import RiskItemCreate, RiskItemVersionCreate

    created_ids: List[str] = []
    for s in suggestions:
        create_data = RiskItemCreate(
            project_id=project_id,
            title=s.hazard_name or f"Hazard from {s.source_name}",
            description=s.hazard_description or f"Source: {s.source_type} {s.source_name}",
            category="Safety",
            risk_type="Hazard",
            source="SmartRisk Architecture",
            status="open",
        )
        risk_item = risk_item_crud.create_risk_item(db, create_data, created_by=created_by)
        version_data = RiskItemVersionCreate(
            hazard=s.hazard_name or "",
            hazard_library_id=s.hazard_library_id,
        )
        version_crud.create_risk_item_version(
            db, risk_item.id, version_data, changed_by=created_by or "system", created_by=created_by
        )
        db.commit()
        db.refresh(risk_item)
        created_ids.append(risk_item.id)
    return created_ids
