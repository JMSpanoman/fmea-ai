from __future__ import annotations

from datetime import datetime, timezone
import os
import re
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import component as component_crud
from crud import document as document_crud
from crud import project as project_crud
from crud import project_profile as profile_crud
from schemas.document import DocumentUpdate
from services.document_ai_prompt_registry import get_document_ai_prompt_registry


AI_DRAFT_FN = Callable[[str, str, Dict[str, Any]], str]


MISSING_SETUP_DETAIL = (
    "Project setup information is missing. Complete Project Setup to generate better examples."
)


def _safe_meta(d: Any) -> Dict[str, Any]:
    return d if isinstance(d, dict) else {}


def _summarize_existing_headings(content: Optional[str]) -> str:
    """
    Extract a small, safe 'headings only' summary from existing content.
    Works for markdown-ish text and simple HTML.
    """
    c = (content or "").strip()
    if not c:
        return ""

    headings: list[str] = []

    # Markdown headings
    for line in c.splitlines():
        s = line.strip()
        if s.startswith("#"):
            headings.append(s[:160])
        if len(headings) >= 20:
            break

    # HTML headings (best-effort)
    if not headings and "<h" in c.lower():
        for m in re.finditer(r"<h[1-6][^>]*>(.*?)</h[1-6]>", c, flags=re.IGNORECASE | re.DOTALL):
            txt = re.sub(r"<[^>]+>", "", m.group(1) or "").strip()
            if txt:
                headings.append(txt[:160])
            if len(headings) >= 20:
                break

    return "\n".join(f"- {h}" for h in headings)


def _format_registry_entry(doc_type: str) -> str:
    reg = get_document_ai_prompt_registry()
    entry = reg.get(doc_type) or reg.get("_default") or {}

    purpose = (entry.get("purpose") or "").strip()
    req = entry.get("required_sections") or []
    constraints = entry.get("constraints") or []
    style = entry.get("style") or []

    def _bullets(items: Any) -> str:
        if not isinstance(items, list):
            return ""
        return "\n".join([f"- {str(x)}" for x in items if str(x).strip()])

    return (
        f"Document type: {doc_type}\n"
        f"Purpose: {purpose}\n\n"
        "Required sections:\n"
        f"{_bullets(req) or '- (none)'}\n\n"
        "Safety constraints (must follow):\n"
        f"{_bullets(constraints) or '- (none)'}\n\n"
        "Style:\n"
        f"{_bullets(style) or '- (none)'}\n"
    )


def _append_ai_example_section(*, existing: str, draft: str, generated_at: str) -> str:
    divider = "\n" + ("=" * 72) + "\n"
    header = (
        f"{divider}"
        "AI-GENERATED EXAMPLE — DRAFT ONLY. Must be reviewed and edited before use.\n"
        f"Source: AI Example\n"
        f"generated_at: {generated_at}\n"
        f"{divider}\n"
    )
    base = (existing or "").rstrip()
    body = (draft or "").strip()
    if base:
        return base + "\n\n" + header + body + "\n"
    return header + body + "\n"


def _enforce_rate_limit(
    *,
    meta: Dict[str, Any],
    user_id: str,
    doc_type: str,
    seconds: int = 30,
) -> Dict[str, Any]:
    """
    Basic per-user/per-doc_type rate limit stored in ai_metadata.
    """
    now = datetime.now(timezone.utc)
    key = f"{user_id}:{doc_type}"
    rate = meta.get("ai_rate_limit") if isinstance(meta.get("ai_rate_limit"), dict) else {}
    last = rate.get(key)
    if isinstance(last, str):
        try:
            last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
            if (now - last_dt).total_seconds() < seconds:
                raise HTTPException(status_code=429, detail="Please wait a moment before generating again.")
        except HTTPException:
            raise
        except Exception:
            # Ignore parsing errors and continue.
            pass
    rate[key] = now.isoformat()
    # Keep map small (best-effort prune)
    if len(rate) > 50:
        for k in list(rate.keys())[: len(rate) - 50]:
            rate.pop(k, None)
    return {**meta, "ai_rate_limit": rate}


def _default_or_stub_ai_draft_fn() -> AI_DRAFT_FN:
    """
    Use the existing OpenAI integration, but allow a deterministic stub for tests/dev.
    """
    if os.getenv("SMARTQS_TEST_AI", "").strip() == "1":
        def _stub(doc_type: str, context: str, meta: Dict[str, Any]) -> str:
            return (
                f"## AI Example Draft ({doc_type})\n\n"
                f"- Project: {meta.get('project_name')} ({meta.get('project_id')})\n"
                "- NOTE: This is a deterministic stub (SMARTQS_TEST_AI=1).\n"
                "- Replace with real AI output in runtime environments.\n"
            )
        return _stub

    from services.project_ai_doc_generator import _default_ai_draft_fn

    return _default_ai_draft_fn


def generate_ai_example_for_document(
    *,
    db: Session,
    project_id: str,
    user_id: str,
    document_type: str,
    ai_draft_fn: Optional[AI_DRAFT_FN] = None,
) -> Any:
    """
    Create an AI-generated example draft for the given document_type.

    Hard rules:
    - Must not overwrite user-entered content (append as a clearly-marked AI Example section)
    - Must create a NEW document version
    - Must be labeled Draft + AI Example + generated_at
    """
    project = project_crud.get_project(db, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    doc_type = (document_type or "").strip().lower()
    if not doc_type:
        raise HTTPException(status_code=400, detail="document_type is required")

    doc = document_crud.get_document_by_type(db, project_id=project_id, doc_type=doc_type)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document of type '{doc_type}' not found for project")

    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)
    if profile is None or not components:
        raise HTTPException(status_code=400, detail=MISSING_SETUP_DETAIL)

    meta0 = _safe_meta(getattr(doc, "ai_metadata", None))
    meta1 = _enforce_rate_limit(meta=meta0, user_id=str(user_id), doc_type=doc_type, seconds=30)

    component_lines = [
        f"- {getattr(c, 'name', '')}" + (f": {getattr(c, 'description', '')}" if getattr(c, "description", None) else "")
        for c in components
    ]

    existing_headings = _summarize_existing_headings(getattr(doc, "content", None))
    registry_block = _format_registry_entry(doc_type)

    context = (
        f"Project ID: {project_id}\n"
        f"Project name: {project.name}\n\n"
        "Project Profile:\n"
        f"- intended_use: {getattr(profile, 'intended_use', None)}\n"
        f"- device_description: {getattr(profile, 'device_description', None)}\n"
        f"- user_population: {getattr(profile, 'user_population', None)}\n"
        f"- use_environment: {getattr(profile, 'use_environment', None)}\n"
        f"- key_safety_characteristics: {getattr(profile, 'key_safety_characteristics', None)}\n\n"
        "Components:\n"
        + ("\n".join(component_lines) if component_lines else "- (none)\n")
        + "\n\n"
        "Document AI prompt registry entry:\n"
        + registry_block
        + "\n"
        + ("Existing document headings (summary):\n" + (existing_headings or "- (none)") + "\n")
    )

    now = datetime.now(timezone.utc).isoformat()
    ai_fn = ai_draft_fn or _default_or_stub_ai_draft_fn()

    try:
        draft = ai_fn(
            doc_type,
            context,
            {
                "project_id": project_id,
                "project_name": project.name,
                "document_type": doc_type,
                "source": "AI Example",
                "generated_at": now,
                "current_version": getattr(doc, "version", None),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

    new_content = _append_ai_example_section(existing=getattr(doc, "content", "") or "", draft=draft, generated_at=now)
    new_meta = {
        **meta1,
        "ai_example_generated": True,
        "ai_example_last_generated_at": now,
        "ai_example_last_generated_by": str(user_id),
        "generated_with_ai": True,
        "ai_example_source": "generate_ai_endpoint",
    }

    updated = document_crud.update_document(
        db,
        getattr(doc, "id"),
        DocumentUpdate(content=new_content, status="draft", ai_metadata=new_meta),
        project_id,
    )
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update document")

    # Patch version metadata for auditability.
    try:
        vno = int(getattr(updated, "version", 0) or 0)
        v = document_crud.get_document_version_by_no(db, getattr(updated, "id"), vno)
        if v is not None:
            ch = v.changes if isinstance(v.changes, dict) else {}
            v.changes = {
                **ch,
                "source": "AI Example",
                "generated_at": now,
                "document_type": doc_type,
                "ai_example": True,
            }
            db.commit()
    except Exception:
        # Never break the main path if this best-effort patch fails.
        pass

    return updated

