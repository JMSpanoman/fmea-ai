import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import logging
import re
from datetime import datetime

from auth.dependencies import get_current_user
from models.user import User
from sqlalchemy.orm import Session
from database import get_db
from crud import generated_artifact as artifact_crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Create templates directory if it doesn't exist
TEMPLATES_DIR = Path("templates")
TEMPLATES_DIR.mkdir(exist_ok=True)

# --- Security helpers ---
_SAFE_TEMPLATE_NAME_RE = re.compile(r"^[a-zA-Z0-9._-]+\.(docx|doc)$", re.IGNORECASE)



def _is_safe_template_filename(filename: str) -> bool:
    """Strict allowlist: no path separators; only safe chars and .docx/.doc extension."""
    if not isinstance(filename, str) or not filename:
        return False
    if "/" in filename or "\\" in filename:
        return False
    return _SAFE_TEMPLATE_NAME_RE.fullmatch(filename) is not None


def _safe_path_in_dir(base_dir: Path, filename: str) -> Path:
    """Resolve filename within base_dir; prevent traversal and nested directories."""
    base = base_dir.resolve()
    candidate = (base / filename).resolve()
    if candidate.parent != base:
        raise ValueError("Invalid filename path")
    try:
        if not candidate.is_relative_to(base):
            raise ValueError("Invalid filename path")
    except AttributeError:
        if str(candidate).find(str(base)) != 0:
            raise ValueError("Invalid filename path")
    return candidate


def _is_production_env() -> bool:
    return (os.getenv("ENVIRONMENT") or "").lower() == "production"

class TemplateInfo(BaseModel):
    filename: str
    size: int
    upload_date: str
    template_type: str

class TemplateResponse(BaseModel):
    message: str
    template_info: Optional[TemplateInfo] = None

@router.post("/upload", response_model=TemplateResponse)
async def upload_template(
    file: UploadFile = File(...),
    template_type: str = "risk_management_report",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a Word template file for risk management reports
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.docx', '.doc')):
            raise HTTPException(
                status_code=400, 
                detail="Only Word documents (.docx, .doc) are allowed"
            )
        
        # Validate file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail="File size must be less than 10MB"
            )
        
        # Create template filename
        raw_name = Path(file.filename).name  # strip any directories just in case
        sanitized_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", raw_name).strip("._-")
        sanitized_type = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(template_type)).strip("._-") or "template"
        safe_filename = f"{sanitized_type}_{sanitized_name}"
        if not _is_safe_template_filename(safe_filename):
            raise HTTPException(status_code=400, detail="Invalid template filename")

        template_path = _safe_path_in_dir(TEMPLATES_DIR, safe_filename)
        
        # Save the uploaded file
        with open(template_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Persist artifact record for multi-user authorization across restarts
        artifact_crud.create_generated_artifact(
            db,
            user_id=current_user.id,
            project_id=None,
            filename=safe_filename,
            artifact_type="template",
        )
        
        # Get file info
        file_size = os.path.getsize(template_path)
        
        template_info = TemplateInfo(
            filename=safe_filename,
            size=file_size,
            upload_date=os.path.getctime(template_path),
            template_type=template_type
        )
        
        logger.info(f"Template uploaded successfully: {safe_filename}")
        
        return TemplateResponse(
            message="Template uploaded successfully",
            template_info=template_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload template: {str(e)}")

@router.get("/list", response_model=List[TemplateInfo])
async def list_templates():
    """
    List all available templates
    """
    try:
        templates = []
        for template_file in TEMPLATES_DIR.glob("*"):
            if template_file.is_file():
                template_info = TemplateInfo(
                    filename=template_file.name,
                    size=os.path.getsize(template_file),
                    upload_date=os.path.getctime(template_file),
                    template_type=template_file.stem.split('_')[0] if '_' in template_file.stem else 'unknown'
                )
                templates.append(template_info)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")

@router.get("/download/{filename}")
async def download_template(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Download a specific template file
    """
    try:
        if not _is_safe_template_filename(filename):
            raise HTTPException(status_code=400, detail="Invalid filename")

        rec = artifact_crud.get_generated_artifact_for_user(
            db,
            user_id=current_user.id,
            filename=filename,
            artifact_type="template",
        )
        if not rec:
            # Fail closed (and don't leak existence)
            raise HTTPException(status_code=404, detail="Template not found")

        template_path = _safe_path_in_dir(TEMPLATES_DIR, filename)
        
        if not template_path.exists():
            raise HTTPException(status_code=404, detail="Template not found")
        
        return FileResponse(
            path=template_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download template: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_template(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a specific template file
    """
    try:
        if not _is_safe_template_filename(filename):
            raise HTTPException(status_code=400, detail="Invalid filename")

        rec = artifact_crud.get_generated_artifact_for_user(
            db,
            user_id=current_user.id,
            filename=filename,
            artifact_type="template",
        )
        if _is_production_env():
            # In production, require a matching ownership record
            if not rec:
                raise HTTPException(status_code=403, detail="Not allowed to delete this template")
        else:
            # In non-production, fail closed if we have no record (prevents cross-user deletes)
            if not rec:
                raise HTTPException(status_code=403, detail="Not allowed to delete this template")

        template_path = _safe_path_in_dir(TEMPLATES_DIR, filename)
        
        if not template_path.exists():
            raise HTTPException(status_code=404, detail="Template not found")
        
        os.remove(template_path)
        artifact_crud.delete_generated_artifact_for_user(
            db,
            user_id=current_user.id,
            filename=filename,
            artifact_type="template",
        )
        logger.info(f"Template deleted successfully: {filename}")
        
        return {"message": f"Template {filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")

@router.get("/types")
async def get_template_types():
    """
    Get available template types
    """
    return {
        "template_types": [
            "risk_management_report",
            "fmea_report",
            "hazard_analysis",
            "risk_evaluation",
            "general"
        ]
    }
