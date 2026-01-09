"""
Design Outputs Documentation evidence builder (implementation artifacts).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from sqlalchemy.orm import Session

from models.design_output import DesignOutput
from models.trace_link import TraceLink
from models.design_input import DesignInput
from models.vv_test import VVTest


def build_design_outputs_doc_evidence(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    MVP: list Design Outputs and their upstream DIs and downstream VV tests via trace_links.
    Component scoping is best-effort (DesignOutputs don't have component fields). If a component_filter
    is provided, we include outputs that have at least one upstream DI that is linked (directly/indirectly)
    to the component via risk-control chain in other reports; for now we do not filter aggressively.
    """

    outputs: List[DesignOutput] = db.query(DesignOutput).filter(DesignOutput.project_id == project_id).all()
    out_ids = [o.id for o in outputs]

    di_links: List[TraceLink] = []
    vv_links: List[TraceLink] = []
    if out_ids:
        di_links = db.query(TraceLink).filter(
            TraceLink.project_id == project_id,
            TraceLink.to_type == "design_output",
            TraceLink.to_id.in_(out_ids),
            TraceLink.from_type == "design_input",
        ).all()
        vv_links = db.query(TraceLink).filter(
            TraceLink.project_id == project_id,
            TraceLink.from_type == "design_output",
            TraceLink.from_id.in_(out_ids),
            TraceLink.to_type == "vv_test",
        ).all()

    di_ids: Set[str] = {l.from_id for l in di_links}
    vv_ids: Set[str] = {l.to_id for l in vv_links}

    dis = db.query(DesignInput).filter(DesignInput.project_id == project_id, DesignInput.id.in_(list(di_ids))).all() if di_ids else []
    vvs = db.query(VVTest).filter(VVTest.project_id == project_id, VVTest.id.in_(list(vv_ids))).all() if vv_ids else []
    di_by_id = {d.id: d for d in dis}
    vv_by_id = {v.id: v for v in vvs}

    upstream_dis_by_do: Dict[str, List[Dict[str, Any]]] = {}
    for l in di_links:
        di = di_by_id.get(l.from_id)
        if not di:
            continue
        upstream_dis_by_do.setdefault(l.to_id, []).append(
            {
                "id": di.id,
                "di_key": di.di_key or f"DI-{di.id[:8]}",
                "title": di.title or "(untitled)",
                "link_type": l.link_type or "implements",
            }
        )

    downstream_vv_by_do: Dict[str, List[Dict[str, Any]]] = {}
    for l in vv_links:
        vv = vv_by_id.get(l.to_id)
        if not vv:
            continue
        downstream_vv_by_do.setdefault(l.from_id, []).append(
            {
                "id": vv.id,
                "vv_key": vv.vv_key or f"V-{vv.id[:8]}",
                "title": vv.name or "V&V Test",
                "link_type": l.link_type or "verified_by",
            }
        )

    rows: List[Dict[str, Any]] = []
    missing_impl = 0
    missing_ver = 0
    for o in outputs:
        upstream_dis = upstream_dis_by_do.get(o.id, [])
        downstream_vv = downstream_vv_by_do.get(o.id, [])
        has_impl = len(upstream_dis) > 0
        has_ver = len(downstream_vv) > 0
        if not has_impl:
            missing_impl += 1
        if not has_ver:
            missing_ver += 1

        rows.append(
            {
                "do_id": o.id,
                "do_key": o.do_key or f"DO-{o.id[:8]}",
                "title": o.title or "(untitled)",
                "description": o.description or o.text or "",
                "status": o.status,
                "updated_at": o.updated_at.isoformat() if o.updated_at else None,
                "upstream": {"design_inputs": upstream_dis},
                "downstream": {"vv_tests": downstream_vv},
                "completeness": {"has_implementation_link": has_impl, "has_verification_link": has_ver},
            }
        )

    return {
        "project_id": project_id,
        "components": component_filter or [],
        "rows": rows,
        "counts": {
            "design_outputs": len(rows),
            "missing_implementation_link": missing_impl,
            "missing_verification_link": missing_ver,
        },
    }

