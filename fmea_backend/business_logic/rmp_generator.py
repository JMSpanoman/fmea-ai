"""
Business Logic for Risk Management Plan (RMP) Generation
Generates all required sections and HTML rendering
"""
import json
from typing import List, Dict, Any, Optional
from schemas.risk_management_plan import RMPGenerateRequest, ComponentInput

def generate_acceptability_criteria(profile: str = "default_med_device", custom: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate acceptability criteria based on profile"""
    if custom:
        return custom
    
    # Default medical device profile
    return {
        "severity_scale": {
            "1": "Negligible",
            "2": "Minor",
            "3": "Serious",
            "4": "Critical",
            "5": "Catastrophic"
        },
        "probability_scale": {
            "1": "Remote",
            "2": "Unlikely",
            "3": "Possible",
            "4": "Probable",
            "5": "Frequent"
        },
        "risk_score_formula": "risk_score = severity × probability_of_harm",
        "thresholds": {
            "Critical": {"min": 20, "max": 25, "description": "Unacceptable - requires immediate mitigation"},
            "High": {"min": 12, "max": 19, "description": "Unacceptable - requires mitigation"},
            "Medium": {"min": 6, "max": 11, "description": "Acceptable with mitigation"},
            "Low": {"min": 1, "max": 5, "description": "Acceptable"}
        },
        "acceptability_rules": {
            "Critical": "Requires immediate mitigation and management approval",
            "High": "Requires mitigation and benefit-risk analysis",
            "Medium": "Requires mitigation or benefit-risk justification",
            "Low": "Acceptable as-is"
        }
    }

def generate_risk_methodology() -> str:
    """Generate risk evaluation methodology text"""
    return """This Risk Management Plan follows ISO 14971:2019 requirements for medical device risk management.

Risk Evaluation Process:
1. Hazard Identification: Identify potential sources of harm
2. Hazardous Situation: Identify circumstances that could lead to harm
3. Harm: Identify the nature of the harm that could occur
4. Sequence of Events: Document the sequence leading from hazard to harm
5. Failure Mode Analysis: Analyze potential failure modes

Risk Score Calculation:
The risk score is calculated using the formula:
risk_score = severity × probability_of_harm

Where:
- severity: Rated on a scale of 1-5 (Negligible to Catastrophic)
- probability_of_harm: Rated on a scale of 1-5 (Remote to Frequent)

Residual Risk Assessment:
After implementation of risk controls, residual risk is assessed using the same methodology. All residual risks must be evaluated for acceptability, and benefit-risk analysis must be performed for any unacceptable residual risks."""

def generate_risk_control_categories() -> List[str]:
    """Generate risk control categories"""
    return [
        "Inherent Safety by Design",
        "Protective Measures (in device, manufacturing, process)",
        "Information for Safety (labeling, IFU, training)"
    ]

def generate_benefit_risk_criteria() -> str:
    """Generate benefit-risk criteria text"""
    return """Benefit-Risk Analysis is required when:
1. Residual risk remains unacceptable after implementation of all feasible risk controls
2. Risk level is High or Critical
3. Risk controls introduce new risks that must be evaluated

Evidence Requirements:
- Clinical data demonstrating benefits
- Risk-benefit justification documentation
- Management approval for all benefit-risk decisions

Approval Requirements:
All benefit-risk analyses must be reviewed and approved by:
- Risk Manager
- Design Lead
- Quality Lead
- Management Representative"""

def generate_lifecycle_linkage() -> str:
    """Generate lifecycle linkage text"""
    return """Risk Management Lifecycle Integration:

Design Controls:
- Risk controls are traced to Design Inputs via trace_links
- Design Outputs must demonstrate implementation of risk controls
- V&V Tests validate that risk controls are effective
- Traceability matrix links risks → controls → design outputs → V&V

CAPA Integration:
- Risk-driven CAPAs are created when new risks are identified
- CAPAs are linked to risk items via trace_links
- Risk re-evaluation is triggered upon CAPA completion

Change Control:
- Change control records are created from risk version diffs
- All changes affecting risk require risk re-evaluation
- Risk versions track changes and require approval

Re-evaluation Triggers:
1. New risk identified
2. Risk control implemented or modified
3. Design change affecting risk
4. Post-market signal indicating new risk
5. Change control affecting risk-related design elements"""

def generate_governance_rules() -> str:
    """Generate governance rules text"""
    return """SmartQS Risk Management Governance:

Human-in-the-Loop Requirements:
- No automatic acceptance of risk items
- All risk item versions require human review and approval
- AI-generated content must be reviewed and approved by qualified personnel
- Risk scores and acceptability decisions require human judgment

Approval Requirements:
- Risk item versions require approval before becoming current
- Risk Management Plan requires approval before use
- Benefit-risk analyses require management approval
- All approvals are logged with approver, timestamp, and rationale

AI Event Logging:
- All AI-assisted operations are logged in ai_events table
- AI suggestions must be reviewed and accepted/rejected by users
- AI-generated content is marked with ai_metadata
- AI events include: operation type, input, output, user decision

Audit Log Events:
- All handoffs between systems are logged in audit_log_events
- Risk item creation, updates, approvals are logged
- Trace link creation and updates are logged
- Change control events affecting risk are logged

Idempotency Guarantee:
- All operations support idempotency via idempotency_request table
- Duplicate requests are detected and handled gracefully
- Transactional integrity ensures no orphan links

Versioning Logic:
- Risk items maintain version history in risk_item_versions table
- RMP maintains version number for tracking changes
- Version approval is required before version becomes current
- Superseded versions are retained for audit trail"""

def generate_rmp_html(
    title: str,
    scope: str,
    intended_use: str,
    components: List[ComponentInput],
    acceptability_criteria: Dict[str, Any],
    risk_methodology: str,
    review_roles: Dict[str, str],
    risk_control_categories: List[str],
    benefit_risk_criteria: str,
    lifecycle_linkage: str,
    governance_rules: str,
    version_no: int = 1,
    created_at: str = None
) -> str:
    """Generate HTML for the RMP document"""
    components_html = ""
    for comp in components:
        desc = f" - {comp.description}" if comp.description else ""
        components_html += f"<li><strong>{comp.name}</strong>{desc}</li>\n"
    
    severity_scale_html = ""
    for level, desc in acceptability_criteria.get("severity_scale", {}).items():
        severity_scale_html += f"<tr><td>{level}</td><td>{desc}</td></tr>\n"
    
    probability_scale_html = ""
    for level, desc in acceptability_criteria.get("probability_scale", {}).items():
        probability_scale_html += f"<tr><td>{level}</td><td>{desc}</td></tr>\n"
    
    thresholds_html = ""
    for level, info in acceptability_criteria.get("thresholds", {}).items():
        thresholds_html += f"<tr><td>{level}</td><td>{info.get('min')}-{info.get('max')}</td><td>{info.get('description', '')}</td></tr>\n"
    
    review_roles_html = ""
    for role, requirement in review_roles.items():
        review_roles_html += f"<tr><td>{role}</td><td>{requirement}</td></tr>\n"
    
    control_categories_html = ""
    for category in risk_control_categories:
        control_categories_html += f"<li>{category}</li>\n"
    
    created_date = created_at if created_at else "Not specified"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
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
    <h1>{title}</h1>
    <div class="meta">Version: {version_no} | Created: {created_date}</div>
    
    <div class="section">
        <h2>1. Scope and Intended Use</h2>
        <h3>Scope</h3>
        <p>{scope}</p>
        
        <h3>Intended Use</h3>
        <p>{intended_use}</p>
        
        <h3>Components Covered</h3>
        <ul>
{components_html}
        </ul>
        
        <h3>Lifecycle Boundaries</h3>
        <p>This Risk Management Plan covers the following lifecycle phases:</p>
        <ul>
            <li>Development: Design and development activities</li>
            <li>Manufacturing: Production and manufacturing processes</li>
            <li>Post-Market: Post-market surveillance and monitoring</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>2. Risk Acceptability Criteria</h2>
        
        <h3>Scoring Inputs</h3>
        <h4>Severity Scale</h4>
        <table>
            <tr><th>Level</th><th>Description</th></tr>
{severity_scale_html}
        </table>
        
        <h4>Probability of Harm Scale</h4>
        <table>
            <tr><th>Level</th><th>Description</th></tr>
{probability_scale_html}
        </table>
        
        <h3>Risk Score Formula</h3>
        <p><strong>{acceptability_criteria.get('risk_score_formula', 'risk_score = severity × probability_of_harm')}</strong></p>
        
        <h3>Risk Thresholds</h3>
        <table>
            <tr><th>Risk Level</th><th>Score Range</th><th>Description</th></tr>
{thresholds_html}
        </table>
        
        <h3>Acceptability Rules</h3>
        <ul>
            <li><strong>Critical:</strong> {acceptability_criteria.get('acceptability_rules', {}).get('Critical', 'Requires immediate mitigation')}</li>
            <li><strong>High:</strong> {acceptability_criteria.get('acceptability_rules', {}).get('High', 'Requires mitigation')}</li>
            <li><strong>Medium:</strong> {acceptability_criteria.get('acceptability_rules', {}).get('Medium', 'Requires mitigation or justification')}</li>
            <li><strong>Low:</strong> {acceptability_criteria.get('acceptability_rules', {}).get('Low', 'Acceptable as-is')}</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>3. Risk Evaluation Methodology</h2>
        <div style="white-space: pre-line;">{risk_methodology}</div>
    </div>
    
    <div class="section">
        <h2>4. Review & Approval Responsibilities</h2>
        <table>
            <tr><th>Role</th><th>Requirement</th></tr>
{review_roles_html}
        </table>
        
        <h3>Approval Requirements</h3>
        <ul>
            <li>Version approval required for all risk item versions</li>
            <li>Version approval required for Risk Management Plan updates</li>
            <li>All approvals must include rationale and timestamp</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>5. Risk Control Categories</h2>
        <p>The following risk control categories are used in this Risk Management Plan:</p>
        <ul>
{control_categories_html}
        </ul>
        <p>These categories are tied to risk_controls.control_type in the SmartQS system.</p>
    </div>
    
    <div class="section">
        <h2>6. Benefit-Risk Criteria</h2>
        <div style="white-space: pre-line;">{benefit_risk_criteria}</div>
    </div>
    
    <div class="section">
        <h2>7. Lifecycle Linkage to Design/CAPA/Change</h2>
        <div style="white-space: pre-line;">{lifecycle_linkage}</div>
    </div>
    
    <div class="section">
        <h2>8. SmartQS Governance Rules</h2>
        <div style="white-space: pre-line;">{governance_rules}</div>
    </div>
    
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
        <p style="color: #6b7280; font-size: 0.9em;">
            This document was generated by SmartQS Risk Management System.
            All risk management activities must comply with ISO 14971:2019.
        </p>
    </div>
</body>
</html>"""
    
    return html

