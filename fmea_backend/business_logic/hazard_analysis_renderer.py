"""
Hazard Analysis HTML Renderer
Generates audit-ready Hazard Analysis HTML report with full ISO 14971-style fields.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime as dt_datetime
from business_logic.hazard_analysis_builder import compute_canonical_approval_state


STATUS_ORDER = ["approved", "draft", "in_review", "rejected", "unapproved", "unknown"]


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


def _normalize_row_approval(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recompute canonical approval fields for renderer consistency.
    This prevents stale/missing precomputed fields from drifting the table status
    away from summary/appendix logic.
    """
    canonical = compute_canonical_approval_state(
        approval_status=row.get("approval_status"),
        approved_by=row.get("approved_by"),
        approved_at=row.get("approved_at"),
    )
    out = dict(row)
    out["canonical_approval_state"] = canonical["canonical_state"]
    out["canonical_is_approved"] = canonical["canonical_is_approved"]
    out["approved_by"] = canonical["canonical_approved_by"]
    out["approved_at"] = canonical["canonical_approved_at"]
    out["approved"] = canonical["canonical_is_approved"]
    return out


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
    raw_rows = evidence.get("rows", [])
    rows = [_normalize_row_approval(r) for r in raw_rows]
    version_scope = evidence.get("version_scope", "approved_only")
    include_unapproved = evidence.get("include_unapproved", False)
    counts = evidence.get("counts", {})
    report_mode = evidence.get("report_mode", "regulatory")
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

    status_counts = {k: 0 for k in STATUS_ORDER}
    for r in rows:
        s = str(r.get("canonical_approval_state") or "").strip().lower()
        if s not in status_counts:
            s = "unknown"
        status_counts[s] += 1
    excluded_unapproved_items = evidence.get("excluded_unapproved_items") or []
    for e in excluded_unapproved_items:
        s = str(e.get("state") or "").strip().lower()
        if s not in status_counts:
            s = "unknown"
        status_counts[s] += 1
    status_total_candidates = sum(status_counts.values())

    approved_count = int(status_counts.get("approved", 0))
    non_approved_total = status_total_candidates - approved_count
    approval_summary = f"{approved_count} approved, {non_approved_total} non-approved"
    status_summary_bits = [f"{k}: {int(status_counts.get(k, 0))}" for k in STATUS_ORDER if int(status_counts.get(k, 0)) > 0]
    status_summary_text = ", ".join(status_summary_bits) if status_summary_bits else "none"
    included_count = len(rows)
    excluded_count = len(excluded_unapproved_items)
    reconciliation_note = (
        f"Candidates: {status_total_candidates} = included {included_count} + excluded {excluded_count}"
    )
    no_approved_data = included_count == 0 and excluded_count > 0 and approved_count == 0
    needs_benefit_risk = [
        r for r in rows
        if r.get("benefit_risk_analysis_required")
        or str(r.get("risk_acceptability_decision") or "").strip().lower() in {"not acceptable", "unacceptable", "high"}
    ]

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
        table_rows_html += '<th>Init Sev</th><th>Init Prob/Occ</th><th>Init Risk</th>'
        table_rows_html += '<th>Risk Controls (structured)</th>'
        table_rows_html += '<th>Res Sev</th><th>Res Prob/Occ</th><th>Res Risk</th><th>Acceptability Decision</th><th>Acceptability Justification</th>'
        table_rows_html += '<th>Traceability</th><th>Status</th><th>Approved By/At</th>'
        table_rows_html += '</tr></thead>\n<tbody>\n'
        for row in component_rows:
            canonical_state = (row.get("canonical_approval_state") or "unknown").strip().lower()
            approval_status = canonical_state
            badge_class = "approved" if canonical_state == "approved" else "draft"
            approved_info = _fmt_date(row.get("approved_at")) if canonical_state == "approved" else "—"
            if canonical_state == "approved" and row.get("approved_by"):
                approved_info = f"{row.get('approved_by', '')}<br/>{approved_info}"
            seq = row.get("foreseeable_sequence_of_events") or row.get("sequence_of_events")
            controls = row.get("risk_control_measures")
            structured_controls = row.get("risk_controls") or []
            controls_str = _fmt_list(controls)
            if isinstance(structured_controls, list) and structured_controls:
                parts = []
                for c in structured_controls:
                    if not isinstance(c, dict):
                        continue
                    ct = c.get("control_type") or "control"
                    cd = c.get("control_description") or "description missing"
                    impl = c.get("implementation_status") or "implementation status n/a"
                    ver_m = c.get("verification_method") or "verification method n/a"
                    ver_s = c.get("verification_status") or "verification status n/a"
                    parts.append(f"{ct}: {cd} (impl: {impl}; verify: {ver_m}/{ver_s})")
                if parts:
                    controls_str = "; ".join(parts)
            trace = []
            for k in ("related_design_input", "related_design_output", "verification_reference", "validation_reference", "capa_reference", "requirement_ids"):
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
            table_rows_html += f'<td>{row.get("initial_probability") or row.get("initial_occurrence") or "—"}</td>'
            table_rows_html += f'<td>{row.get("initial_risk_level") or "—"}</td>'
            table_rows_html += f'<td class="wrap">{controls_str}</td>'
            table_rows_html += f'<td>{row.get("residual_severity") or "—"}</td>'
            table_rows_html += f'<td>{row.get("residual_probability") or row.get("residual_occurrence") or "—"}</td>'
            table_rows_html += f'<td>{row.get("residual_risk_level") or "—"}</td>'
            table_rows_html += f'<td>{row.get("risk_acceptability_decision") or row.get("residual_risk_acceptability") or "—"}</td>'
            table_rows_html += f'<td class="wrap">{row.get("risk_acceptability_justification") or "—"}</td>'
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
    if no_approved_data:
        unapproved_warning += f"""
        <div class="warning critical">
            <p><strong>⚠️ No approved hazard analysis data available</strong></p>
            <p>{excluded_count} risk items exist but are not approved. Only approved items are included in this report.</p>
            <p>To include data:</p>
            <ul>
                <li>review and approve hazard analysis items</li>
                <li>or generate a draft report including unapproved items</li>
            </ul>
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
    unapproved_included_list = [
        f"{r.get('component_name')} / {r.get('risk_key')} ({(r.get('canonical_approval_state') or 'unapproved')})"
        for r in rows
        if not r.get("canonical_is_approved")
    ]
    excluded_unapproved_items = evidence.get("excluded_unapproved_items") or []

    appendix_html = ""
    if appendix_items or reviewer_comments or unapproved_included_list or excluded_unapproved_items:
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
        if unapproved_included_list:
            appendix_html += "<h4>Unapproved items included in this export</h4><ul>"
            for u in unapproved_included_list[:30]:
                appendix_html += f"<li>{u}</li>"
            appendix_html += "</ul>"
        if excluded_unapproved_items:
            appendix_html += "<h4>Unapproved items excluded from this export</h4><ul>"
            for e in excluded_unapproved_items[:30]:
                appendix_html += f"<li>{e.get('component_name')} / {e.get('risk_key')} ({e.get('state')})</li>"
            appendix_html += "</ul>"
        appendix_html += "</div>"

    excluded_preview_html = ""
    if no_approved_data and excluded_unapproved_items:
        excluded_preview_html = '<div class="section"><h2>Excluded items preview</h2><p>Showing first 10 excluded non-approved items.</p><ul>'
        for e in excluded_unapproved_items[:10]:
            comp = e.get("component_name") or "Unknown"
            hz = e.get("hazard") or "—"
            fm = e.get("failure_mode") or "—"
            excluded_preview_html += f"<li><strong>{comp}</strong> — Hazard: {hz}; Failure mode: {fm}</li>"
        excluded_preview_html += "</ul></div>"

    compliance_note_html = """
    <div class="statement">
        <p><strong>Compliance note</strong></p>
        <p>Only approved items are included to ensure this report reflects the controlled risk management file in accordance with ISO 14971.</p>
    </div>
    """

    risk_summary_html = f"""
    <div class="section">
        <h2>Risk summary</h2>
        <ul>
            <li>Total risk items: {status_total_candidates}</li>
            <li>Approved: {int(status_counts.get("approved", 0))}</li>
            <li>Draft / In review: {int(status_counts.get("draft", 0)) + int(status_counts.get("in_review", 0))}</li>
            <li>Included in report: {included_count}</li>
        </ul>
    </div>
    """

    next_steps_html = """
    <div class="section">
        <h2>Next steps</h2>
        <ul>
            <li>Review hazard analysis items</li>
            <li>Approve items to include in official report</li>
            <li>Re-generate report</li>
        </ul>
    </div>
    """

    device_block = f"<p><strong>Device:</strong> {device_name}</p>" if device_name else ""
    intended_block = f"<p><strong>Intended use:</strong> {intended_use}</p>" if intended_use else ""
    mode_block = f"<p><strong>Report mode:</strong> {'Regulatory Mode (approved only)' if report_mode == 'regulatory' else 'Working Mode (draft + in-review + approved)'}</p>"

    benefit_risk_section = ""
    if needs_benefit_risk:
        benefit_risk_section = "<div class=\"section\"><h2>Benefit-risk section</h2><ul>"
        for r in needs_benefit_risk[:40]:
            benefit_risk_section += (
                f"<li><strong>{r.get('component_name')} / {r.get('risk_key')}</strong>: "
                f"{r.get('benefit_risk_justification') or 'Benefit-risk justification required.'}</li>"
            )
        benefit_risk_section += "</ul></div>"

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
        .warning.critical {{ background-color: #fef2f2; border-left-color: #dc2626; }}
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
        {mode_block}
        <p><strong>Generated:</strong> {generated_at}</p>
        <p><strong>Total risks included:</strong> {total_risks}</p>
        <p><strong>Approval summary:</strong> {approval_summary}</p>
        <p><strong>Approval status distribution (candidate versions):</strong> {status_summary_text}</p>
        <p><strong>Count reconciliation:</strong> {reconciliation_note}</p>
    </div>
    <div class="statement">
        <p><strong>Audit statement</strong></p>
        <p>This export is a point-in-time compilation of hazard analysis data. Data is sourced from hazard analysis items or risk item versions. Approved items are immutable unless versioned.</p>
    </div>
    {compliance_note_html}
    {risk_summary_html}
    <div class="section">
        <h2>Risk acceptability criteria</h2>
        <p>Risks are evaluated pre-control and post-control using Severity and Probability/Occurrence. Residual high/not acceptable risks require explicit benefit-risk analysis and justification before approval.</p>
    </div>
    {unapproved_warning}
    {excluded_preview_html}
    <div class="counts">
        <div class="count-box"><div class="count-label">Risk items</div><div class="count-value">{counts.get("risk_items", 0)}</div></div>
        <div class="count-box"><div class="count-label">Versions included</div><div class="count-value">{counts.get("versions_included", 0)}</div></div>
        <div class="count-box"><div class="count-label">Unapproved excluded</div><div class="count-value">{counts.get("unapproved_excluded", 0)}</div></div>
    </div>
    <div class="section">
        <h2>Hazard analysis table</h2>
        {table_rows_html if table_rows_html else "<p>No hazard analysis data found.</p>"}
    </div>
    {benefit_risk_section}
    {appendix_html}
    {next_steps_html}
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb; font-size: 0.9em; color: #6b7280;">
        <p>SmartRisk Hazard Analysis. ISO 14971:2019.</p>
    </div>
</body>
</html>"""
    return html
