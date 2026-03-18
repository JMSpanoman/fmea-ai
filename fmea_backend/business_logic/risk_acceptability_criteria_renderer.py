"""
Renders Risk Acceptability Criteria report dict as HTML.
Uses source_type badges: approved_project, org_default, system_draft, ai_generated, placeholder.
"""
from typing import Any, Dict, List


def _badge_class(source_type: str) -> str:
    if source_type == "approved_project":
        return "badge-approved"
    if source_type == "org_default":
        return "badge-org"
    if source_type == "system_draft":
        return "badge-draft"
    if source_type == "ai_generated":
        return "badge-ai"
    return "badge-placeholder"


def _badge_label(source_type: str) -> str:
    if source_type == "approved_project":
        return "Approved"
    if source_type == "org_default":
        return "Org default"
    if source_type == "system_draft":
        return "Draft"
    if source_type == "ai_generated":
        return "AI-generated"
    return "Needs review"


def render_risk_acceptability_criteria_html(report: Dict[str, Any]) -> str:
    """Produce HTML for the full Risk Acceptability Criteria report."""
    h = report.get("document_header", {})
    title = h.get("document_title", "Risk Acceptability Criteria")
    project_name = h.get("project_name", "")
    project_id = h.get("project_id", "")
    device_name = h.get("device_name", "")
    intended_use = h.get("intended_use", "")
    date_gen = h.get("date_generated", "")
    author_src = h.get("author_source", "SYSTEM-GENERATED DRAFT")
    status = h.get("status", "draft")
    version = h.get("version", 1)

    def section_badge(section_key: str) -> str:
        sect = report.get(section_key, {})
        if isinstance(sect, dict) and "source_type" in sect:
            src = sect.get("source_type", "placeholder")
        else:
            meta = report.get("source_metadata", {})
            src = meta.get(section_key, "placeholder")
        return f'<span class="{_badge_class(src)}">{_badge_label(src)}</span>'

    # Severity scale table
    sev = report.get("severity_scale", {})
    sev_scale = sev.get("scale", [])
    sev_rows = ""
    if isinstance(sev_scale, list):
        for row in sev_scale:
            lvl = row.get("level", row.get("label", ""))
            lbl = row.get("label", "") if isinstance(row, dict) else str(row)
            defn = row.get("definition", "") if isinstance(row, dict) else ""
            sev_rows += f"<tr><td>{lvl}</td><td>{lbl}</td><td>{defn}</td></tr>\n"
    else:
        for k, v in (sev_scale if isinstance(sev_scale, dict) else {}).items():
            sev_rows += f"<tr><td>{k}</td><td>{v}</td><td></td></tr>\n"

    # Probability scale table
    prob = report.get("probability_scale", {})
    prob_scale = prob.get("scale", [])
    prob_rows = ""
    if isinstance(prob_scale, list):
        for row in prob_scale:
            lvl = row.get("level", row.get("label", ""))
            lbl = row.get("label", "") if isinstance(row, dict) else str(row)
            defn = row.get("definition", "") if isinstance(row, dict) else ""
            prob_rows += f"<tr><td>{lvl}</td><td>{lbl}</td><td>{defn}</td></tr>\n"
    else:
        for k, v in (prob_scale if isinstance(prob_scale, dict) else {}).items():
            prob_rows += f"<tr><td>{k}</td><td>{v}</td><td></td></tr>\n"

    # Risk matrix table
    mat = report.get("risk_matrix", {})
    matrix_data = mat.get("matrix", [])
    if isinstance(matrix_data, dict) and "matrix" in matrix_data:
        matrix_data = matrix_data["matrix"]
    matrix_label = mat.get("label", "")
    matrix_src = mat.get("source_type", "system_draft")
    mat_html = ""
    if isinstance(matrix_data, list) and len(matrix_data) > 0:
        mat_html = "<table class=\"rac-table\"><thead><tr><th>Sev \\ Prob</th>"
        n_cols = len(matrix_data[0]) if matrix_data and isinstance(matrix_data[0], (list, tuple)) else 0
        for j in range(n_cols):
            mat_html += f"<th>{j + 1}</th>"
        mat_html += "</tr></thead><tbody>"
        for i, row in enumerate(matrix_data):
            mat_html += f"<tr><th>{i + 1}</th>"
            for j, cell in enumerate(row if isinstance(row, (list, tuple)) else [row]):
                mat_html += f"<td>{cell}</td>"
            mat_html += "</tr>"
        mat_html += "</tbody></table>"
    if matrix_label:
        mat_html = f"<p class=\"matrix-notice\">{matrix_label}</p>" + mat_html

    # Definitions
    defs = report.get("definitions", {})
    def_items = defs.get("items", {})
    def_rows = ""
    for term, meaning in (def_items if isinstance(def_items, dict) else {}).items():
        def_rows += f"<tr><td><strong>{term}</strong></td><td>{meaning}</td></tr>\n"

    # Roles
    roles = report.get("roles_and_responsibilities", {}).get("roles", [])
    role_rows = ""
    for r in roles:
        role = r.get("role", "")
        name = r.get("name", "")
        resp = r.get("responsibility", "")
        role_rows += f"<tr><td>{role}</td><td>{name}</td><td>{resp}</td></tr>\n"

    # Traceability
    trace = report.get("traceability_references", {})
    trace_rows = ""
    for doc_name, info in (trace if isinstance(trace, dict) else {}).items():
        doc_id = info.get("id", "") if isinstance(info, dict) else ""
        status = info.get("status", "") if isinstance(info, dict) else ""
        trace_rows += f"<tr><td>{doc_name.replace('_', ' ').title()}</td><td>{doc_id or 'Not yet linked'}</td><td>{status or '—'}</td></tr>\n"

    # Manual review items
    manual = report.get("manual_review_items", [])
    manual_list = ""
    for g in manual:
        msg = g.get("message", "")
        sec = g.get("section", "")
        manual_list += f"<li><strong>{sec}:</strong> {msg}</li>\n"

    # Review and approval: version history table
    rev = report.get("review_and_approval", {})
    prepared_by = rev.get("prepared_by", "To be assigned")
    reviewed_by = rev.get("reviewed_by", "To be assigned")
    approved_by = rev.get("approved_by", "To be assigned")
    version_history = rev.get("version_history") or []
    version_rows = ""
    for v in version_history:
        ver = v.get("version", "")
        date = v.get("date", "")
        desc = v.get("description", "")
        author = v.get("author", "")
        version_rows += f"<tr><td>{ver}</td><td>{date}</td><td>{desc}</td><td>{author}</td></tr>\n"
    if not version_rows:
        version_rows = f"<tr><td>{version}</td><td>{date_gen[:10] if date_gen else '—'}</td><td>Initial draft</td><td>System</td></tr>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <title>{title} — {project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.5; color: #333; }}
        .badge-approved {{ background: #d1fae5; color: #065f46; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold; }}
        .badge-org {{ background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; }}
        .badge-draft {{ background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; }}
        .badge-ai {{ background: #e9d5ff; color: #5b21b6; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; }}
        .badge-placeholder {{ background: #f3f4f6; color: #6b7280; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; }}
        h1 {{ color: #1e40af; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }}
        h2 {{ color: #1e40af; margin-top: 24px; font-size: 1.1em; }}
        .section {{ margin: 16px 0; }}
        .rac-table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.9em; }}
        .rac-table th, .rac-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .rac-table th {{ background: #f3f4f6; }}
        .matrix-notice {{ font-size: 0.9em; color: #92400e; margin-bottom: 8px; }}
        .meta {{ color: #6b7280; font-size: 0.9em; margin-bottom: 20px; }}
        .manual-review {{ background: #fef2f2; border-left: 4px solid #dc2626; padding: 12px; margin: 20px 0; }}
        .manual-review ul {{ margin: 8px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="meta">
        <p><strong>Project:</strong> {project_name} | <strong>Project ID:</strong> {project_id}</p>
        <p><strong>Device:</strong> {device_name}</p>
        <p><strong>Intended use:</strong> {intended_use}</p>
        <p><strong>Status:</strong> {status} | <strong>Version:</strong> {version}</p>
        <p><strong>Date generated:</strong> {date_gen}</p>
        <p><strong>Author/source:</strong> {author_src}</p>
    </div>

    <div class="section">
        <h2>1. Purpose {section_badge('purpose')}</h2>
        <p>{report.get('purpose', {}).get('text', '')}</p>
    </div>

    <div class="section">
        <h2>2. Scope {section_badge('scope')}</h2>
        <p>{report.get('scope', {}).get('text', '')}</p>
    </div>

    <div class="section">
        <h2>3. Regulatory / standards basis {section_badge('regulatory_basis')}</h2>
        <p>{report.get('regulatory_basis', {}).get('text', '')}</p>
    </div>

    <div class="section">
        <h2>4. Definitions {section_badge('definitions')}</h2>
        <table class="rac-table"><thead><tr><th>Term</th><th>Definition</th></tr></thead><tbody>{def_rows}</tbody></table>
    </div>

    <div class="section">
        <h2>5. Severity scale {section_badge('severity_scale')}</h2>
        <table class="rac-table"><thead><tr><th>Level</th><th>Label</th><th>Definition</th></tr></thead><tbody>{sev_rows}</tbody></table>
    </div>

    <div class="section">
        <h2>6. Probability scale {section_badge('probability_scale')}</h2>
        <table class="rac-table"><thead><tr><th>Level</th><th>Label</th><th>Definition</th></tr></thead><tbody>{prob_rows}</tbody></table>
    </div>

    <div class="section">
        <h2>7. Risk acceptability matrix {section_badge('risk_matrix')}</h2>
        {mat_html}
    </div>

    <div class="section">
        <h2>8. Criteria interpretation / decision rules {section_badge('decision_rules')}</h2>
        <div style="white-space: pre-line;">{report.get('decision_rules', {}).get('text', '')}</div>
    </div>

    <div class="section">
        <h2>9. Residual risk evaluation rules</h2>
        <div style="white-space: pre-line;">{report.get('residual_risk_rules', {}).get('text', '')}</div>
    </div>

    <div class="section">
        <h2>10. Benefit-risk analysis trigger criteria</h2>
        <div style="white-space: pre-line;">{report.get('benefit_risk_triggers', {}).get('text', '')}</div>
    </div>

    <div class="section">
        <h2>11. Risk control effectiveness expectations</h2>
        <p>{report.get('control_effectiveness_expectations', {}).get('text', '')}</p>
    </div>

    <div class="section">
        <h2>12. Overall residual risk</h2>
        <p>{report.get('overall_residual_risk', {}).get('text', '')}</p>
    </div>

    <div class="section">
        <h2>13. Roles and responsibilities</h2>
        <table class="rac-table"><thead><tr><th>Role</th><th>Name</th><th>Responsibility</th></tr></thead><tbody>{role_rows}</tbody></table>
    </div>

    <div class="section">
        <h2>14. Review and approval</h2>
        <p>Prepared by: {prepared_by} | Reviewed by: {reviewed_by} | Approved by: {approved_by}</p>
        <p>Signature / date: To be completed upon approval.</p>
        <h3>Version history</h3>
        <table class="rac-table">
        <thead><tr><th>Version</th><th>Date</th><th>Description of change</th><th>Author</th></tr></thead>
        <tbody>{version_rows}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>15. Traceability references</h2>
        <table class="rac-table"><thead><tr><th>Document</th><th>ID / Link</th><th>Status</th></tr></thead><tbody>{trace_rows}</tbody></table>
    </div>

    <div class="section">
        <h2>16. AI / automation transparency</h2>
        <p>{report.get('ai_transparency', {}).get('text', '')}</p>
    </div>

    <div class="manual-review">
        <h2>17. Required manual review items</h2>
        <ul>{manual_list if manual_list else '<li>None identified.</li>'}</ul>
    </div>

    <p style="margin-top: 32px; font-size: 0.9em; color: #6b7280;">SmartRisk — Risk Acceptability Criteria. ISO 14971. All content requires human review and approval.</p>
</body>
</html>"""
    return html
