"""
Renders Risk Acceptability Criteria report dict as HTML.
"""
import re
from typing import Any, Dict, List


def _badge_class(source_type: str) -> str:
    if source_type in ("project_override", "approved_project"):
        return "badge-approved"
    if source_type == "org_default":
        return "badge-org"
    if source_type == "system_draft":
        return "badge-draft"
    if source_type == "ai_generated":
        return "badge-ai"
    if source_type == "system_default":
        return "badge-default"
    if source_type == "user_edited":
        return "badge-user"
    return "badge-placeholder"


def _badge_label(source_type: str) -> str:
    if source_type == "project_override":
        return "Project override"
    if source_type == "approved_project":
        return "Approved"
    if source_type == "org_default":
        return "Org default"
    if source_type == "system_draft":
        return "Draft"
    if source_type == "ai_generated":
        return "AI-generated"
    if source_type == "system_default":
        return "System default"
    if source_type == "user_edited":
        return "User edited"
    return "Needs review"


def render_risk_acceptability_criteria_html(report: Dict[str, Any]) -> str:
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

    def _display(value: Any, fallback: str = "Not assigned") -> str:
        if value is None:
            return fallback
        if isinstance(value, str) and not value.strip():
            return fallback
        return str(value)

    def _render_multiline(text: str) -> str:
        if not text:
            return ""
        lines = text.splitlines()
        out: List[str] = []
        para: List[str] = []
        in_list = False
        for raw in lines:
            line = raw.rstrip()
            stripped = line.strip()
            if stripped.startswith("- ") or stripped.startswith("• "):
                if para:
                    out.append(f"<p>{' '.join(para)}</p>")
                    para = []
                if not in_list:
                    out.append("<ul>")
                    in_list = True
                out.append(f"<li>{stripped[2:]}</li>")
            elif not line.strip():
                if para:
                    out.append(f"<p>{' '.join(para)}</p>")
                    para = []
                if in_list:
                    out.append("</ul>")
                    in_list = False
            else:
                if in_list:
                    out.append("</ul>")
                    in_list = False
                para.append(line.strip())
        if para:
            out.append(f"<p>{' '.join(para)}</p>")
        if in_list:
            out.append("</ul>")
        return "".join(out)

    def _source_line(section_key: str) -> str:
        section = report.get(section_key, {}) if isinstance(report.get(section_key, {}), dict) else {}
        src = section.get("source_type") or (report.get("source_metadata", {}) or {}).get(section_key, "placeholder")
        review = "Yes" if section.get("requires_human_review", False) else "No"
        approved_by = _display(section.get("approved_by"), "To be assigned")
        approval_status = "Approved" if src in ("project_override", "approved_project") else "Not approved"
        return (
            f'<div class="source-line"><strong>Source:</strong> {_badge_label(src)} | '
            f'<strong>Approval status:</strong> {approval_status} | '
            f'<strong>Human review required:</strong> {review} | '
            f'<strong>Approved by:</strong> {approved_by}</div>'
        )

    alarp_full = (
        report.get("alarp_terminology", {}).get("text")
        or report.get("terminology", {}).get("overrides", {}).get("ALARP")
        or "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)"
    )
    alarp_short = "ALARP"
    m = re.search(r"\(([^)]*)\)", alarp_full)
    if m:
        token = m.group(1).split("–")[0].strip()
        if token:
            alarp_short = token

    sev_scale = (report.get("severity_scale", {}) or {}).get("scale", [])
    sev_rows = ""
    if isinstance(sev_scale, list):
        for row in sev_scale:
            lvl = row.get("level", row.get("label", ""))
            lbl = row.get("label", "") if isinstance(row, dict) else str(row)
            defn = row.get("definition", "") if isinstance(row, dict) else ""
            sev_rows += f"<tr><td>{lvl}</td><td>{lbl}</td><td>{defn}</td></tr>\n"

    prob_scale = (report.get("probability_scale", {}) or {}).get("scale", [])
    prob_rows = ""
    if isinstance(prob_scale, list):
        for row in prob_scale:
            lvl = row.get("level", row.get("label", ""))
            lbl = row.get("label", "") if isinstance(row, dict) else str(row)
            defn = row.get("definition", "") if isinstance(row, dict) else ""
            prob_rows += f"<tr><td>{lvl}</td><td>{lbl}</td><td>{defn}</td></tr>\n"

    mat = report.get("risk_matrix", {}) or {}
    matrix_data = mat.get("matrix", [])
    if isinstance(matrix_data, dict) and "matrix" in matrix_data:
        matrix_data = matrix_data["matrix"]
    mat_html = ""
    if isinstance(matrix_data, list) and matrix_data:
        mat_html = "<table class=\"rac-table\"><thead><tr><th>Sev \\ Prob</th>"
        n_cols = len(matrix_data[0]) if isinstance(matrix_data[0], (list, tuple)) else 0
        for j in range(n_cols):
            mat_html += f"<th>{j + 1}</th>"
        mat_html += "</tr></thead><tbody>"
        for i, row in enumerate(matrix_data):
            mat_html += f"<tr><th>{i + 1}</th>"
            for cell in (row if isinstance(row, (list, tuple)) else [row]):
                val = str(cell)
                if val.strip().upper() == "ALARP":
                    val = alarp_short
                mat_html += f"<td>{val}</td>"
            mat_html += "</tr>"
        mat_html += "</tbody></table>"
    if mat.get("label"):
        mat_html = f"<p class=\"matrix-notice\">{mat.get('label')}</p>" + mat_html

    defs = (report.get("definitions", {}) or {}).get("items", {})
    def_rows = "".join([f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>\n" for k, v in (defs.items() if isinstance(defs, dict) else [])])

    roles = (report.get("roles_and_responsibilities", {}) or {}).get("roles", [])
    role_rows = "".join([f"<tr><td>{r.get('role','')}</td><td>{r.get('name','')}</td><td>{r.get('responsibility','')}</td></tr>\n" for r in roles])

    trace_root = report.get("traceability_references", {}) or {}
    trace = trace_root.get("items", trace_root) if isinstance(trace_root, dict) else {}
    trace_warnings = trace_root.get("warnings", []) if isinstance(trace_root, dict) else []
    trace_rows = ""
    for doc_name, info in (trace.items() if isinstance(trace, dict) else []):
        doc_id = info.get("id", "") if isinstance(info, dict) else ""
        status_val = info.get("status", "") if isinstance(info, dict) else ""
        updated = info.get("last_updated_at", "") if isinstance(info, dict) else ""
        ui_link = info.get("ui_link", "") if isinstance(info, dict) else ""
        id_or_link = f'<a href="{ui_link}">{doc_id}</a>' if ui_link and doc_id else (doc_id or "Not yet linked")
        trace_rows += f"<tr><td>{doc_name.replace('_',' ').title()}</td><td>{id_or_link}</td><td>{status_val or '—'}</td><td>{updated or '—'}</td></tr>\n"

    manual = report.get("manual_review_items", [])
    manual_list = ""
    for g in manual:
        msg = g.get("message", g.get("issue", ""))
        sec = g.get("section", "")
        if isinstance(msg, str) and isinstance(sec, str) and msg.lower().startswith(f"{sec.lower()}:"):
            msg = msg[len(sec) + 1 :].lstrip()
        manual_list += (
            f"<li><strong>{sec}:</strong> {msg}<br/><em>Why:</em> {g.get('why_it_matters','')}"
            f"<br/><em>Fix:</em> {g.get('where_to_fix','')}<br/><em>Approval effect:</em> {g.get('effect_on_approval_readiness','')}</li>\n"
        )

    readiness = report.get("readiness", {})
    readiness_html = f"""
    <div class="section readiness">
        <h2>Readiness indicators</h2>
        <p><strong>Completeness:</strong> {readiness.get('completeness_percentage', 0)}% |
        <strong>Approved content:</strong> {readiness.get('approved_content_percentage', 0)}% |
        <strong>Sections requiring review:</strong> {readiness.get('sections_requiring_manual_review', 0)} |
        <strong>Approval blockers:</strong> {len(readiness.get('blocked_approval_reasons', []) or [])}</p>
        <p>Readiness indicators are based on document completeness and review flags and do not indicate approval status.</p>
    </div>
    """

    rev = report.get("review_and_approval", {}) or {}
    prepared_by = _display(rev.get("prepared_by"), "To be assigned")
    reviewed_by = _display(rev.get("reviewed_by"), "To be assigned")
    approved_by = _display(rev.get("approved_by"), "To be assigned")
    version_history = rev.get("version_history") or []
    version_rows = ""
    for v in version_history:
        version_rows += f"<tr><td>{v.get('version','')}</td><td>{v.get('date','')}</td><td>{v.get('description','')}</td><td>{v.get('author','')}</td></tr>\n"
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
        .badge-default {{ background: #fef3c7; color: #78350f; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; }}
        .badge-user {{ background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; }}
        h1 {{ color: #1e40af; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }}
        h2 {{ color: #1e40af; margin-top: 24px; font-size: 1.1em; }}
        .section {{ margin: 16px 0; }}
        .readiness {{ background: #f5f5f4; border-left: 4px solid #a8a29e; padding: 12px; margin: 20px 0; }}
        .rac-table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.9em; }}
        .rac-table th, .rac-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .rac-table th {{ background: #f3f4f6; }}
        .matrix-notice {{ font-size: 0.9em; color: #92400e; margin-bottom: 8px; }}
        .meta {{ color: #6b7280; font-size: 0.9em; margin-bottom: 20px; }}
        .manual-review {{ background: #f5f5f4; border-left: 4px solid #a8a29e; padding: 12px; margin: 20px 0; }}
        .manual-review ul {{ margin: 8px 0; padding-left: 20px; }}
        .source-line {{ font-size: 0.85em; color: #4b5563; margin: 4px 0 10px 0; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="meta">
        <p><strong>Project:</strong> {project_name} | <strong>Project ID:</strong> {project_id}</p>
        <p><strong>Device:</strong> {device_name}</p>
        <p><strong>Intended use:</strong> {intended_use}</p>
        <p><strong>Status:</strong> {_display(status, "Draft")} | <strong>Version:</strong> {version}</p>
        <p><strong>Date generated:</strong> {_display(date_gen, "—")}</p>
        <p><strong>Author/source:</strong> {author_src}</p>
    </div>
    {readiness_html}

    <div class="section"><h2>1. Purpose</h2>{_source_line('purpose')}<p>{report.get('purpose', {}).get('text', '')}</p></div>
    <div class="section"><h2>2. Scope</h2>{_source_line('scope')}<p>{report.get('scope', {}).get('text', '')}</p></div>
    <div class="section"><h2>3. Regulatory / standards basis</h2>{_source_line('regulatory_basis')}<p>{report.get('regulatory_basis', {}).get('text', '')}</p></div>
    <div class="section"><h2>4. Definitions</h2>{_source_line('definitions')}<table class="rac-table"><thead><tr><th>Term</th><th>Definition</th></tr></thead><tbody>{def_rows}</tbody></table></div>
    <div class="section"><h2>5. Severity scale</h2>{_source_line('severity_scale')}<table class="rac-table"><thead><tr><th>Level</th><th>Label</th><th>Definition</th></tr></thead><tbody>{sev_rows}</tbody></table></div>
    <div class="section"><h2>6. Severity rationale</h2>{_source_line('severity_rationale')}{_render_multiline(report.get('severity_rationale', {}).get('text', report.get('severity_scale', {}).get('rationale', '')))}</div>
    <div class="section"><h2>7. Probability scale</h2>{_source_line('probability_scale')}<table class="rac-table"><thead><tr><th>Level</th><th>Label</th><th>Definition</th></tr></thead><tbody>{prob_rows}</tbody></table></div>
    <div class="section"><h2>8. Probability rationale</h2>{_source_line('probability_rationale')}{_render_multiline(report.get('probability_rationale', {}).get('text', report.get('probability_scale', {}).get('rationale', '')))}</div>
    <div class="section"><h2>9. ALARP terminology</h2>{_source_line('alarp_terminology')}<p>{alarp_full}</p></div>
    <div class="section"><h2>10. Risk acceptability matrix</h2><div class="source-line"><strong>Matrix source:</strong> {_badge_label(mat.get('source_type', 'system_draft'))}<br/><strong>Approval status:</strong> {"Approved" if mat.get('source_type') in ('project_override','approved_project') else 'Not approved'}<br/><strong>Human review required:</strong> {"Yes" if mat.get('requires_human_review', True) else "No"}<br/><strong>Approved by:</strong> {_display(mat.get('approved_by'), 'To be assigned')}</div>{mat_html}</div>
    <div class="section"><h2>11. Matrix rationale</h2>{_source_line('matrix_rationale')}{_render_multiline(report.get('matrix_rationale', {}).get('text', report.get('risk_matrix', {}).get('rationale', '')))}</div>
    <div class="section"><h2>12. Criteria interpretation / decision rules</h2>{_source_line('decision_rule_wording')}{_render_multiline(report.get('decision_rule_wording', {}).get('text', report.get('decision_rules', {}).get('text', '')))}</div>
    <div class="section"><h2>13. Decision rules rationale</h2>{_source_line('decision_rules_rationale')}{_render_multiline(report.get('decision_rules_rationale', {}).get('text', report.get('decision_rules', {}).get('rationale', '')))}</div>
    <div class="section"><h2>14. Residual risk evaluation rules</h2>{_render_multiline(report.get('residual_risk_rules', {}).get('text', ''))}</div>
    <div class="section"><h2>15. Benefit-risk analysis trigger criteria</h2>{_render_multiline(report.get('benefit_risk_triggers', {}).get('text', ''))}</div>
    <div class="section"><h2>16. Risk control effectiveness expectations</h2><p>{report.get('control_effectiveness_expectations', {}).get('text', '')}</p></div>
    <div class="section"><h2>17. Overall residual risk</h2><p>{report.get('overall_residual_risk', {}).get('text', '')}</p></div>
    <div class="section"><h2>18. Roles and responsibilities</h2><table class="rac-table"><thead><tr><th>Role</th><th>Name</th><th>Responsibility</th></tr></thead><tbody>{role_rows}</tbody></table></div>
    <div class="section"><h2>19. Review and approval</h2><p>Prepared by: {prepared_by} | Reviewed by: {reviewed_by} | Approved by: {approved_by}</p><p>Signature / date: To be completed upon approval.</p><h3>Version history</h3><table class="rac-table"><thead><tr><th>Version</th><th>Date</th><th>Description of change</th><th>Author</th></tr></thead><tbody>{version_rows}</tbody></table></div>
    <div class="section"><h2>20. Traceability references</h2><table class="rac-table"><thead><tr><th>Document</th><th>ID / Link</th><th>Status</th><th>Last Updated</th></tr></thead><tbody>{trace_rows}</tbody></table>{"<h3>Traceability validation warnings</h3><ul>" + "".join([f"<li>{w}</li>" for w in trace_warnings]) + "</ul>" if trace_warnings else ""}</div>
    <div class="section"><h2>21. AI / automation transparency</h2><p>{report.get('ai_transparency', {}).get('text', '')}</p></div>
    <div class="manual-review"><h2>22. Required manual review items</h2><ul>{manual_list if manual_list else '<li>None identified.</li>'}</ul></div>
    <p style="margin-top: 32px; font-size: 0.9em; color: #6b7280;">SmartRisk — Risk Acceptability Criteria. ISO 14971. All content requires human review and approval.</p>
</body>
</html>"""
    return html
