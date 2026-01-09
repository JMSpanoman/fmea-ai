"""
Traceability Matrix HTML Renderer
Generates audit-ready Traceability Matrix HTML report from trace_links evidence.
"""

from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime as dt_datetime


def _escape(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


def render_traceability_matrix_html(evidence: Dict[str, Any], project_name: str) -> str:
    rows: List[Dict[str, Any]] = evidence.get("rows", [])
    components = evidence.get("components", [])
    counts = evidence.get("counts", {})
    generated_at = dt_datetime.now().isoformat()

    components_html = ""
    if components:
        for comp in components:
            comp_name = comp.get("name", comp.get("id", "Unknown"))
            components_html += f"<li>{_escape(str(comp_name))}</li>\n"
    else:
        components_html = "<li>All components</li>\n"

    # Table rows
    trs = ""
    for r in rows:
        trs += "<tr>"
        trs += f"<td>{_escape(r.get('from_type',''))}</td>"
        trs += f"<td>{_escape(r.get('from_display',''))}</td>"
        trs += f"<td>{_escape(r.get('link_type',''))}</td>"
        trs += f"<td>{_escape(r.get('to_type',''))}</td>"
        trs += f"<td>{_escape(r.get('to_display',''))}</td>"
        trs += f"<td>{_escape(r.get('rationale') or '')}</td>"
        trs += f"<td>{_escape((r.get('created_at') or '')[:19])}</td>"
        trs += "</tr>\n"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Traceability Matrix - {project_name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; color: #111827; }}
    h1 {{ color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
    .meta {{ color: #6b7280; font-size: 0.9em; margin-bottom: 20px; }}
    .section {{ margin: 20px 0; padding: 15px; background: #f9fafb; border-radius: 6px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px; vertical-align: top; }}
    th {{ background: #f3f4f6; text-align: left; }}
    .counts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 16px 0; }}
    .count-box {{ background: white; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; }}
    .count-label {{ font-size: 0.85em; color: #6b7280; }}
    .count-value {{ font-size: 1.4em; font-weight: bold; color: #111827; }}
    ul {{ margin: 8px 0; padding-left: 22px; }}
  </style>
</head>
<body>
  <h1>Traceability Matrix</h1>

  <div class="meta">
    <p><strong>Project:</strong> {project_name}</p>
    <p><strong>Components:</strong></p>
    <ul>
{components_html}
    </ul>
    <p><strong>Generated:</strong> {generated_at}</p>
  </div>

  <div class="counts">
    <div class="count-box">
      <div class="count-label">Links</div>
      <div class="count-value">{counts.get("links", 0)}</div>
    </div>
  </div>

  <div class="section">
    <h2>Trace Links</h2>
    <table>
      <thead>
        <tr>
          <th>From Type</th>
          <th>From</th>
          <th>Link Type</th>
          <th>To Type</th>
          <th>To</th>
          <th>Rationale</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        {trs if trs else "<tr><td colspan='7'>No trace links found for this project.</td></tr>"}
      </tbody>
    </table>
  </div>
</body>
</html>"""

    return html

