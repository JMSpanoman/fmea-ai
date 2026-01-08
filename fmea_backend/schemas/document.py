from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ComponentFilter(BaseModel):
    id: Optional[str] = None
    name: str

class DocumentGenerateRequest(BaseModel):
    components: Optional[List[ComponentFilter]] = None
    version_scope: str = "approved_only"  # approved_only, current, all
    options: Optional[Dict[str, Any]] = None

class DocumentGenerateResponse(BaseModel):
    doc_id: str
    new_version_no: int
    rendered_html: str
    updated_at: datetime

class DocumentBase(BaseModel):
    name: str
    type: str  # dhf, dmr, sop, form, work_instruction, record
    content: Optional[str] = None
    status: str  # draft, in_review, approved, obsolete
    ai_metadata: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    project_id: str  # UUID

class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class DocumentOut(DocumentBase):
    id: str  # UUID
    project_id: str  # UUID
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentVersionOut(BaseModel):
    id: str  # UUID
    document_id: str  # UUID
    version: int
    content: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# AI Document Assistant
class DocumentDraftRequest(BaseModel):
    type: str
    context: Optional[str] = None
    requirements: Optional[List[str]] = None

class DocumentDraftResponse(BaseModel):
    draft: str
    ai_metadata: Optional[Dict[str, Any]] = None

class DocumentSummarizeRequest(BaseModel):
    document_id: str  # UUID

class DocumentSummarizeResponse(BaseModel):
    summary: str
    ai_metadata: Optional[Dict[str, Any]] = None

class DocumentExtractRequirementsRequest(BaseModel):
    document_id: str  # UUID

class DocumentExtractRequirementsResponse(BaseModel):
    requirements: List[str]
    ai_metadata: Optional[Dict[str, Any]] = None

