"""
Device Architecture API (SmartRisk Phase 1).
CRUD for device architectures, nodes, and interfaces per project.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from crud import project as project_crud
from crud import device_architecture as da_crud
from schemas import device_architecture as schemas
from services.hazard_generation_service import (
    generate_hazards_from_architecture,
    create_risk_items_from_suggestions,
    SuggestedHazard,
)
from services.risk_analysis_generation_service import (
    generate_and_store_for_component,
    generate_and_store_for_architecture,
)
from crud import suggested_risk_analysis as suggested_crud
from schemas import suggested_risk_analysis as suggestion_schemas

router = APIRouter(
    prefix="/projects/{project_id}/device-architectures",
    tags=["Device Architecture"],
    dependencies=[Depends(require_pro)],
)


def _ensure_project(db: Session, project_id: str, user_id: str):
    project = project_crud.get_project(db, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ---------- Architectures ----------
@router.get("", response_model=list[schemas.DeviceArchitectureOut])
def list_architectures(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all device architectures for the project."""
    _ensure_project(db, project_id, current_user.id)
    return da_crud.list_architectures_by_project(db, project_id)


@router.post("", response_model=schemas.DeviceArchitectureOut, status_code=status.HTTP_201_CREATED)
def create_architecture(
    project_id: str,
    body: schemas.DeviceArchitectureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a device architecture."""
    _ensure_project(db, project_id, current_user.id)
    return da_crud.create_architecture(db, project_id, body)


@router.get("/{architecture_id}", response_model=schemas.DeviceArchitectureDetailOut)
def get_architecture(
    project_id: str,
    architecture_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one architecture with all nodes and interfaces."""
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    nodes = da_crud.list_all_nodes(db, architecture_id)
    interfaces = da_crud.list_interfaces_by_architecture(db, architecture_id)
    return schemas.DeviceArchitectureDetailOut(
        **schemas.DeviceArchitectureOut.model_validate(arch).model_dump(),
        nodes=[schemas.DeviceArchitectureNodeOut.model_validate(n) for n in nodes],
        interfaces=[schemas.DeviceInterfaceOut.model_validate(i) for i in interfaces],
    )


@router.patch("/{architecture_id}", response_model=schemas.DeviceArchitectureOut)
def update_architecture(
    project_id: str,
    architecture_id: str,
    body: schemas.DeviceArchitectureUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an architecture."""
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    updated = da_crud.update_architecture(db, architecture_id, body)
    return updated


@router.delete("/{architecture_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_architecture(
    project_id: str,
    architecture_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an architecture and all its nodes and interfaces."""
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    da_crud.delete_architecture(db, architecture_id)


# ---------- Nodes ----------
@router.get("/{architecture_id}/nodes", response_model=list[schemas.DeviceArchitectureNodeOut])
def list_nodes(
    project_id: str,
    architecture_id: str,
    parent_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List nodes; omit parent_id for root nodes."""
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    return da_crud.list_nodes_by_architecture(db, architecture_id, parent_id=parent_id)


@router.post(
    "/{architecture_id}/nodes",
    response_model=schemas.DeviceArchitectureNodeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_node(
    project_id: str,
    architecture_id: str,
    body: schemas.DeviceArchitectureNodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a node (system, subsystem, or component)."""
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    node = da_crud.create_node(db, architecture_id, body)
    if not node:
        raise HTTPException(status_code=400, detail="Invalid parent_id or architecture")
    return node


@router.patch(
    "/{architecture_id}/nodes/{node_id}",
    response_model=schemas.DeviceArchitectureNodeOut,
)
def update_node(
    project_id: str,
    architecture_id: str,
    node_id: str,
    body: schemas.DeviceArchitectureNodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a node."""
    _ensure_project(db, project_id, current_user.id)
    node = da_crud.get_node(db, node_id)
    if not node or node.architecture_id != architecture_id:
        raise HTTPException(status_code=404, detail="Node not found")
    updated = da_crud.update_node(db, node_id, body)
    return updated


@router.delete("/{architecture_id}/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(
    project_id: str,
    architecture_id: str,
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a node (and any interfaces referencing it)."""
    _ensure_project(db, project_id, current_user.id)
    node = da_crud.get_node(db, node_id)
    if not node or node.architecture_id != architecture_id:
        raise HTTPException(status_code=404, detail="Node not found")
    da_crud.delete_node(db, node_id)


# ---------- Interfaces ----------
@router.get("/{architecture_id}/interfaces", response_model=list[schemas.DeviceInterfaceOut])
def list_interfaces(
    project_id: str,
    architecture_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all interfaces for an architecture."""
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    return da_crud.list_interfaces_by_architecture(db, architecture_id)


@router.post(
    "/{architecture_id}/interfaces",
    response_model=schemas.DeviceInterfaceOut,
    status_code=status.HTTP_201_CREATED,
)
def create_interface(
    project_id: str,
    architecture_id: str,
    body: schemas.DeviceInterfaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an interface between two nodes."""
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    iface = da_crud.create_interface(db, architecture_id, body)
    if not iface:
        raise HTTPException(status_code=400, detail="Invalid from_node_id or to_node_id")
    return iface


@router.patch(
    "/{architecture_id}/interfaces/{interface_id}",
    response_model=schemas.DeviceInterfaceOut,
)
def update_interface(
    project_id: str,
    architecture_id: str,
    interface_id: str,
    body: schemas.DeviceInterfaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an interface."""
    _ensure_project(db, project_id, current_user.id)
    iface = da_crud.get_interface(db, interface_id)
    if not iface or iface.architecture_id != architecture_id:
        raise HTTPException(status_code=404, detail="Interface not found")
    return da_crud.update_interface(db, interface_id, body)


@router.delete(
    "/{architecture_id}/interfaces/{interface_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_interface(
    project_id: str,
    architecture_id: str,
    interface_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an interface."""
    _ensure_project(db, project_id, current_user.id)
    iface = da_crud.get_interface(db, interface_id)
    if not iface or iface.architecture_id != architecture_id:
        raise HTTPException(status_code=404, detail="Interface not found")
    da_crud.delete_interface(db, interface_id)


# ---------- Hazard generation (Phase 2 / 3) ----------
@router.post(
    "/{architecture_id}/generate-hazards",
    response_model=schemas.GenerateHazardsResponse,
)
def generate_hazards(
    project_id: str,
    architecture_id: str,
    body: schemas.GenerateHazardsRequest | None = None,
    only_active_rules: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run the component-to-hazard rules engine on this architecture.
    Returns suggested hazards with traceability.
    Optionally create risk items (Phase 3) with hazard_library_id linking.
    """
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    suggestions: list[SuggestedHazard] = generate_hazards_from_architecture(
        db, architecture_id, only_active_rules=only_active_rules
    )
    out_list = [
        schemas.SuggestedHazardOut(
            source_type=s.source_type,
            source_id=s.source_id,
            source_name=s.source_name,
            source_extra=s.source_extra,
            rule_id=s.rule_id,
            hazard_library_id=s.hazard_library_id,
            hazard_code=s.hazard_code,
            hazard_name=s.hazard_name,
            hazard_description=s.hazard_description,
        )
        for s in suggestions
    ]
    created_ids = None
    if body and body.create_risk_items and out_list:
        created_ids = create_risk_items_from_suggestions(
            db, project_id, suggestions, created_by=body.created_by or current_user.id
        )
    return schemas.GenerateHazardsResponse(
        suggestions=out_list,
        created_risk_item_ids=created_ids,
    )


# ---------- Hazard log table (Phase 4 document generation) ----------
@router.get(
    "/{architecture_id}/hazard-log",
    response_model=schemas.HazardLogTableOut,
)
def get_hazard_log(
    project_id: str,
    architecture_id: str,
    only_active_rules: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return hazard log table for this architecture (for document/table generation).
    Runs the rules engine and returns structured rows for export or reporting.
    """
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    suggestions = generate_hazards_from_architecture(
        db, architecture_id, only_active_rules=only_active_rules
    )
    rows = [
        schemas.HazardLogRowOut(
            source_type=s.source_type,
            source_id=s.source_id,
            source_name=s.source_name,
            source_extra=s.source_extra,
            hazard_code=s.hazard_code,
            hazard_name=s.hazard_name,
            hazard_description=s.hazard_description,
            hazard_library_id=s.hazard_library_id,
            risk_item_id=None,
        )
        for s in suggestions
    ]
    return schemas.HazardLogTableOut(
        architecture_id=architecture_id,
        architecture_name=arch.name,
        project_id=project_id,
        rows=rows,
    )


# ---------- Stored suggestions (generate and store in suggested_* tables) ----------
class GenerateSuggestionsRequest(BaseModel):
    regenerate: bool = True
    only_active_rules: bool = True


@router.post(
    "/{architecture_id}/generate-suggestions",
    response_model=suggestion_schemas.GenerateSuggestionsResponse,
)
def generate_suggestions_for_architecture(
    project_id: str,
    architecture_id: str,
    body: GenerateSuggestionsRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Read all components (nodes and interfaces), evaluate active rules,
    generate failure modes, hazards, hazardous situations, harms, controls,
    and verification methods; store in suggested_* tables.
    When regenerate is True, existing suggestions for this architecture are deleted first.
    """
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    regenerate = body.regenerate if body else True
    only_active = body.only_active_rules if body else True
    created = generate_and_store_for_architecture(
        db, architecture_id, regenerate=regenerate, only_active_rules=only_active
    )
    return suggestion_schemas.GenerateSuggestionsResponse(created=created)


@router.post(
    "/{architecture_id}/sources/{source_type}/{source_id}/generate-suggestions",
    response_model=suggestion_schemas.GenerateSuggestionsResponse,
)
def generate_suggestions_for_component(
    project_id: str,
    architecture_id: str,
    source_type: str,
    source_id: str,
    body: GenerateSuggestionsRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate and store suggestions for a single component (node or interface).
    Use source_type 'node' or 'interface'. Regeneration replaces existing suggestions for this source.
    """
    if source_type not in ("node", "interface"):
        raise HTTPException(status_code=400, detail="source_type must be 'node' or 'interface'")
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    regenerate = body.regenerate if body else True
    only_active = body.only_active_rules if body else True
    created = generate_and_store_for_component(
        db, source_type=source_type, source_id=source_id, architecture_id=architecture_id,
        regenerate=regenerate, only_active_rules=only_active
    )
    return suggestion_schemas.GenerateSuggestionsResponse(created=created)


@router.get(
    "/{architecture_id}/suggestions",
    response_model=list[suggestion_schemas.SuggestionSetOut],
)
def list_stored_suggestions(
    project_id: str,
    architecture_id: str,
    source_type: str | None = None,
    source_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List stored suggestion sets for this architecture, optionally filtered by source."""
    _ensure_project(db, project_id, current_user.id)
    arch = da_crud.get_architecture(db, architecture_id)
    if not arch or arch.project_id != project_id:
        raise HTTPException(status_code=404, detail="Architecture not found")
    if source_type is not None and source_id is not None:
        sets = suggested_crud.list_suggestion_sets_by_source(
            db, source_type=source_type, source_id=source_id, architecture_id=architecture_id
        )
    else:
        sets = suggested_crud.list_suggestion_sets_by_architecture(db, architecture_id)
    out = []
    for s in sets:
        out.append(suggestion_schemas.SuggestionSetOut(
            id=s.id,
            source_type=s.source_type,
            source_id=s.source_id,
            architecture_id=s.architecture_id,
            project_id=getattr(s, "project_id", None),
            rule_id=s.rule_id,
            created_at=s.created_at,
            failure_modes=[suggestion_schemas.SuggestedFailureModeOut.model_validate(f) for f in s.failure_modes],
            hazards=[suggestion_schemas.SuggestedHazardOut.model_validate(h) for h in s.hazards],
            hazardous_situations=[suggestion_schemas.SuggestedHazardousSituationOut.model_validate(x) for x in s.hazardous_situations],
            harms=[suggestion_schemas.SuggestedHarmOut.model_validate(h) for h in s.harms],
            controls=[suggestion_schemas.SuggestedControlOut.model_validate(c) for c in s.controls],
            verification_methods=[suggestion_schemas.SuggestedVerificationMethodOut.model_validate(v) for v in s.verification_methods],
        ))
    return out
