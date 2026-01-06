"""
Residual Risk Evaluation HTML Renderer
Generates audit-ready Residual Risk Evaluation HTML report
"""
from typing import Dict, Any, List
from datetime import datetime

def render_residual_risk_html(evidence: Dict[str, Any], project_name: str) -> str:
    """
    Render residual risk evaluation evidence into HTML report
    
    Args:
        evidence: Evidence dictionary from build_residual_risk_evidence
        project_name: Project name
    
    Returns:
        HTML string
    """
    components = evidence.get("components", [])
    rows = evidence.get("rows", [])
    version_scope = evidence.get("version_scope", "approved_only")
    thresholds = evidence.get("thresholds", {})
    missing_field_list = evidence.get("missing_field_list", [])
    counts = evidence.get("counts", {})
    generated_at = datetime.now().isoformat()
    
    # Build component list HTML
    components_html = ""
    if components:
        for comp in components:
            comp_name = comp.get("name", comp.get("id", "Unknown"))
            components_html += f"<li>{comp_name}</li>\n"
    else:
        components_html = "<li>All components</li>\n"
    
    # Version scope statement
    version_scope_statement = ""
    if version_scope == "approved_only":
        version_scope_statement = "Approved versions only"
    elif version_scope == "current":
        version_scope_statement = "Current versions only"
    else:
        version_scope_statement = "All versions"
    
    # Build thresholds HTML
    thresholds_html = ""
    for level, threshold in thresholds.items():
        min_score = threshold.get("min", 0)
        max_score = threshold.get("max", 100)
        acceptability = threshold.get("acceptability", "unknown")
        thresholds_html += f'<tr>'
        thresholds_html += f'<td>{level}</td>'
        thresholds_html += f'<td>{min_score}-{max_score}</td>'
        thresholds_html += f'<td>{acceptability}</td>'
        thresholds_html += '</tr>\n'
    
    # Group rows by component
    rows_by_component: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        comp_name = row.get("component_name", "Unknown")
        if comp_name not in rows_by_component:
            rows_by_component[comp_name] = []
        rows_by_component[comp_name].append(row)
    
    # Build table rows HTML
    table_rows_html = ""
    for component_name, component_rows in rows_by_component.items():
        table_rows_html += f'<h3>Component: {component_name}</h3>\n'
        table_rows_html += '<table>\n'
        table_rows_html += '<thead><tr>'
        table_rows_html += '<th>Risk Key</th>'
        table_rows_html += '<th>Version No</th>'
        table_rows_html += '<th>Residual Severity</th>'
        table_rows_html += '<th>Residual Probability of Harm</th>'
        table_rows_html += '<th>Residual Risk Score</th>'
        table_rows_html += '<th>Residual Acceptability</th>'
        table_rows_html += '<th>Acceptability Source</th>'
        table_rows_html += '<th>Approval Status</th>'
        table_rows_html += '</tr></thead>\n<tbody>\n'
        
        for row in component_rows:
            approval_status = "Approved" if row.get("approved") else "Draft"
            approval_badge_class = "approved" if row.get("approved") else "draft"
            acceptability_source = row.get("acceptability_source", "unknown")
            source_badge_class = "stored" if acceptability_source == "stored" else "inferred"
            
            table_rows_html += '<tr>'
            table_rows_html += f'<td>{row.get("risk_key", "N/A")}</td>'
            table_rows_html += f'<td>{row.get("version_no", "N/A")}</td>'
            table_rows_html += f'<td>{row.get("residual_severity") if row.get("residual_severity") is not None else "N/A"}</td>'
            table_rows_html += f'<td>{row.get("residual_probability_of_harm") if row.get("residual_probability_of_harm") is not None else "N/A"}</td>'
            table_rows_html += f'<td>{row.get("residual_risk_score") if row.get("residual_risk_score") is not None else "N/A"}</td>'
            table_rows_html += f'<td>{row.get("residual_acceptability", "N/A")}</td>'
            table_rows_html += f'<td><span class="{source_badge_class}">{acceptability_source}</span></td>'
            table_rows_html += f'<td><span class="{approval_badge_class}">{approval_status}</span></td>'
            table_rows_html += '</tr>\n'
        
        table_rows_html += '</tbody></table>\n'
    
    # Missing fields section
    missing_fields_html = ""
    if missing_field_list:
        missing_fields_html = '<div class="warning">'
        missing_fields_html += '<h3>Missing Residual Fields</h3>'
        missing_fields_html += '<p>The following risk versions are missing residual risk fields:</p>'
        missing_fields_html += '<ul>'
        for item in missing_field_list:
            missing_fields_html += f'<li>Risk {item.get("risk_key")} - Version {item.get("version_no")} (ID: {item.get("version_id", "")[:8]})</li>'
        missing_fields_html += '</ul>'
        missing_fields_html += '</div>'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Residual Risk Evaluation - {project_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #1e40af;
            margin-top: 30px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #374151;
            margin-top: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #f3f4f6;
            font-weight: bold;
        }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            background: #f9fafb;
            border-radius: 5px;
        }}
        .meta {{
            color: #6b7280;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .approved {{
            background-color: #d1fae5;
            color: #065f46;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .draft {{
            background-color: #fef3c7;
            color: #92400e;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .stored {{
            background-color: #dbeafe;
            color: #1e40af;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .inferred {{
            background-color: #f3f4f6;
            color: #374151;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .warning {{
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin: 20px 0;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        .statement {{
            background-color: #eff6ff;
            border-left: 4px solid #2563eb;
            padding: 15px;
            margin: 20px 0;
            font-style: italic;
        }}
        .counts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .count-box {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e5e7eb;
        }}
        .count-label {{
            font-size: 0.9em;
            color: #6b7280;
        }}
        .count-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #1f2937;
        }}
    </style>
</head>
<body>
    <h1>Residual Risk Evaluation</h1>
    
    <div class="meta">
        <p><strong>Project:</strong> {project_name}</p>
        <p><strong>Components:</strong></p>
        <ul>
{components_html}
        </ul>
        <p><strong>Version Scope:</strong> {version_scope_statement}</p>
        <p><strong>Generated:</strong> {generated_at}</p>
    </div>
    
    <div class="statement">
        <p><strong>Audit Statement:</strong></p>
        <p>This export is a point-in-time compilation of immutable SmartQS risk versions.</p>
        <p>All residual risk data is sourced from risk_item_versions records.</p>
    </div>
    
    <div class="counts">
        <div class="count-box">
            <div class="count-label">Versions Included</div>
            <div class="count-value">{counts.get("versions_included", 0)}</div>
        </div>
        <div class="count-box">
            <div class="count-label">Missing Residual Fields</div>
            <div class="count-value">{counts.get("missing_residual_fields", 0)}</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Acceptability Thresholds</h2>
        <p>The following thresholds are used to determine residual risk acceptability:</p>
        <table>
            <thead>
                <tr>
                    <th>Risk Level</th>
                    <th>Score Range</th>
                    <th>Acceptability</th>
                </tr>
            </thead>
            <tbody>
{thresholds_html}
            </tbody>
        </table>
        <p><em>Note: Acceptability values marked as "inferred" are calculated using these thresholds. Values marked as "stored" come directly from the risk version record.</em></p>
    </div>
    
    {missing_fields_html}
    
    <div class="section">
        <h2>Residual Risk Evaluation</h2>
        {table_rows_html if table_rows_html else "<p>No residual risk data found.</p>"}
    </div>
    
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
        <p style="color: #6b7280; font-size: 0.9em;">
            This document was generated by SmartQS Risk Management System.
            All residual risk evaluation data complies with ISO 14971:2019.
        </p>
    </div>
</body>
</html>"""
    
    return html

