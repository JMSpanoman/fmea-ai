"""
V&V Evidence Report HTML renderer.
"""

from __future__ import annotations

from datetime import datetime as dt_datetime
from typing import Any, Dict, List


def _esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


def render_vv_evidence_html(evidence: Dict[str, Any], project_name: str) -> str:
    rows: List[Dict[str, Any]] = evidence.get("rows", [])
    counts = evidence.get("counts", {})
    strength = (counts.get("strength") or {}) if isinstance(counts.get("strength"), dict) else {}
    components = evidence.get("components", [])
    generated_at = dt_datetime.now().isoformat()

    components_html = ""
    if components:
        for c in components:
            components_html += f"<li>{_esc(str(c.get('name') or c.get('id') or 'Unknown'))}</li>\n"
    else:
        components_html = "<li>All components</li>\n"

    def badge(txt: str, kind: str) -> str:
        return f"<span class='badge {kind}'>{_esc(txt)}</span>"

    trs = ""
    for r in rows:
        es = r.get("evidence_strength", "shortcut")
        es_badge = badge(es, "preferred" if es == "preferred" else ("allowed" if es == "allowed" else "shortcut"))
        st = r.get("status", "")
        st_badge = badge(st, "status")
        flags = []
        if not r.get("completeness", {}).get("has_design_output_link", False):
            flags.append("⚠ Missing DO link")
        if not r.get("completeness", {}).get("has_acceptance_criteria", True):
            flags.append("⚠ Missing AC")
        if not r.get("completeness", {}).get("has_upstream_links", True):
            flags.append("⚠ Unlinked")

        upstream = r.get("upstream", {}) or {}
        do_keys = ", ".join([x.get("do_key", "") for x in upstream.get("design_outputs", [])]) or "—"
        di_keys = ", ".join([x.get("di_key", "") for x in upstream.get("design_inputs", [])]) or "—"
        rc_keys = ", ".join([x.get("control_key", "") for x in upstream.get("risk_controls", [])]) or "—"

        ac = (r.get("acceptance_criteria") or "").strip()
        ac_short = (ac[:120] + "…") if len(ac) > 120 else ac

        trs += "<tr>"
        trs += f"<td class='mono'>{_esc(r.get('vv_key',''))}</td>"
        trs += f"<td>{_esc(r.get('title',''))}</td>"
        trs += f"<td>{_esc(r.get('test_type',''))}</td>"
        trs += f"<td>{st_badge}</td>"
        trs += f"<td>{es_badge}</td>"
        trs += f"<td class='mono'>{_esc(ac_short)}</td>"
        trs += f"<td class='mono'>{_esc(do_keys)}</td>"
        trs += f"<td class='mono'>{_esc(di_keys)}</td>"
        trs += f"<td class='mono'>{_esc(rc_keys)}</td>"
        trs += f"<td>{_esc(' • '.join(flags)) if flags else ''}</td>"
        trs += "</tr>\n"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Verification &amp; Validation Evidence Report - {project_name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; color: #111827; }}
    h1 {{ color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
    .meta {{ color: #6b7280; font-size: 0.9em; margin-bottom: 20px; }}
    .statement {{ background: #eff6ff; border-left: 4px solid #2563eb; padding: 12px; margin: 16px 0; }}
    .counts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 16px 0; }}
    .count-box {{ background: white; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; }}
    .count-label {{ font-size: 0.85em; color: #6b7280; }}
    .count-value {{ font-size: 1.4em; font-weight: bold; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px; vertical-align: top; }}
    th {{ background: #f3f4f6; text-align: left; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; white-space: pre-wrap; }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; border: 1px solid #e5e7eb; }}
    .preferred {{ background: #d1fae5; color: #065f46; border-color: #a7f3d0; }}
    .allowed {{ background: #e0f2fe; color: #075985; border-color: #bae6fd; }}
    .shortcut {{ background: #fef3c7; color: #92400e; border-color: #fde68a; }}
    .status {{ background: #f3f4f6; color: #374151; }}
    ul {{ margin: 6px 0; padding-left: 18px; }}
  </style>
</head>
<body>
  <h1>Verification &amp; Validation Evidence Report</h1>

  <div class="meta">
    <p><strong>Project:</strong> {project_name}</p>
    <p><strong>Components:</strong></p>
    <ul>
{components_html}
    </ul>
    <p><strong>Generated:</strong> {generated_at}</p>
  </div>

  <div class="statement">
    <p><strong>Statement:</strong> This report compiles V&amp;V evidence from SmartQS artifacts and trace links. Missing links indicate incomplete evidence, not missing paperwork.</p>
  </div>

  <div class="counts">
    <div class="count-box"><div class="count-label">Total tests</div><div class="count-value">{counts.get("tests", 0)}</div></div>
    <div class="count-box"><div class="count-label">Unlinked tests</div><div class="count-value">{counts.get("unlinked", 0)}</div></div>
    <div class="count-box"><div class="count-label">Missing DO link</div><div class="count-value">{counts.get("missing_design_output_link", 0)}</div></div>
    <div class="count-box"><div class="count-label">Missing acceptance criteria</div><div class="count-value">{counts.get("missing_acceptance_criteria", 0)}</div></div>
    <div class="count-box"><div class="count-label">Preferred</div><div class="count-value">{strength.get("preferred", 0)}</div></div>
    <div class="count-box"><div class="count-label">Allowed</div><div class="count-value">{strength.get("allowed", 0)}</div></div>
    <div class="count-box"><div class="count-label">Shortcut</div><div class="count-value">{strength.get("shortcut", 0)}</div></div>
  </div>

  <table>
    <thead>
      <tr>
        <th>V Key</th>
        <th>Title</th>
        <th>Type</th>
        <th>Status</th>
        <th>Evidence Strength</th>
        <th>Acceptance Criteria</th>
        <th>Upstream DO</th>
        <th>Upstream DI</th>
        <th>Upstream RC</th>
        <th>Notes</th>
      </tr>
    </thead>
    <tbody>
      {trs if trs else "<tr><td colspan='10'>No V&amp;V tests found for this filter.</td></tr>"}
    </tbody>
  </table>
</body>
</html>"""

    return html

