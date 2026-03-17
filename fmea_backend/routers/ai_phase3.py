from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas.document import DocumentDraftRequest, DocumentDraftResponse, DocumentSummarizeRequest, DocumentSummarizeResponse, DocumentExtractRequirementsRequest, DocumentExtractRequirementsResponse
from schemas.audit import AuditPrepareRequest, AuditPrepareResponse
from schemas.change_control import ChangeControlImpactRequest, ChangeControlImpactResponse
from schemas.complaint import ComplaintInvestigateRequest, ComplaintInvestigateResponse
from schemas.ncr import NCRAnalyzeRequest, NCRAnalyzeResponse
from schemas.supplier import SupplierRiskRequest, SupplierRiskResponse
from typing import Optional
import openai
import os
import json
from pathlib import Path

router = APIRouter(prefix="/ai", tags=["AI Phase 3"], dependencies=[Depends(require_pro)])

# Load AI prompts
PROMPTS_DIR = Path(__file__).parent.parent.parent / "ai_prompts"

def load_prompt(filename: str) -> str:
    """Load prompt from file"""
    try:
        with open(PROMPTS_DIR / filename, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

SYSTEM_PROMPT = load_prompt("phase3_system_prompt.txt") or "You are Smart Risk Phase 3 AI. You generate, review, analyze, and cross-link quality system documents, audits, changes, suppliers, complaints, NCRs, and training content based on ISO 13485, FDA QSR, EU MDR, and GAMP5. Output JSON only."
DOCUMENT_DRAFTING_PROMPT = load_prompt("document_drafting_prompt.txt") or "Create a complete document of the specified type (DHF, DMR, SOP, WI, form) given the context. Include full structured content. Return JSON: {draft: 'text'}."
AUDIT_ASSISTANT_PROMPT = load_prompt("audit_assistant_prompt.txt") or "Given project data, risks, design outputs, and previous audits, generate an audit preparation checklist, likely findings, and regulatory gap warnings. Return JSON."
CHANGE_CONTROL_IMPACT_PROMPT = load_prompt("change_control_impact_prompt.txt") or "Analyze a proposed change. Identify all affected risks, design inputs, design outputs, tests, CAPAs, PMS signals. Return JSON."
COMPLAINT_INVESTIGATION_PROMPT = load_prompt("complaint_investigation_prompt.txt") or "Given a complaint description, generate a complete investigation, reportability assessment, and affected risks. Return JSON."
NCR_ROOT_CAUSE_PROMPT = load_prompt("ncr_root_cause_prompt.txt") or "Given an NCR, generate root cause, containment, corrective action, and verification. Return JSON."
VALIDATION_ASSISTANT_PROMPT = load_prompt("validation_assistant_prompt.txt") or "Given a system or module, generate CSV and CSA validation deliverables: URS, validation plan, test scripts, and summary report. Return JSON."

@router.post("/documents/draft", response_model=DocumentDraftResponse)
async def draft_document(
    request: DocumentDraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Document Drafting Assistant"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        prompt = f"{DOCUMENT_DRAFTING_PROMPT}\n\nType: {request.type}\nContext: {request.context or 'N/A'}\nRequirements: {', '.join(request.requirements or [])}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return DocumentDraftResponse(
            draft=data.get("draft", ""),
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/documents/summarize", response_model=DocumentSummarizeResponse)
async def summarize_document(
    request: DocumentSummarizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Document Summarization"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        from crud import document as doc_crud
        from models.document import Document
        
        document = db.query(Document).filter(Document.id == request.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        prompt = f"Summarize this document:\n\n{document.content or 'No content available'}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return DocumentSummarizeResponse(
            summary=data.get("summary", ""),
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/documents/extract-requirements", response_model=DocumentExtractRequirementsResponse)
async def extract_requirements(
    request: DocumentExtractRequirementsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Requirements Extraction"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        from models.document import Document
        
        document = db.query(Document).filter(Document.id == request.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        prompt = f"Extract all requirements from this document:\n\n{document.content or 'No content available'}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return DocumentExtractRequirementsResponse(
            requirements=data.get("requirements", []),
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/audits/prepare", response_model=AuditPrepareResponse)
async def prepare_audit(
    request: AuditPrepareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Audit Preparation Assistant"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        # Verify project ownership
        from crud import project as project_crud
        project = project_crud.get_project(db, request.project_id, current_user.id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Gather project context
        from crud import fmea as fmea_crud
        from crud import design_control as dc_crud
        from crud import audit_phase3 as audit_crud
        
        fmea_rows = fmea_crud.get_fmea_rows_by_project(db, request.project_id)
        design_outputs = dc_crud.get_design_outputs_by_project(db, request.project_id)
        previous_audits = audit_crud.get_audits_by_project(db, request.project_id)
        
        context = {
            "project_name": project.name,
            "fmea_count": len(fmea_rows),
            "design_outputs_count": len(design_outputs),
            "previous_audits_count": len(previous_audits),
            "audit_type": request.audit_type
        }
        
        prompt = f"{AUDIT_ASSISTANT_PROMPT}\n\nProject Context: {json.dumps(context)}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return AuditPrepareResponse(
            checklist=data.get("checklist", []),
            gaps=data.get("gaps", []),
            risk_areas=data.get("risk_areas", []),
            compliance_warnings=data.get("compliance_warnings", []),
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/changes/impact", response_model=ChangeControlImpactResponse)
async def analyze_change_impact(
    request: ChangeControlImpactRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Change Control Impact Analysis"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        from crud import change_control_phase3 as cc_crud
        from crud import project as project_crud
        
        change_control = cc_crud.get_change_control(db, request.change_control_id, "")
        if not change_control:
            raise HTTPException(status_code=404, detail="Change control not found")
        
        # Verify project ownership
        project = project_crud.get_project(db, change_control.project_id, current_user.id)
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        
        prompt = f"{CHANGE_CONTROL_IMPACT_PROMPT}\n\nChange Control: {change_control.title}\nDescription: {change_control.description}\nReason: {change_control.reason}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return ChangeControlImpactResponse(
            affected_risks=data.get("affected_risks", []),
            affected_design_inputs=data.get("affected_design_inputs", []),
            affected_design_outputs=data.get("affected_design_outputs", []),
            affected_vv_tests=data.get("affected_vv_tests", []),
            affected_capas=data.get("affected_capas", []),
            affected_pms_signals=data.get("affected_pms_signals", []),
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/complaints/investigate", response_model=ComplaintInvestigateResponse)
async def investigate_complaint(
    request: ComplaintInvestigateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Complaint Investigation Assistant"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        from crud import complaint_phase3 as complaint_crud
        from crud import project as project_crud
        
        complaint = complaint_crud.get_complaint(db, request.complaint_id, "")
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # Verify project ownership
        project = project_crud.get_project(db, complaint.project_id, current_user.id)
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        
        prompt = f"{COMPLAINT_INVESTIGATION_PROMPT}\n\nComplaint Description: {complaint.description}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return ComplaintInvestigateResponse(
            investigation=data.get("investigation", ""),
            affected_risks=data.get("affected_risks", []),
            reportability_decision=data.get("reportability_decision", "non_reportable"),
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/ncrs/analyze", response_model=NCRAnalyzeResponse)
async def analyze_ncr(
    request: NCRAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI NCR Analysis Assistant"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        from crud import ncr_phase3 as ncr_crud
        from crud import project as project_crud
        
        ncr = ncr_crud.get_ncr(db, request.ncr_id, "")
        if not ncr:
            raise HTTPException(status_code=404, detail="NCR not found")
        
        # Verify project ownership
        project = project_crud.get_project(db, ncr.project_id, current_user.id)
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        
        prompt = f"{NCR_ROOT_CAUSE_PROMPT}\n\nNCR Description: {ncr.description}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return NCRAnalyzeResponse(
            root_cause=data.get("root_cause", ""),
            corrective_action=data.get("corrective_action", ""),
            verification_steps=data.get("verification_steps", []),
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/suppliers/risk", response_model=SupplierRiskResponse)
async def assess_supplier_risk(
    request: SupplierRiskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Supplier Risk Assessment"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        from crud import supplier_phase3 as supplier_crud
        from models.supplier import Supplier
        
        supplier = db.query(Supplier).filter(Supplier.id == request.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        # Verify project ownership
        from crud import project as project_crud
        project = project_crud.get_project(db, supplier.project_id, current_user.id)
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get supplier evaluations
        evaluations = supplier_crud.get_supplier_evaluations(db, request.supplier_id)
        
        context = {
            "supplier_name": supplier.name,
            "category": supplier.category,
            "current_risk_rating": supplier.risk_rating,
            "evaluations_count": len(evaluations)
        }
        
        prompt = f"Assess supplier risk. Supplier: {supplier.name}, Category: {supplier.category}, Current Rating: {supplier.risk_rating}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return SupplierRiskResponse(
            risk_rating=data.get("risk_rating", 5),
            concerns=data.get("concerns", []),
            recommended_actions=data.get("recommended_actions", []),
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/validation/generate")
async def generate_validation_deliverables(
    system_name: str,
    module_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Validation Assistant (CSV and CSA)"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        prompt = f"{VALIDATION_ASSISTANT_PROMPT}\n\nSystem: {system_name}\nModule: {module_name or 'N/A'}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return {
            "urs": data.get("urs", ""),
            "validation_plan": data.get("validation_plan", ""),
            "test_scripts": data.get("test_scripts", []),
            "summary_report": data.get("summary_report", ""),
            "ai_metadata": data.get("ai_metadata")
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

