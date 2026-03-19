"""
Residual Risk Evaluation HTML Renderer
Generates a complete, audit-ready Residual Risk Evaluation report (ISO 14971)
with all required sections for notified body or FDA review.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone


def _norm_text(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if "unacceptable" in raw:
        return "unacceptable"
    if "benefit" in raw or "needs_benefit_risk" in raw:
        return "needs_benefit_risk"
    if "justification" in raw:
        return "acceptable_with_justification"
    if "acceptable" in raw:
        return "acceptable"
    return "unknown"


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
    thresholds_meta = evidence.get("thresholds_meta", {})
    profile = evidence.get("profile", {})
    pre = evidence.get("pre_control_summary", {})
    controls_section = evidence.get("risk_control_measures", {})
    post = evidence.get("post_control_summary", {})
    missing_list = evidence.get("missing_field_list", [])
    counts = evidence.get("counts", {})
    meta = evidence.get("metadata", {})
    data_quality = evidence.get("data_quality", {})
    risk_reduction = evidence.get("risk_reduction_summary", {})
    traceability_summary = evidence.get("traceability_summary", {})
    final_decision = evidence.get("final_decision", {})
    report_status = evidence.get("report_status", {})
    observations = evidence.get("regulatory_observations", [])
    version_scope = evidence.get("version_scope", "approved_only")
    components = evidence.get("components", [])
    generated_at = meta.get("generated_at_utc") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    generated_local = meta.get("generated_at_local") or datetime.now().strftime("%Y-%m-%d %H:%M")
    device_context = _device_context(profile, project_name)

    # Components list
    comp_html = ""
    if components:
        for c in components:
            comp_html += f"<li>{c.get('name', c.get('id', 'Unknown'))}</li>\n"
    else:
        comp_html = "<li>All project components</li>\n"

    # --- Section 0: Data quality ---
    missing_counts = data_quality.get("missingFieldCounts", {})
    dq_status = data_quality.get("dataQualityStatus", "EMPTY")
    dq_interpretation = data_quality.get("interpretation", "Residual risk evaluation cannot be meaningfully performed because no risk data is available.")
    atypical_warning = data_quality.get("atypicalWarning")
    no_approved_warning = ""
    if (data_quality.get("totalRiskItems", 0) == 0) and counts.get("excluded_versions", 0) > 0:
        no_approved_warning = f"""
        <div class="warning">
            <p><strong>⚠️ No approved hazard analysis data available</strong></p>
            <p>{counts.get("excluded_versions", 0)} risk items exist but are not approved. Only approved items are included in this report.</p>
            <p>To include data:</p>
            <ul>
                <li>review and approve hazard analysis items</li>
                <li>or generate a draft report including unapproved items</li>
            </ul>
        </div>
        """
    atypical_html = f'<div class="warning"><p><strong>{atypical_warning}</strong></p></div>' if atypical_warning else ""

    # --- Section 1: Pre-Control Risk Summary ---
    num_hazards = pre.get("number_of_hazards", len(rows))
    dist = pre.get("initial_risk_distribution", {})
    high, med, low, unk = dist.get("high", 0), dist.get("medium", 0), dist.get("low", 0), dist.get("unknown", 0)
    highest = pre.get("highest_risks", [])
    methodology = pre.get("methodology", "Risk estimation follows ISO 14971: severity of harm and probability of occurrence; risk score = severity × probability. Thresholds are defined in the project Risk Acceptability Criteria.")
    initial_scores = [r.get("initial_risk_score") for r in rows if r.get("initial_risk_score") is not None]
    highest_initial = max(initial_scores) if initial_scores else None
    avg_initial = (sum(initial_scores) / len(initial_scores)) if initial_scores else None
    highest_rows = ""
    for h in highest:
        key = h.get("risk_key", "")
        hazard = (h.get("hazard") or "")[:80]
        score = h.get("initial_score", "—")
        level = h.get("initial_level", "—")
        highest_rows += f"<tr><td>{key}</td><td>{hazard}</td><td>{score}</td><td>{level}</td></tr>\n"

    # --- Risk reduction subsection ---
    rr_text = "Risk reduction effectiveness cannot be quantitatively evaluated because paired initial and residual risk values are not available."
    if risk_reduction.get("hasComparativeData"):
        rr_text = (
            f"Risks reduced: {risk_reduction.get('reducedCount', 0)}; unchanged: {risk_reduction.get('unchangedCount', 0)}; worsened: {risk_reduction.get('worsenedCount', 0)}; "
            f"percent reduced: {risk_reduction.get('reducedPercent', 0)}%."
        )

    # --- Section 2: Risk Control Measures ---
    design_list = controls_section.get("design_controls", [])
    protective_list = controls_section.get("protective_measures", [])
    info_list = controls_section.get("information_for_safety", [])
    controls_total = len(design_list) + len(protective_list) + len(info_list)
    no_controls_count = sum(1 for r in rows if not r.get("has_linked_controls"))
    controls_without_verification = sum(1 for r in rows if r.get("has_linked_controls") and not r.get("verification_refs"))
    design_html = "".join(f"<li>{x}</li>\n" for x in design_list) if design_list else "<li>Design controls are documented in the Hazard Analysis and Risk Control documentation for each risk.</li>\n"
    protective_html = "".join(f"<li>{x}</li>\n" for x in protective_list) if protective_list else "<li>Protective measures (e.g. hardware safeguards, software interlocks) are implemented as documented in risk control records.</li>\n"
    info_html = "".join(f"<li>{x}</li>\n" for x in info_list) if info_list else "<li>Information for safety (labeling, IFU, warnings) is defined in the risk control and labeling documentation.</li>\n"

    # --- Section 3: Post-Control Summary ---
    res_dist = post.get("residual_risk_distribution", {})
    res_high, res_med, res_low, res_unknown = (
        res_dist.get("high", 0),
        res_dist.get("medium", 0),
        res_dist.get("low", 0),
        res_dist.get("unknown", 0),
    )
    effectiveness = post.get(
        "effectiveness_narrative",
        "Control effectiveness cannot be evaluated because linked initial and residual risk data are unavailable."
    )
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
        "Benefit-risk evaluation references intended use, clinical benefit, target patient population, and use environment where documented."
    )
    overall_statement = final_decision.get(
        "narrative",
        "An overall residual risk evaluation cannot be concluded because no risk data was available in the selected export scope."
    )
    benefit_required = int(final_decision.get("benefitRiskRequiredCount", 0))
    unacceptable_count = int(final_decision.get("unacceptableResidualRiskCount", 0))

    # --- Section 7: Traceability ---
    trace_rows = ""
    for r in rows:
        trace_rows += (
            "<tr>"
            f"<td>{r.get('risk_key','—')}</td>"
            f"<td>{(r.get('hazard') or '—')[:80]}</td>"
            f"<td>{(r.get('hazardous_situation') or '—')[:80]}</td>"
            f"<td>{r.get('initial_risk_score') if r.get('initial_risk_score') is not None else '—'}</td>"
            f"<td>{(r.get('controls_summary') or '—')[:80]}</td>"
            f"<td>{'mixed' if r.get('has_linked_controls') else 'missing'}</td>"
            f"<td>{'linked' if r.get('verification_refs') else 'missing'}</td>"
            f"<td>{r.get('residual_risk_score') if r.get('residual_risk_score') is not None else '—'}</td>"
            f"<td>{r.get('residual_acceptability') or '—'}</td>"
            f"<td>{'required' if _norm_text(r.get('residual_acceptability')) in {'needs_benefit_risk', 'unacceptable'} else 'n/a'}</td>"
            "</tr>"
        )
    if not trace_rows:
        trace_rows = "<tr><td colspan='10'>No traceability data available in selected scope.</td></tr>"

    # --- Section 8: Residual Risk Table ---
    table_body = ""
    for r in rows:
        hazard = (r.get("hazard") or "—")[:120]
        haz_sit = (r.get("hazardous_situation") or "—")[:120]
        seq = (r.get("sequence_of_events") or "—")[:80]
        harm = (r.get("harm") or "—")[:80]
        init = r.get("initial_risk_score") is not None and f"S{r.get('initial_severity')}×P{r.get('initial_probability')}={r.get('initial_risk_score')}" or "—"
        controls = (r.get("controls_summary") or "—")[:100]
        res = r.get("residual_risk_display") or (str(r.get("residual_risk_score")) if r.get("residual_risk_score") is not None else "—")
        acc = r.get("residual_acceptability") or "—"
        acc_src = r.get("acceptability_source") or "—"
        br = "yes" if _norm_text(acc) in {"needs_benefit_risk", "unacceptable"} else "no"
        table_body += (
            f"<tr><td>{r.get('risk_key','—')}</td><td>{hazard}</td><td>{haz_sit}</td><td>{seq}</td><td>{harm}</td>"
            f"<td>{init}</td><td>{controls}</td><td>{res}</td><td>{acc}</td><td>{acc_src}</td><td>{br}</td></tr>\n"
        )
    if not table_body:
        table_body = "<tr><td colspan=\"11\">No residual risk data is available in the selected export scope. Populate approved risk item versions with hazard, initial risk, controls, and residual risk information to generate this table.</td></tr>\n"

    # --- Section 9: Assumptions and Limitations ---
    assumptions = [
        "Version scope limitation: " + str(meta.get("version_scope_description") or version_scope.replace("_", " ")) + ".",
        "Approved-only inclusion: " + ("yes" if version_scope == "approved_only" else "no"),
        "Where residual severity or probability was not recorded, acceptability may be inferred from project thresholds; such items are marked in the table.",
        "Device context (intended use, user population, use environment) is taken from the project profile where available; otherwise a generic medical device context is assumed.",
    ]
    if missing_list:
        assumptions.append(f"{len(missing_list)} risk version(s) have missing residual risk fields; these are listed in the Missing Residual Fields section and should be completed for a full evaluation.")
    assumptions_html = "".join(f"<li>{a}</li>\n" for a in assumptions)

    # --- Section 10: Approval ---
    approval_html = """
    <table class="report-table">
    <thead><tr><th>Field</th><th>Value</th></tr></thead>
    <tbody>
    <tr><td>Report status</td><td>""" + str(report_status.get("reportStatus") or "Draft") + """</td></tr>
    <tr><td>Blocking reason</td><td>""" + str(report_status.get("blockingReason") or "—") + """</td></tr>
    <tr><td>Prepared by</td><td>[To be assigned] / e-signature: __________</td></tr>
    <tr><td>Reviewed by</td><td>[To be assigned] / e-signature: __________</td></tr>
    <tr><td>Approved by</td><td>[To be assigned] / e-signature: __________</td></tr>
    <tr><td>Date generated</td><td>""" + str(generated_at) + """</td></tr>
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
        <p><strong>Version scope:</strong> {meta.get("version_scope_description") or version_scope.replace("_", " ")}</p>
        <p><strong>Total included versions:</strong> {meta.get("total_included_versions", len(rows))}</p>
        <p><strong>Total excluded versions:</strong> {meta.get("total_excluded_versions", 0)}</p>
        <p><strong>Generated (UTC):</strong> {generated_at}</p>
        <p><strong>Generated (local):</strong> {generated_local}</p>
        <p><strong>Last approved risk item update:</strong> {meta.get("last_approved_risk_item_update") or "—"}</p>
    </div>

    <div class="section">
        <h2>0) Data Quality & Completeness Assessment</h2>
        <div class="counts">
            <div class="count-box"><div class="count-label">Total risk items included</div><div class="count-value">{data_quality.get("totalRiskItems", 0)}</div></div>
            <div class="count-box"><div class="count-label">Hazards/hazardous situations</div><div class="count-value">{data_quality.get("totalHazardsOrSituations", 0)}</div></div>
            <div class="count-box"><div class="count-label">Completeness score</div><div class="count-value">{data_quality.get("completenessScore", 0)}%</div></div>
            <div class="count-box"><div class="count-label">Data quality status</div><div class="count-value">{dq_status}</div></div>
        </div>
        <ul>
            <li>Missing initial severity: {missing_counts.get("initial_severity", 0)}</li>
            <li>Missing initial probability: {missing_counts.get("initial_probability", 0)}</li>
            <li>Missing residual severity: {missing_counts.get("residual_severity", 0)}</li>
            <li>Missing residual probability: {missing_counts.get("residual_probability", 0)}</li>
            <li>Missing linked controls: {missing_counts.get("linked_controls", 0)}</li>
            <li>Missing acceptability decision: {missing_counts.get("acceptability_decision", 0)}</li>
        </ul>
        <p><strong>Interpretation:</strong> {dq_interpretation}</p>
        {no_approved_warning}
        {atypical_html}
    </div>

    <div class="section">
        <h2>1) Pre-Control Risk Summary</h2>
        <p>This section summarizes the risk picture before application of risk control measures.</p>
        <p><strong>Total risk items included:</strong> {len(rows)}</p>
        <p><strong>Number of hazards / hazardous situations evaluated:</strong> {num_hazards}</p>
        <p><strong>Initial risk distribution:</strong> High/Critical: {high}, Medium: {med}, Low: {low}, Unknown: {unk}.</p>
        <p><strong>Highest initial risk score:</strong> {highest_initial if highest_initial is not None else "—"}</p>
        <p><strong>Average initial risk score:</strong> {round(avg_initial, 2) if avg_initial is not None else "—"}</p>
        <p><strong>Identification of highest risks:</strong></p>
        <table>
            <thead><tr><th>Risk key</th><th>Hazard</th><th>Initial score</th><th>Level</th></tr></thead>
            <tbody>{highest_rows if highest_rows else '<tr><td colspan="4">No pre-control risk data is available for the selected version scope.</td></tr>'}</tbody>
        </table>
        <p><strong>Risk estimation methodology:</strong> {methodology}</p>
        <h3>Risk Reduction Overview</h3>
        <p>{rr_text}</p>
        <ul>
            <li>Average initial score: {risk_reduction.get("averageInitialScore") if risk_reduction.get("averageInitialScore") is not None else "—"}</li>
            <li>Average residual score: {risk_reduction.get("averageResidualScore") if risk_reduction.get("averageResidualScore") is not None else "—"}</li>
            <li>Mean risk reduction delta: {risk_reduction.get("meanRiskReductionDelta") if risk_reduction.get("meanRiskReductionDelta") is not None else "—"}</li>
            <li>Inherent safety by design links: {risk_reduction.get("controlTypeBreakdown", {}).get("inherent_safety_by_design", 0)}</li>
            <li>Protective measures links: {risk_reduction.get("controlTypeBreakdown", {}).get("protective_measures", 0)}</li>
            <li>Information for safety links: {risk_reduction.get("controlTypeBreakdown", {}).get("information_for_safety", 0)}</li>
        </ul>
    </div>

    <div class="section">
        <h2>2) Risk Control Measures Implemented</h2>
        <p>Risk controls are implemented in accordance with ISO 14971 (inherent safety by design, protective measures, information for safety).</p>
        <ul>
            <li>Total linked control measures: {controls_total}</li>
            <li>Count by type - design controls: {len(design_list)}, protective measures: {len(protective_list)}, information for safety: {len(info_list)}</li>
            <li>Risk items with no linked controls: {no_controls_count}</li>
            <li>Controls lacking verification linkage: {controls_without_verification} (where linkage data is available)</li>
        </ul>
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
        <p><strong>Residual risk distribution:</strong> High: {res_high}, Medium: {res_med}, Low: {res_low}, Unknown: {res_unknown}.</p>
        <p><strong>Effectiveness of controls:</strong> {effectiveness}</p>
        <ul>
            <li>Count above threshold: {len(remaining)}</li>
            <li>Count requiring benefit-risk review: {benefit_required}</li>
            <li>Count unacceptable: {unacceptable_count}</li>
            <li>Count acceptable with justification: {sum(1 for r in rows if _norm_text(r.get("residual_acceptability")) == "acceptable_with_justification")}</li>
            <li>Count fully acceptable: {sum(1 for r in rows if _norm_text(r.get("residual_acceptability")) == "acceptable")}</li>
        </ul>
        <p><strong>Remaining significant risks (if any):</strong></p>
        <table>
            <thead><tr><th>Risk key</th><th>Hazard</th><th>Residual score</th><th>Acceptability</th></tr></thead>
            <tbody>{remaining_rows if remaining_rows else '<tr><td colspan="4">None above threshold.</td></tr>'}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>4) Risk Acceptability Criteria</h2>
        <p>Risk acceptability is determined using the project Risk Acceptability Criteria (risk matrix or policy). Acceptable, ALARP (as low as reasonably practicable), and unacceptable regions are defined in accordance with ISO 14971. Reference: Risk Acceptability Criteria document and Risk Management Plan.</p>
        <p><strong>Threshold source:</strong> {thresholds_meta.get("source", "project_risk_matrix_or_policy")} | <strong>Revision:</strong> {thresholds_meta.get("revision", "latest")} | <strong>Profile:</strong> {thresholds_meta.get("profile", "default_med_device")}</p>
        <p><strong>Acceptability source in this report:</strong> recorded fields when available; inferred from thresholds when missing.</p>
        <p><em>For records lacking an explicit acceptability decision, acceptability was inferred from configured project thresholds.</em></p>
        <table>
            <thead><tr><th>Risk level</th><th>Score range</th><th>Acceptability</th></tr></thead>
            <tbody>{thresholds_rows}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>5) Benefit-Risk Analysis</h2>
        <p>{benefit_text}</p>
        <ul>
            <li>Intended use: {(profile.get("intended_use") or "—")}</li>
            <li>Target patient population: {(profile.get("user_population") or "—")}</li>
            <li>Use environment: {(profile.get("use_environment") or "—")}</li>
            <li>Device class / implantable / life-sustaining flags: {(profile.get("device_class") or "—")} / {(profile.get("implantable") or "—")} / {(profile.get("life_sustaining") or "—")}</li>
        </ul>
        <p>{'No residual risks in the selected export scope require a formal benefit-risk override based on current project thresholds.' if benefit_required == 0 else f'{benefit_required} residual risk item(s) require formal benefit-risk review.'}</p>
    </div>

    <div class="section">
        <h2>6) Overall Residual Risk Evaluation</h2>
        <div class="statement">
            <p><strong>Final determination:</strong> {final_decision.get("finalDetermination", "NOT EVALUABLE")}</p>
            <p><strong>Overall residual risk statement:</strong></p>
            <p>{overall_statement}</p>
            <p><strong>Basis:</strong> {'; '.join(final_decision.get("basis", []))}</p>
            <p><strong>Limitations:</strong> {'; '.join(final_decision.get("limitations", [])) or '—'}</p>
            <p><strong>Further review required:</strong> {'yes' if final_decision.get("requiresFurtherReview") else 'no'}</p>
            <p><strong>Approval blocked/pending:</strong> {'yes' if final_decision.get("approvalBlocked") else 'no'} {('- ' + str(report_status.get('blockingReason'))) if report_status.get('blockingReason') else ''}</p>
        </div>
    </div>

    <div class="section">
        <h2>7) Traceability</h2>
        <p>Risks are traced from hazard records to controls, verification references, residual risk, and acceptability outcomes.</p>
        <table>
            <thead><tr><th>Risk ID / Key</th><th>Hazard</th><th>Hazardous Situation</th><th>Initial Risk</th><th>Control Reference</th><th>Control Type</th><th>Verification/Validation Ref</th><th>Residual Risk</th><th>Acceptability</th><th>Benefit-Risk Link</th></tr></thead>
            <tbody>{trace_rows}</tbody>
        </table>
        <ul>
            <li>Fully traceable risk items: {traceability_summary.get("fullyTraceable", 0)}</li>
            <li>Partially traceable risk items: {traceability_summary.get("partiallyTraceable", 0)}</li>
            <li>Missing control linkage: {traceability_summary.get("missingControlLinkage", 0)}</li>
            <li>Missing verification linkage: {traceability_summary.get("missingVerificationLinkage", 0)}</li>
        </ul>
    </div>

    <div class="section">
        <h2>8) Residual Risk Table</h2>
        <p>Structured summary of residual risk records in selected scope.</p>
        <table class="report-table">
            <thead>
                <tr>
                    <th>Risk key</th>
                    <th>Hazard</th>
                    <th>Hazardous situation</th>
                    <th>Sequence of events</th>
                    <th>Harm</th>
                    <th>Initial Risk</th>
                    <th>Controls</th>
                    <th>Residual Risk</th>
                    <th>Acceptability</th>
                    <th>Acceptability Source</th>
                    <th>Benefit-risk required?</th>
                </tr>
            </thead>
            <tbody>{table_body}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>Residual Risk Data Gaps and Regulatory Observations</h2>
        <ul>
            {''.join(f'<li>{o}</li>' for o in observations)}
        </ul>
    </div>

    <div class="section">
        <h2>9) Assumptions and Limitations</h2>
        <ul>{assumptions_html}</ul>
        <p><strong>Report readiness:</strong> {"ready for formal review" if dq_status == "COMPLETE" and len(rows) > 0 and version_scope == "approved_only" else "draft / pending completion of source risk records"}</p>
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
