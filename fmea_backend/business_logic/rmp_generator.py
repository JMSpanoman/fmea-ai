"""
Business Logic for Risk Management Plan (RMP) Generation.
Audit-ready, ISO 14971-aligned output. Regulatory language; no system-specific terms in main body.
"""
import json
from typing import List, Dict, Any, Optional
from schemas.risk_management_plan import RMPGenerateRequest, ComponentInput


def generate_acceptability_criteria(profile: str = "default_med_device", custom: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate acceptability criteria based on profile."""
    if custom:
        return custom
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
            "Critical": {"min": 20, "max": 25, "description": "Unacceptable — requires immediate mitigation"},
            "High": {"min": 12, "max": 19, "description": "Unacceptable — requires mitigation"},
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


def generate_acceptability_statement() -> str:
    """Regulatory statement for risk acceptability criteria."""
    return """Risk acceptability criteria shall be defined prior to risk analysis and shall be approved by the organization.
Risk reduction shall be carried out as far as practicable (ALARP — As Low As Reasonably Practicable).
Where residual risk remains above the acceptable level after implementation of risk controls, benefit-risk analysis shall be performed and documented."""


def generate_risk_methodology() -> str:
    """Risk evaluation methodology with hazard identification sources and expected categories."""
    return """This Risk Management Plan follows ISO 14971:2019 requirements for medical device risk management.

Risk Evaluation Process:
1. Hazard Identification: Identify potential sources of harm.
2. Hazardous Situation: Identify circumstances that could lead to harm.
3. Harm: Identify the nature of the harm that could occur.
4. Sequence of Events: Document the sequence leading from hazard to harm.
5. Failure Mode Analysis: Analyze potential failure modes where applicable.

Sources of hazard identification shall include, as applicable:
- Relevant standards and guidance (e.g. ISO 14971, product-specific standards)
- Historical data and post-market data from similar devices
- Clinical input and literature
- Similar devices and state of the art
- Design and process FMEAs

For implantable and life-sustaining devices, expected hazard categories may include: electrical safety, mechanical failure, software anomaly, biocompatibility, use error, labeling/IFU deficiency, environmental factors, and supply chain. Applicability shall be confirmed by the project team.

Risk Score Calculation:
The risk score is calculated using the formula: risk_score = severity × probability_of_harm

Where:
- Severity: Rated on a scale of 1–5 (Negligible to Catastrophic).
- Probability of harm: Rated on a scale of 1–5 (Remote to Frequent).

Residual Risk Assessment:
After implementation of risk controls, residual risk shall be assessed using the same methodology. All residual risks must be evaluated for acceptability. Benefit-risk analysis shall be performed for any unacceptable residual risks."""


def generate_risk_control_categories() -> List[Dict[str, str]]:
    """Risk control categories with explicit priority order (ISO 14971)."""
    return [
        {"priority": "1", "category": "Inherent safety by design", "description": "Risk reduction built into the design; highest priority."},
        {"priority": "2", "category": "Protective measures", "description": "Protective measures in the device, manufacturing, or process."},
        {"priority": "3", "category": "Information for safety", "description": "Labeling, instructions for use, training, and other information."},
    ]


def generate_benefit_risk_criteria() -> str:
    """Benefit-risk criteria with state of the art and formal documentation."""
    return """Benefit-risk analysis is required when:
1. Residual risk remains unacceptable after implementation of all feasible risk controls.
2. Risk level is High or Critical.
3. Risk controls introduce new risks that must be evaluated.

Consideration of state of the art:
The benefit-risk determination shall take into account the generally acknowledged state of the art in the relevant technical and medical fields. Alternative treatments and devices shall be considered where applicable.

Documentation requirements:
- Formal benefit-risk analysis documentation is required.
- Clinical data demonstrating benefits shall be documented.
- Risk-benefit justification shall be approved by management.
- All benefit-risk analyses shall be reviewed and approved by: Risk Manager, Design Lead, Quality Lead, and Management Representative."""


def generate_lifecycle_linkage() -> str:
    """Lifecycle linkage in regulatory language; no system/database terms."""
    return """Risk Management Lifecycle Integration

Design controls:
- Risk controls shall be traced to design inputs via traceability links.
- Design outputs shall demonstrate implementation of risk controls.
- Verification and validation shall confirm that risk controls are effective.
- A traceability matrix shall link risks, controls, design outputs, and V&V.

CAPA integration:
- Risk-driven corrective and preventive actions shall be initiated when new risks are identified.
- CAPAs shall be linked to risk records via traceability.
- Risk re-evaluation shall be triggered upon CAPA completion.

Change control:
- Changes affecting risk shall be documented in change control records.
- All changes affecting risk shall trigger risk re-evaluation.
- Version-controlled risk records shall be maintained; version approval is required before a version is considered current. Superseded versions shall be retained for the audit trail.

Re-evaluation triggers:
1. New risk identified.
2. Risk control implemented or modified.
3. Design change affecting risk.
4. Post-market signal indicating new risk.
5. Change control affecting risk-related design elements."""


def generate_governance_rules() -> str:
    """Governance in regulatory language only (no database/table names)."""
    return """Risk Management Governance

Human-in-the-loop requirements:
- No automatic acceptance of risk decisions; all risk acceptability decisions shall be made by qualified personnel.
- All risk records shall require human review and approval before use.
- AI-generated or system-generated content shall be reviewed and approved by qualified personnel prior to use.
- Risk scores and acceptability decisions shall be based on human judgment.

Approval requirements:
- Risk records shall require approval before being considered current.
- The Risk Management Plan shall require approval before use.
- Benefit-risk analyses shall require management approval.
- All approvals shall be logged with approver, timestamp, and rationale.

Audit and traceability:
- Audit logs shall record risk-related activities (creation, updates, approvals, traceability links).
- Traceability records shall link risks to controls, design outputs, and verification evidence.
- Version-controlled records shall be retained for the audit trail."""


def generate_governance_appendix() -> str:
    """Optional appendix: system implementation details (not in main regulator-facing body)."""
    return """Appendix — System Implementation (for internal reference only)

The following implementation details support the governance rules above and are not part of the regulator-facing RMP:
- Automated logging of risk-related events for audit.
- Version control and idempotency handling for risk records.
- Traceability link management between risks, controls, and design artifacts.
Applicability and configuration are defined in the quality management system."""


def generate_applicable_standards() -> str:
    """Applicable standards and regulations; safe wording."""
    return """The following standards and regulations may apply. Applicability shall be confirmed by the project team.

Risk management:
- ISO 14971:2019 — Medical devices — Application of risk management to medical devices.
- ISO/TR 24971 — Guidance on the application of ISO 14971.

Product and process:
- IEC 62304 — Medical device software — Software life cycle processes (if the device contains software).
- IEC 62366 — Medical devices — Application of usability engineering (human factors).
- ISO 10993 — Biological evaluation of medical devices (biocompatibility, where applicable).
- IEC 60601 — Medical electrical equipment (electrical safety, where applicable).

Implantable and active implantable devices (where applicable):
- ISO 14708 (active implantable medical devices); other product-specific standards as applicable.

Regulatory frameworks:
- EU MDR 2017/745 (where CE marking is sought).
- FDA regulatory requirements (where US market is intended).

The project shall confirm which of the above apply and shall document any additional standards in the design and development documentation."""


def generate_verification_of_risk_controls() -> str:
    """Verification of risk control measures; link to V&V."""
    return """Verification of Risk Control Measures

Each risk control shall be verified. Verification methods shall include, as appropriate:
- Test (e.g. performance testing, safety testing).
- Inspection (e.g. design review, document review).
- Analysis (e.g. calculation, FMEA).
- Simulation (e.g. where testing is not feasible).

Requirements:
- Each risk control shall be traced to verification activities.
- Verification shall be linked to design and development V&V activities where applicable.
- Traceability shall be maintained: risk control → verification activity → result (pass/fail or conclusion).
- Verification results shall be documented and retained in the risk management file."""


def generate_evaluation_of_residual_risk() -> str:
    """Evaluation of residual risk (individual and overall)."""
    return """Evaluation of Residual Risk

Individual residual risk:
- After implementation of risk controls, residual risk for each identified hazard shall be evaluated.
- Residual risk shall be compared against the risk acceptability criteria defined in this plan.
- Where residual risk is acceptable, no further action is required beyond documentation.
- Where residual risk remains in the ALARP region, documented justification and review are required.
- Where residual risk remains unacceptable, escalation to benefit-risk analysis is required before acceptance.

Overall residual risk:
- Overall residual risk of the device shall be evaluated in addition to individual risks.
- The evaluation shall consider the combination of residual risks and shall be documented in the Risk Management Report.

Approval requirements:
- Residual risk evaluation shall be approved in accordance with the roles defined in this plan.
- Benefit-risk analysis (when required) shall be approved by management."""


def generate_rmf_deliverables() -> str:
    """Risk Management File deliverables list."""
    return """Risk Management File Deliverables

The following outputs shall be produced and maintained in the Risk Management File:

- Risk Management Plan (this document).
- Hazard analysis / FMEA (hazard identification and risk estimation).
- Risk control measures documentation (implementation of controls).
- Verification evidence (evidence that risk controls have been verified).
- Residual risk evaluation (individual and overall).
- Benefit-risk analysis (where residual risk remains unacceptable).
- Risk Management Report (summary for management review).
- Post-market surveillance data (as input to ongoing risk monitoring).

Additional deliverables may be required by applicable standards or the quality management system."""


def generate_ai_disclaimer() -> str:
    """AI disclaimer for draft content."""
    return """AI-generated content within this document is provided as draft material and shall be reviewed and approved by qualified personnel prior to use."""


def generate_roles_table() -> List[Dict[str, str]]:
    """Roles with responsibility and minimum competence (for table)."""
    return [
        {"role": "Risk Management Lead", "responsibility": "Owns the risk management process; ensures RMP is maintained and applied.", "minimum_competence": "Trained in ISO 14971; quality or engineering background."},
        {"role": "Design Lead", "responsibility": "Ensures risk controls are implemented in design; provides technical input to risk evaluation.", "minimum_competence": "Relevant design and development experience."},
        {"role": "Quality / Regulatory", "responsibility": "Ensures compliance with standards and regulations; reviews risk documentation.", "minimum_competence": "Quality management and regulatory awareness."},
        {"role": "Approver", "responsibility": "Approves risk acceptability and the Risk Management Plan; accountable for risk decisions.", "minimum_competence": "Management responsibility; authority to approve."},
    ]


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
    created_at: str = None,
    *,
    scope_device_description: Optional[str] = None,
    scope_intended_user: Optional[str] = None,
    scope_patient_population: Optional[str] = None,
    scope_use_environment: Optional[str] = None,
    applicable_standards: Optional[str] = None,
    verification_of_risk_controls: Optional[str] = None,
    evaluation_of_residual_risk: Optional[str] = None,
    rmf_deliverables: Optional[str] = None,
    roles_table: Optional[List[Dict[str, str]]] = None,
    acceptability_statement: Optional[str] = None,
    ai_disclaimer: Optional[str] = None,
    governance_appendix: Optional[str] = None,
) -> str:
    """Generate audit-ready RMP HTML. New optional kwargs add sections and structured scope."""
    components_html = ""
    for comp in components:
        desc = f" — {comp.description}" if comp.description else ""
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

    # Roles: use roles_table (role, responsibility, minimum_competence) if provided; else fallback to review_roles
    roles_rows_html = ""
    if roles_table:
        for r in roles_table:
            roles_rows_html += f"<tr><td>{r.get('role', '')}</td><td>{r.get('responsibility', '')}</td><td>{r.get('minimum_competence', '')}</td></tr>\n"
    else:
        for role, requirement in review_roles.items():
            roles_rows_html += f"<tr><td>{role.replace('_', ' ').title()}</td><td>{requirement}</td><td>—</td></tr>\n"

    # Risk control categories: support list of dicts (priority, category, description) or list of strings
    control_categories_html = ""
    for item in risk_control_categories:
        if isinstance(item, dict):
            control_categories_html += f"<li><strong>{item.get('priority', '')}. {item.get('category', '')}</strong> — {item.get('description', '')}</li>\n"
        else:
            control_categories_html += f"<li>{item}</li>\n"

    created_date = created_at if created_at else "Not specified"

    # Structured scope (optional)
    device_desc = scope_device_description if scope_device_description is not None else scope
    intended_user = scope_intended_user or "To be defined by the project team."
    patient_pop = scope_patient_population or "To be defined by the project team."
    use_env = scope_use_environment or "To be defined by the project team."

    sect_standards = applicable_standards or generate_applicable_standards()
    sect_verification = verification_of_risk_controls or generate_verification_of_risk_controls()
    sect_residual = evaluation_of_residual_risk or generate_evaluation_of_residual_risk()
    sect_rmf = rmf_deliverables or generate_rmf_deliverables()
    stmt_acceptability = acceptability_statement or generate_acceptability_statement()
    disclaimer = ai_disclaimer or generate_ai_disclaimer()
    appendix = governance_appendix or generate_governance_appendix()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }}
        h1 {{ color: #1e40af; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
        h2 {{ color: #1e40af; margin-top: 28px; border-bottom: 2px solid #e5e7eb; padding-bottom: 5px; }}
        h3 {{ color: #374151; margin-top: 18px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #f3f4f6; font-weight: bold; }}
        .section {{ margin: 18px 0; padding: 15px; background: #f9fafb; border-radius: 5px; }}
        .meta {{ color: #6b7280; font-size: 0.9em; margin-bottom: 20px; }}
        ul {{ margin: 10px 0; padding-left: 30px; }}
        li {{ margin: 5px 0; }}
        .appendix {{ margin-top: 24px; padding: 15px; background: #f3f4f6; font-size: 0.95em; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="meta">Version: {version_no} | Created: {created_date}</div>

    <div class="section">
        <h2>1. Scope and Intended Use</h2>
        <h3>Device Description</h3>
        <p>{device_desc}</p>
        <h3>Intended Use</h3>
        <p>{intended_use}</p>
        <h3>Intended User</h3>
        <p>{intended_user}</p>
        <h3>Patient Population</h3>
        <p>{patient_pop}</p>
        <h3>Use Environment</h3>
        <p>{use_env}</p>
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
        <h2>2. Applicable Standards and Regulations</h2>
        <div style="white-space: pre-line;">{sect_standards}</div>
    </div>

    <div class="section">
        <h2>3. Risk Acceptability Criteria</h2>
        <p>{stmt_acceptability}</p>
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
        <h2>4. Risk Evaluation Methodology</h2>
        <div style="white-space: pre-line;">{risk_methodology}</div>
    </div>

    <div class="section">
        <h2>5. Risk Control Categories</h2>
        <p>Risk controls shall be applied in the following priority order:</p>
        <ul>
{control_categories_html}
        </ul>
    </div>

    <div class="section">
        <h2>6. Verification of Risk Control Measures</h2>
        <div style="white-space: pre-line;">{sect_verification}</div>
    </div>

    <div class="section">
        <h2>7. Evaluation of Residual Risk</h2>
        <div style="white-space: pre-line;">{sect_residual}</div>
    </div>

    <div class="section">
        <h2>8. Risk Management File Deliverables</h2>
        <div style="white-space: pre-line;">{sect_rmf}</div>
    </div>

    <div class="section">
        <h2>9. Benefit-Risk Criteria</h2>
        <div style="white-space: pre-line;">{benefit_risk_criteria}</div>
    </div>

    <div class="section">
        <h2>10. Lifecycle Linkage to Design / CAPA / Change</h2>
        <div style="white-space: pre-line;">{lifecycle_linkage}</div>
    </div>

    <div class="section">
        <h2>11. Roles and Responsibilities</h2>
        <table>
            <tr><th>Role</th><th>Responsibility</th><th>Minimum Competence</th></tr>
{roles_rows_html}
        </table>
        <p>Approval requirements: Version approval is required for risk records and for Risk Management Plan updates. All approvals shall include rationale and timestamp.</p>
    </div>

    <div class="section">
        <h2>12. Governance Rules</h2>
        <div style="white-space: pre-line;">{governance_rules}</div>
    </div>

    <div class="section">
        <h2>13. AI and Draft Content</h2>
        <p>{disclaimer}</p>
    </div>

    <div class="appendix">
        <h2>Appendix — System Implementation (Optional)</h2>
        <div style="white-space: pre-line;">{appendix}</div>
    </div>

    <p style="margin-top: 32px; font-size: 0.9em; color: #6b7280;">
        This document was generated by SmartRisk. All risk management activities shall comply with ISO 14971:2019. The plan shall be reviewed and approved by qualified personnel.
    </p>
</body>
</html>"""
    return html
