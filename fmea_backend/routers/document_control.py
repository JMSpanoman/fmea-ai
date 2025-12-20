from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import document as doc_schemas
from crud import document as doc_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["Document Control"])

@router.get("/documents", response_model=List[doc_schemas.DocumentOut])
def get_documents(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all documents for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return doc_crud.get_documents_by_project(db, project_id)

@router.post("/documents", response_model=doc_schemas.DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    project_id: str,
    document: doc_schemas.DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new document"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter
    if hasattr(document, 'model_copy'):
        document = document.model_copy(update={'project_id': project_id})
    else:
        document_dict = document.dict() if hasattr(document, 'dict') else document.model_dump()
        document_dict['project_id'] = project_id
        document = doc_schemas.DocumentCreate(**document_dict)
    
    return doc_crud.create_document(db, document)

@router.get("/documents/{document_id}", response_model=doc_schemas.DocumentOut)
def get_document(
    project_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    document = doc_crud.get_document(db, document_id, project_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.put("/documents/{document_id}", response_model=doc_schemas.DocumentOut)
def update_document(
    project_id: str,
    document_id: str,
    document: doc_schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a document"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_doc = doc_crud.update_document(db, document_id, document, project_id)
    if not updated_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return updated_doc

@router.post("/documents/{document_id}/approve", response_model=doc_schemas.DocumentOut)
def approve_document(
    project_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a document with automatic training assignment"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Use business logic for approval workflow
    from business_logic.approval_workflow import approve_document_with_workflow
    
    result = approve_document_with_workflow(db, document_id, project_id, current_user)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Auto-assign training to project team
    from business_logic.training_auto_assignment import auto_assign_training_on_document_approval
    auto_assign_training_on_document_approval(db, document_id, project_id)
    
    return result["document"]

@router.get("/documents/{document_id}/versions", response_model=List[doc_schemas.DocumentVersionOut])
def get_document_versions(
    project_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all versions of a document"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    document = doc_crud.get_document(db, document_id, project_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    versions = doc_crud.get_document_versions(db, document_id)
    return versions

