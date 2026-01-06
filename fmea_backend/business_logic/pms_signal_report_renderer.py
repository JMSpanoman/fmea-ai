"""
PMS Signal Feedback Report HTML Renderer
Generates audit-ready PMS Signal Feedback Report HTML document
"""
from typing import Dict, Any, List
from datetime import datetime

def render_pms_signal_feedback_html(evidence: Dict[str, Any], project_name: str) -> str:
    """
    Render PMS signal feedback evidence into HTML report
    
    Args:
        evidence: Evidence dictionary from build_pms_signal_feedback_evidence
        project_name: Project name
    
    Returns:
        HTML string
    """
    components = evidence.get("components", [])
    signals = evidence.get("signals", [])
    summary = evidence.get("summary", {})
    gaps = evidence.get("gaps", {})
    date_from = evidence.get("date_from")
    date_to = evidence.get("date_to")
    generated_at = datetime.now().isoformat()
    
    # Build component list HTML
    components_html = ""
    if components:
        for comp in components:
            comp_name = comp.get("name", comp.get("id", "Unknown"))
            components_html += f"<li>{comp_name}</li>\n"
    else:
        components_html = "<li>All components</li>\n"
    
    # Date range display
    date_range_html = ""
    if date_from or date_to:
        date_range_html = "<p><strong>Date Range:</strong> "
        if date_from:
            date_range_html += f"From {date_from[:10]} "
        if date_to:
            date_range_html += f"To {date_to[:10]}"
        date_range_html += "</p>"
    
    # Executive Summary
    summary_html = f"""
    <div class="summary-grid">
        <div class="summary-box">
            <div class="summary-label">Total Signals</div>
            <div class="summary-value">{summary.get("total_signals", 0)}</div>
        </div>
        <div class="summary-box">
            <div class="summary-label">Under Review</div>
            <div class="summary-value">{summary.get("signals_under_review", 0)}</div>
        </div>
        <div class="summary-box">
            <div class="summary-label">Confirmed Trends</div>
            <div class="summary-value">{summary.get("signals_confirmed", 0)}</div>
        </div>
        <div class="summary-box">
            <div class="summary-label">Triggered Risk Review</div>
            <div class="summary-value">{summary.get("signals_triggered_risk", 0)}</div>
        </div>
        <div class="summary-box">
            <div class="summary-label">Resulted in CAPA</div>
            <div class="summary-value">{summary.get("signals_resulted_capa", 0)}</div>
        </div>
        <div class="summary-box">
            <div class="summary-label">Resulted in Change</div>
            <div class="summary-value">{summary.get("signals_resulted_change", 0)}</div>
        </div>
        <div class="summary-box warning">
            <div class="summary-label">Missing Risk Link</div>
            <div class="summary-value">{summary.get("signals_no_risk_link", 0)}</div>
        </div>
    </div>
    """
    
    # Signal Register Table
    signal_table_html = ""
    if signals:
        signal_table_html = '<table class="signal-table">'
        signal_table_html += '<thead><tr>'
        signal_table_html += '<th>Signal Key</th>'
        signal_table_html += '<th>Type</th>'
        signal_table_html += '<th>Components</th>'
        signal_table_html += '<th>Date Detected</th>'
        signal_table_html += '<th>Trend Status</th>'
        signal_table_html += '<th>Trigger Status</th>'
        signal_table_html += '<th>Linked Risks</th>'
        signal_table_html += '<th>Linked CAPAs</th>'
        signal_table_html += '<th>Linked Changes</th>'
        signal_table_html += '<th>Status</th>'
        signal_table_html += '</tr></thead><tbody>'
        
        for signal_data in signals:
            signal = signal_data["signal"]
            links = signal_data["links"]
            
            risk_links = ", ".join([link["display"] for link in links["risk_items"]]) or "None"
            capa_links = ", ".join([link["display"] for link in links["capas"]]) or "None"
            change_links = ", ".join([link["display"] for link in links["change_controls"]]) or "None"
            
            components_str = ", ".join(signal.get("component_names", [])) or "N/A"
            date_detected = signal.get("date_detected", "")[:10] if signal.get("date_detected") else "N/A"
            
            trend_badge_class = {
                "none": "badge-neutral",
                "under_review": "badge-warning",
                "confirmed": "badge-danger",
                "false_alarm": "badge-success"
            }.get(signal.get("trend_status", "").lower(), "badge-neutral")
            
            trigger_badge_class = {
                "not_triggered": "badge-neutral",
                "risk_review_required": "badge-warning",
                "capa_required": "badge-danger",
                "change_required": "badge-danger"
            }.get(signal.get("trigger_status", "").lower(), "badge-neutral")
            
            status_badge_class = {
                "open": "badge-warning",
                "investigating": "badge-info",
                "closed": "badge-success"
            }.get(signal.get("status", "").lower(), "badge-neutral")
            
            signal_table_html += '<tr>'
            signal_table_html += f'<td>{signal.get("signal_key", "N/A")}</td>'
            signal_table_html += f'<td>{signal.get("signal_type", "N/A")}</td>'
            signal_table_html += f'<td>{components_str}</td>'
            signal_table_html += f'<td>{date_detected}</td>'
            signal_table_html += f'<td><span class="badge {trend_badge_class}">{signal.get("trend_status", "N/A")}</span></td>'
            signal_table_html += f'<td><span class="badge {trigger_badge_class}">{signal.get("trigger_status", "N/A")}</span></td>'
            signal_table_html += f'<td>{risk_links}</td>'
            signal_table_html += f'<td>{capa_links}</td>'
            signal_table_html += f'<td>{change_links}</td>'
            signal_table_html += f'<td><span class="badge {status_badge_class}">{signal.get("status", "N/A")}</span></td>'
            signal_table_html += '</tr>'
        
        signal_table_html += '</tbody></table>'
    else:
        signal_table_html = "<p>No signals found for the selected criteria.</p>"
    
    # Trend Detection Section
    confirmed_trends = [s for s in signals if s["signal"].get("trend_status") == "confirmed"]
    trends_html = ""
    if confirmed_trends:
        trends_html = '<div class="section">'
        trends_html += '<h2>Trend Detection</h2>'
        trends_html += '<table class="trend-table">'
        trends_html += '<thead><tr>'
        trends_html += '<th>Signal Key</th>'
        trends_html += '<th>Title</th>'
        trends_html += '<th>Frequency Observed</th>'
        trends_html += '<th>Rate Observed</th>'
        trends_html += '<th>Rationale</th>'
        trends_html += '</tr></thead><tbody>'
        
        for signal_data in confirmed_trends:
            signal = signal_data["signal"]
            trends_html += '<tr>'
            trends_html += f'<td>{signal.get("signal_key", "N/A")}</td>'
            trends_html += f'<td>{signal.get("title", "N/A")}</td>'
            trends_html += f'<td>{signal.get("frequency_observed") or "N/A"}</td>'
            trends_html += f'<td>{signal.get("rate_observed") or "N/A"}</td>'
            trends_html += f'<td>{signal.get("description") or "N/A"}</td>'
            trends_html += '</tr>'
        
        trends_html += '</tbody></table>'
        trends_html += '</div>'
    
    # Risk Re-evaluation Triggers Section
    triggered_signals = [s for s in signals if s["signal"].get("trigger_status") != "not_triggered"]
    triggers_html = ""
    if triggered_signals:
        triggers_html = '<div class="section">'
        triggers_html += '<h2>Risk Re-evaluation Triggers</h2>'
        
        for signal_data in triggered_signals:
            signal = signal_data["signal"]
            links = signal_data["links"]
            
            triggers_html += '<div class="trigger-item">'
            triggers_html += f'<h3>{signal.get("signal_key")} – {signal.get("title")}</h3>'
            triggers_html += f'<p><strong>Trigger Status:</strong> {signal.get("trigger_status")}</p>'
            triggers_html += f'<p><strong>Recommended Action:</strong> {signal.get("recommended_action") or "N/A"}</p>'
            
            if links["risk_items"]:
                triggers_html += '<p><strong>Linked Risk Items:</strong></p><ul>'
                for risk in links["risk_items"]:
                    triggers_html += f'<li>{risk["display"]}</li>'
                triggers_html += '</ul>'
            
            if links["capas"]:
                triggers_html += '<p><strong>Resulting CAPAs:</strong></p><ul>'
                for capa in links["capas"]:
                    triggers_html += f'<li>{capa["display"]}</li>'
                triggers_html += '</ul>'
            
            if links["change_controls"]:
                triggers_html += '<p><strong>Resulting Changes:</strong></p><ul>'
                for change in links["change_controls"]:
                    triggers_html += f'<li>{change["display"]}</li>'
                triggers_html += '</ul>'
            
            triggers_html += '</div>'
        
        triggers_html += '</div>'
    
    # Actions Taken Section
    actions_html = ""
    signals_with_actions = [s for s in signals if s["links"]["capas"] or s["links"]["change_controls"]]
    if signals_with_actions:
        actions_html = '<div class="section">'
        actions_html += '<h2>Actions Taken (CAPA / Change)</h2>'
        
        for signal_data in signals_with_actions:
            signal = signal_data["signal"]
            links = signal_data["links"]
            
            actions_html += '<div class="action-item">'
            actions_html += f'<h3>{signal.get("signal_key")} – {signal.get("title")}</h3>'
            
            if links["capas"]:
                actions_html += '<p><strong>CAPAs Created:</strong></p><ul>'
                for capa in links["capas"]:
                    actions_html += f'<li>{capa["display"]} (Created: {capa.get("created_at", "N/A")[:10] if capa.get("created_at") else "N/A"})</li>'
                actions_html += '</ul>'
            
            if links["change_controls"]:
                actions_html += '<p><strong>Changes Created:</strong></p><ul>'
                for change in links["change_controls"]:
                    actions_html += f'<li>{change["display"]} (Created: {change.get("created_at", "N/A")[:10] if change.get("created_at") else "N/A"})</li>'
                actions_html += '</ul>'
            
            actions_html += '</div>'
        
        actions_html += '</div>'
    
    # Connectivity Audit Check
    gaps_html = ""
    if gaps.get("signals_missing_risk_link") or gaps.get("signals_missing_action_despite_trigger"):
        gaps_html = '<div class="section warning-section">'
        gaps_html += '<h2>Connectivity Audit Check</h2>'
        
        if gaps.get("signals_missing_risk_link"):
            gaps_html += '<h3>Signals Missing Risk Link</h3>'
            gaps_html += '<p>The following signals do not have a link to a risk item:</p>'
            gaps_html += '<ul>'
            for gap in gaps["signals_missing_risk_link"]:
                gaps_html += f'<li>{gap.get("signal_key")} – {gap.get("title")}</li>'
            gaps_html += '</ul>'
        
        if gaps.get("signals_missing_action_despite_trigger"):
            gaps_html += '<h3>Signals Missing Action Despite Trigger</h3>'
            gaps_html += '<p>The following signals have a trigger status but no resulting CAPA or Change:</p>'
            gaps_html += '<ul>'
            for gap in gaps["signals_missing_action_despite_trigger"]:
                gaps_html += f'<li>{gap.get("signal_key")} – {gap.get("title")} (Trigger: {gap.get("trigger_status")})</li>'
            gaps_html += '</ul>'
        
        gaps_html += '</div>'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PMS Signal Feedback Report - {project_name}</title>
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
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .summary-box {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e5e7eb;
        }}
        .summary-box.warning {{
            border-color: #f59e0b;
            background-color: #fef3c7;
        }}
        .summary-label {{
            font-size: 0.9em;
            color: #6b7280;
        }}
        .summary-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #1f2937;
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
        .badge {{
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-neutral {{
            background-color: #f3f4f6;
            color: #374151;
        }}
        .badge-warning {{
            background-color: #fef3c7;
            color: #92400e;
        }}
        .badge-danger {{
            background-color: #fee2e2;
            color: #991b1b;
        }}
        .badge-success {{
            background-color: #d1fae5;
            color: #065f46;
        }}
        .badge-info {{
            background-color: #dbeafe;
            color: #1e40af;
        }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            background: #f9fafb;
            border-radius: 5px;
        }}
        .warning-section {{
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
        }}
        .trigger-item, .action-item {{
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-left: 4px solid #2563eb;
            border-radius: 4px;
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
    <h1>Post-Market Surveillance Signal Feedback Report</h1>
    
    <div class="meta">
        <p><strong>Project:</strong> {project_name}</p>
        <p><strong>Components:</strong></p>
        <ul>
{components_html}
        </ul>
        {date_range_html}
        <p><strong>Generated:</strong> {generated_at}</p>
    </div>
    
    <div class="statement">
        <p><strong>Audit Statement:</strong></p>
        <p>This report compiles PMS signals and their traceable feedback into risk, CAPA, and change control.</p>
        <p>All signal data is sourced from controlled SmartQS records.</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        {summary_html}
    </div>
    
    <div class="section">
        <h2>Signal Register</h2>
        {signal_table_html}
    </div>
    
    {trends_html}
    {triggers_html}
    {actions_html}
    {gaps_html}
    
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
        <p style="color: #6b7280; font-size: 0.9em;">
            This document was generated by SmartQS Risk Management System.
            All PMS signal feedback data complies with ISO 14971:2019 and ISO 13485:2016.
        </p>
    </div>
</body>
</html>"""
    
    return html

