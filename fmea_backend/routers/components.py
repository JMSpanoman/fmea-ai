from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas import component as component_schemas
from schemas import suggested_risk_analysis as suggestion_schemas
from crud import component as component_crud
from crud import project as project_crud
from crud import suggested_risk_analysis as suggested_crud
from services.risk_analysis_generation_service import generate_and_store_for_project_component
from typing import Optional, Union, List

router = APIRouter(prefix="/projects/{project_id}/components", tags=["components"], dependencies=[Depends(require_pro)])

@router.get("", response_model=list[component_schemas.ComponentOut])
def get_components(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all components for a project"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    components = component_crud.get_components_by_project(db, project_id)
    return components

@router.post(
    "",
    response_model=Union[component_schemas.ComponentOut, List[component_schemas.ComponentOut]],
    status_code=status.HTTP_201_CREATED,
)
def create_component(
    project_id: str,
    component: Union[component_schemas.ComponentCreate, List[component_schemas.ComponentBulkItem]] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create components for a project.

    Backward compatible:
    - If body is an object => create a single component (legacy behavior).
    - If body is a list => bulk create/update + best-effort replace cleanup.
    """
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if isinstance(component, list):
        final_components, _stats = component_crud.bulk_create_replace_components(
            db, project_id=project_id, items=component
        )
        return final_components

    return component_crud.create_component(db, component, project_id)


@router.patch("/{component_id}", response_model=component_schemas.ComponentOut)
def patch_component(
    project_id: str,
    component_id: str,
    body: component_schemas.ComponentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a component (optional convenience endpoint)."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    updated = component_crud.update_component(db, component_id, body, project_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Component not found")
    return updated


# ---------- Risk suggestions (generate, list, delete) ----------
class GenerateRiskSuggestionsRequest(BaseModel):
    regenerate: bool = True
    only_active_rules: bool = True


@router.post(
    "/{component_id}/generate-risk-suggestions",
    response_model=suggestion_schemas.GenerateSuggestionsResponse,
)
def generate_risk_suggestions(
    project_id: str,
    component_id: str,
    body: GenerateRiskSuggestionsRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate risk suggestions for this component: evaluate active rules (trigger_type=component),
    create suggested failure modes, hazards, hazardous situations, harms, controls, verification;
    store in suggested_* tables. Component type is derived from tags.type or tags.component_type.
    """
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    regenerate = body.regenerate if body else True
    only_active = body.only_active_rules if body else True
    created = generate_and_store_for_project_component(
        db, project_id, component_id, regenerate=regenerate, only_active_rules=only_active
    )
    return suggestion_schemas.GenerateSuggestionsResponse(created=created)


@router.get(
    "/{component_id}/risk-suggestions",
    response_model=list[suggestion_schemas.SuggestionSetOut],
)
def get_risk_suggestions(
    project_id: str,
    component_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List stored risk suggestion sets for this component."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    sets = suggested_crud.list_suggestion_sets_by_component(db, project_id, component_id)
    out = []
    for s in sets:
        out.append(suggestion_schemas.SuggestionSetOut(
            id=s.id,
            source_type=s.source_type,
            source_id=s.source_id,
            architecture_id=s.architecture_id,
            project_id=s.project_id,
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


@router.delete("/{component_id}/risk-suggestions", status_code=status.HTTP_204_NO_CONTENT)
def delete_risk_suggestions(
    project_id: str,
    component_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all stored risk suggestions for this component."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    suggested_crud.delete_suggestions_by_component(db, project_id, component_id)


@router.delete(
    "/{component_id}/risk-suggestions/{suggestion_set_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_one_risk_suggestion(
    project_id: str,
    component_id: str,
    suggestion_set_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject: delete a single suggestion set for this component."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    s = suggested_crud.get_suggestion_set(db, suggestion_set_id)
    if not s or s.source_type != "component" or s.source_id != component_id or s.project_id != project_id:
        raise HTTPException(status_code=404, detail="Suggestion set not found")
    suggested_crud.delete_suggestion_set(db, suggestion_set_id)


class ControlAcceptItem(BaseModel):
    """Per-control text and optional library link when accepting."""
    control_text: Optional[str] = None
    risk_control_library_id: Optional[str] = None


class VerificationAcceptItem(BaseModel):
    """Per-verification text and optional library link when accepting."""
    verification_text: Optional[str] = None
    verification_library_id: Optional[str] = None


class AcceptSuggestionRequest(BaseModel):
    """Optional overrides when accepting: edited text, library links, per-control/verification items."""
    failure_mode: Optional[str] = None
    hazard: Optional[str] = None
    hazardous_situation: Optional[str] = None
    harm: Optional[str] = None
    control: Optional[str] = None
    verification: Optional[str] = None
    hazard_library_id: Optional[str] = None
    harm_library_id: Optional[str] = None
    controls: Optional[List[ControlAcceptItem]] = None
    verifications: Optional[List[VerificationAcceptItem]] = None


class AcceptSuggestionResponse(BaseModel):
    risk_item_id: str
    project_risk_item_id: Optional[str] = None


@router.post(
    "/{component_id}/risk-suggestions/{suggestion_set_id}/accept",
    response_model=AcceptSuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def accept_risk_suggestion(
    project_id: str,
    component_id: str,
    suggestion_set_id: str,
    body: AcceptSuggestionRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accept a suggestion set: create a risk item (and version) and a traceable project risk chain.

    - Uses suggestion set content; body overrides (edited text, hazard_library_id, harm_library_id,
      controls[], verifications[]) take precedence.
    - Library links: use existing links on the suggestion set (set in the UI via Link to existing /
      Create new entry / Make project-specific), or pass hazard_library_id, harm_library_id and
      per-control/verification library ids in the body.
    - Traceability: also creates project_risk_item + project_risk_controls + project_verifications
      (component → failure mode → hazard → hazardous situation → harm → control → verification)
      with project-specific text and library references preserved.
    """
    from crud import risk_item as risk_item_crud
    from crud import risk_item_version as version_crud
    from schemas.risk_item import RiskItemCreate, RiskItemVersionCreate

    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    comp = component_crud.get_component(db, component_id, project_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    s = suggested_crud.get_suggestion_set(db, suggestion_set_id)
    if not s or s.source_type != "component" or s.source_id != component_id or s.project_id != project_id:
        raise HTTPException(status_code=404, detail="Suggestion set not found")

    def _first_text(items: list, attr: str = "text") -> str:
        if not items:
            return ""
        return (getattr(items[0], attr, None) or "").strip()

    def _all_text(items: list, attr: str = "text") -> str:
        if not items:
            return ""
        return "\n".join((getattr(x, attr, None) or "").strip() for x in items if getattr(x, attr, None))

    failure_mode = (body.failure_mode if body else None) or _first_text(s.failure_modes)
    hazard = (body.hazard if body else None) or _first_text(s.hazards)
    hazardous_situation = (body.hazardous_situation if body else None) or _first_text(s.hazardous_situations)
    harm = (body.harm if body else None) or _first_text(s.harms)
    control = (body.control if body else None) or _all_text(s.controls)
    verification = (body.verification if body else None) or _all_text(s.verification_methods)

    hazard_library_id = (body.hazard_library_id if body else None) or (s.hazards[0].hazard_library_id if s.hazards else None)
    harm_library_id = (body.harm_library_id if body else None) or (s.harms[0].harm_library_id if s.harms else None)
    risk_control_library_id = s.controls[0].risk_control_library_id if s.controls else None
    verification_library_id = s.verification_methods[0].verification_library_id if s.verification_methods else None

    title = hazard or f"Risk from {comp.name}"
    create_data = RiskItemCreate(
        project_id=project_id,
        title=title[: 256],
        description=f"Accepted from component suggestion (component: {comp.name})",
        category="Safety",
        risk_type="Hazard",
        source="Component risk suggestion",
        status="open",
        component_id=component_id,
        component_name=comp.name,
    )
    risk_item = risk_item_crud.create_risk_item(db, create_data, created_by=current_user.id)
    version_data = RiskItemVersionCreate(
        hazard=hazard or "",
        hazardous_situation=hazardous_situation or None,
        harm=harm or None,
        failure_mode=failure_mode or None,
        hazard_library_id=hazard_library_id,
        harm_library_id=harm_library_id,
        risk_control_library_id=risk_control_library_id,
        verification_library_id=verification_library_id,
        control_measures_summary=control or None,
        information_for_safety=verification or None,
    )
    version_crud.create_risk_item_version(
        db, risk_item.id, version_data, changed_by=current_user.id, created_by=current_user.id
    )

    # Traceability: create project_risk_item + controls + verifications
    # (component → failure mode → hazard → hazardous situation → harm → control → verification)
    project_risk_item_id = None
    try:
        from models.device import Device
        from models.project_risk_item import ProjectRiskItem
        from models.project_risk_control import ProjectRiskControl
        from models.project_verification import ProjectVerification

        def _get_or_create_default_device(session: Session, proj_id: str):
            device = session.query(Device).filter(Device.project_id == proj_id).first()
            if device:
                return device
            proj = project_crud.get_project(session, proj_id, current_user.id)
            name = (proj.name + " (Default)")[:256] if proj else "Default"
            device = Device(project_id=proj_id, name=name)
            session.add(device)
            session.flush()
            return device

        device = _get_or_create_default_device(db, project_id)
        pri = ProjectRiskItem(
            device_id=device.id,
            component_id=component_id,
            failure_mode=failure_mode or None,
            hazard_library_id=hazard_library_id,
            hazard_text=hazard or None,
            hazardous_situation=hazardous_situation or None,
            harm_library_id=harm_library_id,
            harm_text=harm or None,
            status="open",
        )
        db.add(pri)
        db.flush()
        project_risk_item_id = pri.id

        # Build control list: from body.controls or from suggestion set
        control_items = []
        if body and body.controls:
            control_items = [
                (c.control_text or "", c.risk_control_library_id) for c in body.controls
            ]
        if not control_items and s.controls:
            control_items = [
                (getattr(c, "text", None) or "", getattr(c, "risk_control_library_id", None))
                for c in s.controls
            ]
        if not control_items and control:
            control_items = [(control, risk_control_library_id)]

        created_controls = []
        for c_text, c_lib_id in control_items:
            pc = ProjectRiskControl(
                project_risk_item_id=pri.id,
                risk_control_library_id=c_lib_id,
                control_text=(c_text or "").strip() or None,
            )
            db.add(pc)
            db.flush()
            created_controls.append(pc)

        # Build verification list: from body.verifications or from suggestion set
        verification_items = []
        if body and body.verifications:
            verification_items = [
                (v.verification_text or "", v.verification_library_id)
                for v in body.verifications
            ]
        if not verification_items and s.verification_methods:
            verification_items = [
                (getattr(v, "text", None) or "", getattr(v, "verification_library_id", None))
                for v in s.verification_methods
            ]
        if not verification_items and verification:
            verification_items = [(verification, verification_library_id)]

        for idx, (v_text, v_lib_id) in enumerate(verification_items):
            control_for_verification = (
                created_controls[min(idx, len(created_controls) - 1)]
                if created_controls
                else None
            )
            if not control_for_verification:
                continue
            pv = ProjectVerification(
                project_risk_control_id=control_for_verification.id,
                verification_library_id=v_lib_id,
                verification_text=(v_text or "").strip() or None,
                status="pending",
            )
            db.add(pv)
        db.commit()
    except Exception as e:
        if project_risk_item_id:
            db.rollback()
            raise
        db.rollback()
        project_risk_item_id = None

    return AcceptSuggestionResponse(risk_item_id=risk_item.id, project_risk_item_id=project_risk_item_id)


# ---------- Phase 3: Link suggestions to master libraries ----------
class LinkToLibraryRequest(BaseModel):
    """Set or clear library link. null = project-specific."""
    hazard_library_id: Optional[str] = None
    harm_library_id: Optional[str] = None
    risk_control_library_id: Optional[str] = None
    verification_library_id: Optional[str] = None


def _ensure_suggested_item_belongs_to_component(
    db: Session, project_id: str, component_id: str, suggestion_set_id: str
) -> None:
    if not suggested_crud._suggestion_set_belongs_to_component(
        db, suggestion_set_id, project_id, component_id
    ):
        raise HTTPException(status_code=404, detail="Suggestion not found for this component")


@router.patch(
    "/{component_id}/risk-suggestions/suggested-hazards/{suggested_id}",
    response_model=suggestion_schemas.SuggestedHazardOut,
)
def link_suggested_hazard(
    project_id: str,
    component_id: str,
    suggested_id: str,
    body: LinkToLibraryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link this suggested hazard to an existing library entry, or set null for project-specific."""
    if not project_crud.get_project(db, project_id, current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    row = suggested_crud.get_suggested_hazard(db, suggested_id)
    if not row:
        raise HTTPException(status_code=404, detail="Suggested hazard not found")
    _ensure_suggested_item_belongs_to_component(db, project_id, component_id, row.suggestion_set_id)
    updated = suggested_crud.update_suggested_hazard_library(
        db, suggested_id, body.hazard_library_id
    )
    return suggestion_schemas.SuggestedHazardOut.model_validate(updated)


@router.patch(
    "/{component_id}/risk-suggestions/suggested-harms/{suggested_id}",
    response_model=suggestion_schemas.SuggestedHarmOut,
)
def link_suggested_harm(
    project_id: str,
    component_id: str,
    suggested_id: str,
    body: LinkToLibraryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link this suggested harm to an existing library entry, or set null for project-specific."""
    if not project_crud.get_project(db, project_id, current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    row = suggested_crud.get_suggested_harm(db, suggested_id)
    if not row:
        raise HTTPException(status_code=404, detail="Suggested harm not found")
    _ensure_suggested_item_belongs_to_component(db, project_id, component_id, row.suggestion_set_id)
    updated = suggested_crud.update_suggested_harm_library(db, suggested_id, body.harm_library_id)
    return suggestion_schemas.SuggestedHarmOut.model_validate(updated)


@router.patch(
    "/{component_id}/risk-suggestions/suggested-controls/{suggested_id}",
    response_model=suggestion_schemas.SuggestedControlOut,
)
def link_suggested_control(
    project_id: str,
    component_id: str,
    suggested_id: str,
    body: LinkToLibraryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link this suggested control to an existing library entry, or set null for project-specific."""
    if not project_crud.get_project(db, project_id, current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    row = suggested_crud.get_suggested_control(db, suggested_id)
    if not row:
        raise HTTPException(status_code=404, detail="Suggested control not found")
    _ensure_suggested_item_belongs_to_component(db, project_id, component_id, row.suggestion_set_id)
    updated = suggested_crud.update_suggested_control_library(
        db, suggested_id, body.risk_control_library_id
    )
    return suggestion_schemas.SuggestedControlOut.model_validate(updated)


@router.patch(
    "/{component_id}/risk-suggestions/suggested-verifications/{suggested_id}",
    response_model=suggestion_schemas.SuggestedVerificationMethodOut,
)
def link_suggested_verification(
    project_id: str,
    component_id: str,
    suggested_id: str,
    body: LinkToLibraryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link this suggested verification to an existing library entry, or set null for project-specific."""
    if not project_crud.get_project(db, project_id, current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    row = suggested_crud.get_suggested_verification(db, suggested_id)
    if not row:
        raise HTTPException(status_code=404, detail="Suggested verification not found")
    _ensure_suggested_item_belongs_to_component(db, project_id, component_id, row.suggestion_set_id)
    updated = suggested_crud.update_suggested_verification_library(
        db, suggested_id, body.verification_library_id
    )
    return suggestion_schemas.SuggestedVerificationMethodOut.model_validate(updated)


# Create new library entry from suggestion text and link it
@router.post(
    "/{component_id}/risk-suggestions/suggested-hazards/{suggested_id}/create-and-link",
    response_model=suggestion_schemas.SuggestedHazardOut,
    status_code=status.HTTP_201_CREATED,
)
def create_hazard_and_link(
    project_id: str,
    component_id: str,
    suggested_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new hazard library entry from this suggestion's text and link the suggestion to it."""
    from crud import risk_knowledge_base as rkb_crud
    from schemas.risk_knowledge_base import HazardLibraryCreate

    if not project_crud.get_project(db, project_id, current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    row = suggested_crud.get_suggested_hazard(db, suggested_id)
    if not row:
        raise HTTPException(status_code=404, detail="Suggested hazard not found")
    _ensure_suggested_item_belongs_to_component(db, project_id, component_id, row.suggestion_set_id)
    hazard_name = (row.text or "New hazard")[:256]
    lib = rkb_crud.create_hazard_library(
        db, HazardLibraryCreate(hazard_name=hazard_name, description=row.text or None)
    )
    suggested_crud.update_suggested_hazard_library(db, suggested_id, lib.id)
    updated = suggested_crud.get_suggested_hazard(db, suggested_id)
    return suggestion_schemas.SuggestedHazardOut.model_validate(updated)


@router.post(
    "/{component_id}/risk-suggestions/suggested-harms/{suggested_id}/create-and-link",
    response_model=suggestion_schemas.SuggestedHarmOut,
    status_code=status.HTTP_201_CREATED,
)
def create_harm_and_link(
    project_id: str,
    component_id: str,
    suggested_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new harm library entry from this suggestion's text and link the suggestion to it."""
    from crud import risk_knowledge_base as rkb_crud
    from schemas.risk_knowledge_base import HarmLibraryCreate

    if not project_crud.get_project(db, project_id, current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    row = suggested_crud.get_suggested_harm(db, suggested_id)
    if not row:
        raise HTTPException(status_code=404, detail="Suggested harm not found")
    _ensure_suggested_item_belongs_to_component(db, project_id, component_id, row.suggestion_set_id)
    name = (row.text or "New harm")[:256]
    lib = rkb_crud.create_harm_library(
        db, HarmLibraryCreate(harm_name=name, description=row.text or None)
    )
    suggested_crud.update_suggested_harm_library(db, suggested_id, lib.id)
    updated = suggested_crud.get_suggested_harm(db, suggested_id)
    return suggestion_schemas.SuggestedHarmOut.model_validate(updated)


@router.post(
    "/{component_id}/risk-suggestions/suggested-controls/{suggested_id}/create-and-link",
    response_model=suggestion_schemas.SuggestedControlOut,
    status_code=status.HTTP_201_CREATED,
)
def create_control_and_link(
    project_id: str,
    component_id: str,
    suggested_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new risk control library entry from this suggestion's text and link the suggestion to it."""
    from crud import risk_knowledge_base as rkb_crud
    from schemas.risk_knowledge_base import RiskControlLibraryCreate

    if not project_crud.get_project(db, project_id, current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    row = suggested_crud.get_suggested_control(db, suggested_id)
    if not row:
        raise HTTPException(status_code=404, detail="Suggested control not found")
    _ensure_suggested_item_belongs_to_component(db, project_id, component_id, row.suggestion_set_id)
    name = (row.text or "New control")[:256]
    lib = rkb_crud.create_risk_control_library(
        db, RiskControlLibraryCreate(control_name=name, description=row.text or None, control_type="protective")
    )
    suggested_crud.update_suggested_control_library(db, suggested_id, lib.id)
    updated = suggested_crud.get_suggested_control(db, suggested_id)
    return suggestion_schemas.SuggestedControlOut.model_validate(updated)


@router.post(
    "/{component_id}/risk-suggestions/suggested-verifications/{suggested_id}/create-and-link",
    response_model=suggestion_schemas.SuggestedVerificationMethodOut,
    status_code=status.HTTP_201_CREATED,
)
def create_verification_and_link(
    project_id: str,
    component_id: str,
    suggested_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new verification library entry from this suggestion's text and link the suggestion to it."""
    from crud import risk_knowledge_base as rkb_crud
    from schemas.risk_knowledge_base import VerificationLibraryCreate

    if not project_crud.get_project(db, project_id, current_user.id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not component_crud.get_component(db, component_id, project_id):
        raise HTTPException(status_code=404, detail="Component not found")
    row = suggested_crud.get_suggested_verification(db, suggested_id)
    if not row:
        raise HTTPException(status_code=404, detail="Suggested verification not found")
    _ensure_suggested_item_belongs_to_component(db, project_id, component_id, row.suggestion_set_id)
    name = (row.text or "New verification")[:256]
    lib = rkb_crud.create_verification_library(
        db, VerificationLibraryCreate(verification_method=name, description=row.text or None)
    )
    suggested_crud.update_suggested_verification_library(db, suggested_id, lib.id)
    updated = suggested_crud.get_suggested_verification(db, suggested_id)
    return suggestion_schemas.SuggestedVerificationMethodOut.model_validate(updated)

