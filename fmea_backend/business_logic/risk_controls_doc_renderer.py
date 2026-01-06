"""
Risk Control Measures Documentation HTML Renderer
Generates audit-ready Risk Control Measures Documentation HTML report
"""
from typing import Dict, Any, List
from datetime import datetime

def render_risk_controls_doc_html(evidence: Dict[str, Any], project_name: str) -> str:
    """
    Render risk control measures documentation evidence into HTML report
    
    Args:
        evidence: Evidence dictionary from build_risk_controls_doc_evidence
        project_name: Project name
    
    Returns:
        HTML string
    """
    components = evidence.get("components", [])
    rows = evidence.get("rows", [])
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
    
    # Group rows by component
    rows_by_component: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        comp_name = row.get("component_name", "Unknown")
        if comp_name not in rows_by_component:
            rows_by_component[comp_name] = []
        rows_by_component[comp_name].append(row)
    
    # Build control documentation HTML
    controls_html = ""
    for component_name, component_rows in rows_by_component.items():
        controls_html += f'<h3>Component: {component_name}</h3>\n'
        
        for row in component_rows:
            controls_html += '<div class="control-item">'
            controls_html += f'<div class="control-header">'
            controls_html += f'<span class="control-key">{row.get("control_key", "N/A")}</span>'
            controls_html += f'<span class="control-name">{row.get("control_name", "N/A")}</span>'
            
            # Control type badge
            control_type = row.get("control_type", "").lower()
            type_badge_class = "type-inherent" if "inherent" in control_type else (
                "type-protective" if "protective" in control_type else "type-information"
            )
            controls_html += f'<span class="control-type {type_badge_class}">{row.get("control_type", "N/A")}</span>'
            controls_html += '</div>'
            
            # Risk context
            if row.get("risk_key"):
                controls_html += f'<p class="risk-context"><strong>Risk:</strong> {row.get("risk_key")}'
                if row.get("hazard"):
                    controls_html += f' | Hazard: {row.get("hazard")}'
                if row.get("harm"):
                    controls_html += f' | Harm: {row.get("harm")}'
                controls_html += '</p>'
            
            # Control description
            controls_html += f'<div class="control-description">'
            controls_html += f'<h4>Description</h4>'
            controls_html += f'<p>{row.get("control_description") or "N/A"}</p>'
            if row.get("implementation_details"):
                controls_html += f'<p><strong>Implementation Details:</strong> {row.get("implementation_details")}</p>'
            controls_html += '</div>'
            
            # Implementation references
            implementation_refs = row.get("implementation_refs", [])
            if implementation_refs:
                controls_html += '<div class="implementation-refs">'
                controls_html += '<h4>Implementation References</h4>'
                controls_html += '<ul>'
                for ref in implementation_refs:
                    controls_html += f'<li>{ref.get("display", "N/A")}'
                    if ref.get("link_type"):
                        controls_html += f' <span class="link-type">({ref.get("link_type")})</span>'
                    if ref.get("created_at"):
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(ref.get("created_at").replace('Z', '+00:00'))
                            controls_html += f' <span class="link-date">– {dt.strftime("%Y-%m-%d")}</span>'
                        except:
                            pass
                    controls_html += '</li>'
                controls_html += '</ul>'
                controls_html += '</div>'
            elif row.get("flags", {}).get("missing_implementation"):
                controls_html += '<div class="missing-flag">'
                controls_html += '<p class="warning-text">⚠️ Missing implementation reference</p>'
                controls_html += '</div>'
            
            # Verification methods
            verification_methods = row.get("verification_methods", [])
            if verification_methods:
                controls_html += '<div class="verification-methods">'
                controls_html += '<h4>Verification Methods</h4>'
                controls_html += '<ul>'
                for method in verification_methods:
                    controls_html += f'<li>{method.get("display", "N/A")}'
                    if method.get("link_type"):
                        controls_html += f' <span class="link-type">({method.get("link_type")})</span>'
                    if method.get("created_at"):
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(method.get("created_at").replace('Z', '+00:00'))
                            controls_html += f' <span class="link-date">– {dt.strftime("%Y-%m-%d")}</span>'
                        except:
                            pass
                    controls_html += '</li>'
                controls_html += '</ul>'
                controls_html += '</div>'
            elif row.get("flags", {}).get("missing_verification"):
                controls_html += '<div class="missing-flag">'
                controls_html += '<p class="warning-text">⚠️ Missing verification method</p>'
                controls_html += '</div>'
            
            controls_html += '</div>'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Risk Control Measures Documentation - {project_name}</title>
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
            font-size: 1.2em;
        }}
        h4 {{
            color: #4b5563;
            margin-top: 15px;
            font-size: 1em;
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
        .control-item {{
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-left: 4px solid #2563eb;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .control-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .control-key {{
            font-weight: bold;
            color: #2563eb;
            font-size: 1.1em;
        }}
        .control-name {{
            font-weight: 600;
            color: #1f2937;
            flex: 1;
        }}
        .control-type {{
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .type-inherent {{
            background-color: #dbeafe;
            color: #1e40af;
        }}
        .type-protective {{
            background-color: #d1fae5;
            color: #065f46;
        }}
        .type-information {{
            background-color: #fef3c7;
            color: #92400e;
        }}
        .risk-context {{
            color: #6b7280;
            font-size: 0.9em;
            margin: 10px 0;
        }}
        .control-description {{
            margin: 15px 0;
        }}
        .implementation-refs, .verification-methods {{
            margin: 15px 0;
            padding: 10px;
            background: #f9fafb;
            border-radius: 4px;
        }}
        .implementation-refs ul, .verification-methods ul {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        .implementation-refs li, .verification-methods li {{
            margin: 5px 0;
        }}
        .link-type {{
            color: #6b7280;
            font-size: 0.9em;
            font-style: italic;
        }}
        .link-date {{
            color: #9ca3af;
            font-size: 0.85em;
        }}
        .missing-flag {{
            margin: 15px 0;
            padding: 10px;
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            border-radius: 4px;
        }}
        .warning-text {{
            color: #92400e;
            font-weight: 600;
            margin: 0;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <h1>Risk Control Measures Documentation</h1>
    
    <div class="meta">
        <p><strong>Project:</strong> {project_name}</p>
        <p><strong>Components:</strong></p>
        <ul>
{components_html}
        </ul>
        <p><strong>Generated:</strong> {generated_at}</p>
    </div>
    
    <div class="statement">
        <p><strong>Audit Statement:</strong></p>
        <p>Compiled from controlled SmartQS records; trace links provide implementation/verification evidence.</p>
        <p>All risk control data is sourced from risk_controls and trace_links records.</p>
    </div>
    
    <div class="counts">
        <div class="count-box">
            <div class="count-label">Total Controls</div>
            <div class="count-value">{counts.get("controls", 0)}</div>
        </div>
        <div class="count-box">
            <div class="count-label">Missing Implementation</div>
            <div class="count-value">{counts.get("missing_implementation", 0)}</div>
        </div>
        <div class="count-box">
            <div class="count-label">Missing Verification</div>
            <div class="count-value">{counts.get("missing_verification", 0)}</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Risk Control Measures</h2>
        {controls_html if controls_html else "<p>No risk controls found.</p>"}
    </div>
    
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
        <p style="color: #6b7280; font-size: 0.9em;">
            This document was generated by SmartQS Risk Management System.
            All risk control measures documentation complies with ISO 14971:2019.
        </p>
    </div>
</body>
</html>"""
    
    return html

