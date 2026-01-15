from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import csv
import io
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import get_db
from models.project import Project
from models.fmea import FMEARow
# Legacy models (commented out for Phase 1)
# from models.change_control import ChangeControl
# from models.capa import CAPA
# from models.nonconformance import NonConformance

from schemas import project as project_schemas
from schemas import fmea as fmea_schemas
from schemas import change_control as change_control_schemas
from schemas import capa as capa_schemas
from schemas import nonconformance as nonconformance_schemas

from crud import project as project_crud
from crud import fmea as fmea_crud
from crud import change_control as change_control_crud
from crud import capa as capa_crud
from crud import nonconformance as nonconformance_crud

from auth.dependencies import get_current_user
from routers import ai, auth, capa, change_control, mitigations, nonconformance, projects, tracibility, templates
from routes.mastercontrol import router as mastercontrol_router
# Phase 1 routers
from routers import projects as projects_phase1, components, fmea as fmea_phase1, ai_phase1, export
# Phase 2 routers
from routers import design_controls, vv, capa_phase2, pms, traceability, ai_phase2
# Phase 3 routers
from routers import document_control, training_phase3, change_control_phase3, audit_phase3, supplier_phase3, ncr_phase3, complaint_phase3, equipment_phase3, quality_event_phase3, approval_phase3, ai_phase3
# Risk Items router
from routers import risk_items
# Risk Management Plan router
from routers import risk_management_plan
# Risk Management File router
from routers import rmf
# Hazard Analysis router
from routers import hazard_analysis
# Residual Risk Evaluation router
from routers import residual_risk
# Risk Control Measures Documentation router
from routers import risk_controls_doc
# Reports - Risk Control Measures router
from routers import reports_risk_control_measures
# Reports - Design Inputs router
from routers import reports_design_inputs
# PMS Signal router
from routers import pms_signal
# Reports - V&V Evidence router
from routers import reports_vv_evidence
from routers import project_profile
from routers import project_initialize
from routers import document_guidance
from routers import traceability_impact



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get CORS origins from environment
def get_cors_origins():
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:4173")
    return [origin.strip() for origin in cors_origins.split(",")]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Smart FMEA Builder API")
    # Create database tables if they don't exist
    from database import engine, Base
    # Import all models to ensure they're registered
    from models import user, project, fmea, component, project_profile as _project_profile, risk_item, risk_item_version, risk_control, approval, trace_link, ai_event, audit_log_event, design_input, design_output, vv_test, risk_management_plan, pms_signal, generated_artifact
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")

    # SQLite runtime migrations (add missing columns on existing tables)
    try:
        from db.runtime_migrations import ensure_component_columns
        ensure_component_columns(engine)
    except Exception as mig_err:
        logger.error(f"Runtime migrations failed: {mig_err}", exc_info=True)

    # Cleanup expired filesystem artifacts (best-effort, safe for multi-user)
    try:
        from database import SessionLocal
        from crud.generated_artifact import cleanup_generated_artifacts
        db = SessionLocal()
        try:
            stats = cleanup_generated_artifacts(db)
            logger.info(f"GeneratedArtifact cleanup: {stats}")
        finally:
            db.close()
    except Exception as cleanup_err:
        logger.error(f"GeneratedArtifact cleanup failed: {cleanup_err}", exc_info=True)

    # Backfill document ai_metadata flags for existing starter content (best-effort).
    # This enables consistent frontend behavior ("hasAiSample") without touching user content.
    try:
        from database import SessionLocal
        from services.document_sample_backfill import backfill_default_sample_flags
        db = SessionLocal()
        try:
            stats = backfill_default_sample_flags(db)
            logger.info(f"Starter content backfill: {stats}")
        finally:
            db.close()
    except Exception as backfill_err:
        logger.error(f"Starter content backfill failed: {backfill_err}", exc_info=True)

    yield
    # Shutdown
    logger.info("Shutting down Smart FMEA Builder API")

# Create FastAPI app
app = FastAPI(
    title="Smart FMEA Builder API",
    description="Backend API for the Smart FMEA Builder application",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Phase 1 routers (primary)
app.include_router(projects_phase1.router, tags=["Projects"])
app.include_router(components.router, tags=["Components"])
app.include_router(project_profile.router, tags=["Project Profile"])
app.include_router(project_initialize.router, tags=["Project Initialize"])
app.include_router(fmea_phase1.router, tags=["FMEA"])
app.include_router(ai_phase1.router, tags=["AI Phase 1"])
app.include_router(export.router, tags=["Export"])

# Phase 2 routers
app.include_router(design_controls.router, tags=["Design Controls"])
app.include_router(vv.router, tags=["V&V"])
app.include_router(capa_phase2.router, tags=["CAPA Phase 2"])
app.include_router(pms.router, tags=["PMS"])
app.include_router(traceability.router, tags=["Traceability"])
app.include_router(ai_phase2.router, tags=["AI Phase 2"])

# Phase 3 routers
app.include_router(document_control.router, tags=["Document Control"])
app.include_router(document_guidance.router, tags=["Document Guidance"])
app.include_router(traceability_impact.router, tags=["Traceability & Impact"])
app.include_router(training_phase3.router, tags=["Training Phase 3"])
app.include_router(change_control_phase3.router, tags=["Change Control Phase 3"])
app.include_router(audit_phase3.router, tags=["Audit Phase 3"])
app.include_router(supplier_phase3.router, tags=["Supplier Quality Phase 3"])
app.include_router(ncr_phase3.router, tags=["NCR Phase 3"])
app.include_router(complaint_phase3.router, tags=["Complaint Handling Phase 3"])
app.include_router(equipment_phase3.router, tags=["Equipment Phase 3"])
app.include_router(quality_event_phase3.router, tags=["Quality Events Phase 3"])
app.include_router(approval_phase3.router, tags=["Approvals Phase 3"])
app.include_router(ai_phase3.router, tags=["AI Phase 3"])

# Risk Items router
app.include_router(risk_items.router, tags=["Risk Items"])
# Risk Management Plan router
app.include_router(risk_management_plan.router, tags=["Risk Management Plan"])
# Risk Management File router
app.include_router(rmf.router, tags=["Risk Management File"])
# Hazard Analysis router
app.include_router(hazard_analysis.router, tags=["Hazard Analysis"])
# Residual Risk Evaluation router
app.include_router(residual_risk.router, tags=["Residual Risk Evaluation"])
# Risk Control Measures Documentation router
app.include_router(risk_controls_doc.router, tags=["Risk Control Measures Documentation"])
# Reports - Risk Control Measures router
app.include_router(reports_risk_control_measures.router, tags=["Reports - Risk Control Measures"])
# Reports - Design Inputs router
app.include_router(reports_design_inputs.router, tags=["Reports - Design Inputs"])
# PMS Signal router
app.include_router(pms_signal.router, tags=["PMS Signals"])
# Reports - V&V Evidence router
app.include_router(reports_vv_evidence.router, tags=["Reports - V&V Evidence"])

# Legacy routers (for backward compatibility - can be removed later)
app.include_router(ai.router, prefix="/fmea", tags=["AI (Legacy)"])
app.include_router(tracibility.router, prefix="/api", tags=["Tracibility"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(mitigations.router, prefix="/fmea", tags=["Mitigations"])
app.include_router(nonconformance.router, prefix="/fmea", tags=["Non-Conformance"])
app.include_router(capa.router, prefix="/fmea", tags=["CAPA"])
app.include_router(change_control.router, prefix="/fmea", tags=["Change Control"])
app.include_router(mastercontrol_router)


# CORS middleware - must be added before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handlers to ensure CORS headers are included in error responses
from fastapi import Request
from fastapi.exceptions import RequestValidationError

def get_cors_headers(request: Request) -> dict:
    """Get CORS headers for a request"""
    origin = request.headers.get("origin")
    allowed_origins = get_cors_origins()
    
    if origin and origin in allowed_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    return {}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with CORS headers"""
    headers = get_cors_headers(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers"""
    headers = get_cors_headers(request)
    return JSONResponse(
        status_code=422,
        # Pydantic v2 errors may include non-JSON-serializable objects (e.g., ValueError in ctx).
        content={"detail": jsonable_encoder(exc.errors())},
        headers=headers
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler that includes CORS headers"""
    headers = get_cors_headers(request)
    
    # Log the error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Return error response with CORS headers
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
        headers=headers
    )

# Security

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Smart FMEA Builder API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "message": "Smart FMEA Builder API is running",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }

# Test endpoint for debugging
@app.get("/test")
def test_endpoint():
    return {"message": "Backend is working correctly"}

# Development authentication endpoint (only in development)
# REMOVED: Duplicate route definition - now handled by auth router
# @app.post("/auth/dev-login")
# def dev_login():
#     """Development endpoint to get a test token"""
#     if os.getenv("ENVIRONMENT") == "production":
#         raise HTTPException(status_code=404, detail="Endpoint not available in production")
#     token = create_dev_token()
#     return {"access_token": token, "token_type": "bearer"}

#
# Project endpoints
#
# NOTE: These were legacy/duplicate route definitions that conflicted with
# `routers/projects.py` (the canonical UUID-based project API). Keeping both
# resulted in inconsistent behavior and hard-to-debug failures.
#
# The active Project API is implemented in `fmea_backend/routers/projects.py`
# and is included via `app.include_router(projects_phase1.router, ...)`.

#
# Legacy FMEA endpoints removed:
# - /projects/{project_id}/fmeas (plural)
# These conflict with the canonical, project-first FMEA router:
# - `fmea_backend/routers/fmea.py` mounted at /projects/{project_id}/fmea (singular)
#
# The frontend does not call the plural endpoints anymore, so we remove them to
# reduce attack surface area and avoid ambiguous behavior.

# Change Control endpoints
@app.post("/projects/{project_id}/change-controls", status_code=status.HTTP_201_CREATED)
def create_change_control(
    project_id: int,
    change_control: change_control_schemas.ChangeControlCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new change control entry for a project"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        return change_control_crud.create_change_control(db=db, project_id=project_id, change_control=change_control, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/projects/{project_id}/change-controls", response_model=List[change_control_schemas.ChangeControlOut])
def get_change_controls(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all change control entries for a project"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        change_controls = change_control_crud.get_change_controls_for_project(db=db, project_id=project_id, user_id=user_id)
        
        # Convert SQLAlchemy models to Pydantic schemas
        change_control_outputs = []
        for change_control in change_controls:
            change_control_out = change_control_schemas.ChangeControlOut(
                id=change_control.id,
                project_id=change_control.project_id,
                user_id=change_control.user_id,
                change_description=change_control.change_description,
                initiator=change_control.initiator,
                date_initiated=change_control.date_initiated,
                status=change_control.status,
                impact_assessment=change_control.impact_assessment,
                actions_required=change_control.actions_required,
                action_owner=change_control.action_owner,
                due_date=change_control.due_date,
                closure_summary=change_control.closure_summary,
                analysis_timestamp=change_control.analysis_timestamp,
                version=change_control.version,
                created_at=change_control.created_at,
                updated_at=change_control.updated_at
            )
            change_control_outputs.append(change_control_out)
        
        return change_control_outputs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/projects/{project_id}/change-controls/{change_control_id}", response_model=change_control_schemas.ChangeControlOut)
def get_change_control(
    project_id: int,
    change_control_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific change control entry by ID"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        change_control = change_control_crud.get_change_control(db=db, change_control_id=change_control_id, user_id=user_id)
        if not change_control:
            raise HTTPException(status_code=404, detail="Change control entry not found")
        return change_control
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/projects/{project_id}/change-controls/{change_control_id}", response_model=change_control_schemas.ChangeControlOut)
def update_change_control(
    project_id: int,
    change_control_id: int,
    change_control: change_control_schemas.ChangeControlUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a change control entry"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        updated_change_control = change_control_crud.update_change_control(db=db, change_control_id=change_control_id, change_control=change_control, user_id=user_id)
        if not updated_change_control:
            raise HTTPException(status_code=404, detail="Change control entry not found")
        return updated_change_control
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/projects/{project_id}/change-controls/{change_control_id}")
def delete_change_control(
    project_id: int,
    change_control_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a change control entry"""
    try:
        result = change_control_crud.delete_change_control(db, project_id, change_control_id)
        if not result:
            raise HTTPException(status_code=404, detail="Change control not found")
        return {"message": "Change control deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting change control: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# CAPA endpoints
@app.post("/projects/{project_id}/capas", status_code=status.HTTP_201_CREATED)
def create_capa(
    project_id: int,
    capa: capa_schemas.CAPACreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new CAPA entry"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        return capa_crud.create_capa(db=db, project_id=project_id, capa_data=capa, user_id=user_id)
    except Exception as e:
        logger.error(f"Error creating CAPA: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/projects/{project_id}/capas", response_model=List[capa_schemas.CAPAOut])
def get_capas(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all CAPA entries for a project"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        capas = capa_crud.get_capas_for_project(db=db, project_id=project_id, user_id=user_id)
        
        # Convert SQLAlchemy models to Pydantic schemas
        capa_outputs = []
        for capa_entry in capas:
            capa_out = capa_schemas.CAPAOut(
                id=capa_entry.id,
                project_id=capa_entry.project_id,
                user_id=capa_entry.user_id,
                issue_description=capa_entry.issue_description,
                source=capa_entry.source,
                detection_date=capa_entry.detection_date,
                severity=capa_entry.severity,
                root_cause=capa_entry.root_cause,
                corrective_action=capa_entry.corrective_action,
                preventive_action=capa_entry.preventive_action,
                action_owner=capa_entry.action_owner,
                due_date=capa_entry.due_date,
                status=capa_entry.status,
                effectiveness_check_plan=capa_entry.effectiveness_check_plan,
                fmea_link=capa_entry.fmea_link,
                regulatory_impact=capa_entry.regulatory_impact,
                closure_summary=capa_entry.closure_summary,
                milestones=capa_entry.milestones,
                risk_controls_update=capa_entry.risk_controls_update,
                analysis_timestamp=capa_entry.analysis_timestamp,
                version=capa_entry.version,
                created_at=capa_entry.created_at,
                updated_at=capa_entry.updated_at
            )
            capa_outputs.append(capa_out)
        
        return capa_outputs
    except Exception as e:
        logger.error(f"Error getting CAPAs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Non-Conformance endpoints
@app.post("/projects/{project_id}/non-conformances", status_code=status.HTTP_201_CREATED)
def create_nonconformance(
    project_id: int,
    nonconformance: nonconformance_schemas.NonConformanceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new Non-Conformance entry"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        return nonconformance_crud.create_nonconformance(db=db, project_id=project_id, nonconformance_data=nonconformance, user_id=user_id)
    except Exception as e:
        logger.error(f"Error creating Non-Conformance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/projects/{project_id}/non-conformances", response_model=List[nonconformance_schemas.NonConformanceOut])
def get_nonconformances(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all Non-Conformance entries for a project"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        nonconformances = nonconformance_crud.get_nonconformances_for_project(db=db, project_id=project_id, user_id=user_id)
        
        # Convert SQLAlchemy models to Pydantic schemas
        nonconformance_outputs = []
        for nonconformance_entry in nonconformances:
            nonconformance_out = nonconformance_schemas.NonConformanceOut(
                id=nonconformance_entry.id,
                project_id=nonconformance_entry.project_id,
                user_id=nonconformance_entry.user_id,
                issue_description=nonconformance_entry.issue_description,
                source=nonconformance_entry.source,
                detection_date=nonconformance_entry.detection_date,
                severity=nonconformance_entry.severity,
                root_cause=nonconformance_entry.root_cause,
                corrective_action=nonconformance_entry.corrective_action,
                preventive_action=nonconformance_entry.preventive_action,
                action_owner=nonconformance_entry.action_owner,
                due_date=nonconformance_entry.due_date,
                status=nonconformance_entry.status,
                investigation_details=nonconformance_entry.investigation_details,
                regulatory_impact=nonconformance_entry.regulatory_impact,
                closure_summary=nonconformance_entry.closure_summary,
                analysis_timestamp=nonconformance_entry.analysis_timestamp,
                version=nonconformance_entry.version,
                created_at=nonconformance_entry.created_at,
                updated_at=nonconformance_entry.updated_at
            )
            nonconformance_outputs.append(nonconformance_out)
        
        return nonconformance_outputs
    except Exception as e:
        logger.error(f"Error getting Non-Conformances: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



# AI Suggestions endpoint
@app.post("/ai/suggestions")
def get_ai_suggestions(
    request: fmea_schemas.AISuggestionRequest,
    current_user = Depends(get_current_user)
):
    """Get AI suggestions for FMEA entries"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        # This would integrate with your AI service
        suggestions = fmea_crud.get_ai_suggestions(request, user_id)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Export endpoints
@app.get("/projects/{project_id}/export/csv")
def export_fmea_csv(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export FMEA data as CSV"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        csv_data = fmea_crud.export_fmea_csv(db=db, project_id=project_id, user_id=user_id)
        return JSONResponse(content=csv_data, media_type="text/csv")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/projects/{project_id}/export/pdf")
def export_fmea_pdf(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export FMEA data as PDF"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        pdf_data = fmea_crud.export_fmea_pdf(db=db, project_id=project_id, user_id=user_id)
        return JSONResponse(content=pdf_data, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/projects/{project_id}/import/csv")
def import_fmea_csv(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Import FMEA data from a CSV file"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        
        # Verify project exists and user has access
        project = project_crud.get_project(db=db, project_id=project_id, user_id=user_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check file type
        if not file.filename or not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read CSV content
        content = file.file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(content))
        
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
            try:
                # Map CSV columns to FMEA fields
                fmea_data = {
                    "component": row.get("Component", row.get("component", "")),
                    "failure_mode": row.get("Failure Mode", row.get("failure_mode", "")),
                    "effect": row.get("Effect", row.get("effect", "")),
                    "cause": row.get("Cause", row.get("cause", "")),
                    "severity": int(row.get("Severity", row.get("severity", 1))),
                    "occurrence": int(row.get("Occurrence", row.get("occurrence", row.get("Probability", 1)))),
                    "detection": int(row.get("Detection", row.get("detection", 1))),
                    "rpn": int(row.get("RPN", row.get("rpn", 1))),
                    "mitigation": row.get("Mitigation", row.get("mitigation", "")),
                    "action_taken": row.get("Action Taken", row.get("action_taken", "")),
                    "revised_severity": int(row.get("Revised Severity", row.get("revised_severity", 0))) if row.get("Revised Severity") or row.get("revised_severity") else None,
                    "revised_occurrence": int(row.get("Revised Occurrence", row.get("revised_occurrence", row.get("Revised Probability", 0)))) if row.get("Revised Occurrence") or row.get("revised_occurrence") or row.get("Revised Probability") else None,
                    "revised_detection": int(row.get("Revised Detection", row.get("revised_detection", 0))) if row.get("Revised Detection") or row.get("revised_detection") else None,
                    "revised_rpn": int(row.get("Revised RPN", row.get("revised_rpn", 0))) if row.get("Revised RPN") or row.get("revised_rpn") else None,
                }
                
                # Create FMEA entry
                fmea_create = fmea_schemas.FMEACreate(**fmea_data)
                fmea_crud.create_fmea(db=db, project_id=project_id, fmea=fmea_create, user_id=user_id)
                imported_count += 1
                
            except (ValueError, KeyError) as e:
                errors.append(f"Row {row_num}: {str(e)}")
            except Exception as e:
                errors.append(f"Row {row_num}: Unexpected error - {str(e)}")
        
        return {
            "message": f"Successfully imported {imported_count} FMEA entries",
            "imported_count": imported_count,
            "errors": errors if errors else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
