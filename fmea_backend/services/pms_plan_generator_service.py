"""
PMS Plan generation: FMEA + MAUDE-like signals + OpenAI structured JSON.

- Persists to `pms_generated_plans` (primary retrieval).
- Also logs `ai_events` (context_type=pms_plan) for audit compatibility.
"""
from __future__ import annotations

import html as html_mod
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from crud import fmea as fmea_crud
from crud import project as project_crud
from crud.ai_event import create_ai_event, get_ai_event, get_ai_events_by_context
from crud.pms_generated_plan import (
    create_pms_generated_plan,
    get_pms_generated_plan,
    list_pms_generated_plans_by_project,
    next_plan_version,
)
from schemas.ai_event import AIEventCreate
from schemas.pms_plan import (
    MaudeSignalPublic,
    PmsPlanGenerateRequest,
    PmsPlanGenerateResponse,
    PmsPlanHistoryItem,
    PmsPlanHistoryListResponse,
    PmsPlanSections,
)
from services.maude_signal_provider import get_maude_signal_provider

REQUIRED_SECTION_KEYS = (
    "device_overview",
    "pms_objectives",
    "data_sources",
    "maude_analysis",
    "risk_mapping",
    "signal_detection",
    "pms_activities",
    "capa_integration",
    "benefit_risk",
    "reporting",
)

EMPTY_FMEA_WARNING = (
    "No FMEA rows were found for this project. The plan is based on device name, intended use, "
    "and simulated post-market signals only. Populate FMEA for full design-phase traceability into PMS."
)


def _fmea_rows_for_prompt(db: Session, project_id: str) -> Tuple[List[Dict[str, Any]], int]:
    rows = fmea_crud.get_fmea_rows_by_project(db, project_id)
    out: List[Dict[str, Any]] = []
    for r in rows:
        comp_name = ""
        try:
            comp = getattr(r, "component", None)
            if comp is not None:
                comp_name = str(getattr(comp, "name", "") or "")
        except Exception:
            comp_name = ""
        md = getattr(r, "ai_metadata", None)
        hazard_hint = ""
        if isinstance(md, dict):
            hazard_hint = str(md.get("hazard") or "").strip()
        out.append(
            {
                "id": getattr(r, "id", None),
                "component_name": comp_name or None,
                "device_function": getattr(r, "device_function", None),
                "failure_mode": getattr(r, "failure_mode", None),
                "effect": getattr(r, "effect", None),
                "cause": getattr(r, "cause", None),
                "hazard": getattr(r, "hazard", None) or (hazard_hint or None),
                "harm": getattr(r, "harm", None),
                "severity": getattr(r, "severity", None),
                "occurrence": getattr(r, "probability", None),
                "detection": getattr(r, "detection", None),
                "rpn": getattr(r, "rpn", None),
                "mitigation": getattr(r, "mitigation", None),
                "action_taken": getattr(r, "action_taken", None),
                "residual_rpn": getattr(r, "residual_rpn", None),
            }
        )
    return out, len(out)


def _normalize_section_value(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, str):
        return v.strip() or "—"
    try:
        return json.dumps(v, ensure_ascii=False, indent=2)
    except Exception:
        return str(v)


def _normalize_plan_dict(raw: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k in REQUIRED_SECTION_KEYS:
        out[k] = _normalize_section_value(raw.get(k))
    return out


def _extract_json_object(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text or "")
        if not m:
            raise ValueError("No JSON object in model output")
        return json.loads(m.group(0))


def _make_summary(*, device_name: str, device_overview: str) -> str:
    text = (device_overview or "").strip().replace("\n", " ")
    if len(text) > 240:
        text = text[:237] + "…"
    if text and text != "—":
        return f"{device_name}: {text}"
    return f"PMS plan for {device_name}"


def _stub_plan(
    *,
    device_name: str,
    intended_use: str,
    fmea_count: int,
    signal_count: int,
    warning: Optional[str],
) -> Dict[str, str]:
    wblock = f"\n\n**Warning:** {warning}\n" if warning else ""
    return {
        "device_overview": (
            f"**Device:** {device_name}\n\n**Intended use (input):** {intended_use}\n\n"
            f"**Design-phase FMEA rows referenced:** {fmea_count}\n"
            f"{wblock}\n"
            "_Stub plan (SMARTQS_TEST_AI=1 or AI unavailable). Replace with model output in production._"
        ),
        "pms_objectives": (
            "- Monitor performance and safety signals in post-market use.\n"
            "- Relate external database themes and complaints to FMEA failure modes and residual risk.\n"
            "- Trigger RMF updates, benefit–risk reassessment, and CAPA when predefined thresholds are met."
        ),
        "data_sources": (
            "- Internal: complaints, service records, CAPA, NCRs, management review outputs.\n"
            "- External: regulatory databases (e.g., MAUDE) when integrated — **currently simulated signals only**.\n"
            "- Literature, standards, and notified body feedback (per procedure)."
        ),
        "maude_analysis": (
            f"**Signals reviewed (simulated):** {signal_count}\n\n"
            "Summarize qualitative trends by failure theme; require verified MAUDE extracts before regulatory claims."
        ),
        "risk_mapping": (
            "For each signal theme, map to FMEA row(s) by failure mode/effect/hazard language; document trace in RMF."
        ),
        "signal_detection": (
            "**Cadence:** Monthly dashboard review; quarterly deep-dive.\n"
            "**Triggers:** unexpected upward trend vs. baseline; clustering in geography/lot/firmware; severity shift.\n"
            "**Escalation:** Quality review board within 5 business days if trigger met; medical safety review if patient harm indicated."
        ),
        "pms_activities": (
            "- Complaint coding consistency audits\n"
            "- Trend and rate analysis vs. sales/exposure proxy\n"
            "- Literature scan per SOP\n"
            "- RMF linkage updates after substantive reviews"
        ),
        "capa_integration": (
            "CAPA when systemic or safety-impacting patterns emerge; link to FMEA mitigations and verification evidence."
        ),
        "benefit_risk": (
            "Re-evaluate benefit–risk when new hazards or frequency/severity shifts are indicated; record conclusions in RMF."
        ),
        "reporting": (
            "Follow vigilance/MIR and regulatory reporting rules; retain decision rationale and data extracts in technical documentation."
        ),
    }


def _call_openai_pms_plan(
    *,
    device_name: str,
    intended_use: str,
    fmea_rows: List[Dict[str, Any]],
    maude_signals: List[Dict[str, Any]],
    empty_fmea_warning: Optional[str],
) -> Tuple[Dict[str, str], str]:
    import openai

    prompts_dir = Path(__file__).resolve().parent.parent.parent / "ai_prompts"
    try:
        system_prompt = (prompts_dir / "phase3_system_prompt.txt").read_text().strip()
    except Exception:
        system_prompt = (
            "You are SmartQS AI. Produce audit-ready regulatory documentation drafts. Return JSON only."
        )
    try:
        doc_prompt = (prompts_dir / "pms_plan_generator_prompt.txt").read_text().strip()
    except Exception:
        doc_prompt = "Generate a PMS plan as JSON with the required section keys. Return JSON only."

    payload: Dict[str, Any] = {
        "device_name": device_name,
        "intended_use": intended_use,
        "fmea_rows": fmea_rows,
        "maude_like_signals": maude_signals,
    }
    if empty_fmea_warning:
        payload["empty_fmea_warning"] = empty_fmea_warning

    user_prompt = (
        f"{doc_prompt}\n\n## Inputs (JSON)\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = openai.OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.35,
        )
        content = resp.choices[0].message.content or ""
    except Exception:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.35,
        )
        content = resp.choices[0].message.content or ""

    data = _extract_json_object(content)
    if not isinstance(data, dict):
        raise ValueError("Model returned non-object JSON")
    return _normalize_plan_dict(data), model


def _payload_from_parts(
    *,
    sections: Dict[str, str],
    maude_signals: List[Dict[str, Any]],
    fmea_row_count: int,
    model_name: Optional[str],
    ai_generated: bool,
    warning: Optional[str],
) -> Dict[str, Any]:
    return {
        "sections": sections,
        "maude_signals": maude_signals,
        "fmea_row_count": fmea_row_count,
        "model": model_name,
        "ai_generated": ai_generated,
        "warning": warning,
    }


def _signals_to_public(maude_signals: List[Dict[str, Any]]) -> List[MaudeSignalPublic]:
    out: List[MaudeSignalPublic] = []
    for s in maude_signals:
        if isinstance(s, dict):
            try:
                out.append(MaudeSignalPublic.model_validate(s))
            except Exception:
                pass
    return out


def _ai_event_to_history_item(ev: Any) -> Optional[PmsPlanHistoryItem]:
    raw = ev.output_json if isinstance(ev.output_json, dict) else {}
    sec = raw.get("sections") if isinstance(raw.get("sections"), dict) else {}
    if not sec and raw:
        sec = {k: raw.get(k) for k in REQUIRED_SECTION_KEYS}
    try:
        plan = PmsPlanSections(**_normalize_plan_dict(sec))
    except Exception:
        return None
    sigs = _signals_to_public(raw.get("maude_signals") if isinstance(raw.get("maude_signals"), list) else [])
    return PmsPlanHistoryItem(
        id=ev.id,
        project_id=ev.project_id,
        device_name=raw.get("device_name") if isinstance(raw.get("device_name"), str) else None,
        intended_use=raw.get("intended_use") if isinstance(raw.get("intended_use"), str) else None,
        created_at=ev.created_at,
        input_summary=ev.input_summary,
        summary=raw.get("summary") if isinstance(raw.get("summary"), str) else None,
        status=raw.get("status") if isinstance(raw.get("status"), str) else "draft",
        version=raw.get("version") if isinstance(raw.get("version"), int) else None,
        plan=plan,
        maude_signals=sigs,
        fmea_row_count=raw.get("fmea_row_count") if isinstance(raw.get("fmea_row_count"), int) else None,
        model=raw.get("model") if isinstance(raw.get("model"), str) else None,
        warning=raw.get("warning") if isinstance(raw.get("warning"), str) else None,
        ai_generated=raw.get("ai_generated") if isinstance(raw.get("ai_generated"), bool) else None,
    )


def _db_row_to_history_item(row: Any) -> PmsPlanHistoryItem:
    payload = row.payload_json if isinstance(row.payload_json, dict) else {}
    sec = payload.get("sections") if isinstance(payload.get("sections"), dict) else {}
    plan = PmsPlanSections(**_normalize_plan_dict(sec))
    sigs = _signals_to_public(
        payload.get("maude_signals") if isinstance(payload.get("maude_signals"), list) else []
    )
    return PmsPlanHistoryItem(
        id=row.id,
        project_id=row.project_id,
        device_name=getattr(row, "device_name", None),
        intended_use=getattr(row, "intended_use", None),
        created_at=row.created_at,
        input_summary=None,
        summary=getattr(row, "summary", None),
        status=getattr(row, "status", None) or "draft",
        version=int(getattr(row, "version", 1) or 1),
        plan=plan,
        maude_signals=sigs,
        fmea_row_count=payload.get("fmea_row_count")
        if isinstance(payload.get("fmea_row_count"), int)
        else None,
        model=payload.get("model") if isinstance(payload.get("model"), str) else None,
        warning=payload.get("warning") if isinstance(payload.get("warning"), str) else None,
        ai_generated=payload.get("ai_generated") if isinstance(payload.get("ai_generated"), bool) else None,
    )


def generate_pms_plan(
    db: Session,
    *,
    user_id: str,
    body: PmsPlanGenerateRequest,
) -> PmsPlanGenerateResponse:
    project = project_crud.get_project(db, body.project_id, user_id)
    if not project:
        raise PermissionError("Project not found or access denied")

    fmea_rows, fmea_count = _fmea_rows_for_prompt(db, body.project_id)
    warning: Optional[str] = EMPTY_FMEA_WARNING if fmea_count == 0 else None

    provider = get_maude_signal_provider()
    maude_signals = provider.get_signals(
        project_id=body.project_id,
        device_name=body.device_name,
        intended_use=body.intended_use,
        fmea_rows=fmea_rows,
    )

    generation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    model_name: Optional[str] = None
    ai_generated = False

    if os.getenv("SMARTQS_TEST_AI", "").strip() == "1":
        sections = _stub_plan(
            device_name=body.device_name,
            intended_use=body.intended_use,
            fmea_count=fmea_count,
            signal_count=len(maude_signals),
            warning=warning,
        )
        model_name = "stub"
    else:
        try:
            sections, model_name = _call_openai_pms_plan(
                device_name=body.device_name,
                intended_use=body.intended_use,
                fmea_rows=fmea_rows,
                maude_signals=maude_signals,
                empty_fmea_warning=warning,
            )
            ai_generated = True
        except Exception:
            env = (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "development").lower()
            if env in ("production", "prod", "staging"):
                raise
            sections = _stub_plan(
                device_name=body.device_name,
                intended_use=body.intended_use,
                fmea_count=fmea_count,
                signal_count=len(maude_signals),
                warning=warning,
            )
            model_name = "stub_fallback"

    summary = _make_summary(device_name=body.device_name, device_overview=sections.get("device_overview", ""))
    version = next_plan_version(db, body.project_id)
    status = "draft"

    maude_public = _signals_to_public(maude_signals)

    payload = _payload_from_parts(
        sections=sections,
        maude_signals=maude_signals,
        fmea_row_count=fmea_count,
        model_name=model_name,
        ai_generated=ai_generated,
        warning=warning,
    )

    output_payload: Dict[str, Any] = {
        "generation_id": generation_id,
        "created_at": now.isoformat(),
        "project_id": body.project_id,
        "device_name": body.device_name,
        "intended_use": body.intended_use,
        "summary": summary,
        "status": status,
        "version": version,
        "sections": sections,
        "maude_signals": maude_signals,
        "fmea_row_count": fmea_count,
        "model": model_name,
        "ai_generated": ai_generated,
        "warning": warning,
    }

    summary_line = (
        f"device={body.device_name[:80]!r}, intended_use_len={len(body.intended_use)}, "
        f"fmea_rows={fmea_count}, signals={len(maude_signals)}"
    )
    create_ai_event(
        db,
        AIEventCreate(
            project_id=body.project_id,
            context_type="pms_plan",
            context_id=generation_id,
            prompt_name="pms_plan_generate",
            input_summary=summary_line,
            output_json=output_payload,
        ),
        user_id,
    )

    create_pms_generated_plan(
        db,
        generation_id=generation_id,
        project_id=body.project_id,
        user_id=user_id,
        device_name=body.device_name,
        intended_use=body.intended_use,
        summary=summary,
        status=status,
        version=version,
        payload_json=payload,
    )

    plan = PmsPlanSections(**sections)
    return PmsPlanGenerateResponse(
        **plan.model_dump(),
        generation_id=generation_id,
        project_id=body.project_id,
        created_at=now,
        maude_signals=maude_public,
        fmea_row_count=fmea_count,
        model=model_name,
        ai_generated=ai_generated,
        summary=summary,
        status=status,
        version=version,
        warning=warning,
    )


def get_pms_plan_for_user(
    db: Session,
    *,
    user_id: str,
    generation_id: str,
    project_id: Optional[str] = None,
) -> Optional[PmsPlanHistoryItem]:
    row = get_pms_generated_plan(db, generation_id)
    if row:
        if not project_crud.get_project(db, row.project_id, user_id):
            return None
        if project_id is not None and row.project_id != project_id:
            return None
        return _db_row_to_history_item(row)

    ev = get_ai_event(db, generation_id)
    if not ev or getattr(ev, "context_type", None) != "pms_plan":
        return None
    if not project_crud.get_project(db, ev.project_id, user_id):
        return None
    if project_id is not None and ev.project_id != project_id:
        return None
    return _ai_event_to_history_item(ev)


def list_pms_plans_merged(
    db: Session,
    *,
    user_id: str,
    project_id: str,
) -> PmsPlanHistoryListResponse:
    if not project_crud.get_project(db, project_id, user_id):
        raise PermissionError("Project not found or access denied")

    db_rows = list_pms_generated_plans_by_project(db, project_id)
    items: List[PmsPlanHistoryItem] = [_db_row_to_history_item(r) for r in db_rows]
    seen = {i.id for i in items}

    events = get_ai_events_by_context(db, project_id, "pms_plan")
    for ev in events:
        if ev.id in seen:
            continue
        parsed = _ai_event_to_history_item(ev)
        if parsed:
            items.append(parsed)

    items.sort(key=lambda x: x.created_at, reverse=True)
    return PmsPlanHistoryListResponse(project_id=project_id, items=items)


def build_pms_plan_printable_html(*, item: PmsPlanHistoryItem) -> str:
    """Printable HTML: metadata, MAUDE table, ten sections (browser Print → PDF)."""
    title = (
        f"PMS Plan — {item.plan.device_overview[:60]}…"
        if len(item.plan.device_overview) > 60
        else "PMS Plan"
    )
    created = item.created_at
    created_s = created.isoformat() if hasattr(created, "isoformat") else str(created)

    meta_rows = [
        ("Project ID", html_mod.escape(item.project_id)),
        ("Generation ID", html_mod.escape(item.id)),
        ("Device name", html_mod.escape(item.device_name or "—")),
        ("Intended use", html_mod.escape(item.intended_use or "—")),
        ("Created", html_mod.escape(created_s)),
        (
            "FMEA rows used",
            html_mod.escape(str(item.fmea_row_count if item.fmea_row_count is not None else "—")),
        ),
        ("Model", html_mod.escape(item.model or "—")),
        (
            "AI-generated",
            html_mod.escape(str(item.ai_generated) if item.ai_generated is not None else "—"),
        ),
        ("Status", html_mod.escape(item.status or "draft")),
        ("Version", html_mod.escape(str(item.version) if item.version is not None else "—")),
    ]
    meta_html = "<table class='meta'><tbody>"
    for k, v in meta_rows:
        meta_html += f"<tr><th>{k}</th><td>{v}</td></tr>"
    meta_html += "</tbody></table>"

    sig_rows = ""
    for s in item.maude_signals:
        sig_rows += (
            f"<tr><td>{html_mod.escape(s.failure_mode)}</td>"
            f"<td>{s.event_count}</td>"
            f"<td>{html_mod.escape(s.trend)}</td>"
            f"<td>{html_mod.escape(s.severity)}</td>"
            f"<td>{html_mod.escape(s.recommended_monitoring_focus or '—')}</td>"
            f"<td>{html_mod.escape(s.source or '—')}</td></tr>"
        )
    table = (
        "<h2>MAUDE-like signals (summary)</h2>"
        "<table class='sig'><thead><tr>"
        "<th>Failure theme</th><th>Event count (sim.)</th><th>Trend</th><th>Severity</th>"
        "<th>Monitoring focus</th><th>Source</th>"
        "</tr></thead><tbody>"
        f"{sig_rows or '<tr><td colspan=6>—</td></tr>'}"
        "</tbody></table>"
    )

    if item.summary:
        summary_block = f"<div class='summary'><strong>Summary</strong><p>{html_mod.escape(item.summary)}</p></div>"
    else:
        summary_block = ""

    warn = ""
    if item.warning:
        warn = f"<div class='warn'><strong>Warning</strong><p>{html_mod.escape(item.warning)}</p></div>"

    parts = []
    for key in REQUIRED_SECTION_KEYS:
        label = key.replace("_", " ").title()
        val = getattr(item.plan, key, "") or "—"
        parts.append(
            f"<h2>{html_mod.escape(label)}</h2>\n<div class='sec'>{html_mod.escape(val)}</div>"
        )
    inner = "\n".join(parts)

    return f"""<!doctype html>
<html><head><meta charset="utf-8"/><title>{html_mod.escape(title)}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 960px; color: #111; }}
h1 {{ font-size: 1.35rem; }}
h2 {{ font-size: 1.05rem; margin-top: 1.4rem; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
.sec {{ white-space: pre-wrap; margin-top: 0.5rem; line-height: 1.45; }}
.meta {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }}
.meta th {{ text-align: left; width: 180px; padding: 6px 8px; vertical-align: top; }}
.meta td {{ padding: 6px 8px; }}
.sig {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 0.5rem; }}
.sig th, .sig td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
.summary, .warn {{ margin: 1rem 0; padding: 12px; border-radius: 8px; }}
.summary {{ background: #f0f9ff; border: 1px solid #bae6fd; }}
.warn {{ background: #fffbeb; border: 1px solid #fcd34d; }}
</style></head>
<body>
<h1>{html_mod.escape(title)}</h1>
<p class="hint">Print via browser (Save as PDF) for export.</p>
{summary_block}
{warn}
{meta_html}
{table}
{inner}
</body></html>"""


def list_pms_plans_for_project(
    db: Session,
    *,
    user_id: str,
    project_id: str,
) -> PmsPlanHistoryListResponse:
    """Alias for merged DB + legacy AI-event list (backward compatible)."""
    return list_pms_plans_merged(db, user_id=user_id, project_id=project_id)


def get_pms_plan_history_item(
    db: Session,
    *,
    user_id: str,
    project_id: str,
    generation_id: str,
) -> Optional[PmsPlanHistoryItem]:
    """Backward-compatible: requires project_id in path."""
    return get_pms_plan_for_user(db, user_id=user_id, generation_id=generation_id, project_id=project_id)
