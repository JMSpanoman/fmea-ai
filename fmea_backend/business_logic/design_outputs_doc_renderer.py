"""
HTML renderer for Design Outputs Documentation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def render_design_outputs_doc_html(evidence: Dict[str, Any]) -> str:
    generated_at = datetime.utcnow().isoformat()
    components = evidence.get("components") or []
    comp_str = ", ".join([c.get("name") for c in components if isinstance(c, dict) and c.get("name")]) or "All"

    counts = evidence.get("counts") or {}
    rows = evidence.get("rows") or []

    def esc(s: Any) -> str:
        return (
            str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    table_rows = []
    for r in rows:
        upstream_dis = r.get("upstream", {}).get("design_inputs", [])
        downstream_vv = r.get("downstream", {}).get("vv_tests", [])
        impl_chip = "✅" if r.get("completeness", {}).get("has_implementation_link") else "⚠ Missing DI link"
        ver_chip = "✅" if r.get("completeness", {}).get("has_verification_link") else "⚠ Missing V&V link"

        upstream_txt = "<br/>".join([f"{esc(d.get('di_key'))}: {esc(d.get('title'))}" for d in upstream_dis]) or "—"
        downstream_txt = "<br/>".join([f"{esc(v.get('vv_key'))}: {esc(v.get('title'))}" for v in downstream_vv]) or "—"

        table_rows.append(
            f"""
            <tr>
              <td>{esc(r.get('do_key'))}</td>
              <td>{esc(r.get('title'))}</td>
              <td>{esc(r.get('status') or '')}</td>
              <td style="max-width:520px">{esc(r.get('description') or '')}</td>
              <td>{upstream_txt}</td>
              <td>{downstream_txt}</td>
              <td>{impl_chip}<br/>{ver_chip}</td>
            </tr>
            """
        )

    tbody_html = "".join(table_rows) if table_rows else '<tr><td colspan="7">No design outputs found.</td></tr>'

    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Design Outputs Documentation</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; padding: 24px; }}
      h1, h2 {{ margin: 0 0 12px 0; }}
      .meta {{ color: #555; margin-bottom: 16px; }}
      table {{ border-collapse: collapse; width: 100%; }}
      th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
      th {{ background: #f6f6f6; text-align: left; }}
      .summary {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 16px 0; }}
      .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 12px; }}
      .k {{ color: #666; font-size: 12px; }}
      .v {{ font-weight: 600; font-size: 18px; }}
    </style>
  </head>
  <body>
    <h1>Design Outputs Documentation</h1>
    <div class="meta">
      <div><b>Generated:</b> {esc(generated_at)}</div>
      <div><b>Components:</b> {esc(comp_str)}</div>
      <div style="margin-top:8px;">
        Design Outputs are implementation artifacts. This document is generated from SmartQS records and trace links.
        Missing links indicate incomplete evidence—not missing paperwork.
      </div>
    </div>

    <div class="summary">
      <div class="card"><div class="k">Design Outputs</div><div class="v">{esc(counts.get('design_outputs', 0))}</div></div>
      <div class="card"><div class="k">Missing DI link</div><div class="v">{esc(counts.get('missing_implementation_link', 0))}</div></div>
      <div class="card"><div class="k">Missing V&V link</div><div class="v">{esc(counts.get('missing_verification_link', 0))}</div></div>
    </div>

    <h2>Register</h2>
    <table>
      <thead>
        <tr>
          <th>DO Key</th>
          <th>Title</th>
          <th>Status</th>
          <th>Description</th>
          <th>Upstream Design Inputs</th>
          <th>Downstream V&amp;V Tests</th>
          <th>Completeness</th>
        </tr>
      </thead>
      <tbody>
        {tbody_html}
      </tbody>
    </table>
  </body>
</html>
""".strip()

