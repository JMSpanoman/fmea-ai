"""
Hazard Analysis HTML Renderer
Generates audit-ready Hazard Analysis HTML report with full ISO 14971-style fields.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime as dt_datetime


def _fmt_list(val: Any) -> str:
    if val is None:
        return "—"
    if isinstance(val, list):
        if not val:
            return "—"
        return "; ".join(str(x) for x in val)
    return str(val).strip() or "—"


def _fmt_date(iso_str: Optional[str]) -> str:
    if not iso_str:
        return "—"
    try:
        dt = dt_datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str


def render_hazard_analysis_html(
    evidence: Dict[str, Any],
    project_name: str,
    device_name: Optional[str] = None,
    intended_use: Optional[str] = None,
) -> str:
    """
    Render hazard analysis evidence into HTML report with full columns and appendix.
    """
    components = evidence.get("components", [])
    rows = evidence.get("rows", [])
    version_scope = evidence.get("version_scope", "approved_only")
    include_unapproved = evidence.get("include_unapproved", False)
    counts = evidence.get("counts", {})
    generated_at = dt_datetime.now().isoformat()
    total_risks = counts.get("versions_included", counts.get("risk_items", len(rows)))

    components_html = ""
    if components:
        for comp in components:
            comp_name = comp.get("name", comp.get("id", "Unknown"))
            components_html += f"<li>{comp_name}</li>\n"
    else:
        components_html = "<li>All components</li>\n"

    if version_scope == "approved_only":
        version_scope_statement = "Approved versions only"
        if include_unapproved:
            version_scope_statement += " (includes unapproved entries marked as Draft)"
    elif version_scope == "current":
        version_scope_statement = "Current versions only"
    else:
        version_scope_statement = "All versions"

    approved_count = sum(1 for r in rows if r.get("approved"))
    approval_summary = f"{approved_count} approved, {len(rows) - approved_count} draft or in review"

    rows_by_component: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        comp_name = row.get("component_name", "Unknown")
        if comp_name not in rows_by_component:
            rows_by_component[comp_name] = []
        rows_by_component[comp_name].append(row)

    table_rows_html = ""
    for component_name, component_rows in sorted(rows_by_component.items()):
        table_rows_html += f'<h3 class="component-heading">Component: {component_name}</h3>\n'
        table_rows_html += '<table class="ha-table">\n<thead><tr>'
        table_rows_html += '<th>Risk Key</th><th>Ver</th><th>Hazard Category</th><th>Hazard</th>'
        table_rows_html += '<th>Failure Mode</th><th>Cause</th><th>Sequence of Events</th>'
        table_rows_html += '<th>Hazardous Situation</th><th>Harm</th>'
        table_rows_html += '<th>Init Sev</th><th>Init Prob</th><th>Init Risk</th>'
        table_rows_html += '<th>Risk Controls</th>'
        table_rows_html += '<th>Res Sev</th><th>Res Prob</th><th>Res Risk</th><th>Res Accept</th>'
        table_rows_html += '<th>Traceability</th><th>Status</th><th>Approved By/At</th>'
        table_rows_html += '</tr></thead>\n<tbody>\n'
        for row in component_rows:
            approval_status = "Approved" if row.get("approved") else (row.get("approval_status") or "Draft")
            badge_class = "approved" if row.get("approved") else "draft"
            approved_info = _fmt_date(row.get("approved_at")) if row.get("approved") else "—"
            if row.get("approved_by"):
                approved_info = f"{row.get('approved_by', '')}<br/>{approved_info}"
            seq = row.get("foreseeable_sequence_of_events") or row.get("sequence_of_events")
            controls = row.get("risk_control_measures")
            trace = []
            for k in ("verification_reference", "validation_reference", "requirement_ids"):
                v = row.get(k)
                if v:
                    trace.extend(v if isinstance(v, list) else [v])
            trace_str = _fmt_list(trace) if trace else "—"
            table_rows_html += "<tr>"
            table_rows_html += f'<td>{row.get("risk_key") or "—"}</td>'
            table_rows_html += f'<td>{row.get("version_no", "—")}</td>'
            table_rows_html += f'<td>{row.get("hazard_category") or "—"}</td>'
            table_rows_html += f'<td>{row.get("hazard") or "—"}</td>'
            table_rows_html += f'<td>{row.get("failure_mode") or "—"}</td>'
            table_rows_html += f'<td>{row.get("cause_of_failure") or "—"}</td>'
            table_rows_html += f'<td class="wrap">{seq or "—"}</td>'
            table_rows_html += f'<td class="wrap">{row.get("hazardous_situation") or "—"}</td>'
            table_rows_html += f'<td class="wrap">{row.get("harm") or "—"}</td>'
            table_rows_html += f'<td>{row.get("initial_severity") or "—"}</td>'
            table_rows_html += f'<td>{row.get("initial_probability") or "—"}</td>'
            table_rows_html += f'<td>{row.get("initial_risk_level") or "—"}</td>'
            table_rows_html += f'<td class="wrap">{_fmt_list(controls)}</td>'
            table_rows_html += f'<td>{row.get("residual_severity") or "—"}</td>'
            table_rows_html += f'<td>{row.get("residual_probability") or "—"}</td>'
            table_rows_html += f'<td>{row.get("residual_risk_level") or "—"}</td>'
            table_rows_html += f'<td>{row.get("residual_risk_acceptability") or "—"}</td>'
            table_rows_html += f'<td class="wrap small">{trace_str}</td>'
            table_rows_html += f'<td><span class="{badge_class}">{approval_status}</span></td>'
            table_rows_html += f'<td class="small">{approved_info}</td>'
            table_rows_html += "</tr>\n"
        table_rows_html += "</tbody></table>\n"

    unapproved_warning = ""
    if include_unapproved and version_scope == "approved_only":
        unapproved_warning = """
        <div class="warning">
            <p><strong>Includes Draft (Unapproved) Entries</strong></p>
            <p>This report includes hazard analysis items that have not been approved. Draft entries are marked accordingly.</p>
        </div>
        """

    appendix_items = []
    ai_rows = [r for r in rows if r.get("ai_generated")]
    if ai_rows:
        for r in ai_rows:
            ass = r.get("assumptions") or []
            if ass or r.get("ai_confidence"):
                appendix_items.append({
                    "risk_key": r.get("risk_key"),
                    "component": r.get("component_name"),
                    "assumptions": ass,
                    "ai_confidence": r.get("ai_confidence"),
                })
    reviewer_comments = [r for r in rows if r.get("reviewer_comments")]
    unapproved_list = [f"{r.get('component_name')} / {r.get('risk_key')}" for r in rows if not r.get("approved")]

    appendix_html = ""
    if appendix_items or reviewer_comments or unapproved_list:
        appendix_html = '<div class="section"><h2>Appendix</h2>'
        if appendix_items:
            appendix_html += "<h4>AI-generated content (assumptions / confidence)</h4><ul>"
            for a in appendix_items[:20]:
                appendix_html += f"<li><strong>{a.get('component')} / {a.get('risk_key')}</strong>"
                if a.get("ai_confidence"):
                    appendix_html += f" — Confidence: {a['ai_confidence']}"
                appendix_html += "<ul>"
                for x in (a.get("assumptions") or [])[:5]:
                    appendix_html += f"<li>{x}</li>"
                appendix_html += "</ul></li>"
            appendix_html += "</ul>"
        if reviewer_comments:
            appendix_html += "<h4>Reviewer comments</h4><ul>"
            for r in reviewer_comments[:15]:
                appendix_html += f"<li>{r.get('risk_key')}: {r.get('reviewer_comments', '')[:200]}</li>"
            appendix_html += "</ul>"
        if unapproved_list:
            appendix_html += "<h4>Unapproved items in this export</h4><ul>"
            for u in unapproved_list[:30]:
                appendix_html += f"<li>{u}</li>"
            appendix_html += "</ul>"
        appendix_html += "</div>"

    device_block = f"<p><strong>Device:</strong> {device_name}</p>" if device_name else ""
    intended_block = f"<p><strong>Intended use:</strong> {intended_use}</p>" if intended_use else ""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hazard Analysis — {project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.5; color: #333; }}
        h1 {{ color: #1e40af; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
        h2 {{ color: #1e40af; margin-top: 28px; border-bottom: 2px solid #e5e7eb; padding-bottom: 5px; }}
        h3.component-heading {{ color: #374151; margin-top: 22px; margin-bottom: 8px; }}
        h4 {{ color: #4b5563; margin-top: 14px; }}
        table.ha-table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.9em; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
        th {{ background-color: #f3f4f6; font-weight: bold; }}
        td.wrap {{ max-width: 220px; word-wrap: break-word; }}
        td.small {{ font-size: 0.85em; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f9fafb; border-radius: 6px; }}
        .meta {{ color: #6b7280; font-size: 0.9em; margin-bottom: 20px; }}
        .approved {{ background-color: #d1fae5; color: #065f46; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }}
        .draft {{ background-color: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; }}
        .warning {{ background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
        .statement {{ background-color: #eff6ff; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0; }}
        .counts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 20px 0; }}
        .count-box {{ background: white; padding: 12px; border-radius: 5px; border: 1px solid #e5e7eb; }}
        .count-label {{ font-size: 0.85em; color: #6b7280; }}
        .count-value {{ font-size: 1.4em; font-weight: bold; color: #1f2937; }}
        ul {{ margin: 8px 0; padding-left: 24px; }}
    </style>
</head>
<body>
    <h1>Hazard Analysis Report</h1>
    <div class="meta">
        <p><strong>Project:</strong> {project_name}</p>
        {device_block}
        {intended_block}
        <p><strong>Components:</strong></p>
        <ul>{components_html}</ul>
        <p><strong>Version scope:</strong> {version_scope_statement}</p>
        <p><strong>Generated:</strong> {generated_at}</p>
        <p><strong>Total risks included:</strong> {total_risks}</p>
        <p><strong>Approval summary:</strong> {approval_summary}</p>
    </div>
    <div class="statement">
        <p><strong>Audit statement</strong></p>
        <p>This export is a point-in-time compilation of hazard analysis data. Data is sourced from hazard analysis items or risk item versions. Approved items are immutable unless versioned.</p>
    </div>
    {unapproved_warning}
    <div class="counts">
        <div class="count-box"><div class="count-label">Risk items</div><div class="count-value">{counts.get("risk_items", 0)}</div></div>
        <div class="count-box"><div class="count-label">Versions included</div><div class="count-value">{counts.get("versions_included", 0)}</div></div>
        <div class="count-box"><div class="count-label">Unapproved excluded</div><div class="count-value">{counts.get("unapproved_excluded", 0)}</div></div>
    </div>
    <div class="section">
        <h2>Hazard analysis table</h2>
        {table_rows_html if table_rows_html else "<p>No hazard analysis data found.</p>"}
    </div>
    {appendix_html}
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb; font-size: 0.9em; color: #6b7280;">
        <p>SmartRisk Hazard Analysis. ISO 14971:2019.</p>
    </div>
</body>
</html>"""
    return html
