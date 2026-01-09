"""
V&V Evidence Report (component-scoped) evidence builder.

Key principle: Only claim evidence that exists via trace_links. If a vv_test has a foreign-key
to a design_output but no trace link design_output → vv_test, we treat that as a missing link.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.component import Component
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from models.risk_control import RiskControl
from models.trace_link import TraceLink
from models.design_input import DesignInput
from models.design_output import DesignOutput
from models.vv_test import VVTest


def _component_filter_to_names_and_ids(component_filter: Optional[List[Dict[str, Any]]]) -> tuple[list[str], list[str]]:
    ids: list[str] = []
    names: list[str] = []
    for c in component_filter or []:
        if c.get("id"):
            ids.append(str(c["id"]))
        if c.get("name"):
            names.append(str(c["name"]))
    return names, ids


def build_vv_evidence_report_evidence(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
    test_type: Optional[str] = None,  # verification|validation (best-effort for now)
    status: Optional[str] = None,
    unlinked_only: Optional[bool] = None,
    missing_acceptance_criteria: Optional[bool] = None,
    missing_design_output_link: Optional[bool] = None,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    comp_names, comp_ids = _component_filter_to_names_and_ids(component_filter)

    # Resolve component names by IDs if provided
    if comp_ids and not comp_names:
        comps = db.query(Component).filter(Component.project_id == project_id, Component.id.in_(comp_ids)).all()
        comp_names = [c.name for c in comps if c.name]

    # Scope risk items by components
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

    # Controls under scoped risks
    risk_item_ids = list(risk_item_by_id.keys())
    controls: List[RiskControl] = []
    if risk_item_ids:
        controls = db.query(RiskControl).filter(RiskControl.risk_item_id.in_(risk_item_ids)).all()
    control_by_id = {c.id: c for c in controls}
    control_ids = list(control_by_id.keys())

    # DI linked from controls
    rc_to_di_links: List[TraceLink] = []
    if control_ids:
        rc_to_di_links = db.query(TraceLink).filter(
            TraceLink.project_id == project_id,
            TraceLink.from_type == "risk_control",
            TraceLink.from_id.in_(control_ids),
            TraceLink.to_type == "design_input",
        ).all()
    di_ids_from_controls: Set[str] = {l.to_id for l in rc_to_di_links}

    # DO linked from DI
    di_to_do_links: List[TraceLink] = []
    if di_ids_from_controls:
        di_to_do_links = db.query(TraceLink).filter(
            TraceLink.project_id == project_id,
            TraceLink.from_type == "design_input",
            TraceLink.from_id.in_(list(di_ids_from_controls)),
            TraceLink.to_type == "design_output",
        ).all()
    do_ids_from_inputs: Set[str] = {l.to_id for l in di_to_do_links}

    # VV tests linked from DO (preferred)
    do_to_vv_links: List[TraceLink] = []
    if do_ids_from_inputs:
        do_to_vv_links = db.query(TraceLink).filter(
            TraceLink.project_id == project_id,
            TraceLink.from_type == "design_output",
            TraceLink.from_id.in_(list(do_ids_from_inputs)),
            TraceLink.to_type == "vv_test",
        ).all()
    vv_ids_preferred: Set[str] = {l.to_id for l in do_to_vv_links}

    # Allowed: DI -> VV
    di_to_vv_links: List[TraceLink] = []
    if di_ids_from_controls:
        di_to_vv_links = db.query(TraceLink).filter(
            TraceLink.project_id == project_id,
            TraceLink.from_type == "design_input",
            TraceLink.from_id.in_(list(di_ids_from_controls)),
            TraceLink.to_type == "vv_test",
        ).all()
    vv_ids_allowed: Set[str] = {l.to_id for l in di_to_vv_links}

    # Shortcut: RC -> VV
    rc_to_vv_links: List[TraceLink] = []
    if control_ids:
        rc_to_vv_links = db.query(TraceLink).filter(
            TraceLink.project_id == project_id,
            TraceLink.from_type == "risk_control",
            TraceLink.from_id.in_(control_ids),
            TraceLink.to_type == "vv_test",
        ).all()
    vv_ids_shortcut: Set[str] = {l.to_id for l in rc_to_vv_links}

    vv_ids = vv_ids_preferred | vv_ids_allowed | vv_ids_shortcut

    # Load vv_tests
    vv_query = db.query(VVTest).filter(VVTest.project_id == project_id)
    if vv_ids:
        vv_query = vv_query.filter(VVTest.id.in_(list(vv_ids)))
    else:
        # No chain evidence found for these components
        vv_query = vv_query.filter(VVTest.id == "__none__")
    if status:
        vv_query = vv_query.filter(VVTest.status == status)
    vv_tests = vv_query.all()
    vv_by_id = {v.id: v for v in vv_tests}

    # Load DI/DO for display
    di_by_id: Dict[str, DesignInput] = {}
    if di_ids_from_controls:
        dis = db.query(DesignInput).filter(DesignInput.project_id == project_id, DesignInput.id.in_(list(di_ids_from_controls))).all()
        di_by_id = {d.id: d for d in dis}
    do_by_id: Dict[str, DesignOutput] = {}
    if do_ids_from_inputs:
        dos = db.query(DesignOutput).filter(DesignOutput.project_id == project_id, DesignOutput.id.in_(list(do_ids_from_inputs))).all()
        do_by_id = {d.id: d for d in dos}

    # Current risk versions for hazard/harm
    current_version_ids: Set[str] = set()
    for ri in risk_items:
        if getattr(ri, "current_version_id", None):
            current_version_ids.add(ri.current_version_id)
    versions_by_id: Dict[str, RiskItemVersion] = {}
    if current_version_ids:
        vs = db.query(RiskItemVersion).filter(RiskItemVersion.id.in_(list(current_version_ids))).all()
        versions_by_id = {v.id: v for v in vs}

    # Build reverse mappings to compile upstream lists per vv_test
    dos_by_vv: Dict[str, List[str]] = {}
    for l in do_to_vv_links:
        if l.to_id in vv_by_id:
            dos_by_vv.setdefault(l.to_id, []).append(l.from_id)

    dis_by_vv_direct: Dict[str, List[str]] = {}
    for l in di_to_vv_links:
        if l.to_id in vv_by_id:
            dis_by_vv_direct.setdefault(l.to_id, []).append(l.from_id)

    rcs_by_vv_direct: Dict[str, List[str]] = {}
    for l in rc_to_vv_links:
        if l.to_id in vv_by_id:
            rcs_by_vv_direct.setdefault(l.to_id, []).append(l.from_id)

    # Build helper maps: DO -> DI, DI -> RC
    dis_by_do: Dict[str, List[str]] = {}
    for l in di_to_do_links:
        dis_by_do.setdefault(l.to_id, []).append(l.from_id)

    rcs_by_di: Dict[str, List[str]] = {}
    for l in rc_to_di_links:
        rcs_by_di.setdefault(l.to_id, []).append(l.from_id)

    rows: List[Dict[str, Any]] = []

    counts = {
        "tests": 0,
        "unlinked": 0,
        "missing_design_output_link": 0,
        "missing_acceptance_criteria": 0,
        "strength_preferred": 0,
        "strength_allowed": 0,
        "strength_shortcut": 0,
    }

    for vv_id, vv in vv_by_id.items():
        # Determine evidence strength based on trace_links present
        has_do_link = len(dos_by_vv.get(vv_id, [])) > 0
        has_di_link = len(dis_by_vv_direct.get(vv_id, [])) > 0
        has_rc_link = len(rcs_by_vv_direct.get(vv_id, [])) > 0

        if has_do_link:
            evidence_strength = "preferred"
            counts["strength_preferred"] += 1
        elif has_di_link:
            evidence_strength = "allowed"
            counts["strength_allowed"] += 1
        elif has_rc_link:
            evidence_strength = "shortcut"
            counts["strength_shortcut"] += 1
        else:
            evidence_strength = "shortcut"
            counts["strength_shortcut"] += 1

        # Upstream DOs
        do_ids = list(dict.fromkeys(dos_by_vv.get(vv_id, [])))
        do_list = []
        for did in do_ids:
            d = do_by_id.get(did)
            if d:
                do_list.append({"id": d.id, "do_key": d.do_key or f"DO-{d.id[:8]}", "title": d.title or "(untitled)"})

        # Upstream DIs (from DOs and direct links)
        di_ids: List[str] = []
        for did in do_ids:
            di_ids.extend(dis_by_do.get(did, []))
        di_ids.extend(dis_by_vv_direct.get(vv_id, []))
        di_ids = list(dict.fromkeys(di_ids))
        di_list = []
        for diid in di_ids:
            di = di_by_id.get(diid)
            if di:
                di_list.append({"id": di.id, "di_key": di.di_key or f"DI-{di.id[:8]}", "title": di.title or "(untitled)"})

        # Upstream RCs (from DIs and direct links)
        rc_ids: List[str] = []
        for diid in di_ids:
            rc_ids.extend(rcs_by_di.get(diid, []))
        rc_ids.extend(rcs_by_vv_direct.get(vv_id, []))
        rc_ids = list(dict.fromkeys(rc_ids))
        rc_list = []
        for rcid in rc_ids:
            rc = control_by_id.get(rcid)
            if rc:
                rc_list.append({"id": rc.id, "control_key": rc.control_key or f"RC-{rc.id[:8]}", "name": rc.control_name})

        # Upstream risk items (via controls)
        risk_list = []
        for rcid in rc_ids:
            rc = control_by_id.get(rcid)
            if not rc:
                continue
            ri = risk_item_by_id.get(rc.risk_item_id)
            if not ri:
                continue
            v = versions_by_id.get(getattr(ri, "current_version_id", "") or "")
            risk_list.append(
                {
                    "id": ri.id,
                    "risk_key": ri.risk_key or f"R-{ri.id[:8]}",
                    "hazard": getattr(v, "hazard", None) if v else None,
                    "harm": getattr(v, "harm", None) if v else None,
                }
            )

        risk_list = list({r["id"]: r for r in risk_list}.values())

        has_upstream_links = bool(do_list or di_list or rc_list or risk_list)
        has_acceptance = bool((vv.acceptance_criteria or "").strip())

        # Best-effort mapping to spec fields
        vv_key = vv.vv_key or f"V-{vv.id[:8]}"
        title = vv.name or "V&V Test"
        method = "test"  # MVP: infer later from test_method
        inferred_test_type = "verification"
        if test_type and inferred_test_type != test_type:
            continue

        # Filters
        if unlinked_only is True and has_upstream_links:
            continue
        if missing_acceptance_criteria is True and has_acceptance:
            continue
        if missing_design_output_link is True and has_do_link:
            continue
        if search:
            s = search.lower().strip()
            blob = f"{vv_key} {title} {vv.test_method or ''} {vv.acceptance_criteria or ''}".lower()
            if s not in blob:
                continue

        counts["tests"] += 1
        if not has_upstream_links:
            counts["unlinked"] += 1
        if not has_do_link:
            counts["missing_design_output_link"] += 1
        if not has_acceptance:
            counts["missing_acceptance_criteria"] += 1

        rows.append(
            {
                "vv_test_id": vv.id,
                "vv_key": vv_key,
                "title": title,
                "test_type": inferred_test_type,
                "method": method,
                "acceptance_criteria": vv.acceptance_criteria,
                "status": vv.status,
                "updated_at": vv.updated_at.isoformat() if vv.updated_at else None,
                "upstream": {
                    "design_outputs": do_list,
                    "design_inputs": di_list,
                    "risk_controls": rc_list,
                    "risk_items": risk_list,
                },
                "evidence_strength": evidence_strength,
                "completeness": {
                    "has_design_output_link": has_do_link,
                    "has_acceptance_criteria": has_acceptance,
                    "has_upstream_links": has_upstream_links,
                },
            }
        )

    return {
        "project_id": project_id,
        "components": component_filter or [],
        "generated_at": None,
        "rows": rows,
        "counts": {
            "tests": counts["tests"],
            "unlinked": counts["unlinked"],
            "missing_design_output_link": counts["missing_design_output_link"],
            "missing_acceptance_criteria": counts["missing_acceptance_criteria"],
            "strength": {
                "preferred": counts["strength_preferred"],
                "allowed": counts["strength_allowed"],
                "shortcut": counts["strength_shortcut"],
            },
        },
    }

