"""
Hazard Analysis HTML Renderer
Generates audit-ready Hazard Analysis HTML report with ISO 14971 chain fields
"""
from typing import Dict, Any, List
from datetime import datetime as dt_datetime

def render_hazard_analysis_html(evidence: Dict[str, Any], project_name: str) -> str:
    """
    Render hazard analysis evidence into HTML report
    
    Args:
        evidence: Evidence dictionary from build_hazard_analysis
        project_name: Project name
    
    Returns:
        HTML string
    """
    components = evidence.get("components", [])
    rows = evidence.get("rows", [])
    version_scope = evidence.get("version_scope", "approved_only")
    include_unapproved = evidence.get("include_unapproved", False)
    counts = evidence.get("counts", {})
    generated_at = dt_datetime.now().isoformat()
    
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
        if include_unapproved:
            version_scope_statement += " (includes unapproved entries marked as Draft)"
    elif version_scope == "current":
        version_scope_statement = "Current versions only"
    else:
        version_scope_statement = "All versions"
    
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
        table_rows_html += '<th>Hazard</th>'
        table_rows_html += '<th>Hazardous Situation</th>'
        table_rows_html += '<th>Harm</th>'
        table_rows_html += '<th>Sequence of Events</th>'
        table_rows_html += '<th>Failure Mode</th>'
        table_rows_html += '<th>Approval Status</th>'
        table_rows_html += '<th>Approved By/At</th>'
        table_rows_html += '</tr></thead>\n<tbody>\n'
        
        for row in component_rows:
            approval_status = "Approved" if row.get("approved") else "Draft"
            approval_badge_class = "approved" if row.get("approved") else "draft"
            approved_info = ""
            if row.get("approved"):
                approved_by = row.get("approved_by", "N/A")
                approved_at = row.get("approved_at", "N/A")
                if approved_at and approved_at != "N/A":
                    try:
                        dt = dt_datetime.fromisoformat(approved_at.replace('Z', '+00:00'))
                        approved_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                approved_info = f"{approved_by}<br/>{approved_at}"
            else:
                approved_info = "N/A"
            
            table_rows_html += '<tr>'
            table_rows_html += f'<td>{row.get("risk_key", "N/A")}</td>'
            table_rows_html += f'<td>{row.get("version_no", "N/A")}</td>'
            table_rows_html += f'<td>{row.get("hazard") or "N/A"}</td>'
            table_rows_html += f'<td>{row.get("hazardous_situation") or "N/A"}</td>'
            table_rows_html += f'<td>{row.get("harm") or "N/A"}</td>'
            table_rows_html += f'<td>{row.get("sequence_of_events") or "N/A"}</td>'
            table_rows_html += f'<td>{row.get("failure_mode") or "N/A"}</td>'
            table_rows_html += f'<td><span class="{approval_badge_class}">{approval_status}</span></td>'
            table_rows_html += f'<td>{approved_info}</td>'
            table_rows_html += '</tr>\n'
        
        table_rows_html += '</tbody></table>\n'
    
    # Warning for unapproved entries
    unapproved_warning = ""
    if include_unapproved and version_scope == "approved_only":
        unapproved_warning = """
        <div class="warning">
            <p><strong>⚠️ Includes Draft (Unapproved) Entries</strong></p>
            <p>This report includes risk versions that have not been approved. Draft entries are marked accordingly.</p>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hazard Analysis - {project_name}</title>
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
    <h1>Hazard Analysis</h1>
    
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
        <p>All data is sourced from risk_item_versions records, which are immutable once created.</p>
    </div>
    
    {unapproved_warning}
    
    <div class="counts">
        <div class="count-box">
            <div class="count-label">Risk Items</div>
            <div class="count-value">{counts.get("risk_items", 0)}</div>
        </div>
        <div class="count-box">
            <div class="count-label">Versions Included</div>
            <div class="count-value">{counts.get("versions_included", 0)}</div>
        </div>
        <div class="count-box">
            <div class="count-label">Unapproved Excluded</div>
            <div class="count-value">{counts.get("unapproved_excluded", 0)}</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Hazard Analysis</h2>
        {table_rows_html if table_rows_html else "<p>No hazard analysis data found.</p>"}
    </div>
    
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
        <p style="color: #6b7280; font-size: 0.9em;">
            This document was generated by SmartQS Risk Management System.
            All hazard analysis data complies with ISO 14971:2019.
        </p>
    </div>
</body>
</html>"""
    
    return html

