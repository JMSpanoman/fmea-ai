"""
Deterministic CAPA controlled-document builder (JSON in Document.content for type=capa).

- Single structured object; no duplicated scaffolds.
- AI enriches only `ai_assist` (merged server-side; never concatenated with a second template).
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Tuple

from schemas.capa_document_record import (
    CapaDocumentRecord,
    CapaDocStatus,
)


def build_capa_document_record(*, project_id: str, project_name: Optional[str] = None) -> CapaDocumentRecord:
    """Step 1: deterministic base record (no placeholder prose like '(blank)')."""
    _ = project_name  # reserved for future deterministic fills from project profile
    return CapaDocumentRecord(
        project_id=project_id,
        capa_id="CAPA-001",
        status=CapaDocStatus.DRAFT,
        legacy_format=False,
    )


def compute_gates(rec: Dict[str, Any]) -> Dict[str, bool]:
    """Workflow gates (computed; not authoritative approval)."""

    def _nonempty_str(v: Any) -> bool:
        return isinstance(v, str) and bool(v.strip())

    t = rec.get("trigger") if isinstance(rec.get("trigger"), dict) else {}
    trigger_ok = any(_nonempty_str(t.get(k)) for k in ("type", "reference")) or (
        t.get("date_detected") not in (None, "")
    )

    p = rec.get("problem_definition") if isinstance(rec.get("problem_definition"), dict) else {}
    prob_ok = _nonempty_str(p.get("statement"))

    c = rec.get("containment") if isinstance(rec.get("containment"), dict) else {}
    actions = c.get("actions") if isinstance(c.get("actions"), list) else []
    cont_ok = len(actions) > 0 or bool(c.get("implemented"))

    can_start_rca = bool(trigger_ok and prob_ok and cont_ok)

    rca = rec.get("root_cause") if isinstance(rec.get("root_cause"), dict) else {}
    ev = rca.get("evidence") if isinstance(rca.get("evidence"), list) else []
    can_approve_root_cause = len([x for x in ev if _nonempty_str(x)]) > 0

    corr = rec.get("corrective_actions") if isinstance(rec.get("corrective_actions"), list) else []
    prev = rec.get("preventive_actions") if isinstance(rec.get("preventive_actions"), list) else []

    def _done(a: Any) -> bool:
        if not isinstance(a, dict):
            return False
        s = (a.get("status") or "").strip().lower()
        return s in {"complete", "closed", "done", "implemented"}

    have_actions = len(corr) + len(prev) > 0
    actions_ok = have_actions and all(_done(a) for a in corr) and all(_done(a) for a in prev)

    eff = rec.get("effectiveness_result")
    eff_ok = False
    if isinstance(eff, dict):
        ids = eff.get("referenced_evidence_ids") if isinstance(eff.get("referenced_evidence_ids"), list) else []
        eff_ok = _nonempty_str(eff.get("evidence_summary")) or len(ids) > 0

    appr = rec.get("approvals") if isinstance(rec.get("approvals"), list) else []
    appr_ok = len(appr) > 0 and all(
        isinstance(a, dict) and (a.get("status") or "").strip().lower() == "approved" for a in appr
    )

    can_close = bool(actions_ok and eff_ok and appr_ok)

    return {
        "can_start_rca": can_start_rca,
        "can_approve_root_cause": can_approve_root_cause,
        "can_close": can_close,
    }


def _deep_merge_ai_assist(base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Shallow merge for ai_assist keys only."""
    out = dict(base)
    cur = dict(out.get("ai_assist") or {}) if isinstance(out.get("ai_assist"), dict) else {}
    for k, v in incoming.items():
        if k in {"problem_review"} and v is not None:
            cur[k] = v
        elif k in {"root_cause_challenges", "missing_information", "suggested_actions"} and isinstance(v, list):
            cur[k] = v
    out["ai_assist"] = cur
    return out


def finalize_record_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recompute gates from current dict; ensure gates key exists."""
    data = dict(data)
    ai = data.get("ai_assist")
    if isinstance(ai, dict):
        pr = ai.get("problem_review")
        lists_ok = any(
            isinstance(ai.get(k), list) and len(ai.get(k) or []) > 0
            for k in ("root_cause_challenges", "missing_information", "suggested_actions")
        )
        if not pr and not lists_ok:
            data["ai_assist"] = None
    data["gates"] = compute_gates(data)
    return data


def merge_ai_assist_only(base: Dict[str, Any], ai_assist: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Step 3: merge AI reviewer output without touching structural fields."""
    if not ai_assist:
        return finalize_record_dict(base)
    clean = {
        k: v
        for k, v in ai_assist.items()
        if k in {"problem_review", "root_cause_challenges", "missing_information", "suggested_actions"}
    }
    merged = _deep_merge_ai_assist(base, clean)
    return finalize_record_dict(merged)


def parse_capa_document_content(content: Optional[str]) -> Tuple[Optional[Dict[str, Any]], bool]:
    """
    Returns (record_dict_or_none, legacy_format).
    Legacy = old plain-text CAPA bodies that cannot be parsed as JSON.
    """
    c = (content or "").strip()
    if not c:
        return None, False
    if c.startswith("{"):
        try:
            data = json.loads(c)
            if isinstance(data, dict) and ("project_id" in data or data.get("schema_version")):
                return data, bool(data.get("legacy_format"))
        except Exception:
            pass
    low = c.lower()
    if "capa starter" in low:
        return None, True
    if "capa — draft" in low or "sample empty entry" in low or "(blank)" in low:
        return None, True
    if re.match(r"^\s*capa\b", low):
        return None, True
    return None, True


def load_or_build_capa_record(
    content: Optional[str],
    *,
    project_id: str,
    project_name: str,
) -> Dict[str, Any]:
    parsed, legacy = parse_capa_document_content(content)
    if parsed and not legacy:
        # Ensure gates exist
        return finalize_record_dict(parsed)
    base = build_capa_document_record(project_id=project_id, project_name=project_name)
    d = base.model_dump(mode="json")
    if legacy:
        d["legacy_format"] = True
        raw = (content or "").strip()
        if raw:
            d["legacy_text"] = raw
    return finalize_record_dict(d)


def serialize_capa_document(record: Dict[str, Any] | CapaDocumentRecord) -> str:
    if isinstance(record, CapaDocumentRecord):
        data = record.model_dump(mode="json")
    else:
        data = dict(record)
    data = finalize_record_dict(data)
    return json.dumps(data, indent=2, ensure_ascii=False)


def render_capa_document_html(
    record: Dict[str, Any],
    *,
    title: str,
    project_name: str,
    doc_status: str,
    version: int,
) -> str:
    """Readable HTML export for structured CAPA JSON."""
    import html as html_mod

    def esc(x: Any) -> str:
        if x is None:
            return "—"
        if isinstance(x, (list, dict)):
            return html_mod.escape(json.dumps(x, ensure_ascii=False))
        return html_mod.escape(str(x))

    def _nonempty_str(x: Any) -> bool:
        return isinstance(x, str) and bool(x.strip())

    ai = record.get("ai_assist") if isinstance(record.get("ai_assist"), dict) else {}
    gates = record.get("gates") if isinstance(record.get("gates"), dict) else {}

    sections: list[str] = []

    def block(title_h: str, inner: str) -> None:
        sections.append(f'<section class="capa-sec"><h2>{html_mod.escape(title_h)}</h2>{inner}</section>')

    t = record.get("trigger") or {}
    block(
        "Trigger",
        f"<dl>"
        f"<dt>Type</dt><dd>{esc(t.get('type'))}</dd>"
        f"<dt>Reference</dt><dd>{esc(t.get('reference'))}</dd>"
        f"<dt>Date detected</dt><dd>{esc(t.get('date_detected'))}</dd>"
        f"</dl>",
    )

    p = record.get("problem_definition") or {}
    block(
        "Problem definition",
        f"<dl>"
        f"<dt>Statement</dt><dd>{esc(p.get('statement'))}</dd>"
        f"<dt>Scope</dt><dd>{esc(p.get('scope'))}</dd>"
        f"<dt>Impact</dt><dd>{esc(p.get('impact'))}</dd>"
        f"</dl>",
    )

    c = record.get("containment") or {}
    acts = c.get("actions") if isinstance(c.get("actions"), list) else []
    act_html = "<ul>" + "".join(f"<li>{esc(a)}</li>" for a in acts) + "</ul>" if acts else "<p>—</p>"
    block(
        "Containment",
        f"{act_html}"
        f"<p><strong>Implemented:</strong> {esc(c.get('implemented'))} &nbsp; "
        f"<strong>Verified:</strong> {esc(c.get('verified'))}</p>",
    )

    rca = record.get("root_cause") or {}
    ev = rca.get("evidence") if isinstance(rca.get("evidence"), list) else []
    ev_html = "<ul>" + "".join(f"<li>{esc(e)}</li>" for e in ev) + "</ul>" if ev else "<p>—</p>"
    block(
        "Root cause",
        f"<dl>"
        f"<dt>Method</dt><dd>{esc(rca.get('method'))}</dd>"
        f"<dt>Description</dt><dd>{esc(rca.get('description'))}</dd>"
        f"<dt>Status</dt><dd>{esc(rca.get('status'))}</dd>"
        f"</dl>"
        f"<h3>Evidence</h3>{ev_html}",
    )

    def actions_table(label: str, key: str) -> None:
        rows = record.get(key) if isinstance(record.get(key), list) else []
        if not rows:
            block(label, "<p>—</p>")
            return
        thead = "<tr><th>ID</th><th>Description</th><th>Owner</th><th>Due</th><th>Status</th></tr>"
        body = ""
        for a in rows:
            if not isinstance(a, dict):
                continue
            body += (
                f"<tr><td>{esc(a.get('id'))}</td><td>{esc(a.get('description'))}</td>"
                f"<td>{esc(a.get('owner'))}</td><td>{esc(a.get('due_date'))}</td><td>{esc(a.get('status'))}</td></tr>"
            )
        block(label, f"<table class='capa-table'><thead>{thead}</thead><tbody>{body}</tbody></table>")

    actions_table("Corrective actions", "corrective_actions")
    actions_table("Preventive actions", "preventive_actions")

    ep = record.get("effectiveness_plan") or {}
    block(
        "Effectiveness plan",
        f"<dl>"
        f"<dt>Criteria</dt><dd>{esc(ep.get('criteria'))}</dd>"
        f"<dt>Method</dt><dd>{esc(ep.get('method'))}</dd>"
        f"<dt>Due date</dt><dd>{esc(ep.get('due_date'))}</dd>"
        f"</dl>",
    )

    er = record.get("effectiveness_result")
    if isinstance(er, dict):
        block(
            "Effectiveness result",
            f"<dl>"
            f"<dt>Evidence summary</dt><dd>{esc(er.get('evidence_summary'))}</dd>"
            f"<dt>Result</dt><dd>{esc(er.get('result'))}</dd>"
            f"<dt>Conclusion</dt><dd>{esc(er.get('conclusion'))}</dd>"
            f"</dl>",
        )

    rl = record.get("risk_linkage") or {}
    for label, k in (("Hazards", "hazards"), ("FMEA rows", "fmea_rows"), ("Risk controls", "risk_controls")):
        xs = rl.get(k) if isinstance(rl.get(k), list) else []
        inner = "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in xs) + "</ul>" if xs else "<p>—</p>"
        block(f"Risk linkage — {label}", inner)

    appr = record.get("approvals") if isinstance(record.get("approvals"), list) else []
    if appr:
        body = ""
        for a in appr:
            if not isinstance(a, dict):
                continue
            body += f"<tr><td>{esc(a.get('id'))}</td><td>{esc(a.get('kind'))}</td><td>{esc(a.get('status'))}</td><td>{esc(a.get('approver_name'))}</td></tr>"
        block("Approvals", f"<table class='capa-table'><thead><tr><th>ID</th><th>Kind</th><th>Status</th><th>Approver</th></tr></thead><tbody>{body}</tbody></table>")
    else:
        block("Approvals", "<p>—</p>")

    dates = record.get("dates") or {}
    block(
        "Dates",
        f"<dl>"
        f"<dt>Opened</dt><dd>{esc(dates.get('opened'))}</dd>"
        f"<dt>Target</dt><dd>{esc(dates.get('target'))}</dd>"
        f"<dt>Closed</dt><dd>{esc(dates.get('closed'))}</dd>"
        f"</dl>",
    )

    gates_html = (
        f"<ul class='capa-gates'>"
        f"<li><strong>Can start RCA:</strong> {esc(gates.get('can_start_rca'))}</li>"
        f"<li><strong>Can approve root cause:</strong> {esc(gates.get('can_approve_root_cause'))}</li>"
        f"<li><strong>Can close:</strong> {esc(gates.get('can_close'))}</li>"
        f"</ul>"
    )
    block("Workflow gates (computed)", gates_html)

    ai_panel = ""
    if any(ai.get(k) for k in ("problem_review",)) or any(
        ai.get(k) for k in ("root_cause_challenges", "missing_information", "suggested_actions") if ai.get(k)
    ):
        pr = esc(ai.get("problem_review")) if ai.get("problem_review") else "—"

        def list_sec(name: str, key: str) -> str:
            xs = ai.get(key) if isinstance(ai.get(key), list) else []
            if not xs:
                return ""
            return "<h3>" + html_mod.escape(name) + "</h3><ul>" + "".join(f"<li>{esc(i)}</li>" for i in xs) + "</ul>"

        ai_panel = (
            f'<aside class="capa-ai-assist">'
            f"<h2>AI assist (review only — not the controlled record)</h2>"
            f"<p><strong>Problem review</strong></p><p>{pr}</p>"
            f"{list_sec('Root cause challenges', 'root_cause_challenges')}"
            f"{list_sec('Missing information', 'missing_information')}"
            f"{list_sec('Suggested actions', 'suggested_actions')}"
            f"</aside>"
        )

    legacy_note = ""
    if _nonempty_str(record.get("legacy_text")):
        legacy_note = (
            f'<div class="banner" style="margin-bottom:16px;background:#fffbeb;border:1px solid #fcd34d;padding:12px 16px;border-radius:8px;">'
            f"<strong>legacy_text preserved</strong> (plain-text CAPA migrated; see structured fields above).</div>"
            f"<details style='margin-bottom:16px;'><summary>Original plain-text excerpt</summary>"
            f"<pre style='white-space:pre-wrap;background:#f9fafb;padding:12px;border-radius:8px;'>"
            f"{esc(record.get('legacy_text'))}</pre></details>"
        )

    body_inner = (
        f'{legacy_note}<div class="capa-grid"><main class="capa-main">'
        + "".join(sections)
        + "</main>"
        + ai_panel
        + "</div>"
    )

    capa_id = esc(record.get("capa_id"))
    st = esc(record.get("status"))

    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{esc(title)} — structured CAPA</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; color: #111; }}
      h1 {{ margin: 0 0 8px 0; }}
      .meta {{ color: #555; margin-bottom: 20px; font-size: 14px; }}
      .badge {{ display: inline-block; padding: 2px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; }}
      .capa-grid {{ display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }}
      .capa-main {{ flex: 2 1 520px; min-width: 280px; }}
      .capa-ai-assist {{ flex: 1 1 280px; max-width: 480px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; }}
      .capa-ai-assist h2 {{ font-size: 16px; margin-top: 0; color: #0f172a; }}
      .capa-sec {{ margin-bottom: 24px; }}
      .capa-sec h2 {{ font-size: 18px; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; }}
      .capa-sec h3 {{ font-size: 14px; margin: 12px 0 6px; color: #374151; }}
      dl dt {{ font-weight: 600; margin-top: 8px; }}
      dl dd {{ margin: 0 0 0 0; }}
      .capa-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
      .capa-table th, .capa-table td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; }}
      .capa-gates {{ padding-left: 18px; }}
    </style>
  </head>
  <body>
    <h1>{esc(title)}</h1>
    <div class="meta">
      <span class="badge">capa (structured)</span>
      &nbsp; Project: {esc(project_name)} &nbsp;|&nbsp; Document status: {esc(doc_status)} &nbsp;|&nbsp; Version: {esc(version)}
      &nbsp;|&nbsp; CAPA ID: {capa_id} &nbsp;|&nbsp; CAPA status: {st}
    </div>
    {body_inner}
  </body>
</html>"""


def render_capa_legacy_text_html(
    raw_text: str,
    *,
    title: str,
    project_name: str,
    doc_status: str,
    version: int,
) -> str:
    import html as html_mod

    safe = html_mod.escape(raw_text or "")
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{html_mod.escape(title)} — legacy CAPA text</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 32px; }}
      .banner {{ background: #fff7ed; border: 1px solid #fdba74; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; color: #9a3412; }}
      pre {{ background: #f7f7f7; padding: 16px; border-radius: 8px; white-space: pre-wrap; }}
    </style>
  </head>
  <body>
    <h1>{html_mod.escape(title)}</h1>
    <div class="banner"><strong>legacy_format:</strong> This document is stored as plain text. Convert to structured JSON via a new draft or re-initialization when ready.</div>
    <p style="color:#555">Project: {html_mod.escape(project_name)} | Status: {html_mod.escape(doc_status)} | v{version}</p>
    <pre>{safe}</pre>
  </body>
</html>"""


def normalize_ai_assist_dict(raw: Any) -> Dict[str, Any]:
    """Coerce model output to ai_assist shape."""
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, Any] = {}
    if raw.get("problem_review") is not None:
        out["problem_review"] = str(raw.get("problem_review"))
    for key in ("root_cause_challenges", "missing_information", "suggested_actions"):
        v = raw.get(key)
        if isinstance(v, list):
            out[key] = [str(x) for x in v if x is not None]
        elif v is None:
            out[key] = []
    return out
