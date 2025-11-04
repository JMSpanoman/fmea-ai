from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from models.fmea import FMEA
from models.change_control import ChangeControl
from models.capa import CAPA
from models.nonconformance import NonConformance

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

from auth.dependencies import get_current_user, create_dev_token
from routers import ai, auth, capa, change_control, fmeas, mitigations, nonconformance, projects, tracibility, templates
from routes.mastercontrol import router as mastercontrol_router



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
app.include_router(ai.router, prefix="/fmea", tags=["AI"])
app.include_router(tracibility.router, prefix="/api", tags=["Tracibility"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(mitigations.router, prefix="/fmea", tags=["Mitigations"])
app.include_router(nonconformance.router, prefix="/fmea", tags=["Non-Conformance"])
app.include_router(capa.router, prefix="/fmea", tags=["CAPA"])
app.include_router(change_control.router, prefix="/fmea", tags=["Change Control"])
app.include_router(mastercontrol_router)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Project endpoints
@app.post("/projects", response_model=project_schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project: project_schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new FMEA project"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, 'id') else current_user.username)
        return project_crud.create_project(db=db, project=project, user_id=user_id)
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/projects", response_model=List[project_schemas.ProjectOut])
def get_projects(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all projects for the authenticated user"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, 'id') else current_user.username)
        projects = project_crud.get_projects_by_user(db=db, user_id=user_id)
        
        # Convert SQLAlchemy models to Pydantic schemas
        project_outputs = []
        for project in projects:
            project_out = project_schemas.ProjectOut(
                id=project.id,
                name=project.name,
                description=project.description,
                user_id=project.user_id,
                status=project.status,
                created_at=project.created_at,
                updated_at=project.updated_at
            )
            project_outputs.append(project_out)
        
        return project_outputs
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/projects/{project_id}", response_model=project_schemas.ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific project by ID"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        project = project_crud.get_project(db=db, project_id=project_id, user_id=user_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/projects/{project_id}", response_model=project_schemas.ProjectOut)
def update_project(
    project_id: int,
    project: project_schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a project"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        updated_project = project_crud.update_project(db=db, project_id=project_id, project=project, user_id=user_id)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return updated_project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a project"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        success = project_crud.delete_project(db=db, project_id=project_id, user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# FMEA endpoints
@app.post("/projects/{project_id}/fmeas", status_code=status.HTTP_201_CREATED)
def create_fmea(
    project_id: int,
    fmea: fmea_schemas.FMEACreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new FMEA entry for a project"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        
        # Test the CRUD function directly
        db_fmea = fmea_crud.create_fmea(db=db, project_id=project_id, fmea=fmea, user_id=user_id)
        
        # Return a simple success response
        return {
            "message": "FMEA created successfully",
            "id": db_fmea.id,
            "component": db_fmea.component
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/projects/{project_id}/fmeas", response_model=List[fmea_schemas.FMEAOut])
def get_fmeas(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all FMEA entries for a project"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        db_fmeas = fmea_crud.get_fmeas_for_project(db=db, project_id=project_id, user_id=user_id)
        
        # Use automatic conversion with from_attributes=True
        return [fmea_schemas.FMEAOut.model_validate(db_fmea) for db_fmea in db_fmeas]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Temporarily commented out to isolate the issue
# @app.get("/projects/{project_id}/fmeas/{fmea_id}", response_model=fmea_schemas.FMEAOut)
# def get_fmea(
#     project_id: int,
#     fmea_id: int,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     """Get a specific FMEA entry"""
#     try:
#         # Get user ID from the authenticated user
#         user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
#         db_fmea = fmea_crud.get_fmea(db=db, project_id=project_id, fmea_id=fmea_id, user_id=user_id)
#         if not db_fmea:
#             raise HTTPException(status_code=404, detail="FMEA entry not found")
#         
#         # Use automatic conversion with from_attributes=True
#         return fmea_schemas.FMEAOut.parse_obj(db_fmea.__dict__)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# Temporarily commented out to isolate the issue
# @app.put("/projects/{project_id}/fmeas/{fmea_id}", response_model=fmea_schemas.FMEAOut)
# def update_fmea(
#     project_id: int,
#     fmea_id: int,
#     fmea: fmea_schemas.FMEAUpdate,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     """Update a FMEA entry"""
#     try:
#         # Get user ID from the authenticated user
#         user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
#         db_fmea = fmea_crud.update_fmea(db=db, project_id=project_id, fmea_id=fmea_id, fmea=fmea, user_id=user_id)
#         if not db_fmea:
#             raise HTTPException(status_code=404, detail="FMEA entry not found")
#         
#         # Use automatic conversion with from_attributes=True
#         return fmea_schemas.FMEAOut.parse_obj(db_fmea.__dict__)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

@app.delete("/projects/{project_id}/fmeas/{fmea_id}")
def delete_fmea(
    project_id: int,
    fmea_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a FMEA entry"""
    try:
        # Get user ID from the authenticated user
        user_id = str(current_user.id if hasattr(current_user, "id") else current_user.username)
        success = fmea_crud.delete_fmea(db=db, project_id=project_id, fmea_id=fmea_id, user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="FMEA entry not found")
        return {"message": "FMEA entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
