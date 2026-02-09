"""
Business Logic for Traceability Matrix Evidence Builder
Builds a project-scoped traceability view from trace_links + linked artifacts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from models.component import Component
from models.fmea import FMEARow
from models.trace_link import TraceLink


def _resolve_display(db: Session, artifact_type: str, artifact_id: str) -> str:
    """
    Resolve an artifact into a stable display string for the traceability matrix.
    Falls back to `<type> (<id8>)` if unknown/missing.
    """
    t = (artifact_type or "").lower()
    try:
        if t == "component":
            c = db.query(Component).filter(Component.id == artifact_id).first()
            if c:
                name = getattr(c, "name", None) or f"Component {c.id[:8]}"
                return f"C-{c.id[:8]} – {name}"

        if t == "risk_item":
            from models.risk_item import RiskItem
            ri = db.query(RiskItem).filter(RiskItem.id == artifact_id).first()
            if ri:
                key = ri.risk_key or f"R-{ri.id[:8]}"
                title = getattr(ri, "title", None) or ""
                comp = ri.component_name or ""
                bits = [key]
                if title:
                    bits.append(title)
                if comp:
                    bits.append(f"[{comp}]")
                return " – ".join(bits).replace(" – [", " [")

        if t == "fmea_row":
            r = db.query(FMEARow).filter(FMEARow.id == artifact_id).first()
            if r:
                fm = (getattr(r, "failure_mode", None) or "").strip() or "FMEA row"
                comp = ""
                try:
                    comp = str(getattr(getattr(r, "component", None), "name", "") or "").strip()
                except Exception:
                    comp = ""
                if not comp:
                    comp = "Unknown component"
                return f"FMEA-{r.id[:8]} – {fm} [{comp}]"

        if t == "risk_control":
            from models.risk_control import RiskControl
            rc = db.query(RiskControl).filter(RiskControl.id == artifact_id).first()
            if rc:
                key = rc.control_key or f"RC-{rc.id[:8]}"
                name = rc.control_name or "Risk Control"
                return f"{key} – {name}"

        if t == "design_input":
            from models.design_input import DesignInput
            di = db.query(DesignInput).filter(DesignInput.id == artifact_id).first()
            if di:
                key = di.di_key or f"DI-{di.id[:8]}"
                title = di.title or di.requirement or di.text or "Design Input"
                return f"{key} – {title}"

        if t == "design_output":
            from models.design_output import DesignOutput
            do = db.query(DesignOutput).filter(DesignOutput.id == artifact_id).first()
            if do:
                key = do.do_key or f"DO-{do.id[:8]}"
                title = do.title or do.description or do.text or "Design Output"
                return f"{key} – {title}"

        if t == "vv_test":
            from models.vv_test import VVTest
            vv = db.query(VVTest).filter(VVTest.id == artifact_id).first()
            if vv:
                key = vv.vv_key or f"V-{vv.id[:8]}"
                name = vv.name or "V&V Test"
                return f"{key} – {name}"

        if t == "capa":
            from models.capa import CAPA
            c = db.query(CAPA).filter(CAPA.id == artifact_id).first()
            if c:
                title = getattr(c, "title", None) or getattr(c, "root_cause", None) or "CAPA"
                return f"CAPA-{c.id[:8]} – {title}"
    except Exception:
        # Keep evidence builder robust; renderer should still work with fallbacks.
        pass

    return f"{t or 'artifact'} ({artifact_id[:8]})"


def _infer_component_name_for_link(
    db: Session,
    *,
    from_type: str,
    from_id: str,
    to_type: str,
    to_id: str,
) -> str:
    """
    Best-effort component inference for a trace link row.
    """
    ft = (from_type or "").lower()
    tt = (to_type or "").lower()
    try:
        if ft == "component":
            c = db.query(Component).filter(Component.id == from_id).first()
            return (getattr(c, "name", None) or "").strip() if c else ""
        if tt == "component":
            c = db.query(Component).filter(Component.id == to_id).first()
            return (getattr(c, "name", None) or "").strip() if c else ""
    except Exception:
        pass

    try:
        if ft == "risk_item":
            from models.risk_item import RiskItem
            ri = db.query(RiskItem).filter(RiskItem.id == from_id).first()
            return (getattr(ri, "component_name", None) or "").strip() if ri else ""
        if tt == "risk_item":
            from models.risk_item import RiskItem
            ri = db.query(RiskItem).filter(RiskItem.id == to_id).first()
            return (getattr(ri, "component_name", None) or "").strip() if ri else ""
    except Exception:
        pass

    try:
        if ft == "fmea_row":
            r = db.query(FMEARow).filter(FMEARow.id == from_id).first()
            if r and getattr(r, "component_id", None):
                c = db.query(Component).filter(Component.id == str(r.component_id)).first()
                return (getattr(c, "name", None) or "").strip() if c else ""
        if tt == "fmea_row":
            r = db.query(FMEARow).filter(FMEARow.id == to_id).first()
            if r and getattr(r, "component_id", None):
                c = db.query(Component).filter(Component.id == str(r.component_id)).first()
                return (getattr(c, "name", None) or "").strip() if c else ""
    except Exception:
        pass

    return ""


def build_traceability_matrix_evidence(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Build traceability matrix evidence. If a component_filter is provided, we attempt
    to scope to related risk_items/risk_controls, but fall back to all links if none match.
    """

    # Always include component info by default (wizard components live in `components` table).
    if component_filter:
        comps = [{"id": str(c.get("id") or ""), "name": str(c.get("name") or "").strip()} for c in component_filter if str(c.get("name") or "").strip()]
    else:
        comps = [{"id": str(c.id), "name": str(c.name or "").strip(), "description": str(c.description or "")} for c in db.query(Component).filter(Component.project_id == project_id).order_by(Component.created_at.asc(), Component.id.asc()).all()]

    component_name_by_id = {str(c.get("id") or ""): str(c.get("name") or "") for c in comps if c.get("id")}

    q = db.query(TraceLink).filter(TraceLink.project_id == project_id)
    links = q.order_by(TraceLink.created_at.desc()).all()

    rows: List[Dict[str, Any]] = []
    counts = {
        "links": 0,
        "auto_links": 0,
        "by_link_type": {},
        "by_from_type": {},
        "by_to_type": {},
    }

    # Auto rows: always show Component -> FMEA row coverage (derived from persisted rows).
    fmea_rows = (
        db.query(FMEARow)
        .filter(FMEARow.project_id == project_id)
        .order_by(FMEARow.created_at.asc(), FMEARow.id.asc())
        .all()
    )
    fmea_count_by_component: Dict[str, int] = {}
    for idx, r in enumerate(fmea_rows):
        comp_id = str(getattr(r, "component_id", None) or "")
        comp_name = component_name_by_id.get(comp_id, "") if comp_id else ""
        if not comp_name:
            try:
                comp_name = str(getattr(getattr(r, "component", None), "name", "") or "").strip()
            except Exception:
                comp_name = ""
        if not comp_name:
            comp_name = "Unknown component"

        fmea_count_by_component[comp_name] = fmea_count_by_component.get(comp_name, 0) + 1

        fm = (getattr(r, "failure_mode", None) or "").strip() or "—"
        hazard = ""
        try:
            md = getattr(r, "ai_metadata", None)
            if isinstance(md, dict):
                hazard = str(md.get("hazard") or "").strip()
        except Exception:
            hazard = ""

        to_disp = f"FMEA-{str(idx + 1).zfill(2)} – {fm}"
        if hazard:
            to_disp += f" (hazard: {hazard})"

        rows.append(
            {
                "id": f"auto:fmea:{getattr(r, 'id', '')}",
                "row_source": "auto_fmea",
                "component_name": comp_name,
                "from_type": "component",
                "from_id": comp_id or "",
                "from_display": comp_name,
                "to_type": "fmea_row",
                "to_id": str(getattr(r, "id", "") or ""),
                "to_display": to_disp,
                "link_type": "has_fmea_row",
                "rationale": (
                    "Auto-derived: this FMEA row is associated to the component via FMEA.component_id "
                    "(wizard component list + persisted FMEA rows)."
                ),
                "created_at": r.created_at.isoformat() if getattr(r, "created_at", None) else None,
            }
        )
        counts["links"] += 1
        counts["auto_links"] += 1
        counts["by_link_type"]["has_fmea_row"] = counts["by_link_type"].get("has_fmea_row", 0) + 1
        counts["by_from_type"]["component"] = counts["by_from_type"].get("component", 0) + 1
        counts["by_to_type"]["fmea_row"] = counts["by_to_type"].get("fmea_row", 0) + 1

    for l in links:
        from_type = (l.from_type or "").lower()
        to_type = (l.to_type or "").lower()
        link_type = (l.link_type or "traces_to").lower()

        from_display = _resolve_display(db, from_type, l.from_id)
        to_display = _resolve_display(db, to_type, l.to_id)
        component_name = _infer_component_name_for_link(
            db, from_type=from_type, from_id=l.from_id, to_type=to_type, to_id=l.to_id
        )

        rationale = l.rationale
        if not (rationale or "").strip():
            rationale = "No rationale provided in trace link record."

        rows.append(
            {
                "id": l.id,
                "row_source": "trace_link",
                "component_name": component_name,
                "from_type": from_type,
                "from_id": l.from_id,
                "from_display": from_display,
                "to_type": to_type,
                "to_id": l.to_id,
                "to_display": to_display,
                "link_type": link_type,
                "rationale": rationale,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
        )

        counts["links"] += 1
        counts["by_link_type"][link_type] = counts["by_link_type"].get(link_type, 0) + 1
        counts["by_from_type"][from_type] = counts["by_from_type"].get(from_type, 0) + 1
        counts["by_to_type"][to_type] = counts["by_to_type"].get(to_type, 0) + 1

    return {
        "project_id": project_id,
        "components": comps,
        "component_summary": {
            "component_count": len(comps),
            "fmea_rows_total": len(fmea_rows),
            "fmea_rows_by_component": fmea_count_by_component,
        },
        "rows": rows,
        "counts": counts,
    }

