"""
Risk Control Measures Documentation HTML Renderer
Audit-ready Risk Control Measures Documentation per ISO 14971:2019 control hierarchy.
"""
from __future__ import annotations

import html
from typing import Dict, Any, List
from datetime import datetime as dt_datetime, timezone


def _esc(s: Any) -> str:
    if s is None:
        return "—"
    return html.escape(str(s), quote=True)


def _normalize_control_type_hierarchy(raw: Any) -> str:
    """Map stored control_type to ISO 14971 category label."""
    t = str(raw or "").strip().lower()
    if "inherent" in t or t in {"design", "design_control", "engineering_control"}:
        return "Inherent Safety by Design"
    if "protect" in t or "safeguard" in t:
        return "Protective Measure"
    if "information" in t or "label" in t or "ifu" in t or "instruction" in t:
        return "Information for Safety"
    if "unclassified" in t:
        return str(raw or "Unclassified — assign per ISO 14971 hierarchy").strip()
    if t and t not in {"tbd", "n/a", "na"}:
        # Title-case unknown DB values for display
        return str(raw).strip()
    return "Unclassified — assign per ISO 14971 §7 hierarchy"


def _format_implementation_block(row: Dict[str, Any]) -> str:
    refs: List[Dict[str, Any]] = row.get("implementation_refs") or []
    details = (row.get("implementation_details") or "").strip()
    lines: List[str] = []
    if details:
        lines.append(_esc(details))
    if refs:
        lines.append("<strong>Linked design artifacts:</strong>")
        lines.append("<ul>")
        for ref in refs:
            lines.append(f"<li>{_esc(ref.get('display', ref.get('id', '—')))}</li>")
        lines.append("</ul>")
    if not lines:
        return (
            "<p><em>No Design Input or Design Output trace links are recorded for this control in SmartRisk. "
            "Record DI/DO references (e.g. DI-xxx, DO-xxx, drawing/configuration identifiers) in traceability "
            "before design transfer.</em></p>"
        )
    return "\n".join(lines)


def _format_verification_block(row: Dict[str, Any]) -> str:
    methods: List[Dict[str, Any]] = row.get("verification_methods") or []
    vm = (row.get("verification_method") or "").strip()
    lines: List[str] = []
    if vm:
        lines.append(f"<p>{_esc(vm)}</p>")
    if methods:
        lines.append("<strong>Linked verification / validation records:</strong>")
        lines.append("<ul>")
        for m in methods:
            lines.append(f"<li>{_esc(m.get('display', m.get('id', '—')))}</li>")
        lines.append("</ul>")
    if not lines:
        return (
            "<p><em>No verification artifacts are linked. Link executed or approved protocols/reports "
            "(e.g. bench test, EMI test, software unit verification, clinical evaluation excerpts where applicable) "
            "prior to claiming control implementation closure.</em></p>"
        )
    return "\n".join(lines)


def _acceptance_criteria_block(row: Dict[str, Any]) -> str:
    if row.get("verification_methods"):
        return (
            "Pass/fail and quantitative limits defined in the linked verification record(s); objective evidence "
            "retained under document control. If no numerical limit applies, record expected behaviour and "
            "observed result in the linked report."
        )
    return (
        "Define measurable pass criteria in the verification protocol before execution (e.g. maximum leakage current "
        "per IEC 60601-1 clause, software unit test assertions, dimensional tolerance on controlled drawing). "
        "This record cannot assert closure until criteria are documented and linked."
    )


def _residual_evaluation_block(row: Dict[str, Any]) -> str:
    rs = row.get("residual_severity")
    rp = row.get("residual_probability")
    score = row.get("residual_risk_score")
    level = row.get("residual_risk_level")
    acc = row.get("risk_acceptability")
    rat = row.get("risk_rationale")
    if rs is None and rp is None and score is None and not acc:
        return (
            "<p><em>Residual severity, probability, and acceptability are not recorded on the current risk item "
            "version. Complete residual estimation and acceptability per the Risk Management Plan after "
            "verification of this control.</em></p>"
        )
    parts = [
        f"<p><strong>Residual severity (as recorded):</strong> {_esc(rs)}</p>",
        f"<p><strong>Residual probability / occurrence (as recorded):</strong> {_esc(rp)}</p>",
        f"<p><strong>Residual risk score / index (as recorded):</strong> {_esc(score)}</p>",
        f"<p><strong>Residual level (as recorded):</strong> {_esc(level)}</p>",
        f"<p><strong>Risk acceptability (per RMP / RAC):</strong> {_esc(acc)}</p>",
    ]
    if rat:
        parts.append(f"<p><strong>Rationale:</strong> {_esc(rat)}</p>")
    return "\n".join(parts)


def _collect_gaps_and_key_areas(rows: List[Dict[str, Any]]) -> tuple[List[str], List[str]]:
    gaps: List[str] = []
    areas: List[str] = []
    if not rows:
        gaps.append("No risk controls compiled for the selected scope — populate RiskControl entities or formalize FMEA mitigations into risk items.")
        return areas, gaps
    miss_both = sum(
        1 for r in rows
        if r.get("flags", {}).get("missing_implementation") and r.get("flags", {}).get("missing_verification")
    )
    if miss_both:
        gaps.append(f"{miss_both} control(s) lack both implementation and verification trace links.")
    mi = sum(1 for r in rows if r.get("flags", {}).get("missing_implementation"))
    mv = sum(1 for r in rows if r.get("flags", {}).get("missing_verification"))
    if mi:
        gaps.append(f"{mi} control(s) lack linked Design Input / Design Output evidence.")
    if mv:
        gaps.append(f"{mv} control(s) lack linked verification / validation evidence.")
    unclass = sum(
        1 for r in rows
        if "Unclassified" in _normalize_control_type_hierarchy(r.get("control_type"))
    )
    if unclass:
        gaps.append(f"{unclass} control(s) require ISO 14971 control-type classification (inherent / protective / information).")
    # Key risk areas: components with most controls
    by_comp: Dict[str, int] = {}
    for r in rows:
        c = r.get("component_name") or "Unknown"
        by_comp[c] = by_comp.get(c, 0) + 1
    top = sorted(by_comp.items(), key=lambda x: -x[1])[:5]
    for name, n in top:
        areas.append(f"{name}: {n} control measure(s) in this export")
    return areas, gaps


def render_risk_controls_doc_html(evidence: Dict[str, Any], project_name: str) -> str:
    """
    Render risk control measures documentation evidence into HTML report.

    Structure: document control → executive summary → strict per-control records (ISO 14971-aligned).
    """
    components = evidence.get("components", [])
    rows: List[Dict[str, Any]] = evidence.get("rows", [])
    counts = evidence.get("counts", {})
    project_id = evidence.get("project_id", "")
    version_scope = evidence.get("version_scope", "current")

    generated_utc = dt_datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    doc_id = f"RCM-{str(project_id)[:8].upper()}" if project_id else "RCM-PROJECT"
    revision = "01"
    date_str = dt_datetime.now(timezone.utc).strftime("%Y-%m-%d")

    components_html = ""
    if components:
        for comp in components:
            comp_name = comp.get("name", comp.get("id", "Unknown"))
            components_html += f"<li>{_esc(comp_name)}</li>\n"
    else:
        components_html = "<li>All project components</li>\n"

    n_controls = int(counts.get("controls", len(rows)))
    pct = counts.get("percent_complete_implementation_verification", 0.0)
    key_areas, major_gaps = _collect_gaps_and_key_areas(rows)

    key_areas_html = "".join(f"<li>{_esc(a)}</li>\n" for a in key_areas) or "<li>—</li>\n"
    gaps_html = "".join(f"<li>{_esc(g)}</li>\n" for g in major_gaps) or "<li>—</li>\n"

    controls_html = ""
    if not rows:
        controls_html = (
            "<div class='statement'><strong>No structured risk controls in scope.</strong><br/>"
            "Add <code>RiskControl</code> records with trace links to Design Inputs, Design Outputs, and "
            "verification / validation artifacts, or migrate FMEA mitigations into controlled risk items.</div>"
        )
    else:
        # Sort for stable output: component, control key
        sorted_rows = sorted(
            rows,
            key=lambda r: (str(r.get("component_name") or ""), str(r.get("control_key") or "")),
        )
        for row in sorted_rows:
            cid_display = _esc(row.get("control_key") or row.get("control_id") or "—")
            comp = _esc(row.get("component_name") or "—")
            hz = row.get("hazard") or "Not recorded — complete hazard analysis chain in risk item version."
            hs = row.get("hazardous_situation") or "Not recorded — state the hazardous situation (exposure scenario) in the risk item version."
            hm = row.get("harm") or "Not recorded — state the harm in the risk item version."
            ctype = _normalize_control_type_hierarchy(row.get("control_type"))

            measure = (row.get("control_description") or "").strip() or (
                "Control text not captured — enter a specific design, manufacturing, or labeling control in the "
                "RiskControl record."
            )

            controls_html += f"""
    <div class="control-record">
      <h3 class="control-id">Control ID: {cid_display}</h3>
      <table class="field-table">
        <tr><th>Component</th><td>{comp}</td></tr>
        <tr><th>Hazard</th><td>{_esc(hz)}</td></tr>
        <tr><th>Hazardous situation</th><td>{_esc(hs)}</td></tr>
        <tr><th>Harm</th><td>{_esc(hm)}</td></tr>
        <tr><th>Risk reference</th><td>{_esc(row.get("risk_key") or "—")}</td></tr>
        <tr><th>Control type (ISO 14971)</th><td>{_esc(ctype)}</td></tr>
        <tr><th>Risk control measure(s)</th><td>{_esc(measure)}</td></tr>
        <tr><th>Implementation</th><td>{_format_implementation_block(row)}</td></tr>
        <tr><th>Verification method</th><td>{_format_verification_block(row)}</td></tr>
        <tr><th>Acceptance criteria</th><td>{_esc(_acceptance_criteria_block(row))}</td></tr>
        <tr><th>Effectiveness / residual risk evaluation</th><td>{_residual_evaluation_block(row)}</td></tr>
      </table>
    </div>
"""

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Risk Control Measures Documentation — {_esc(project_name)}</title>
    <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            margin: 40px;
            line-height: 1.55;
            color: #1f2937;
        }}
        h1 {{
            color: #1e40af;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #1e40af;
            margin-top: 28px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 6px;
            font-size: 1.15em;
        }}
        h3.control-id {{
            color: #111827;
            margin-top: 24px;
            font-size: 1.05em;
        }}
        .doc-control, .summary-box, .statement {{
            margin: 16px 0;
            padding: 14px 16px;
            border-radius: 6px;
        }}
        .doc-control {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
        }}
        .summary-box {{
            background: #eff6ff;
            border-left: 4px solid #2563eb;
        }}
        .statement {{
            background: #fefce8;
            border-left: 4px solid #ca8a04;
            font-size: 0.95em;
        }}
        .field-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0 24px 0;
            font-size: 0.92em;
        }}
        .field-table th {{
            width: 22%;
            text-align: left;
            vertical-align: top;
            background: #f3f4f6;
            border:               1px solid #d1d5db;
            padding: 10px;
            font-weight: 600;
        }}
        .field-table td {{
            border: 1px solid #d1d5db;
            padding: 10px;
            vertical-align: top;
        }}
        .control-record {{
            page-break-inside: avoid;
        }}
        .meta {{ color: #6b7280; font-size: 0.9em; margin-bottom: 16px; }}
        ul {{ margin: 8px 0; padding-left: 22px; }}
        .footer-note {{ margin-top: 36px; padding-top: 16px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 0.88em; }}
    </style>
</head>
<body>
    <h1>Risk Control Measures Documentation</h1>

    <div class="doc-control">
        <p><strong>Document ID:</strong> {_esc(doc_id)}</p>
        <p><strong>Revision:</strong> {_esc(revision)}</p>
        <p><strong>Date:</strong> {_esc(date_str)}</p>
        <p><strong>Project:</strong> {_esc(project_name)}</p>
        <p><strong>Prepared by:</strong> Risk management representative — identity recorded in the controlled approval workflow.</p>
        <p><strong>Approved by:</strong> Management with delegated responsibility for risk management — identity recorded in the controlled approval workflow.</p>
        <p><strong>Scope:</strong> Components listed below; risk item version context = {_esc(version_scope)}</p>
        <p><strong>Generated (UTC):</strong> {_esc(generated_utc)}</p>
    </div>

    <div class="meta">
        <p><strong>Components in this export:</strong></p>
        <ul>
{components_html}
        </ul>
    </div>

    <div class="summary-box">
        <h2>Summary</h2>
        <ul>
            <li><strong>Total controls (unique records):</strong> {n_controls}</li>
            <li><strong>Implementation + verification defined (linked):</strong> {counts.get('complete_implementation_and_verification', 0)} ({_esc(pct)}%)</li>
            <li><strong>Missing implementation links:</strong> {counts.get('missing_implementation', 0)}</li>
            <li><strong>Missing verification links:</strong> {counts.get('missing_verification', 0)}</li>
        </ul>
        <p><strong>Key risk areas (by control count):</strong></p>
        <ul>{key_areas_html}</ul>
        <p><strong>Major gaps:</strong></p>
        <ul>{gaps_html}</ul>
    </div>

    <div class="statement">
        <p><strong>Regulatory context:</strong> Controls are categorized per ISO 14971:2019 (inherently safe design, protective measures, information for safety).
        Traceability to design artifacts and verification evidence is required for audit; narrative-only entries without links are flagged above.</p>
        <p><strong>IEC 60601 / design control:</strong> Electrical safety and essential performance controls reference controlled design outputs and verification per the project V&amp;V plan.</p>
    </div>

    <h2>Risk control register</h2>
    {controls_html}

    <p class="footer-note">
        This document was generated by SmartRisk from controlled risk control and traceability records.
        It does not replace protocol execution, design reviews, or formal approval in the quality management system.
        ISO 14971:2019; align essential performance and IEC 60601-1 verification where applicable.
    </p>
</body>
</html>"""

    return html_out
