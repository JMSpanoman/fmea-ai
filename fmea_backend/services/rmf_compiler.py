from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session

from crud import document as document_crud


def _doc_link(project_id: str, doc_id: str) -> str:
    # Frontend route (ProjectDocumentPage)
    return f"/projects/{project_id}/documents/{doc_id}"


def _doc_preview_link(project_id: str, doc_id: str) -> str:
    # Backend HTML export endpoint (opens in browser)
    return f"/projects/{project_id}/documents/{doc_id}/export/html"


def _status_label(status: Optional[str]) -> str:
    s = (status or "").strip().lower()
    if s in {"not started", "not_started", "not-started"}:
        return "Not started"
    if s in {"draft"}:
        return "Draft"
    if s in {"in_review", "in review"}:
        return "In review"
    if s in {"approved"}:
        return "Approved"
    if not s:
        return "Unknown"
    return status or "Unknown"


def _pick_doc(by_type: Dict[str, any], *types: str):
    for t in types:
        d = by_type.get(t)
        if d:
            return d
    return None


def compile_rmf(db: Session, *, project_id: str, project_name: str) -> Tuple[str, bool]:
    """
    Compile an RMF/RMR as an evidence-based compilation document.

    Rules:
    - Deterministic, non-AI.
    - Does not invent risk content: only references authoritative documents and their metadata.
    - Returns (rendered_html, ready) where ready indicates whether prerequisites were met.
    """
    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}

    rmp = _pick_doc(by_type, "rmp")
    hazard = _pick_doc(by_type, "hazard_analysis")
    fmea = _pick_doc(by_type, "fmea")
    risk_controls = _pick_doc(by_type, "risk_controls_doc")
    residual = _pick_doc(by_type, "residual_risk")
    review = _pick_doc(by_type, "risk_management_review", "rmr", "risk_management_report")

    missing = []
    if not rmp:
        missing.append("Risk Management Plan (RMP)")
    if not hazard:
        missing.append("Hazard Analysis")

    ready = len(missing) == 0
    generated_at = datetime.now(timezone.utc).isoformat()

    def section(title: str, doc_obj: Optional[any], brief: str) -> str:
        if not doc_obj:
            return f"""
              <div class="sec">
                <h2>{title}</h2>
                <div class="meta"><span class="pill s-not">Not started</span> <span class="muted">No authoritative document found.</span></div>
                <div class="body">{brief}</div>
              </div>
            """
        st = _status_label(getattr(doc_obj, "status", None))
        ver = getattr(doc_obj, "version", None) or 1
        doc_id = getattr(doc_obj, "id", "")
        link = _doc_link(project_id, doc_id)
        preview = _doc_preview_link(project_id, doc_id)
        pill_class = "s-draft"
        if st.lower().startswith("approved"):
            pill_class = "s-ok"
        elif st.lower().startswith("in review"):
            pill_class = "s-review"
        elif st.lower().startswith("not"):
            pill_class = "s-not"
        return f"""
          <div class="sec">
            <h2>{title}</h2>
            <div class="meta">
              <span class="pill {pill_class}">{st}</span>
              <span class="muted">v{ver}</span>
              <a class="link" href="{link}">Open</a>
              <a class="link" href="{preview}" target="_blank" rel="noreferrer">Preview</a>
            </div>
            <div class="body">{brief}</div>
          </div>
        """

    not_ready_banner = ""
    if not ready:
        missing_html = "".join([f"<li>{m}</li>" for m in missing])
        not_ready_banner = f"""
          <div class="banner warn">
            <b>RMF not ready to compile.</b>
            <div class="muted">Missing prerequisites:</div>
            <ul>{missing_html}</ul>
          </div>
        """

    html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>Risk Management File (RMF/RMR) — {project_name}</title>
    <style>
      body {{ font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif; margin: 28px; color: #111827; }}
      h1 {{ margin: 0 0 6px 0; }}
      .muted {{ color: #6b7280; }}
      .banner {{ border-radius: 10px; padding: 12px 14px; margin: 14px 0 18px 0; border: 1px solid #e5e7eb; background: #f9fafb; }}
      .banner.warn {{ border-color: #fbbf24; background: #fffbeb; color: #92400e; }}
      .banner.note {{ border-color: #c7d2fe; background: #eef2ff; color: #3730a3; }}
      .sec {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; margin: 12px 0; background: #fff; }}
      .meta {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top: 6px; }}
      .pill {{ display:inline-flex; align-items:center; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
      .s-ok {{ background:#dcfce7; color:#166534; }}
      .s-draft {{ background:#e0f2fe; color:#075985; }}
      .s-review {{ background:#fef9c3; color:#854d0e; }}
      .s-not {{ background:#f3f4f6; color:#374151; }}
      .link {{ font-size: 12px; color: #2563eb; text-decoration: none; }}
      .link:hover {{ text-decoration: underline; }}
      .body {{ margin-top: 10px; line-height: 1.55; }}
      ul {{ margin: 6px 0 0 18px; }}
      .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
      @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
      .k {{ font-weight: 700; }}
    </style>
  </head>
  <body>
    <h1>Risk Management File (RMF/RMR)</h1>
    <div class="muted">Project: <span class="k">{project_name}</span> &nbsp;|&nbsp; Project ID: <span class="k">{project_id}</span></div>
    <div class="muted">Compiled: {generated_at}</div>

    <div class="banner note">
      <b>Compiled document (read-only intent).</b>
      <div>This RMF is compiled from authoritative project documents. It does not invent risk content.</div>
    </div>

    {not_ready_banner}

    <div class="grid">
      {section('Scope (RMP Reference)', rmp, 'See the Risk Management Plan (RMP) document for scope, roles, and acceptability criteria.')}
      {section('Hazard Identification (Hazard Analysis Reference)', hazard, 'See the Hazard Analysis document for hazards, hazardous situations, and harms.')}
      {section('Risk Analysis (FMEA Reference)', fmea, 'See the FMEA document for failure modes, effects/causes, and risk analysis details.')}
      {section('Risk Controls (Risk Control Measures Reference)', risk_controls, 'See the Risk Control Measures Documentation for controls, trace links, and verification method placeholders.')}
      {section('Residual Risk (Residual Risk Evaluation Reference)', residual, 'See the Residual Risk Evaluation document for residual risk summaries and acceptability placeholders.')}
      {section('Review Status (Risk Management Review Reference)', review, 'See the Risk Management Review record for formal review disposition and approvals (if available).')}
    </div>
  </body>
</html>"""

    return html, ready

