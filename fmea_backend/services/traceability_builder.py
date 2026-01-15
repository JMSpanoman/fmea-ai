from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from crud import component as component_crud
from crud import fmea as fmea_crud
from crud import risk_item as risk_item_crud
from crud import risk_control as risk_control_crud
from crud import document as document_crud


@dataclass
class TraceabilityStats:
    components_total: int = 0
    components_missing_fmea: int = 0
    risks_total: int = 0
    risks_missing_control: int = 0
    risks_missing_verification: int = 0
    design_inputs_total: int = 0
    design_inputs_missing_output: int = 0
    design_inputs_missing_verification: int = 0

    def as_dict(self) -> dict:
        return {
            "components_total": self.components_total,
            "components_missing_fmea": self.components_missing_fmea,
            "risks_total": self.risks_total,
            "risks_missing_control": self.risks_missing_control,
            "risks_missing_verification": self.risks_missing_verification,
            "design_inputs_total": self.design_inputs_total,
            "design_inputs_missing_output": self.design_inputs_missing_output,
            "design_inputs_missing_verification": self.design_inputs_missing_verification,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_doc_by_type(db: Session, project_id: str, doc_type: str) -> Any:
    return document_crud.get_document_by_type(db, project_id=project_id, doc_type=doc_type)


def _parse_design_inputs(doc_content: str) -> List[str]:
    """
    Extract DI ids from design_inputs_doc deterministic scaffold.
    """
    ids: List[str] = []
    # Supports keys like DI-01 or DI-LEADS-01 (component-scoped).
    for m in re.finditer(r"\bDI-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+\b|\bDI-\d+\b", (doc_content or ""), flags=re.IGNORECASE):
        ids.append(m.group(0))
    # deterministic unique order
    out: List[str] = []
    for x in ids:
        if x not in out:
            out.append(x)
    return out


def _parse_design_outputs(doc_content: str) -> Dict[str, List[str]]:
    """
    Extract mapping input_id -> [output_ids] from design_outputs_doc scaffold lines like:
      - DO-01 (maps to DI-01): ...
    """
    mapping: Dict[str, List[str]] = {}
    for line in (doc_content or "").splitlines():
        m = re.search(
            r"\b(DO-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)\b.*\bmaps to\b\s*\b(DI-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)\b",
            line,
            flags=re.IGNORECASE,
        )
        if not m:
            # fallback for simpler numeric ids
            m = re.search(r"\b(DO-\d+)\b.*\bmaps to\b\s*\b(DI-\d+)\b", line, flags=re.IGNORECASE)
        if not m:
            continue
        do_id = m.group(1)
        di_id = m.group(2)
        mapping.setdefault(di_id, [])
        if do_id not in mapping[di_id]:
            mapping[di_id].append(do_id)
    return mapping


def _parse_vv_plan(doc_content: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Returns (vv_by_di, vv_by_risk_control_id) using the deterministic vv_plan format we generate:
      - Source type: Design Input / Risk Control
      - Source reference: DI-xx ...
      - Source reference: ... (risk_control_id=UUID)
    """
    vv_by_di: Dict[str, List[str]] = {}
    vv_by_rc: Dict[str, List[str]] = {}

    cur_vv: Optional[str] = None
    cur_source_type: Optional[str] = None
    cur_source_ref: Optional[str] = None
    cur_rc_id: Optional[str] = None

    for line in (doc_content or "").splitlines():
        m = re.match(r"^\s*-\s*(VV-\d{3})\s*$", line.strip())
        if m:
            cur_vv = m.group(1)
            cur_source_type = None
            cur_source_ref = None
            cur_rc_id = None
            continue
        if cur_vv:
            if "Source type:" in line:
                cur_source_type = line.split("Source type:", 1)[1].strip()
            if "Source reference:" in line:
                cur_source_ref = line.split("Source reference:", 1)[1].strip()
                # If it contains a risk_control_id=... capture it.
                mrc = re.search(r"risk_control_id=([0-9a-fA-F\\-]{8,})", cur_source_ref)
                if mrc:
                    cur_rc_id = mrc.group(1)
                mdi = re.search(r"\b(DI-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)\b|\b(DI-\d+)\b", cur_source_ref, flags=re.IGNORECASE)
                if mdi:
                    di_id = mdi.group(1) or mdi.group(2) or ""
                    if di_id:
                        vv_by_di.setdefault(di_id, [])
                        if cur_vv not in vv_by_di[di_id]:
                            vv_by_di[di_id].append(cur_vv)
            # also accept explicit DI id on its own line
            if cur_source_type and cur_source_type.lower().startswith("design input"):
                mdi = re.search(r"\b(DI-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)\b|\b(DI-\d+)\b", line, flags=re.IGNORECASE)
                if mdi:
                    di_id = mdi.group(1) or mdi.group(2) or ""
                    if di_id:
                        vv_by_di.setdefault(di_id, [])
                        if cur_vv not in vv_by_di[di_id]:
                            vv_by_di[di_id].append(cur_vv)
            if cur_rc_id:
                vv_by_rc.setdefault(cur_rc_id, [])
                if cur_vv not in vv_by_rc[cur_rc_id]:
                    vv_by_rc[cur_rc_id].append(cur_vv)

    return vv_by_di, vv_by_rc


def build_traceability(db: Session, *, project_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Deterministic, audit-safe traceability view generator.
    - Never fabricates missing items; it only lists what exists and flags gaps.
    - Does not auto-fix or create missing links.
    Returns (content, stats).
    """
    stats = TraceabilityStats()

    components = component_crud.get_components_by_project(db, project_id)
    fmea_rows = fmea_crud.get_fmea_rows_by_project(db, project_id)

    # A) Component -> FMEA coverage
    fmea_count_by_component: Dict[str, int] = {}
    for r in fmea_rows:
        cid = str(getattr(r, "component_id", "") or "")
        if not cid:
            continue
        fmea_count_by_component[cid] = fmea_count_by_component.get(cid, 0) + 1

    stats.components_total = len(components)
    missing_fmea = []
    for c in components:
        cid = str(getattr(c, "id", "") or "")
        if fmea_count_by_component.get(cid, 0) <= 0:
            missing_fmea.append(c)
    stats.components_missing_fmea = len(missing_fmea)

    # B) Risk -> Control -> Verification (RiskItems + RiskControls + VV plan)
    risk_items = risk_item_crud.get_risk_items_by_project(db, project_id)
    controls = risk_control_crud.get_risk_controls_by_project(db, project_id) if hasattr(risk_control_crud, "get_risk_controls_by_project") else []
    controls_by_risk_item: Dict[str, List[Any]] = {}
    for rc in controls:
        controls_by_risk_item.setdefault(str(getattr(rc, "risk_item_id", "") or ""), []).append(rc)

    vv_plan_doc = _get_doc_by_type(db, project_id, "vv_plan")
    vv_by_di, vv_by_rc = _parse_vv_plan((vv_plan_doc.content if vv_plan_doc else "") or "")

    stats.risks_total = len(risk_items)
    for ri in risk_items:
        rid = str(getattr(ri, "id", "") or "")
        rcs = controls_by_risk_item.get(rid, [])
        if not rcs:
            stats.risks_missing_control += 1
            # no verification possible if no control
            stats.risks_missing_verification += 1
            continue
        # if controls exist, ensure at least one has planned verification (via vv_plan mapping OR trace_to_verification_test)
        has_ver = False
        for rc in rcs:
            rcid = str(getattr(rc, "id", "") or "")
            if rcid and vv_by_rc.get(rcid):
                has_ver = True
                break
            if str(getattr(rc, "trace_to_verification_test", "") or "").strip():
                has_ver = True
                break
        if not has_ver:
            stats.risks_missing_verification += 1

    # C) Input -> Output -> Verification (from documents)
    di_doc = _get_doc_by_type(db, project_id, "design_inputs_doc")
    do_doc = _get_doc_by_type(db, project_id, "design_outputs_doc")
    di_ids = _parse_design_inputs((di_doc.content if di_doc else "") or "")
    do_map = _parse_design_outputs((do_doc.content if do_doc else "") or "")

    stats.design_inputs_total = len(di_ids)
    for di_id in di_ids:
        if not do_map.get(di_id):
            stats.design_inputs_missing_output += 1
        if not vv_by_di.get(di_id):
            stats.design_inputs_missing_verification += 1

    # Build human-readable content (markdown-like plain text)
    lines: List[str] = []
    lines.append("Traceability Matrix — Draft")
    lines.append("")
    lines.append("SYSTEM-GENERATED TRACEABILITY SNAPSHOT (deterministic)")
    lines.append(f"Generated at (UTC): {_now()}")
    lines.append(f"Project ID: {project_id}")
    lines.append("")
    lines.append("Traceability Summary")
    lines.append(f"- Components: {stats.components_total} (GAP: {stats.components_missing_fmea} with no FMEA rows)")
    lines.append(f"- Risks (Risk Items): {stats.risks_total} (GAP: {stats.risks_missing_control} with no control; GAP: {stats.risks_missing_verification} with no verification planned)")
    lines.append(f"- Design Inputs: {stats.design_inputs_total} (GAP: {stats.design_inputs_missing_output} with no output; GAP: {stats.design_inputs_missing_verification} with no verification planned)")
    lines.append("")

    lines.append("A) Component → FMEA")
    lines.append("component_id | component_name | fmea_rows_count | GAP")
    lines.append("-" * 72)
    for c in sorted(components, key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or ""))):
        cid = str(getattr(c, "id", "") or "")
        name = str(getattr(c, "name", "") or "")
        cnt = fmea_count_by_component.get(cid, 0)
        gap = "GAP: No FMEA rows for component" if cnt <= 0 else ""
        lines.append(f"{cid} | {name} | {cnt} | {gap}")
    lines.append("")

    lines.append("B) Risk → Control → Verification (Risk Items)")
    lines.append("risk_item_id | risk_title | controls_count | has_verification | GAP")
    lines.append("-" * 72)
    for ri in sorted(risk_items, key=lambda r: (str(getattr(r, "title", "") or "").lower(), str(getattr(r, "id", "") or ""))):
        rid = str(getattr(ri, "id", "") or "")
        title = str(getattr(ri, "title", "") or "")[:60]
        rcs = controls_by_risk_item.get(rid, [])
        if not rcs:
            lines.append(f"{rid} | {title} | 0 | False | GAP: No control defined; GAP: No verification planned")
            continue
        has_ver = False
        for rc in rcs:
            rcid = str(getattr(rc, "id", "") or "")
            if rcid and vv_by_rc.get(rcid):
                has_ver = True
                break
            if str(getattr(rc, 'trace_to_verification_test', '') or '').strip():
                has_ver = True
                break
        gap = "" if has_ver else "GAP: No verification planned"
        lines.append(f"{rid} | {title} | {len(rcs)} | {has_ver} | {gap}")
    lines.append("")

    lines.append("C) Input → Output → Verification (Design Inputs)")
    lines.append("design_input_id | design_output_ids | vv_activity_ids | GAP")
    lines.append("-" * 72)
    for di_id in di_ids:
        outs = ",".join(do_map.get(di_id, []))
        vvs = ",".join(vv_by_di.get(di_id, []))
        gaps: List[str] = []
        if not outs:
            gaps.append("GAP: No output linked")
        if not vvs:
            gaps.append("GAP: No verification planned")
        lines.append(f"{di_id} | {outs} | {vvs} | {'; '.join(gaps)}")
    if not di_ids:
        lines.append("(No Design Inputs found yet.)")
    lines.append("")

    lines.append("Notes")
    lines.append("- GAP indicators never auto-fix. They highlight missing links that require human action.")
    lines.append("- This snapshot is intended for audit-friendly review; it does not imply completion or compliance.")
    lines.append("")

    return "\n".join(lines), stats.as_dict()

