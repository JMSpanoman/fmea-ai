"""
Risk Analysis Generation Service (SmartRisk).
Reads a component (node or interface) and its attributes, evaluates all active rules,
generates suggested failure modes, hazards, hazardous situations, harms, controls,
and verification methods, and stores them in suggested_* tables.
Supports regeneration when component data changes.
"""
from __future__ import annotations

import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from models.device_architecture import DeviceArchitectureNode, DeviceInterface
from models.component import Component
from models.hazard_generation_rule import HazardGenerationRule
from models.hazard_library import HazardLibrary
from models.harm_library import HarmLibrary
from models.risk_control_library import RiskControlLibrary
from models.verification_library import VerificationLibrary
from models.suggested_risk_analysis import (
    RiskAnalysisSuggestionSet,
    SuggestedFailureMode,
    SuggestedHazard as SuggestedHazardRow,
    SuggestedHazardousSituation,
    SuggestedHarm,
    SuggestedControl,
    SuggestedVerificationMethod,
)
from crud import device_architecture as da_crud
from crud import component as component_crud
from crud import hazard_generation_rule as rule_crud
from crud import suggested_risk_analysis as suggested_crud


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


def _get_component_type_from_tags(tags: Any) -> str:
    """Derive component_type from Component.tags (e.g. {"type": "electrical"} or {"component_type": "mechanical"})."""
    if not tags or not isinstance(tags, dict):
        return ""
    return _normalize(str(tags.get("type") or tags.get("component_type") or ""))


def _rule_matches_project_component(rule: HazardGenerationRule, component: Component) -> bool:
    if rule.trigger_type != "component":
        return False
    comp_type = _get_component_type_from_tags(component.tags)
    if rule.component_type and _normalize(rule.component_type) != comp_type:
        return False
    return True


def _get_component_attributes_project_component(component: Component) -> Dict[str, str]:
    return {
        "component_name": component.name or "",
        "component_type": _get_component_type_from_tags(component.tags),
        "description": component.description or "",
    }


def _template_replace(template: Optional[str], placeholders: Dict[str, str]) -> str:
    if not template or not template.strip():
        return ""
    text = template
    for key, value in placeholders.items():
        text = text.replace("{{" + key + "}}", value or "")
    return text.strip()


def _get_component_attributes_node(node: DeviceArchitectureNode) -> Dict[str, str]:
    return {
        "component_name": node.name or "",
        "component_type": node.component_type or "",
        "node_type": node.node_type or "",
        "description": node.description or "",
    }


def _get_component_attributes_interface(
    iface: DeviceInterface, from_name: str = "", to_name: str = ""
) -> Dict[str, str]:
    return {
        "component_name": iface.name or f"{from_name} to {to_name}".strip() or "Interface",
        "component_type": iface.interface_type or "",
        "interface_type": iface.interface_type or "",
        "from_node": from_name,
        "to_node": to_name,
        "description": iface.description or "",
    }


def _create_suggestion_set_and_children(
    db: Session,
    source_type: str,
    source_id: str,
    rule: HazardGenerationRule,
    placeholders: Dict[str, str],
    libraries: Dict[str, Any],
    architecture_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> RiskAnalysisSuggestionSet:
    """
    Create one RiskAnalysisSuggestionSet and its child rows from a rule and libraries.
    libraries: dict with keys hazard, harm, risk_control, verification (each the ORM object or None).
    For node/interface pass architecture_id; for component pass project_id.
    """
    set_row = RiskAnalysisSuggestionSet(
        source_type=source_type,
        source_id=source_id,
        architecture_id=architecture_id,
        project_id=project_id,
        rule_id=rule.id,
    )
    db.add(set_row)
    db.flush()

    # Failure mode (from template)
    if rule.failure_mode_template:
        text = _template_replace(rule.failure_mode_template, placeholders)
        if text:
            db.add(SuggestedFailureMode(suggestion_set_id=set_row.id, text=text))

    # Hazard (from hazard library)
    hazard = libraries.get("hazard")
    hazard_text = (hazard.hazard_name or "") if hazard else ""
    if hazard and hazard.description:
        hazard_text = f"{hazard_text}: {hazard.description}" if hazard_text else hazard.description
    if not hazard_text:
        hazard_text = "(Hazard from rule)"
    db.add(SuggestedHazardRow(
        suggestion_set_id=set_row.id,
        text=hazard_text,
        hazard_library_id=rule.hazard_library_id,
    ))

    # Hazardous situation (from template)
    if rule.hazardous_situation_template:
        text = _template_replace(rule.hazardous_situation_template, placeholders)
        if text:
            db.add(SuggestedHazardousSituation(suggestion_set_id=set_row.id, text=text))

    # Harm (from harm library if set)
    if rule.harm_library_id:
        harm = libraries.get("harm")
        harm_text = (harm.harm_name or "") if harm else ""
        if harm and harm.description:
            harm_text = f"{harm_text}: {harm.description}" if harm_text else harm.description
        if harm_text:
            db.add(SuggestedHarm(
                suggestion_set_id=set_row.id,
                text=harm_text,
                harm_library_id=rule.harm_library_id,
            ))

    # Control (from risk control library if set)
    if rule.risk_control_library_id:
        control = libraries.get("risk_control")
        control_text = (control.control_name or "") if control else ""
        if control and control.description:
            control_text = f"{control_text}: {control.description}" if control_text else control.description
        if control_text:
            db.add(SuggestedControl(
                suggestion_set_id=set_row.id,
                text=control_text,
                risk_control_library_id=rule.risk_control_library_id,
            ))

    # Verification (from verification library if set)
    if rule.verification_library_id:
        verification = libraries.get("verification")
        verification_text = (verification.verification_method or "") if verification else ""
        if verification and verification.description:
            verification_text = f"{verification_text}: {verification.description}" if verification_text else verification.description
        if verification_text:
            db.add(SuggestedVerificationMethod(
                suggestion_set_id=set_row.id,
                text=verification_text,
                verification_library_id=rule.verification_library_id,
            ))

    return set_row


def _load_libraries_for_rules(
    db: Session, rules: List[HazardGenerationRule]
) -> Dict[str, Dict[str, Any]]:
    """Preload hazard, harm, risk_control, verification by id for all rules."""
    hazard_ids = {r.hazard_library_id for r in rules}
    harm_ids = {r.harm_library_id for r in rules if r.harm_library_id}
    control_ids = {r.risk_control_library_id for r in rules if r.risk_control_library_id}
    verification_ids = {r.verification_library_id for r in rules if r.verification_library_id}

    hazards = {}
    for hid in hazard_ids:
        h = db.query(HazardLibrary).filter(HazardLibrary.id == hid).first()
        if h:
            hazards[hid] = h
    harms = {}
    for hid in harm_ids:
        h = db.query(HarmLibrary).filter(HarmLibrary.id == hid).first()
        if h:
            harms[hid] = h
    controls = {}
    for cid in control_ids:
        c = db.query(RiskControlLibrary).filter(RiskControlLibrary.id == cid).first()
        if c:
            controls[cid] = c
    verifications = {}
    for vid in verification_ids:
        v = db.query(VerificationLibrary).filter(VerificationLibrary.id == vid).first()
        if v:
            verifications[vid] = v

    def libs_for_rule(rule: HazardGenerationRule) -> Dict[str, Any]:
        out = {
            "hazard": hazards.get(rule.hazard_library_id),
            "harm": harms.get(rule.harm_library_id) if rule.harm_library_id else None,
            "risk_control": controls.get(rule.risk_control_library_id) if rule.risk_control_library_id else None,
            "verification": verifications.get(rule.verification_library_id) if rule.verification_library_id else None,
        }
        return out

    return {r.id: libs_for_rule(r) for r in rules}


def generate_and_store_for_component(
    db: Session,
    source_type: str,
    source_id: str,
    architecture_id: str,
    regenerate: bool = True,
    only_active_rules: bool = True,
) -> int:
    """
    Read a component (node or interface), evaluate all active rules, generate suggestions,
    and store them in suggested_* tables.
    If regenerate is True, deletes existing suggestions for this source first.
    Returns the number of suggestion sets created.
    """
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch:
        return 0

    if regenerate:
        suggested_crud.delete_suggestions_by_source(
            db, source_type=source_type, source_id=source_id, architecture_id=architecture_id
        )

    rules = rule_crud.list_rules(db, is_active=only_active_rules, limit=1000)
    if not rules:
        return 0

    libraries_by_rule = _load_libraries_for_rules(db, rules)
    placeholders: Dict[str, str]
    created = 0

    if source_type == "node":
        node = da_crud.get_node(db, source_id)
        if not node or node.architecture_id != architecture_id:
            return 0
        placeholders = _get_component_attributes_node(node)
        for rule in rules:
            if not _rule_matches_node(rule, node):
                continue
            libs = libraries_by_rule.get(rule.id, {})
            _create_suggestion_set_and_children(
                db, "node", source_id, rule, placeholders, libs, architecture_id=architecture_id
            )
            created += 1
    else:
        iface = da_crud.get_interface(db, source_id)
        if not iface or iface.architecture_id != architecture_id:
            return 0
        from_name = ""
        to_name = ""
        if iface.from_node:
            from_name = iface.from_node.name or ""
        if iface.to_node:
            to_name = iface.to_node.name or ""
        placeholders = _get_component_attributes_interface(iface, from_name, to_name)
        for rule in rules:
            if not _rule_matches_interface(rule, iface):
                continue
            libs = libraries_by_rule.get(rule.id, {})
            _create_suggestion_set_and_children(
                db, "interface", source_id, rule, placeholders, libs, architecture_id=architecture_id
            )
            created += 1

    db.commit()
    return created


def generate_and_store_for_architecture(
    db: Session,
    architecture_id: str,
    regenerate: bool = True,
    only_active_rules: bool = True,
) -> int:
    """
    Generate and store suggestions for all nodes and interfaces in an architecture.
    If regenerate is True, deletes all existing suggestions for this architecture first.
    Returns total number of suggestion sets created.
    """
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch:
        return 0

    if regenerate:
        suggested_crud.delete_suggestions_by_architecture(db, architecture_id)

    rules = rule_crud.list_rules(db, is_active=only_active_rules, limit=1000)
    if not rules:
        return 0

    libraries_by_rule = _load_libraries_for_rules(db, rules)
    nodes = da_crud.list_all_nodes(db, architecture_id)
    interfaces = da_crud.list_interfaces_by_architecture(db, architecture_id)
    created = 0

    for node in nodes:
        placeholders = _get_component_attributes_node(node)
        for rule in rules:
            if not _rule_matches_node(rule, node):
                continue
            libs = libraries_by_rule.get(rule.id, {})
            _create_suggestion_set_and_children(
                db, "node", node.id, rule, placeholders, libs, architecture_id=architecture_id
            )
            created += 1

    for iface in interfaces:
        from_name = iface.from_node.name if iface.from_node else ""
        to_name = iface.to_node.name if iface.to_node else ""
        placeholders = _get_component_attributes_interface(iface, from_name, to_name)
        for rule in rules:
            if not _rule_matches_interface(rule, iface):
                continue
            libs = libraries_by_rule.get(rule.id, {})
            _create_suggestion_set_and_children(
                db, "interface", iface.id, rule, placeholders, libs, architecture_id=architecture_id
            )
            created += 1

    db.commit()
    return created


def generate_and_store_for_project_component(
    db: Session,
    project_id: str,
    component_id: str,
    regenerate: bool = True,
    only_active_rules: bool = True,
) -> int:
    """
    Generate and store risk suggestions for a project Component (FMEA/components tree).
    Reads component attributes (name, description, tags); derives component_type from tags.type or tags.component_type.
    Evaluates all active rules with trigger_type='component'; creates suggestion sets with project_id set, architecture_id null.
    If regenerate is True, deletes existing suggestions for this component first.
    Returns the number of suggestion sets created.
    """
    component = component_crud.get_component(db, component_id, project_id)
    if not component:
        return 0

    if regenerate:
        suggested_crud.delete_suggestions_by_component(db, project_id, component_id)

    rules = rule_crud.list_rules(db, is_active=only_active_rules, limit=1000)
    rules = [r for r in rules if r.trigger_type == "component"]
    if not rules:
        return 0

    libraries_by_rule = _load_libraries_for_rules(db, rules)
    placeholders = _get_component_attributes_project_component(component)
    created = 0

    for rule in rules:
        if not _rule_matches_project_component(rule, component):
            continue
        libs = libraries_by_rule.get(rule.id, {})
        _create_suggestion_set_and_children(
            db,
            "component",
            component_id,
            rule,
            placeholders,
            libs,
            project_id=project_id,
        )
        created += 1

    db.commit()
    return created
