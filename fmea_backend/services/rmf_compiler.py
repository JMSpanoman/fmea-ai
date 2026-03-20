from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, Optional, Tuple

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


def _pick_doc(by_type: Dict[str, Any], *types: str):
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
    generated_at = datetime.now(timezone.utc)
    generated_iso = generated_at.isoformat()
    generated_display = generated_at.strftime("%Y-%m-%d %H:%M UTC")

    pn = escape(project_name or "")
    pid = escape(project_id or "")

    def section(
        *,
        slug: str,
        title: str,
        iso_ref: str,
        doc_obj: Optional[Any],
        brief: str,
        placeholder: str,
    ) -> str:
        """One authoritative reference block: version, status, links, brief + neutral placeholder."""
        if not doc_obj:
            return f"""
              <section class="ref-block" aria-labelledby="ref-{slug}">
                <div class="ref-head">
                  <h3 id="ref-{slug}">{title}</h3>
                  <span class="iso-tag">{escape(iso_ref)}</span>
                </div>
                <div class="meta"><span class="pill s-not">Not started</span> <span class="muted">No authoritative document found in this project.</span></div>
                <p class="body">{brief}</p>
                <p class="placeholder">{placeholder}</p>
              </section>
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
              <section class="ref-block" aria-labelledby="ref-{slug}">
                <div class="ref-head">
                  <h3 id="ref-{slug}">{title}</h3>
                  <span class="iso-tag">{escape(iso_ref)}</span>
                </div>
                <div class="meta">
                  <span class="pill {pill_class}">{escape(st)}</span>
                  <span class="ver">Version <strong>{ver}</strong></span>
                  <a class="link" href="{link}">Open in workspace</a>
                  <a class="link" href="{preview}" target="_blank" rel="noreferrer">Preview (HTML export)</a>
                </div>
                <p class="body">{brief}</p>
                <p class="placeholder">{placeholder}</p>
              </section>
            """

    not_ready_banner = ""
    if not ready:
        missing_html = "".join([f"<li>{escape(m)}</li>" for m in missing])
        not_ready_banner = f"""
          <div class="banner warn" role="status">
            <strong>RMF compilation incomplete.</strong>
            <p class="muted tight">The following prerequisite authoritative documents are not yet present in the project document register. Complete them before treating this compilation as a controlled RMF index.</p>
            <ul>{missing_html}</ul>
          </div>
        """

    # --- Reference sections (order and mapping preserved; titles clarify source document) ---
    scope_block = section(
        slug="rmp",
        title="Scope — Risk Management Plan (RMP)",
        iso_ref="RMP",
        doc_obj=rmp,
        brief="The Risk Management Plan defines scope, roles, responsibilities, and the risk management process for this device (including an implantable pacemaker project context where applicable).",
        placeholder="See the referenced Risk Management Plan for the approved scope statement, process description, and criteria. This RMF does not restate that content.",
    )
    hazard_block = section(
        slug="hazard-analysis",
        title="Hazard identification — Hazard Analysis",
        iso_ref="Hazard Analysis",
        doc_obj=hazard,
        brief="Systematic hazard identification and hazardous-situation analysis are recorded in the Hazard Analysis document.",
        placeholder="See the referenced Hazard Analysis for hazards, hazardous situations, harms, and sequences of events. Detailed evidence is not duplicated here.",
    )
    fmea_block = section(
        slug="fmea",
        title="Risk analysis — FMEA",
        iso_ref="FMEA",
        doc_obj=fmea,
        brief="Failure modes, effects, causes, and risk analyses are maintained in the FMEA (failure mode and effects analysis) record. ",
        placeholder="See the referenced FMEA for line-item risk analysis. This RMF provides index and traceability only.",
    )
    controls_block = section(
        slug="risk-controls-doc",
        title="Risk controls — Risk Control Measures Documentation",
        iso_ref="Risk control measures",
        doc_obj=risk_controls,
        brief="Risk control measures, implementation rationale, and traceability to hazards/risks are documented under Risk Control Measures Documentation.",
        placeholder="See the referenced Risk Control Measures Documentation for control descriptions, verification methods, and trace links. The risk control implementation summary (section 3 above) provides a high-level pointer only.",
    )
    residual_block = section(
        slug="residual-risk-eval",
        title="Residual risk — Residual Risk Evaluation",
        iso_ref="Residual risk evaluation",
        doc_obj=residual,
        brief="Residual risk estimation, evaluation, and acceptability conclusions are documented in the Residual Risk Evaluation.",
        placeholder="See the Residual Risk Evaluation document for residual risk summaries and acceptability conclusions. This RMF does not state conclusions not present in that source.",
    )
    review_block = section(
        slug="rm-review",
        title="Review status — Risk Management Review",
        iso_ref="Risk Management Review",
        doc_obj=review,
        brief="Formal review of the risk management activities and outcomes is recorded in the Risk Management Review (or equivalent RMR record).",
        placeholder="See the Risk Management Review record for formal review disposition and approvals. This compilation does not substitute for that record.",
    )

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>Risk Management File (RMF) / Risk Management Report (RMR) — {pn}</title>
    <style>
      :root {{
        --ink: #0f172a;
        --muted: #64748b;
        --border: #e2e8f0;
        --card: #ffffff;
        --soft: #f8fafc;
        --accent: #1e40af;
        --accent-soft: #eff6ff;
        --ok: #166534;
        --ok-bg: #dcfce7;
        --warn-bg: #fffbeb;
        --warn-border: #fbbf24;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Roboto, Arial, sans-serif;
        margin: 0;
        color: var(--ink);
        background: var(--soft);
        line-height: 1.55;
        font-size: 15px;
      }}
      .wrap {{ max-width: 920px; margin: 0 auto; padding: 32px 24px 48px; }}
      .doc-title {{
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0 0 8px 0;
        color: var(--ink);
      }}
      .subtitle {{ color: var(--muted); font-size: 0.95rem; margin: 0 0 20px 0; }}
      .meta-line {{ font-size: 0.9rem; color: var(--muted); margin-bottom: 6px; }}
      .meta-line .k {{ font-weight: 600; color: #334155; }}
      hr.sep {{ border: none; border-top: 1px solid var(--border); margin: 24px 0; }}
      .banner {{
        border-radius: 10px;
        padding: 14px 16px;
        margin: 0 0 20px 0;
        border: 1px solid var(--border);
        background: var(--card);
      }}
      .banner.note {{ border-color: #c7d2fe; background: var(--accent-soft); color: #1e3a8a; }}
      .banner.warn {{ border-color: var(--warn-border); background: var(--warn-bg); color: #78350f; }}
      .banner p.tight {{ margin: 8px 0 0 0; font-size: 0.92rem; }}
      h2 {{
        font-size: 1.15rem;
        font-weight: 700;
        margin: 28px 0 12px 0;
        color: var(--accent);
        padding-bottom: 6px;
        border-bottom: 2px solid var(--border);
      }}
      h3 {{ font-size: 1.05rem; margin: 0; font-weight: 700; color: var(--ink); }}
      .summary-block {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px 18px;
        margin: 12px 0;
      }}
      .summary-block p {{ margin: 0 0 10px 0; }}
      .summary-block p:last-child {{ margin-bottom: 0; }}
      .lede {{ font-size: 0.98rem; }}
      .placeholder {{
        margin: 10px 0 0 0;
        padding: 10px 12px;
        background: #f1f5f9;
        border-left: 3px solid #94a3b8;
        border-radius: 0 6px 6px 0;
        font-size: 0.92rem;
        color: #475569;
      }}
      .muted {{ color: var(--muted); }}
      .ref-block {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 18px;
        margin: 14px 0;
      }}
      .ref-head {{
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 8px;
      }}
      .iso-tag {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--accent);
        background: var(--accent-soft);
        padding: 4px 10px;
        border-radius: 999px;
      }}
      .meta {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top: 6px; font-size: 0.88rem; }}
      .ver {{ color: var(--muted); }}
      .ver strong {{ color: #334155; }}
      .pill {{
        display:inline-flex;
        align-items:center;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
      }}
      .s-ok {{ background: var(--ok-bg); color: var(--ok); }}
      .s-draft {{ background:#e0f2fe; color:#075985; }}
      .s-review {{ background:#fef9c3; color:#854d0e; }}
      .s-not {{ background:#f1f5f9; color:#475569; }}
      .link {{ font-size: 12px; color: #2563eb; text-decoration: none; font-weight: 600; }}
      .link:hover {{ text-decoration: underline; }}
      .body {{ margin-top: 8px; line-height: 1.6; }}
      ul {{ margin: 8px 0 0 20px; padding: 0; }}
      .toc {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 14px 18px;
        margin: 16px 0 8px 0;
      }}
      .toc ol {{ margin: 8px 0 0 0; padding-left: 22px; }}
      .toc li {{ margin: 4px 0; }}
      .footer-note {{
        margin-top: 32px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
        font-size: 0.85rem;
        color: var(--muted);
      }}
      @media print {{
        body {{ background: #fff; }}
        .ref-block, .summary-block, .banner, .toc {{ break-inside: avoid; }}
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <header>
        <h1 class="doc-title">Risk Management File (RMF) / Risk Management Report (RMR) — Compiled index</h1>
        <p class="subtitle">ISO 14971–aligned compilation for an active implantable medical device project (e.g., implantable pacemaker) — reference-only.</p>
        <div class="meta-line">Project: <span class="k">{pn}</span> &nbsp;|&nbsp; Project ID: <span class="k">{pid}</span></div>
        <div class="meta-line">Compiled (UTC): <span class="k">{escape(generated_display)}</span> &nbsp;|&nbsp; <span class="muted">ISO timestamp: {escape(generated_iso)}</span></div>
      </header>

      <div class="banner note">
        <p class="lede" style="margin:0 0 8px 0;"><strong>Compiled document (read-only intent).</strong></p>
        <p style="margin:0;">This Risk Management File is <strong>compiled from authoritative project documents</strong> registered in SmartQS. It <strong>does not invent risk content</strong>, hazard narratives, or numerical risk estimates. Where this index points to a source document, <strong>see the referenced document for detailed evidence</strong>, conclusions, and approvals.</p>
      </div>

      {not_ready_banner}

      <nav class="toc" aria-label="Document outline">
        <strong>Contents</strong>
        <ol>
          <li><a href="#purpose">Purpose</a></li>
          <li><a href="#traceability">Traceability statement</a></li>
          <li><a href="#summary-controls">Risk control implementation summary</a></li>
          <li><a href="#summary-residual">Residual risk evaluation summary</a></li>
          <li><a href="#summary-benefit">Benefit–risk analysis statement</a></li>
          <li><a href="#summary-overall">Overall conclusion</a></li>
          <li><a href="#summary-postmarket">Production and post-production information</a></li>
          <li><a href="#references">Referenced authoritative documents</a></li>
        </ol>
      </nav>

      <h2 id="purpose">1. Purpose</h2>
      <div class="summary-block">
        <p class="lede">This document provides a <strong>controlled, read-only compilation</strong> of the Risk Management File (RMF) / Risk Management Report (RMR) <strong>as an index to authoritative records</strong> in the project repository. It supports audit and submission review by showing <strong>which versioned documents</strong> satisfy ISO 14971 lifecycle expectations (planning, hazard identification, analysis, control, residual risk, benefit–risk, review, and post-market information) without restating underlying analysis.</p>
        <p class="muted" style="margin-top:10px;">This compilation is suitable for implantable pacemaker–class projects when the referenced documents are maintained under the same design control and risk management process.</p>
      </div>

      <h2 id="traceability">2. Traceability statement</h2>
      <div class="summary-block">
        <p class="lede">Traceability from this RMF to evidence is <strong>by document identity and version</strong>. Each section below links to the corresponding SmartQS project document. Detailed traceability matrices (e.g., hazard → control → verification) reside in the <strong>referenced</strong> Hazard Analysis, FMEA, Risk Control Measures, and Verification records — not in this index.</p>
        <p class="placeholder" style="margin-top:12px;">If a referenced document is not yet created or is in draft status, the RMF remains an index only; <strong>do not infer approval or completeness</strong> from this compilation alone.</p>
      </div>

      <h2 id="summary-controls">3. Risk control implementation summary</h2>
      <div class="summary-block">
        <p class="lede">This RMF does not restate individual control measures. Implementation status, design controls, and verification hooks are <strong>documented in the Risk Control Measures Documentation</strong> and linked analyses.</p>
        <p class="placeholder">See the Risk Control Measures Documentation for risk control identification, implementation, and verification planning. See the referenced FMEA and Hazard Analysis for analysis-level linkage.</p>
      </div>

      <h2 id="summary-residual">4. Residual risk evaluation summary</h2>
      <div class="summary-block">
        <p class="lede">Residual risk evaluations and acceptability conclusions are <strong>authorized in the Residual Risk Evaluation</strong> document, not in this index.</p>
        <p class="placeholder">See the Residual Risk Evaluation document for residual risk summaries and acceptability conclusions.</p>
      </div>

      <h2 id="summary-benefit">5. Benefit–risk analysis statement</h2>
      <div class="summary-block">
        <p class="lede">Where benefit–risk determinations are required (including for residual risks that are not reduced to acceptable levels), the <strong>detailed rationale and approvals</strong> are recorded in the project&rsquo;s benefit–risk and risk management records as referenced from the Risk Management Plan and Residual Risk Evaluation.</p>
        <p class="placeholder">See the Residual Risk Evaluation and Risk Management Review records for benefit–risk conclusions and formal disposition. This RMF does not assert a benefit–risk outcome on its own.</p>
      </div>

      <h2 id="summary-overall">6. Overall conclusion</h2>
      <div class="summary-block">
        <p class="lede">An <strong>overall conclusion</strong> that residual risks are acceptable in relation to benefits and that the risk management activities are complete for the intended purpose is <strong>not stated in this compiled index</strong> unless reflected in the referenced Risk Management Review / RMR and supporting documents.</p>
        <p class="placeholder">See the Risk Management Review record for formal review disposition and approvals. See the Residual Risk Evaluation document for residual risk acceptability conclusions.</p>
      </div>

      <h2 id="summary-postmarket">7. Production and post-production information</h2>
      <div class="summary-block">
        <p class="lede">Information collection and post-production monitoring (including feedback from the risk management process) are <strong>defined in the Risk Management Plan</strong> and implemented per project procedures. This RMF index does not duplicate production or post-market data.</p>
        <p class="placeholder">See the Risk Management Plan for planned production and post-production activities. See the Risk Management Review record for evidence of updates to the risk management process as required by ISO 14971.</p>
      </div>

      <h2 id="references">8. Referenced authoritative documents</h2>
      <p class="muted" style="margin-top:0;">The following sections maintain the <strong>standard mapping</strong>: Scope → RMP; Hazard identification → Hazard Analysis; Risk analysis → FMEA; Risk controls → Risk Control Measures Documentation; Residual risk → Residual Risk Evaluation; Review status → Risk Management Review. Each block shows <strong>document status and version</strong> as stored in SmartQS.</p>

      {scope_block}
      {hazard_block}
      {fmea_block}
      {controls_block}
      {residual_block}
      {review_block}

      <p class="footer-note">
        End of compiled Risk Management File index. This RMF is compiled from authoritative project documents; it does not invent risk content. For regulatory submissions, attach or cite the referenced document versions shown above.
      </p>
    </div>
  </body>
</html>"""

    return html, ready
