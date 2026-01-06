"""
RMF HTML Renderer
Generates audit-ready Risk Management File HTML report with all ISO 14971 sections
"""
from typing import Dict, Any, List
from datetime import datetime

def render_rmf_html(evidence: Dict[str, Any], project_name: str) -> str:
    """
    Render RMF evidence into HTML report
    
    Args:
        evidence: Evidence dictionary from build_rmf_evidence
        project_name: Project name
    
    Returns:
        HTML string
    """
    components = evidence.get("components", [])
    risks = evidence.get("risks", [])
    generated_at = datetime.now().isoformat()
    
    # Build component list HTML
    components_html = ""
    if components:
        for comp in components:
            comp_name = comp.get("name", comp.get("id", "Unknown"))
            components_html += f"<li>{comp_name}</li>\n"
    else:
        components_html = "<li>All components</li>\n"
    
    # Build risks HTML by section
    hazard_identification_html = build_hazard_identification_section(risks)
    risk_estimation_html = build_risk_estimation_section(risks)
    risk_evaluation_html = build_risk_evaluation_section(risks)
    risk_controls_html = build_risk_controls_section(risks)
    residual_risk_html = build_residual_risk_section(risks)
    benefit_risk_html = build_benefit_risk_section(risks)
    acceptability_html = build_acceptability_decisions_section(risks)
    approvals_html = build_approvals_section(risks)
    traceability_html = build_traceability_section(risks)
    ai_events_html = build_ai_events_section(risks)
    audit_log_html = build_audit_log_section(risks)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Risk Management File - {project_name}</title>
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
        .risk-item {{
            margin: 20px 0;
            padding: 15px;
            background: white;
            border-left: 4px solid #2563eb;
            border-radius: 4px;
        }}
        .risk-key {{
            font-weight: bold;
            color: #2563eb;
            font-size: 1.1em;
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
    </style>
</head>
<body>
    <h1>Risk Management File (RMF)</h1>
    
    <div class="meta">
        <p><strong>Project:</strong> {project_name}</p>
        <p><strong>Components:</strong></p>
        <ul>
{components_html}
        </ul>
        <p><strong>Generated:</strong> {generated_at}</p>
    </div>
    
    <div class="statement">
        <p><strong>System of Record Statement:</strong></p>
        <p>SmartQS is the system of record for the Risk Management File.</p>
        <p>This export is a point-in-time compilation of RMF evidence derived from controlled SmartQS records.</p>
    </div>
    
    <div class="section">
        <h2>1. Hazard Identification</h2>
{hazard_identification_html}
    </div>
    
    <div class="section">
        <h2>2. Risk Estimation</h2>
{risk_estimation_html}
    </div>
    
    <div class="section">
        <h2>3. Risk Evaluation</h2>
{risk_evaluation_html}
    </div>
    
    <div class="section">
        <h2>4. Risk Control Measures</h2>
{risk_controls_html}
    </div>
    
    <div class="section">
        <h2>5. Residual Risk Evaluation</h2>
{residual_risk_html}
    </div>
    
    <div class="section">
        <h2>6. Benefit-Risk Analysis</h2>
{benefit_risk_html}
    </div>
    
    <div class="section">
        <h2>7. Risk Acceptability Decisions</h2>
{acceptability_html}
    </div>
    
    <div class="section">
        <h2>8. Review and Approval Records</h2>
{approvals_html}
    </div>
    
    <div class="section">
        <h2>9. Traceability</h2>
{traceability_html}
    </div>
    
    <div class="section">
        <h2>10. AI Usage & Disposition</h2>
{ai_events_html}
    </div>
    
    <div class="section">
        <h2>11. Audit Log Evidence</h2>
{audit_log_html}
    </div>
    
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
        <p style="color: #6b7280; font-size: 0.9em;">
            This document was generated by SmartQS Risk Management System.
            All risk management activities comply with ISO 14971:2019.
        </p>
    </div>
</body>
</html>"""
    
    return html

def build_hazard_identification_section(risks: List[Dict[str, Any]]) -> str:
    """Build hazard identification section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        current_version = risk.get("current_version")
        versions = risk.get("versions", [])
        
        html += f'<div class="risk-item">'
        html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
        
        if current_version:
            html += f'<h3>Current Version (v{current_version.get("version_number", "?")})</h3>'
            html += '<table>'
            html += f'<tr><th>Hazard</th><td>{current_version.get("hazard") or "N/A"}</td></tr>'
            html += f'<tr><th>Hazardous Situation</th><td>{current_version.get("hazardous_situation") or "N/A"}</td></tr>'
            html += f'<tr><th>Harm</th><td>{current_version.get("harm") or "N/A"}</td></tr>'
            html += f'<tr><th>Sequence of Events</th><td>{current_version.get("sequence_of_events") or "N/A"}</td></tr>'
            html += f'<tr><th>Failure Mode</th><td>{current_version.get("failure_mode") or "N/A"}</td></tr>'
            html += '</table>'
        
        # Show all versions if multiple
        if len(versions) > 1:
            html += '<h3>Version History</h3>'
            for version in versions:
                approved_badge = '<span class="approved">APPROVED</span>' if version.get("is_approved") else '<span class="draft">DRAFT</span>'
                html += f'<h4>Version {version["version_number"]} {approved_badge}</h4>'
                html += '<table>'
                html += f'<tr><th>Hazard</th><td>{version.get("hazard") or "N/A"}</td></tr>'
                html += f'<tr><th>Hazardous Situation</th><td>{version.get("hazardous_situation") or "N/A"}</td></tr>'
                html += f'<tr><th>Harm</th><td>{version.get("harm") or "N/A"}</td></tr>'
                html += '</table>'
        
        html += '</div>'
    
    return html if html else "<p>No risk items found.</p>"

def build_risk_estimation_section(risks: List[Dict[str, Any]]) -> str:
    """Build risk estimation section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        current_version = risk.get("current_version")
        versions = risk.get("versions", [])
        
        html += f'<div class="risk-item">'
        html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
        
        if current_version:
            html += f'<h3>Current Version (v{current_version.get("version_number", "?")})</h3>'
            html += '<table>'
            html += f'<tr><th>Severity</th><td>{current_version.get("severity") or "N/A"}</td></tr>'
            html += f'<tr><th>Probability of Harm</th><td>{current_version.get("probability_of_harm") or "N/A"}</td></tr>'
            html += f'<tr><th>Risk Score</th><td>{current_version.get("risk_score") or "N/A"}</td></tr>'
            html += '</table>'
        
        # Show all versions
        if len(versions) > 1:
            html += '<h3>Version History</h3>'
            for version in versions:
                approved_badge = '<span class="approved">APPROVED</span>' if version.get("is_approved") else '<span class="draft">DRAFT</span>'
                html += f'<h4>Version {version["version_number"]} {approved_badge}</h4>'
                html += '<table>'
                html += f'<tr><th>Severity</th><td>{version.get("severity") or "N/A"}</td></tr>'
                html += f'<tr><th>Probability of Harm</th><td>{version.get("probability_of_harm") or "N/A"}</td></tr>'
                html += f'<tr><th>Risk Score</th><td>{version.get("risk_score") or "N/A"}</td></tr>'
                html += '</table>'
        
        html += '</div>'
    
    return html if html else "<p>No risk items found.</p>"

def build_risk_evaluation_section(risks: List[Dict[str, Any]]) -> str:
    """Build risk evaluation section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        current_version = risk.get("current_version")
        versions = risk.get("versions", [])
        
        html += f'<div class="risk-item">'
        html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
        
        if current_version:
            html += f'<h3>Current Version (v{current_version.get("version_number", "?")})</h3>'
            html += '<table>'
            html += f'<tr><th>Risk Acceptability</th><td>{current_version.get("risk_acceptability") or "N/A"}</td></tr>'
            html += f'<tr><th>Risk Rationale</th><td>{current_version.get("risk_rationale") or "N/A"}</td></tr>'
            html += '</table>'
        
        # Show all versions
        for version in versions:
            approved_badge = '<span class="approved">APPROVED</span>' if version.get("is_approved") else '<span class="draft">DRAFT</span>'
            html += f'<h4>Version {version["version_number"]} {approved_badge}</h4>'
            html += '<table>'
            html += f'<tr><th>Risk Acceptability</th><td>{version.get("risk_acceptability") or "N/A"}</td></tr>'
            html += f'<tr><th>Risk Rationale</th><td>{version.get("risk_rationale") or "N/A"}</td></tr>'
            html += '</table>'
        
        html += '</div>'
    
    return html if html else "<p>No risk items found.</p>"

def build_risk_controls_section(risks: List[Dict[str, Any]]) -> str:
    """Build risk controls section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        controls = risk.get("controls", [])
        
        html += f'<div class="risk-item">'
        html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
        
        if controls:
            html += '<table>'
            html += '<tr><th>Control Key</th><th>Name</th><th>Type</th><th>Status</th><th>Description</th></tr>'
            for control in controls:
                html += f'<tr>'
                html += f'<td>{control.get("control_key") or "N/A"}</td>'
                html += f'<td>{control.get("control_name") or "N/A"}</td>'
                html += f'<td>{control.get("control_type") or "N/A"}</td>'
                html += f'<td>{control.get("status") or "N/A"}</td>'
                html += f'<td>{control.get("control_description") or "N/A"}</td>'
                html += '</tr>'
            html += '</table>'
        else:
            html += '<p>No risk controls defined.</p>'
        
        html += '</div>'
    
    return html if html else "<p>No risk items found.</p>"

def build_residual_risk_section(risks: List[Dict[str, Any]]) -> str:
    """Build residual risk evaluation section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        current_version = risk.get("current_version")
        versions = risk.get("versions", [])
        
        html += f'<div class="risk-item">'
        html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
        
        if current_version:
            html += f'<h3>Current Version (v{current_version.get("version_number", "?")})</h3>'
            html += '<table>'
            html += f'<tr><th>Residual Severity</th><td>{current_version.get("residual_severity") or "N/A"}</td></tr>'
            html += f'<tr><th>Residual Probability of Harm</th><td>{current_version.get("residual_probability_of_harm") or "N/A"}</td></tr>'
            html += f'<tr><th>Residual Risk Score</th><td>{current_version.get("residual_risk_score") or "N/A"}</td></tr>'
            html += '</table>'
        
        # Show all versions
        for version in versions:
            if version.get("residual_severity") or version.get("residual_risk_score"):
                approved_badge = '<span class="approved">APPROVED</span>' if version.get("is_approved") else '<span class="draft">DRAFT</span>'
                html += f'<h4>Version {version["version_number"]} {approved_badge}</h4>'
                html += '<table>'
                html += f'<tr><th>Residual Severity</th><td>{version.get("residual_severity") or "N/A"}</td></tr>'
                html += f'<tr><th>Residual Probability of Harm</th><td>{version.get("residual_probability_of_harm") or "N/A"}</td></tr>'
                html += f'<tr><th>Residual Risk Score</th><td>{version.get("residual_risk_score") or "N/A"}</td></tr>'
                html += '</table>'
        
        html += '</div>'
    
    return html if html else "<p>No residual risk data found.</p>"

def build_benefit_risk_section(risks: List[Dict[str, Any]]) -> str:
    """Build benefit-risk analysis section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        current_version = risk.get("current_version")
        versions = risk.get("versions", [])
        
        # Only include if benefit-risk data exists
        has_benefit_risk = False
        if current_version and (current_version.get("benefit_risk_summary") or current_version.get("overall_residual_risk_conclusion")):
            has_benefit_risk = True
        
        if not has_benefit_risk:
            for version in versions:
                if version.get("benefit_risk_summary") or version.get("overall_residual_risk_conclusion"):
                    has_benefit_risk = True
                    break
        
        if has_benefit_risk:
            html += f'<div class="risk-item">'
            html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
            
            if current_version:
                html += f'<h3>Current Version (v{current_version.get("version_number", "?")})</h3>'
                html += '<table>'
                html += f'<tr><th>Benefit-Risk Summary</th><td>{current_version.get("benefit_risk_summary") or "N/A"}</td></tr>'
                html += f'<tr><th>Overall Residual Risk Conclusion</th><td>{current_version.get("overall_residual_risk_conclusion") or "N/A"}</td></tr>'
                html += '</table>'
            
            # Show all versions with benefit-risk data
            for version in versions:
                if version.get("benefit_risk_summary") or version.get("overall_residual_risk_conclusion"):
                    approved_badge = '<span class="approved">APPROVED</span>' if version.get("is_approved") else '<span class="draft">DRAFT</span>'
                    html += f'<h4>Version {version["version_number"]} {approved_badge}</h4>'
                    html += '<table>'
                    html += f'<tr><th>Benefit-Risk Summary</th><td>{version.get("benefit_risk_summary") or "N/A"}</td></tr>'
                    html += f'<tr><th>Overall Residual Risk Conclusion</th><td>{version.get("overall_residual_risk_conclusion") or "N/A"}</td></tr>'
                    html += '</table>'
            
            html += '</div>'
    
    return html if html else "<p>No benefit-risk analyses found.</p>"

def build_acceptability_decisions_section(risks: List[Dict[str, Any]]) -> str:
    """Build risk acceptability decisions section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        versions = risk.get("versions", [])
        
        html += f'<div class="risk-item">'
        html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
        
        for version in versions:
            approved_badge = '<span class="approved">APPROVED</span>' if version.get("is_approved") else '<span class="draft">NOT APPROVED</span>'
            html += f'<h4>Version {version["version_number"]} {approved_badge}</h4>'
            html += '<table>'
            html += f'<tr><th>Risk Acceptability</th><td>{version.get("risk_acceptability") or "N/A"}</td></tr>'
            html += f'<tr><th>Rationale</th><td>{version.get("risk_rationale") or "N/A"}</td></tr>'
            html += '</table>'
        
        html += '</div>'
    
    return html if html else "<p>No risk items found.</p>"

def build_approvals_section(risks: List[Dict[str, Any]]) -> str:
    """Build review and approval records section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        approvals = risk.get("approvals", [])
        
        html += f'<div class="risk-item">'
        html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
        
        if approvals:
            for version_approvals in approvals:
                version_id = version_approvals.get("version_id")
                approval_list = version_approvals.get("approvals", [])
                
                if approval_list:
                    html += f'<h4>Version {version_id}</h4>'
                    html += '<table>'
                    html += '<tr><th>Approver ID</th><th>Status</th><th>Comment</th><th>Timestamp</th></tr>'
                    for approval in approval_list:
                        html += f'<tr>'
                        html += f'<td>{approval.get("approver_id") or "N/A"}</td>'
                        html += f'<td>{approval.get("status") or "N/A"}</td>'
                        html += f'<td>{approval.get("comment") or "N/A"}</td>'
                        html += f'<td>{approval.get("timestamp") or "N/A"}</td>'
                        html += '</tr>'
                    html += '</table>'
        else:
            html += '<p>No approvals recorded.</p>'
        
        html += '</div>'
    
    return html if html else "<p>No approval records found.</p>"

def build_traceability_section(risks: List[Dict[str, Any]]) -> str:
    """Build traceability section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        links = risk.get("links", [])
        
        html += f'<div class="risk-item">'
        html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
        
        if links:
            html += '<table>'
            html += '<tr><th>From</th><th>To</th><th>Link Type</th><th>Rationale</th></tr>'
            for link in links:
                html += f'<tr>'
                html += f'<td>{link.get("from_type")} ({link.get("from_id", "")[:8]})</td>'
                html += f'<td>{link.get("to_type")} ({link.get("to_id", "")[:8]})</td>'
                html += f'<td>{link.get("link_type") or "N/A"}</td>'
                html += f'<td>{link.get("rationale") or "N/A"}</td>'
                html += '</tr>'
            html += '</table>'
        else:
            html += '<p>No trace links found.</p>'
        
        html += '</div>'
    
    return html if html else "<p>No traceability data found.</p>"

def build_ai_events_section(risks: List[Dict[str, Any]]) -> str:
    """Build AI usage & disposition section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        ai_events = risk.get("ai_events", [])
        
        if ai_events:
            html += f'<div class="risk-item">'
            html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
            
            html += '<table>'
            html += '<tr><th>Prompt</th><th>Disposition</th><th>Notes</th><th>Timestamp</th></tr>'
            for event in ai_events:
                html += f'<tr>'
                html += f'<td>{event.get("prompt_name") or "N/A"}</td>'
                html += f'<td>{event.get("disposition") or "N/A"}</td>'
                html += f'<td>{event.get("disposition_notes") or "N/A"}</td>'
                html += f'<td>{event.get("created_at") or "N/A"}</td>'
                html += '</tr>'
            html += '</table>'
            html += '</div>'
    
    return html if html else "<p>No AI events found.</p>"

def build_audit_log_section(risks: List[Dict[str, Any]]) -> str:
    """Build audit log evidence section"""
    html = ""
    for risk in risks:
        risk_item = risk["risk_item"]
        audit_events = risk.get("audit_events", [])
        
        if audit_events:
            html += f'<div class="risk-item">'
            html += f'<div class="risk-key">{risk_item.get("risk_key", risk_item["id"][:8])}: {risk_item["title"]}</div>'
            
            html += '<table>'
            html += '<tr><th>Event Type</th><th>Details</th><th>Timestamp</th></tr>'
            for event in audit_events:
                details = event.get("details_json", {})
                details_str = str(details) if details else "N/A"
                html += f'<tr>'
                html += f'<td>{event.get("event_type") or "N/A"}</td>'
                html += f'<td>{details_str}</td>'
                html += f'<td>{event.get("created_at") or "N/A"}</td>'
                html += '</tr>'
            html += '</table>'
            html += '</div>'
    
    return html if html else "<p>No audit log events found.</p>"

