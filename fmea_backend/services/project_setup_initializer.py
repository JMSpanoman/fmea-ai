from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from business_logic.project_initializer import initialize_project_required_docs
from crud import component as component_crud
from crud import project_profile as profile_crud
from crud import risk_item as risk_item_crud
from crud import risk_item_version as version_crud
from crud import document as document_crud
from crud import fmea as fmea_crud
from models.fmea import FMEARow
from models.document import Document
from models.project import Project
from schemas.fmea import FMEARowCreate
from schemas.risk_item import RiskItemCreate, RiskItemVersionCreate


@dataclass
class InitializeStats:
    created_required_docs: int = 0
    seeded_risk_items: int = 0
    seeded_fmea_rows: int = 0
    updated_documents: int = 0

    def as_dict(self) -> dict:
        return {
            "created_required_docs": self.created_required_docs,
            "seeded_risk_items": self.seeded_risk_items,
            "seeded_fmea_rows": self.seeded_fmea_rows,
            "updated_documents": self.updated_documents,
        }


def _normalize_tags(tags: Any) -> List[str]:
    if not tags:
        return []
    if isinstance(tags, list):
        return [str(x).strip() for x in tags if str(x).strip()]
    if isinstance(tags, dict):
        # common pattern: {"type": "...", "domain": "..."} => values
        vals = []
        for v in tags.values():
            if v is None:
                continue
            if isinstance(v, list):
                vals.extend([str(x).strip() for x in v if str(x).strip()])
            else:
                vals.append(str(v).strip())
        return [x for x in vals if x]
    return [str(tags).strip()] if str(tags).strip() else []


def _is_effectively_empty_document(doc: Document) -> bool:
    """
    Conservative empty detection:
    - empty/whitespace => empty
    - the project_initializer placeholder for hazard_analysis => treat as empty for seeding
    - generic starter strings for FMEA => treat as empty (we seed rows, not doc content)
    """
    content = (doc.content or "").strip()
    if not content:
        return True
    lowered = content.lower()
    if "hazard analysis export configuration starter" in lowered:
        return True
    if lowered.startswith("fmea starter"):
        return True
    return False


def _seed_risk_items_from_profile_components(
    db: Session,
    *,
    project_id: str,
    user_id: str,
) -> int:
    """
    Deterministically create a minimal risk register seed so Hazard Analysis has something to show.
    Seed only if the project currently has zero risk items.
    """
    existing = risk_item_crud.get_risk_items_by_project(db, project_id)
    if existing:
        return 0

    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)

    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""

    seeded = 0

    # If there are no components, create one generic seed risk to avoid a blank hazard analysis.
    if not components:
        title = "Initial hazard identification seed (no components defined yet)"
        desc = "Seeded from ProjectProfile. Add Components to improve hazard analysis specificity."
        if intended_use or use_env or device_desc:
            desc += f"\n\nIntended use: {intended_use or '—'}\nUse environment: {use_env or '—'}\nDevice: {device_desc or '—'}"

        ri = risk_item_crud.create_risk_item(
            db,
            RiskItemCreate(
                project_id=project_id,
                title=title,
                description=desc,
                category="Safety",
                risk_type="Hazard",
                status="open",
                source="wizard_seed",
            ),
            created_by=user_id,
        )
        version_crud.create_risk_item_version(
            db,
            ri.id,
            RiskItemVersionCreate(
                hazard="Generic use-related hazard (to be refined)",
                hazardous_situation=f"Use in {use_env or 'intended environment'} during {intended_use or 'intended use'} may lead to unsafe situation.",
                harm="User harm or unintended operation",
                severity=7,
                probability_of_harm=3,
                detection=1,
                risk_rationale="Seeded deterministically from project profile; refine during risk analysis.",
            ),
            changed_by=user_id,
            created_by=user_id,
        )
        return 1

    for c in components:
        tags = _normalize_tags(getattr(c, "tags", None))
        tag_hint = ", ".join(tags[:6]) if tags else "general"

        title = f"Seed hazard for component: {c.name}"
        desc_lines = [
            "Seeded from Project Setup Wizard (deterministic).",
            f"Component: {c.name}",
            f"Tags: {tag_hint}",
        ]
        if c.description:
            desc_lines.append(f"Component description: {c.description}")
        if intended_use or use_env:
            desc_lines.append(f"Intended use: {intended_use or '—'}")
            desc_lines.append(f"Use environment: {use_env or '—'}")

        ri = risk_item_crud.create_risk_item(
            db,
            RiskItemCreate(
                project_id=project_id,
                component_id=c.id,
                component_name=c.name,
                title=title,
                description="\n".join(desc_lines),
                category="Safety",
                risk_type="Hazard",
                status="open",
                source="wizard_seed",
            ),
            created_by=user_id,
        )

        # Make sure hazard analysis chain fields are present in a version.
        version_crud.create_risk_item_version(
            db,
            ri.id,
            RiskItemVersionCreate(
                hazard=f"{c.name}: potential hazard related to {tag_hint}",
                hazardous_situation=(
                    f"During {intended_use or 'intended use'}, in {use_env or 'intended environment'}, "
                    f"an issue in {c.name} could lead to a hazardous situation."
                ),
                harm="Potential injury or harm to user/patient/operator",
                severity=7,
                probability_of_harm=3,
                detection=1,
                risk_rationale="Seeded deterministically from project profile and component tags; refine during analysis.",
            ),
            changed_by=user_id,
            created_by=user_id,
        )

        seeded += 1

    return seeded


def _seed_fmea_rows_from_components(db: Session, *, project_id: str) -> int:
    """
    Deterministically ensure each component has a baseline set of FMEA rows.

    Requirement: seed **at least 5 rows per component** so the FMEA table and generated
    exports have meaningful starter content even before AI generation.
    """
    components = component_crud.get_components_by_project(db, project_id)
    if not components:
        return 0

    seeded = 0
    for c in components:
        try:
            existing_for_component = (
                db.query(FMEARow)
                .filter(FMEARow.project_id == project_id, FMEARow.component_id == c.id)
                .count()
            )
        except Exception:
            existing_for_component = 0

        to_create = max(0, 5 - int(existing_for_component or 0))
        for i in range(to_create):
            n = int(existing_for_component or 0) + i + 1
            fmea_crud.create_fmea_row(
                db,
                FMEARowCreate(
                    project_id=project_id,
                    component_id=c.id,
                    failure_mode=f"{c.name}: TBD failure mode #{n}",
                    effect="TBD effect on system/user",
                    cause="TBD cause / mechanism",
                    severity=5,
                    probability=3,
                    detection=4,
                    mitigation="TBD mitigation / control",
                    ai_metadata={
                        "seeded_by": "wizard_initialize",
                        "component_name": c.name,
                        # Used by FMEA export rendering (hazard column).
                        "hazard": f"{c.name}: TBD hazard",
                    },
                ),
            )
            seeded += 1

    return seeded


def _update_hazard_analysis_document_if_empty(db: Session, *, project_id: str) -> int:
    """
    Keep document versioning behavior: if hazard analysis doc content is empty/starter,
    generate a deterministic HTML snapshot using existing generate logic (builder/renderer),
    and create a new DocumentVersion (via document_crud.update_document).
    """
    docs = document_crud.get_documents_by_project(db, project_id)
    ha = next((d for d in docs if (d.type or "").lower() == "hazard_analysis"), None)
    if not ha:
        return 0
    if not _is_effectively_empty_document(ha):
        return 0

    # Use the same renderer used by /documents/{id}/generate, but without requiring the user to click Generate.
    from business_logic import hazard_analysis_builder, hazard_analysis_renderer
    project = db.query(Project).filter(Project.id == project_id).first()
    project_name = (project.name if project else "Project")

    evidence = hazard_analysis_builder.build_hazard_analysis(
        db=db,
        project_id=project_id,
        component_filter=None,
        version_scope="current",
        include_unapproved=True,
    )
    rendered_html = hazard_analysis_renderer.render_hazard_analysis_html(evidence, project_name)

    # Update document content (this creates a new version if content changes)
    from schemas.document import DocumentUpdate
    document_crud.update_document(
        db,
        ha.id,
        DocumentUpdate(content=rendered_html),
        project_id,
    )
    return 1


def initialize_project_content(
    db: Session,
    *,
    project_id: str,
    user_id: str,
) -> Dict[str, Any]:
    """
    Idempotent project initializer, intended to be called after wizard completion.
    Seed only if empty.
    """
    stats = InitializeStats()

    created_doc_ids = initialize_project_required_docs(db, project_id)
    stats.created_required_docs = len(created_doc_ids)

    stats.seeded_risk_items = _seed_risk_items_from_profile_components(db, project_id=project_id, user_id=user_id)
    stats.seeded_fmea_rows = _seed_fmea_rows_from_components(db, project_id=project_id)
    stats.updated_documents = _update_hazard_analysis_document_if_empty(db, project_id=project_id)

    return stats.as_dict()

