from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import component as component_crud
from crud import document as document_crud
from crud import project as project_crud
from crud import project_profile as profile_crud
from schemas.document import DocumentUpdate
from services.document_guidance_registry import get_document_guidance_registry

# Reuse existing context helpers to keep prompts consistent.
from services.document_ai_example import (  # type: ignore
    MISSING_SETUP_DETAIL,
    _safe_meta,
    _summarize_existing_headings,
    _format_registry_entry,
    _enforce_rate_limit,
    _default_or_stub_ai_draft_fn,
)


_PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
    re.compile(r"\bN\s*/\s*A\b", flags=re.IGNORECASE),
    re.compile(r"\bnot\s+applicable\b", flags=re.IGNORECASE),
    re.compile(r"\bnone\b", flags=re.IGNORECASE),
    re.compile(r"\bnull\b", flags=re.IGNORECASE),
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
]


def _placeholder_hits(text: str) -> int:
    t = text or ""
    return sum(len(p.findall(t)) for p in _PLACEHOLDER_PATTERNS)


def _status_is_not_started(status: Optional[str]) -> bool:
    s = (status or "").strip().lower()
    return s in {"not started", "not_started", "not-started"}


def _should_overwrite_with_ai(*, doc_type: str, content: Optional[str], status: Optional[str], scaffold: Optional[str]) -> Tuple[bool, Dict[str, Any]]:
    """
    Conservative overwrite policy:
    - Overwrite if empty/not-started/exact scaffold/known starter placeholders
    - Otherwise, only overwrite if the document is clearly placeholder-heavy (many TBD/N/A/etc).
      If not, we append an "AI addendum" instead to avoid destroying user edits.
    """
    c = content or ""
    c_strip = c.strip()
    info: Dict[str, Any] = {
        "reason": "",
        "placeholder_hits": _placeholder_hits(c),
        "length": len(c),
    }

    if _status_is_not_started(status):
        info["reason"] = "status_not_started"
        return True, info
    if not c_strip:
        info["reason"] = "empty"
        return True, info
    if scaffold is not None and c == scaffold:
        info["reason"] = "matches_scaffold_exact"
        return True, info

    lowered = c_strip.lower()
    if "export configuration starter" in lowered or (doc_type and (f"{doc_type} starter" in lowered)):
        info["reason"] = "starter_placeholder"
        return True, info

    # Placeholder-heavy heuristic (conservative)
    hits = int(info["placeholder_hits"] or 0)
    if hits >= 12 and len(c_strip) < 12000:
        info["reason"] = "placeholder_heavy"
        return True, info

    info["reason"] = "preserve_user_content"
    return False, info


def _append_ai_populate_addendum(*, existing: str, draft: str, generated_at: str) -> str:
    divider = "\n" + ("=" * 72) + "\n"
    header = (
        f"{divider}"
        "AI POPULATED ADDENDUM — DRAFT ONLY. Must be reviewed and edited before use.\n"
        "Source: Generate with AI\n"
        f"generated_at: {generated_at}\n"
        f"{divider}\n"
    )
    base = (existing or "").rstrip()
    body = (draft or "").strip()
    if base:
        return base + "\n\n" + header + body + "\n"
    return header + body + "\n"


def generate_ai_populated_draft_for_document(
    *,
    db: Session,
    project_id: str,
    user_id: str,
    document_type: str,
) -> Any:
    """
    Generate a populated draft for a document type:
    - If the document is clearly a scaffold / placeholder-heavy, overwrite (new version).
    - Otherwise, append an addendum so we never destroy user edits.
    """
    project = project_crud.get_project(db, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    doc_type = (document_type or "").strip().lower()
    if not doc_type:
        raise HTTPException(status_code=400, detail="document_type is required")

    # Respect product capability flags.
    reg = get_document_guidance_registry()
    entry = reg.get(doc_type)
    if entry and not bool(entry.get("ai_available", False)):
        raise HTTPException(status_code=400, detail=f"AI generation is not available for '{doc_type}'")

    doc = document_crud.get_document_by_type(db, project_id=project_id, doc_type=doc_type)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document of type '{doc_type}' not found for project")

    # RMF is compiled HTML from linked authoritative documents — do not run LLM populate (would corrupt HTML).
    # "Generate with AI" for RMF re-runs the deterministic compiler (same as Compile RMF).
    if doc_type == "rmf":
        from services.rmf_compiler import compile_rmf

        meta0 = _safe_meta(getattr(doc, "ai_metadata", None))
        meta1 = _enforce_rate_limit(meta=meta0, user_id=str(user_id), doc_type=f"{doc_type}:populate", seconds=20)
        rendered_html, _ready = compile_rmf(db, project_id=project_id, project_name=project.name)
        now = datetime.now(timezone.utc).isoformat()
        new_meta = {
            **meta1,
            "ai_populate_generated": True,
            "ai_populate_last_generated_at": now,
            "ai_populate_last_generated_by": str(user_id),
            "ai_populate_mode": "rmf_deterministic_compile",
            "rmf_deterministic_compile": True,
            "generated_with_ai": False,
            "ai_populate_source": "rmf_compiler_via_generate_with_ai",
        }
        updated = document_crud.update_document(
            db,
            getattr(doc, "id"),
            DocumentUpdate(content=rendered_html, status="draft", ai_metadata=new_meta),
            project_id,
        )
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update document")
        try:
            vno = int(getattr(updated, "version", 0) or 0)
            v = document_crud.get_document_version_by_no(db, getattr(updated, "id"), vno)
            if v is not None:
                ch = v.changes if isinstance(v.changes, dict) else {}
                v.changes = {
                    **ch,
                    "source": "Generate with AI (RMF deterministic compile)",
                    "generated_at": now,
                    "document_type": doc_type,
                    "mode": "rmf_deterministic_compile",
                }
                db.commit()
        except Exception:
            pass
        return updated

    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)
    if profile is None or not components:
        raise HTTPException(status_code=400, detail=MISSING_SETUP_DETAIL)

    # Scaffold is useful for safe overwrite decisions.
    try:
        from services.project_profile_initializer import build_project_setup_scaffolds

        scaffolds = build_project_setup_scaffolds(db, project_id=project_id)
        scaffold = scaffolds.get(doc_type) if isinstance(scaffolds, dict) else None
    except Exception:
        scaffold = None

    meta0 = _safe_meta(getattr(doc, "ai_metadata", None))
    meta1 = _enforce_rate_limit(meta=meta0, user_id=str(user_id), doc_type=f"{doc_type}:populate", seconds=20)

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
        + "Document AI prompt registry entry:\n"
        + registry_block
        + "\n"
        + ("Existing document headings (summary):\n" + (existing_headings or "- (none)") + "\n")
        + ("\nDeterministic scaffold (reference only):\n" + (scaffold or "(none)") + "\n")
    )

    now = datetime.now(timezone.utc).isoformat()
    ai_fn = _default_or_stub_ai_draft_fn()

    try:
        draft = ai_fn(
            doc_type,
            context,
            {
                "project_id": project_id,
                "project_name": project.name,
                "document_type": doc_type,
                "source": "Generate with AI",
                "generated_at": now,
                "current_version": getattr(doc, "version", None),
                "mode": "populate",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

    can_overwrite, overwrite_info = _should_overwrite_with_ai(
        doc_type=doc_type, content=getattr(doc, "content", None), status=getattr(doc, "status", None), scaffold=scaffold
    )

    if can_overwrite:
        # Replace the scaffold with a real draft (new version).
        header = (
            "DRAFT — Generated with AI (Populate)\n"
            f"generated_at: {now}\n"
            f"Project ID: {project_id}\n"
            "Do not treat this as approved or executed evidence.\n\n"
        )
        new_content = (draft or "").strip()
        if "project id:" not in (new_content or "").lower():
            new_content = header + new_content
    else:
        new_content = _append_ai_populate_addendum(existing=getattr(doc, "content", "") or "", draft=draft, generated_at=now)

    new_meta = {
        **meta1,
        "ai_populate_generated": True,
        "ai_populate_last_generated_at": now,
        "ai_populate_last_generated_by": str(user_id),
        "ai_populate_mode": "overwrite" if can_overwrite else "append_addendum",
        "ai_populate_overwrite_info": overwrite_info,
        "generated_with_ai": True,
        "ai_populate_source": "generate_with_ai_populate_endpoint",
    }

    updated = document_crud.update_document(
        db,
        getattr(doc, "id"),
        DocumentUpdate(content=new_content, status="draft", ai_metadata=new_meta),
        project_id,
    )
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update document")

    # Best-effort: annotate the created version's change metadata for auditability.
    try:
        vno = int(getattr(updated, "version", 0) or 0)
        v = document_crud.get_document_version_by_no(db, getattr(updated, "id"), vno)
        if v is not None:
            ch = v.changes if isinstance(v.changes, dict) else {}
            v.changes = {
                **ch,
                "source": "Generate with AI",
                "generated_at": now,
                "document_type": doc_type,
                "mode": "populate",
                "populate_mode": ("overwrite" if can_overwrite else "append_addendum"),
                "overwrite_info": overwrite_info,
            }
            db.commit()
    except Exception:
        pass

    return updated

