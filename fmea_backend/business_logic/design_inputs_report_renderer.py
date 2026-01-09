"""
Design Inputs Documentation HTML renderer.
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


def render_design_inputs_html(evidence: Dict[str, Any], project_name: str) -> str:
    components = evidence.get("components", [])
    rows: List[Dict[str, Any]] = evidence.get("rows", [])
    counts = evidence.get("counts", {})
    generated_at = dt_datetime.now().isoformat()

    components_html = ""
    if components:
        for c in components:
            components_html += f"<li>{_esc(str(c.get('name') or c.get('id') or 'Unknown'))}</li>\n"
    else:
        components_html = "<li>All components</li>\n"

    def fmt_controls(items: List[Dict[str, Any]]) -> str:
        if not items:
            return "<span class='flag'>⚠️ Missing</span>"
        lis = []
        for it in items:
            lis.append(f"<li><strong>{_esc(it.get('control_key',''))}</strong> — {_esc(it.get('control_name',''))}</li>")
        return "<ul>" + "".join(lis) + "</ul>"

    def fmt_risks(items: List[Dict[str, Any]]) -> str:
        if not items:
            return ""
        lis = []
        for it in items:
            hazard = _esc(it.get("hazard") or "")
            harm = _esc(it.get("harm") or "")
            extra = ""
            if hazard or harm:
                extra = f" — {hazard}{(' / ' + harm) if harm else ''}"
            lis.append(f"<li><strong>{_esc(it.get('risk_key',''))}</strong>{extra}</li>")
        return "<ul>" + "".join(lis) + "</ul>"

    trs = ""
    for r in rows:
        missing = bool(r.get("completeness", {}).get("has_upstream_control") is False)
        cls = "missing" if missing else ""
        trs += f"<tr class='{cls}'>"
        trs += f"<td>{_esc(r.get('di_key',''))}</td>"
        trs += f"<td>{_esc(r.get('title',''))}</td>"
        trs += f"<td class='mono'>{_esc(r.get('requirement_text',''))}</td>"
        trs += f"<td>{_esc(r.get('status',''))}</td>"
        trs += f"<td>{fmt_controls((r.get('upstream', {}) or {}).get('risk_controls', []))}</td>"
        trs += f"<td>{fmt_risks((r.get('upstream', {}) or {}).get('risks', []))}</td>"
        # downstream summary
        dos = ((r.get('downstream', {}) or {}).get('design_outputs', []) or [])
        vvs = ((r.get('downstream', {}) or {}).get('vv_tests', []) or [])
        dos_txt = ", ".join([_esc(x.get("do_key","")) for x in dos]) if dos else "—"
        vvs_txt = ", ".join([_esc(x.get("vv_key","")) for x in vvs]) if vvs else "—"
        trs += f"<td>{dos_txt}</td>"
        trs += f"<td>{vvs_txt}</td>"
        trs += "</tr>\n"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Design Inputs Documentation - {project_name}</title>
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
    .mono {{ white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; }}
    .missing {{ background: #fef3c7; }}
    .flag {{ color: #92400e; font-weight: 600; }}
    ul {{ margin: 6px 0; padding-left: 18px; }}
  </style>
</head>
<body>
  <h1>Design Inputs Documentation</h1>

  <div class="meta">
    <p><strong>Project:</strong> {project_name}</p>
    <p><strong>Components:</strong></p>
    <ul>
{components_html}
    </ul>
    <p><strong>Generated:</strong> {generated_at}</p>
  </div>

  <div class="statement">
    <p><strong>Statement:</strong> Design Inputs are derived from Risk Controls and linked via <code>trace_links</code> (risk_control → design_input).</p>
  </div>

  <div class="counts">
    <div class="count-box">
      <div class="count-label">Design Inputs</div>
      <div class="count-value">{counts.get("design_inputs", 0)}</div>
    </div>
    <div class="count-box">
      <div class="count-label">Missing output</div>
      <div class="count-value">{counts.get("missing_output", 0)}</div>
    </div>
    <div class="count-box">
      <div class="count-label">Missing verification</div>
      <div class="count-value">{counts.get("missing_verification", 0)}</div>
    </div>
    <div class="count-box">
      <div class="count-label">Unlinked requirements</div>
      <div class="count-value">{counts.get("missing_upstream_control", 0)}</div>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th>DI Key</th>
        <th>Title</th>
        <th>Requirement Text</th>
        <th>Status</th>
        <th>Upstream Risk Control(s)</th>
        <th>Upstream Risk(s)</th>
        <th>Design Output(s)</th>
        <th>V&V Test(s)</th>
      </tr>
    </thead>
    <tbody>
      {trs if trs else "<tr><td colspan='8'>No design inputs found for this filter.</td></tr>"}
    </tbody>
  </table>
</body>
</html>"""

    return html

