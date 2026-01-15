from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from crud import project as project_crud
from crud import fmea as fmea_crud
import csv
import io

router = APIRouter(prefix="/projects/{project_id}/export", tags=["export"])

def _require_reportlab():
    """
    Lazy-import reportlab so environments without the optional PDF dependency can still import this router.
    """
    try:
        from reportlab.lib import colors  # type: ignore
        from reportlab.lib.pagesizes import letter  # type: ignore
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # type: ignore
        from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
        return colors, letter, SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, getSampleStyleSheet
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="PDF export is unavailable because the optional dependency 'reportlab' is not installed.",
        ) from e

@router.get("/csv")
def export_csv(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export FMEA data as CSV"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get FMEA rows
    rows = fmea_crud.get_fmea_rows_by_project(db, project_id)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "Component", "Failure Mode", "Effect", "Cause",
        "Severity", "Probability", "Detection", "RPN",
        "Mitigation", "Residual Severity", "Residual Probability",
        "Residual Detection", "Residual RPN", "Financial Impact",
        "Version", "Created At", "Updated At"
    ])
    
    # Write data
    for row in rows:
        # Get component name - handle both relationship and direct access
        component_name = ""
        if hasattr(row, 'component') and row.component:
            component_name = row.component.name if hasattr(row.component, 'name') else ""
        elif hasattr(row, 'component_id') and row.component_id:
            # If component not loaded, fetch it
            from crud import component as component_crud
            component = component_crud.get_component(db, row.component_id, project_id)
            component_name = component.name if component else ""
        
        writer.writerow([
            row.id,
            component_name,
            row.failure_mode or "",
            row.effect or "",
            row.cause or "",
            row.severity or "",
            row.probability or "",
            row.detection or "",
            row.rpn or "",
            row.mitigation or "",
            row.residual_severity or "",
            row.residual_probability or "",
            row.residual_detection or "",
            row.residual_rpn or "",
            str(row.financial_impact) if row.financial_impact else "",
            row.version,
            row.created_at.isoformat() if row.created_at else "",
            row.updated_at.isoformat() if row.updated_at else ""
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}_fmea.csv"}
    )

@router.get("/pdf")
def export_pdf(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export FMEA data as PDF"""
    colors, letter, SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, getSampleStyleSheet = _require_reportlab()
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get FMEA rows
    rows = fmea_crud.get_fmea_rows_by_project(db, project_id)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"FMEA Report: {project.name}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Description
    if project.description:
        desc = Paragraph(f"Description: {project.description}", styles['Normal'])
        elements.append(desc)
        elements.append(Spacer(1, 12))
    
    # Table data
    data = [["ID", "Component", "Failure Mode", "Effect", "Severity", "Probability", "Detection", "RPN"]]
    
    for row in rows:
        # Get component name - handle both relationship and direct access
        component_name = ""
        if hasattr(row, 'component') and row.component:
            component_name = row.component.name if hasattr(row.component, 'name') else ""
        elif hasattr(row, 'component_id') and row.component_id:
            # If component not loaded, fetch it
            from crud import component as component_crud
            component = component_crud.get_component(db, row.component_id, project_id)
            component_name = component.name if component else ""
        
        data.append([
            str(row.id)[:8] + "...",  # Truncate UUID
            component_name[:20],  # Truncate long names
            (row.failure_mode or "")[:30],
            (row.effect or "")[:30],
            str(row.severity or ""),
            str(row.probability or ""),
            str(row.detection or ""),
            str(row.rpn or "")
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}_fmea.pdf"}
    )

