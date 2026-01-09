"""
Design Inputs Documentation evidence builder (Risk Control → Requirement).
Builds a point-in-time report of Design Inputs derived from Risk Controls via trace_links.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.design_input import DesignInput
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from models.risk_control import RiskControl
from models.trace_link import TraceLink
from models.component import Component


def _component_filter_to_names_and_ids(component_filter: Optional[List[Dict[str, Any]]]) -> tuple[list[str], list[str]]:
    ids: list[str] = []
    names: list[str] = []
    for c in component_filter or []:
        if c.get("id"):
            ids.append(str(c["id"]))
        if c.get("name"):
            names.append(str(c["name"]))
    return names, ids


def build_design_inputs_report_evidence(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    missing_output: Optional[bool] = None,
    missing_verification: Optional[bool] = None,
    include_unlinked: bool = False,
) -> Dict[str, Any]:
    """
    Evidence builder for the Design Inputs Documentation report.

    - If include_unlinked=False (default): include only Design Inputs that have at least one upstream risk_control link.
    - If include_unlinked=True: include all Design Inputs (filtered by status), and flag those missing upstream control links.
    """

    comp_names, comp_ids = _component_filter_to_names_and_ids(component_filter)

    # Resolve component names by IDs if provided
    if comp_ids and not comp_names:
        comps = db.query(Component).filter(Component.project_id == project_id, Component.id.in_(comp_ids)).all()
        comp_names = [c.name for c in comps if c.name]

    # Scope risk items by components (if provided)
    risk_items_query = db.query(RiskItem).filter(RiskItem.project_id == project_id)
    if comp_ids or comp_names:
        filters = []
        if comp_ids:
            filters.append(RiskItem.component_id.in_(comp_ids))
        if comp_names:
            filters.append(RiskItem.component_name.in_(comp_names))
        if filters:
            risk_items_query = risk_items_query.filter(or_(*filters))
    risk_items = risk_items_query.all()
    risk_item_by_id = {r.id: r for r in risk_items}

    # Get controls for scoped risk items
    risk_item_ids = list(risk_item_by_id.keys())
    controls: List[RiskControl] = []
    if risk_item_ids:
        controls = db.query(RiskControl).filter(RiskControl.risk_item_id.in_(risk_item_ids)).all()
    control_by_id = {c.id: c for c in controls}

    # Find trace links: risk_control -> design_input (canonical traces_to OR implements)
    control_ids = list(control_by_id.keys())
    trace_links: List[TraceLink] = []
    if control_ids:
        trace_links = (
            db.query(TraceLink)
            .filter(
                TraceLink.project_id == project_id,
                TraceLink.from_type == "risk_control",
                TraceLink.from_id.in_(control_ids),
                TraceLink.to_type == "design_input",
            )
            .all()
        )

    di_ids_linked: Set[str] = {tl.to_id for tl in trace_links}

    # Candidate DIs for report
    di_query = db.query(DesignInput).filter(DesignInput.project_id == project_id)
    if status_filter:
        di_query = di_query.filter(DesignInput.status == status_filter)
    design_inputs_all = di_query.all()

    if include_unlinked:
        design_inputs = design_inputs_all
    else:
        design_inputs = [di for di in design_inputs_all if di.id in di_ids_linked]

    # Preload risk versions for hazard/harm
    current_version_ids: Set[str] = set()
    for ri in risk_items:
        if getattr(ri, "current_version_id", None):
            current_version_ids.add(ri.current_version_id)
    versions_by_id: Dict[str, RiskItemVersion] = {}
    if current_version_ids:
        versions = db.query(RiskItemVersion).filter(RiskItemVersion.id.in_(list(current_version_ids))).all()
        versions_by_id = {v.id: v for v in versions}

    # Build mapping: di_id -> upstream controls + upstream risks
    upstream_controls_by_di: Dict[str, List[Dict[str, Any]]] = {}
    upstream_risks_by_di: Dict[str, List[Dict[str, Any]]] = {}

    for tl in trace_links:
        di_id = tl.to_id
        ctrl = control_by_id.get(tl.from_id)
        if not ctrl:
            continue

        upstream_controls_by_di.setdefault(di_id, []).append(
            {
                "control_id": ctrl.id,
                "control_key": ctrl.control_key or f"RC-{ctrl.id[:8]}",
                "control_name": ctrl.control_name,
                "name": ctrl.control_name,  # spec convenience
                "link_type": tl.link_type or "traces_to",
                "created_at": tl.created_at.isoformat() if tl.created_at else None,
            }
        )

        # Optionally include upstream risks via risk_controls.risk_item_id -> risk_items + current version
        ri = risk_item_by_id.get(ctrl.risk_item_id)
        if ri:
            v = versions_by_id.get(getattr(ri, "current_version_id", "") or "")
            upstream_risks_by_di.setdefault(di_id, []).append(
                {
                    "risk_item_id": ri.id,
                    "risk_key": ri.risk_key or f"R-{ri.id[:8]}",
                    "hazard": getattr(v, "hazard", None) if v else None,
                    "harm": getattr(v, "harm", None) if v else None,
                }
            )

    # Downstream links:
    # - design_input -> design_output (implements)
    # - design_output -> vv_test (verified_by)
    # - optional design_input -> vv_test (either verified_by or traces_to, tolerate)
    di_ids = [di.id for di in design_inputs_all]

    di_to_do_links: List[TraceLink] = []
    if di_ids:
        di_to_do_links = (
            db.query(TraceLink)
            .filter(
                TraceLink.project_id == project_id,
                TraceLink.from_type == "design_input",
                TraceLink.from_id.in_(di_ids),
                TraceLink.to_type == "design_output",
            )
            .all()
        )

    do_ids: Set[str] = {tl.to_id for tl in di_to_do_links}
    design_outputs_by_id: Dict[str, Any] = {}
    if do_ids:
        from models.design_output import DesignOutput
        dos = db.query(DesignOutput).filter(DesignOutput.project_id == project_id, DesignOutput.id.in_(list(do_ids))).all()
        design_outputs_by_id = {d.id: d for d in dos}

    # do -> vv_test links
    do_to_vv_links: List[TraceLink] = []
    if do_ids:
        do_to_vv_links = (
            db.query(TraceLink)
            .filter(
                TraceLink.project_id == project_id,
                TraceLink.from_type == "design_output",
                TraceLink.from_id.in_(list(do_ids)),
                TraceLink.to_type == "vv_test",
            )
            .all()
        )

    vv_ids: Set[str] = {tl.to_id for tl in do_to_vv_links}
    # optional di -> vv_test direct links
    di_to_vv_links: List[TraceLink] = []
    if di_ids:
        di_to_vv_links = (
            db.query(TraceLink)
            .filter(
                TraceLink.project_id == project_id,
                TraceLink.from_type == "design_input",
                TraceLink.from_id.in_(di_ids),
                TraceLink.to_type == "vv_test",
            )
            .all()
        )
        vv_ids |= {tl.to_id for tl in di_to_vv_links}

    vv_by_id: Dict[str, Any] = {}
    if vv_ids:
        from models.vv_test import VVTest
        vvs = db.query(VVTest).filter(VVTest.project_id == project_id, VVTest.id.in_(list(vv_ids))).all()
        vv_by_id = {v.id: v for v in vvs}

    dos_by_di: Dict[str, List[Dict[str, Any]]] = {}
    for tl in di_to_do_links:
        di_id = tl.from_id
        d = design_outputs_by_id.get(tl.to_id)
        if not d:
            continue
        dos_by_di.setdefault(di_id, []).append(
            {
                "id": d.id,
                "do_key": getattr(d, "do_key", None) or f"DO-{d.id[:8]}",
                "title": getattr(d, "title", None) or "(untitled)",
            }
        )

    vvs_by_di: Dict[str, List[Dict[str, Any]]] = {}
    # via DOs
    for tl in do_to_vv_links:
        do_id = tl.from_id
        vv = vv_by_id.get(tl.to_id)
        if not vv:
            continue
        # find di(s) that link to this do
        for di_id, dos in dos_by_di.items():
            if any(x.get("id") == do_id for x in dos):
                vvs_by_di.setdefault(di_id, []).append(
                    {
                        "id": vv.id,
                        "vv_key": getattr(vv, "vv_key", None) or f"V-{vv.id[:8]}",
                        "title": getattr(vv, "name", None) or "V&V Test",
                    }
                )
    # direct DI->VV
    for tl in di_to_vv_links:
        vv = vv_by_id.get(tl.to_id)
        if not vv:
            continue
        vvs_by_di.setdefault(tl.from_id, []).append(
            {
                "id": vv.id,
                "vv_key": getattr(vv, "vv_key", None) or f"V-{vv.id[:8]}",
                "title": getattr(vv, "name", None) or "V&V Test",
            }
        )

    # De-dupe downstream lists
    def _dedupe(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        seen: Set[str] = set()
        out: List[Dict[str, Any]] = []
        for it in items:
            k = str(it.get(key) or "")
            if not k or k in seen:
                continue
            seen.add(k)
            out.append(it)
        return out

    rows: List[Dict[str, Any]] = []
    missing_upstream = 0
    missing_output_count = 0
    missing_verification_count = 0

    for di in design_inputs:
        upstream_controls = upstream_controls_by_di.get(di.id, [])
        if not upstream_controls:
            missing_upstream += 1

        # Lightweight component tag: derive from upstream risks' component_name if available
        component_name = None
        # first try linked risk ids field
        for rid in (di.linked_risk_ids or []):
            ri = risk_item_by_id.get(rid)
            if ri and (ri.component_name or ri.component_id):
                component_name = ri.component_name or component_name
                break

        downstream_dos = _dedupe(dos_by_di.get(di.id, []), "id")
        downstream_vvs = _dedupe(vvs_by_di.get(di.id, []), "id")

        has_upstream_control = len(upstream_controls) > 0
        has_output = len(downstream_dos) > 0
        has_verification = len(downstream_vvs) > 0

        if not has_output:
            missing_output_count += 1
        if not has_verification:
            missing_verification_count += 1

        requirement_text = di.requirement or di.text or ""

        # Apply search filter (server-side) if provided
        if search:
            s = search.lower().strip()
            blob = f"{di.di_key or ''} {di.title or ''} {requirement_text}".lower()
            if s not in blob:
                continue

        # Apply missing filters
        if missing_output is True and has_output:
            continue
        if missing_verification is True and has_verification:
            continue

        rows.append(
            {
                "di_id": di.id,
                "di_key": di.di_key or f"DI-{di.id[:8]}",
                "title": di.title or "(untitled)",
                "requirement_text": requirement_text,
                "status": di.status,
                "acceptance_criteria": None,
                "updated_at": di.updated_at.isoformat() if di.updated_at else None,
                "upstream": {
                    "risk_controls": upstream_controls,
                    "risks": upstream_risks_by_di.get(di.id, []),
                },
                "downstream": {
                    "design_outputs": downstream_dos,
                    "vv_tests": downstream_vvs,
                },
                "completeness": {
                    "has_upstream_control": has_upstream_control,
                    "has_output": has_output,
                    "has_verification": has_verification,
                },
            }
        )

    return {
        "project_id": project_id,
        "components": component_filter or [],
        "generated_at": None,  # renderer will stamp
        "rows": rows,
        "counts": {
            "design_inputs": len(rows),
            "missing_output": sum(1 for r in rows if not r["completeness"]["has_output"]),
            "missing_verification": sum(1 for r in rows if not r["completeness"]["has_verification"]),
            "missing_upstream_control": sum(1 for r in rows if not r["completeness"]["has_upstream_control"]),
        },
    }

