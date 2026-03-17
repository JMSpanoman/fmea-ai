from __future__ import annotations

from fastapi import APIRouter, Depends
from typing import Any, Dict

from auth.plan import require_pro
from services.document_guidance_registry import get_document_guidance_registry

router = APIRouter(prefix="/documents", tags=["Document Guidance"], dependencies=[Depends(require_pro)])


@router.get("/guidance")
def get_guidance_registry() -> Dict[str, Dict[str, Any]]:
    """
    Read-only guidance registry for document pages.
    Intended for UI help text and consistent behavior across document types.
    """
    return get_document_guidance_registry()

