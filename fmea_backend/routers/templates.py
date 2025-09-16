import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Create templates directory if it doesn't exist
TEMPLATES_DIR = Path("templates")
TEMPLATES_DIR.mkdir(exist_ok=True)

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
    template_type: str = "risk_management_report"
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
        safe_filename = f"{template_type}_{file.filename}"
        template_path = TEMPLATES_DIR / safe_filename
        
        # Save the uploaded file
        with open(template_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
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
async def download_template(filename: str):
    """
    Download a specific template file
    """
    try:
        template_path = TEMPLATES_DIR / filename
        
        if not template_path.exists():
            raise HTTPException(status_code=404, detail="Template not found")
        
        return FileResponse(
            path=template_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Error downloading template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download template: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_template(filename: str):
    """
    Delete a specific template file
    """
    try:
        template_path = TEMPLATES_DIR / filename
        
        if not template_path.exists():
            raise HTTPException(status_code=404, detail="Template not found")
        
        os.remove(template_path)
        logger.info(f"Template deleted successfully: {filename}")
        
        return {"message": f"Template {filename} deleted successfully"}
        
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
