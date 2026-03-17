from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from models.risk_item import RiskItem
from models.risk_control import RiskControl
from models.risk_item_version import RiskItemVersion
from schemas import trace as trace_schemas
from crud import traceability as trace_crud
from crud import project as project_crud
from typing import List, Dict, Any

router = APIRouter(prefix="/projects/{project_id}", tags=["Traceability"], dependencies=[Depends(require_pro)])

@router.get("/trace", response_model=trace_schemas.TraceMatrixResponse)
def get_trace_matrix(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get traceability matrix for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    matrix = trace_crud.get_trace_matrix(db, project_id)
    return trace_schemas.TraceMatrixResponse(
        links=[trace_schemas.TraceLinkOut(
            id=link.id,
            project_id=link.project_id,
            from_type=link.from_type,
            from_id=link.from_id,
            to_type=link.to_type,
            to_id=link.to_id,
            link_type=getattr(link, 'link_type', 'traces_to'),
            created_at=link.created_at
        ) for link in matrix["links"]],
        graph=matrix["graph"]
    )

@router.post("/trace/link", response_model=trace_schemas.TraceLinkOut, status_code=status.HTTP_201_CREATED)
def create_trace_link(
    project_id: str,
    trace_link: trace_schemas.TraceLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a manual trace link"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter (Pydantic v2 compatible)
    if hasattr(trace_link, 'model_copy'):
        trace_link = trace_link.model_copy(update={'project_id': project_id})
    else:
        # Pydantic v1 fallback
        trace_link_dict = trace_link.dict() if hasattr(trace_link, 'dict') else trace_link.model_dump()
        trace_link_dict['project_id'] = project_id
        trace_link = trace_schemas.TraceLinkCreate(**trace_link_dict)
    
    link = trace_crud.create_trace_link(db, trace_link)
    return trace_schemas.TraceLinkOut(
        id=link.id,
        project_id=link.project_id,
        from_type=link.from_type,
        from_id=link.from_id,
        to_type=link.to_type,
        to_id=link.to_id,
        link_type=getattr(link, 'link_type', 'traces_to'),
        created_at=link.created_at
    )

@router.get("/trace/upstream/{artifact_type}/{artifact_id}")
def get_upstream_links(
    project_id: str,
    artifact_type: str,
    artifact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upstream trace links for any artifact (links TO this artifact) with enriched display info"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get links where this artifact is the target
    links = trace_crud.get_trace_links_to(db, artifact_type, artifact_id, project_id)
    
    # Enrich links with display information
    enriched_links = []
    for link in links:
        from_key = None
        from_display = None
        
        # Fetch display info based on from_type
        if link.from_type == 'risk_item':
            risk_item = db.query(RiskItem).filter(RiskItem.id == link.from_id).first()
            if risk_item:
                from_key = risk_item.title or f"R-{risk_item.id[:8].upper()}"
                from_display = f"{from_key}"
                if risk_item.hazard:
                    from_display += f": {risk_item.hazard[:50]}"
        
        elif link.from_type == 'risk_item_version':
            version = db.query(RiskItemVersion).filter(RiskItemVersion.id == link.from_id).first()
            if version:
                risk_item = db.query(RiskItem).filter(RiskItem.id == version.risk_item_id).first()
                if risk_item:
                    risk_key = risk_item.title or f"R-{risk_item.id[:8].upper()}"
                    from_key = f"{risk_key} v{version.version_number}"
                    from_display = f"{from_key}"
                    if version.hazard:
                        from_display += f": {version.hazard[:50]}"
        
        elif link.from_type == 'risk_control':
            control = db.query(RiskControl).filter(RiskControl.id == link.from_id).first()
            if control:
                from_key = control.control_name or f"RC-{control.id[:8].upper()}"
                from_display = f"{from_key}"
                if control.control_description:
                    from_display += f": {control.control_description[:50]}"
        
        # Create enriched link response
        link_dict = {
            "id": link.id,
            "project_id": link.project_id,
            "from_type": link.from_type,
            "from_id": link.from_id,
            "to_type": link.to_type,
            "to_id": link.to_id,
            "link_type": getattr(link, 'link_type', 'traces_to'),
            "created_at": link.created_at.isoformat() if hasattr(link.created_at, 'isoformat') else str(link.created_at),
        }
        
        if from_key:
            link_dict["from_key"] = from_key
        if from_display:
            link_dict["from_display"] = from_display
        
        enriched_links.append(link_dict)
    
    # Filter for risk-related upstream links
    risk_upstream = [link for link in enriched_links if link['from_type'] in ['risk_item', 'risk_item_version', 'risk_control']]
    
    return {
        "upstream_links": risk_upstream,
        "all_upstream": enriched_links
    }

