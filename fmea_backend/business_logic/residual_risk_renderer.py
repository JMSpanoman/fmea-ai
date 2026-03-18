"""
Residual Risk Evaluation HTML Renderer
Generates a complete, audit-ready Residual Risk Evaluation report (ISO 14971)
with all required sections for notified body or FDA review.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone


def _device_context(profile: Dict[str, Any], project_name: str) -> str:
    """Brief device context for narrative (e.g. pacemaker)."""
    desc = (profile or {}).get("device_description") or ""
    use = (profile or {}).get("intended_use") or ""
    if desc or use:
        return f"{desc}. {use}".strip()
    return f"Medical device project: {project_name}. For life-sustaining devices (e.g. implantable pacemaker), the device is used to regulate heart rhythm in patients, typically in home and clinical environments."


def render_residual_risk_html(evidence: Dict[str, Any], project_name: str) -> str:
    """
    Render a complete Residual Risk Evaluation report with 10 sections:
    1) Pre-Control Risk Summary
    2) Risk Control Measures Implemented
    3) Post-Control (Residual Risk) Summary
    4) Risk Acceptability Criteria
    5) Benefit-Risk Analysis
    6) Overall Residual Risk Evaluation
    7) Traceability
    8) Residual Risk Table (Hazard | Initial Risk | Controls | Residual Risk | Acceptability)
    9) Assumptions and Limitations
    10) Approval Section
    """
    rows: List[Dict[str, Any]] = evidence.get("rows", [])
    thresholds = evidence.get("thresholds", {})
    profile = evidence.get("profile", {})
    pre = evidence.get("pre_control_summary", {})
    controls_section = evidence.get("risk_control_measures", {})
    post = evidence.get("post_control_summary", {})
    missing_list = evidence.get("missing_field_list", [])
    counts = evidence.get("counts", {})
    version_scope = evidence.get("version_scope", "approved_only")
    components = evidence.get("components", [])
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    device_context = _device_context(profile, project_name)

    # Components list
    comp_html = ""
    if components:
        for c in components:
            comp_html += f"<li>{c.get('name', c.get('id', 'Unknown'))}</li>\n"
    else:
        comp_html = "<li>All project components</li>\n"

    # --- Section 1: Pre-Control Risk Summary ---
    num_hazards = pre.get("number_of_hazards", len(rows))
    dist = pre.get("initial_risk_distribution", {})
    high, med, low = dist.get("high", 0), dist.get("medium", 0), dist.get("low", 0)
    highest = pre.get("highest_risks", [])
    methodology = pre.get("methodology", "Risk estimation follows ISO 14971: severity of harm and probability of occurrence; risk score = severity × probability. Thresholds are defined in the project Risk Acceptability Criteria.")
    highest_rows = ""
    for h in highest:
        key = h.get("risk_key", "")
        hazard = (h.get("hazard") or "")[:80]
        score = h.get("initial_score", "—")
        level = h.get("initial_level", "—")
        highest_rows += f"<tr><td>{key}</td><td>{hazard}</td><td>{score}</td><td>{level}</td></tr>\n"

    # --- Section 2: Risk Control Measures ---
    design_list = controls_section.get("design_controls", [])
    protective_list = controls_section.get("protective_measures", [])
    info_list = controls_section.get("information_for_safety", [])
    design_html = "".join(f"<li>{x}</li>\n" for x in design_list) if design_list else "<li>Design controls are documented in the Hazard Analysis and Risk Control documentation for each risk.</li>\n"
    protective_html = "".join(f"<li>{x}</li>\n" for x in protective_list) if protective_list else "<li>Protective measures (e.g. hardware safeguards, software interlocks) are implemented as documented in risk control records.</li>\n"
    info_html = "".join(f"<li>{x}</li>\n" for x in info_list) if info_list else "<li>Information for safety (labeling, IFU, warnings) is defined in the risk control and labeling documentation.</li>\n"

    # --- Section 3: Post-Control Summary ---
    res_dist = post.get("residual_risk_distribution", {})
    res_high, res_med, res_low = res_dist.get("high", 0), res_dist.get("medium", 0), res_dist.get("low", 0)
    effectiveness = post.get("effectiveness_narrative", "Control effectiveness is assessed per risk item; residual risk is re-evaluated after implementation of controls.")
    remaining = post.get("remaining_significant_risks", [])
    remaining_rows = ""
    for r in remaining[:10]:
        remaining_rows += f"<tr><td>{r.get('risk_key', '')}</td><td>{(r.get('hazard') or '')[:60]}</td><td>{r.get('residual_score', '—')}</td><td>{r.get('acceptability', '—')}</td></tr>\n"

    # --- Section 4: Risk Acceptability Criteria ---
    thresholds_rows = ""
    for level, t in thresholds.items():
        lo, hi = t.get("min", 0), t.get("max", 100)
        acc = t.get("acceptability", "—")
        thresholds_rows += f"<tr><td>{level}</td><td>{lo}–{hi}</td><td>{acc}</td></tr>\n"

    # --- Section 5 & 6: Benefit-Risk and Overall Statement ---
    benefit_text = (
        "The clinical and functional benefits of the device (e.g. restoration of appropriate heart rhythm, symptom relief, quality of life improvement) are weighed against the residual risks. "
        "For life-sustaining devices, the benefit-risk determination is documented in the Benefit-Risk Analysis report. "
        "Residual risks that remain in the ALARP or acceptable region after implementation of all practicable risk controls are justified with reference to clinical benefit and state of the art."
    )
    overall_statement = (
        "Based on the evaluation of all identified hazards and hazardous situations, the implementation of risk control measures, and the residual risk assessment, "
        "the overall residual risk associated with this device is judged acceptable when weighed against the benefits of the intended use, in accordance with ISO 14971, "
        "subject to the conditions and limitations stated in the risk management file and the information for safety."
    )
    if remaining:
        overall_statement = (
            "Based on the evaluation of all identified hazards, risk controls, and residual risk, "
            "the overall residual risk is acceptable with the following condition: risks that remain above the acceptable threshold have been evaluated in the Benefit-Risk Analysis and are justified. "
            "Ongoing post-market surveillance and risk monitoring are in place as documented in the Risk Management Plan."
        )

    # --- Section 7: Traceability ---
    trace_rows = """
    <tr><td>Hazard identification</td><td>Hazard Analysis / FMEA</td><td>Risk items and versions</td></tr>
    <tr><td>Risk controls</td><td>Risk Control Measures Documentation</td><td>Design, protective, information for safety</td></tr>
    <tr><td>Residual risk</td><td>This report</td><td>Residual Risk Table and acceptability</td></tr>
    <tr><td>Benefit-risk</td><td>Benefit-Risk Analysis</td><td>Justification for residual risks</td></tr>
    """

    # --- Section 8: Residual Risk Table ---
    table_body = ""
    for r in rows:
        hazard = (r.get("hazard") or "—")[:120]
        init = r.get("initial_risk_score") is not None and f"S{r.get('initial_severity')}×P{r.get('initial_probability')}={r.get('initial_risk_score')}" or "—"
        controls = (r.get("controls_summary") or "—")[:100]
        res = r.get("residual_risk_display") or (str(r.get("residual_risk_score")) if r.get("residual_risk_score") is not None else "—")
        acc = r.get("residual_acceptability") or "—"
        table_body += f"<tr><td>{hazard}</td><td>{init}</td><td>{controls}</td><td>{res}</td><td>{acc}</td></tr>\n"
    if not table_body:
        table_body = "<tr><td colspan=\"5\">No residual risk data available. Populate risk item versions with hazard, initial risk, controls, and residual risk.</td></tr>\n"

    # --- Section 9: Assumptions and Limitations ---
    assumptions = [
        "Risk scores and acceptability are based on the risk item versions included in this export (version scope: " + str(version_scope) + ").",
        "Where residual severity or probability was not recorded, acceptability may be inferred from project thresholds; such items are marked in the table.",
        "Device context (intended use, user population, use environment) is taken from the project profile where available; otherwise a generic medical device context is assumed.",
    ]
    if missing_list:
        assumptions.append(f"{len(missing_list)} risk version(s) have missing residual risk fields; these are listed in the Missing Residual Fields section and should be completed for a full evaluation.")
    assumptions_html = "".join(f"<li>{a}</li>\n" for a in assumptions)

    # --- Section 10: Approval ---
    approval_html = """
    <table class="report-table">
    <thead><tr><th>Role</th><th>Name</th><th>Signature</th><th>Date</th></tr></thead>
    <tbody>
    <tr><td>Prepared by</td><td>[To be assigned]</td><td>________________</td><td>__________</td></tr>
    <tr><td>Reviewed by</td><td>[To be assigned]</td><td>________________</td><td>__________</td></tr>
    <tr><td>Approved by</td><td>[To be assigned]</td><td>________________</td><td>__________</td></tr>
    </tbody>
    </table>
    """

    # Missing fields
    missing_html = ""
    if missing_list:
        missing_html = """
    <div class="warning">
    <h3>Missing Residual Fields</h3>
    <p>The following risk versions are missing residual risk fields and should be completed:</p>
    <ul>
    """ + "".join(f"<li>Risk {m.get('risk_key', '')} – Version {m.get('version_no', '')}</li>\n" for m in missing_list) + """
    </ul>
    </div>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Residual Risk Evaluation — {project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }}
        h1 {{ color: #1e40af; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
        h2 {{ color: #1e40af; margin-top: 28px; border-bottom: 2px solid #e5e7eb; padding-bottom: 5px; font-size: 1.1em; }}
        h3 {{ color: #374151; margin-top: 16px; font-size: 1em; }}
        table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.9em; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f3f4f6; font-weight: bold; }}
        .report-table th, .report-table td {{ vertical-align: top; }}
        .meta {{ color: #6b7280; font-size: 0.9em; margin-bottom: 20px; }}
        .section {{ margin: 18px 0; }}
        .statement {{ background-color: #eff6ff; border-left: 4px solid #2563eb; padding: 14px; margin: 18px 0; }}
        .warning {{ background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 14px; margin: 18px 0; }}
        ul {{ margin: 8px 0; padding-left: 24px; }}
        .counts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin: 16px 0; }}
        .count-box {{ background: #f9fafb; padding: 12px; border-radius: 6px; border: 1px solid #e5e7eb; }}
        .count-label {{ font-size: 0.85em; color: #6b7280; }}
        .count-value {{ font-size: 1.3em; font-weight: bold; color: #1f2937; }}
    </style>
</head>
<body>
    <h1>Residual Risk Evaluation</h1>
    <div class="meta">
        <p><strong>Project:</strong> {project_name}</p>
        <p><strong>Device context:</strong> {device_context}</p>
        <p><strong>Components:</strong></p>
        <ul>{comp_html}</ul>
        <p><strong>Version scope:</strong> {version_scope.replace("_", " ")}</p>
        <p><strong>Generated:</strong> {generated_at}</p>
    </div>

    <div class="section">
        <h2>1) Pre-Control Risk Summary</h2>
        <p>This section summarizes the risk picture before application of risk control measures.</p>
        <p><strong>Number of hazards / hazardous situations evaluated:</strong> {num_hazards}</p>
        <p><strong>Initial risk distribution:</strong> High: {high}, Medium: {med}, Low: {low}.</p>
        <p><strong>Identification of highest risks:</strong></p>
        <table>
            <thead><tr><th>Risk key</th><th>Hazard</th><th>Initial score</th><th>Level</th></tr></thead>
            <tbody>{highest_rows if highest_rows else '<tr><td colspan="4">No initial risk data available.</td></tr>'}</tbody>
        </table>
        <p><strong>Risk estimation methodology:</strong> {methodology}</p>
    </div>

    <div class="section">
        <h2>2) Risk Control Measures Implemented</h2>
        <p>Risk controls are implemented in accordance with ISO 14971 (inherent safety by design, protective measures, information for safety).</p>
        <h3>Design controls</h3>
        <ul>{design_html}</ul>
        <h3>Protective measures</h3>
        <ul>{protective_html}</ul>
        <h3>Information for safety (warnings, IFU)</h3>
        <ul>{info_html}</ul>
        <p>Controls are linked to risk reduction in the Residual Risk Table and in the risk item version records.</p>
    </div>

    <div class="section">
        <h2>3) Post-Control (Residual Risk) Summary</h2>
        <p><strong>Residual risk distribution:</strong> High: {res_high}, Medium: {res_med}, Low: {res_low}.</p>
        <p><strong>Effectiveness of controls:</strong> {effectiveness}</p>
        <p><strong>Remaining significant risks (if any):</strong></p>
        <table>
            <thead><tr><th>Risk key</th><th>Hazard</th><th>Residual score</th><th>Acceptability</th></tr></thead>
            <tbody>{remaining_rows if remaining_rows else '<tr><td colspan="4">None above threshold.</td></tr>'}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>4) Risk Acceptability Criteria</h2>
        <p>Risk acceptability is determined using the project Risk Acceptability Criteria (risk matrix or policy). Acceptable, ALARP (as low as reasonably practicable), and unacceptable regions are defined in accordance with ISO 14971. Reference: Risk Acceptability Criteria document and Risk Management Plan.</p>
        <table>
            <thead><tr><th>Risk level</th><th>Score range</th><th>Acceptability</th></tr></thead>
            <tbody>{thresholds_rows}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>5) Benefit-Risk Analysis</h2>
        <p>{benefit_text}</p>
    </div>

    <div class="section">
        <h2>6) Overall Residual Risk Evaluation</h2>
        <div class="statement">
            <p><strong>Overall residual risk statement:</strong></p>
            <p>{overall_statement}</p>
        </div>
    </div>

    <div class="section">
        <h2>7) Traceability</h2>
        <p>Risks are traced from Hazard Analysis / FMEA to risk controls and to residual risk evaluation.</p>
        <table>
            <thead><tr><th>Element</th><th>Source document</th><th>Content</th></tr></thead>
            <tbody>{trace_rows}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>8) Residual Risk Table</h2>
        <p>Structured summary: Hazard | Initial Risk | Controls | Residual Risk | Acceptability.</p>
        <table class="report-table">
            <thead>
                <tr>
                    <th>Hazard</th>
                    <th>Initial Risk</th>
                    <th>Controls</th>
                    <th>Residual Risk</th>
                    <th>Acceptability</th>
                </tr>
            </thead>
            <tbody>{table_body}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>9) Assumptions and Limitations</h2>
        <ul>{assumptions_html}</ul>
    </div>

    {missing_html}

    <div class="section">
        <h2>10) Approval Section</h2>
        {approval_html}
    </div>

    <p style="margin-top: 32px; font-size: 0.9em; color: #6b7280;">
        This Residual Risk Evaluation was generated by SmartRisk. It is intended for use in the risk management file and should be reviewed and approved per the Risk Management Plan. ISO 14971:2019.
    </p>
</body>
</html>"""
    return html
