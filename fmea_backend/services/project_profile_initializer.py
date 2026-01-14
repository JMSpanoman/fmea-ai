from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from business_logic.project_initializer import initialize_project_required_docs
from crud import component as component_crud
from crud import project_profile as profile_crud
from crud import document as document_crud
from crud import fmea as fmea_crud
from models.document import Document
from models.fmea import FMEARow
from schemas.document import DocumentUpdate
from schemas.fmea import FMEARowCreate


@dataclass
class InitFromProfileStats:
    created_required_docs: int = 0
    updated_documents: List[str] = None  # doc types updated
    seeded_fmea_rows: int = 0

    def __post_init__(self):
        if self.updated_documents is None:
            self.updated_documents = []

    def as_dict(self) -> dict:
        return {
            "created_required_docs": self.created_required_docs,
            "updated_documents": self.updated_documents,
            "seeded_fmea_rows": self.seeded_fmea_rows,
        }


def _is_emptyish(content: Optional[str]) -> bool:
    return not (content or "").strip()


def _status_is_not_started(status: Optional[str]) -> bool:
    if status is None:
        return False
    s = str(status).strip().lower()
    return s in {"not started", "not_started", "not-started"}


def _content_is_placeholder_for_type(doc_type: str, content: Optional[str]) -> bool:
    c = (content or "").strip().lower()
    if not c:
        return True

    # These come from business_logic/project_initializer._default_content_for
    if doc_type == "hazard_analysis" and "hazard analysis export configuration starter" in c:
        return True
    if doc_type == "fmea" and c.startswith("fmea starter"):
        return True
    if doc_type == "design_inputs_doc" and c.startswith("design inputs documentation starter"):
        return True
    if doc_type == "rmp" and c.startswith("rmp starter"):
        return True

    return False


def _should_populate(doc: Document) -> bool:
    """
    Populate only if the document is empty/placeholder OR explicitly marked Not started.
    Never overwrite otherwise.
    """
    return _status_is_not_started(doc.status) or _content_is_placeholder_for_type((doc.type or "").lower(), doc.content)


def _normalize_tags(tags: Any) -> List[str]:
    if not tags:
        return []
    if isinstance(tags, list):
        return [str(x).strip() for x in tags if str(x).strip()]
    if isinstance(tags, dict):
        vals: List[str] = []
        for v in tags.values():
            if v is None:
                continue
            if isinstance(v, list):
                vals.extend([str(x).strip() for x in v if str(x).strip()])
            else:
                vals.append(str(v).strip())
        return [x for x in vals if x]
    s = str(tags).strip()
    return [s] if s else []


def _is_pacemaker_context(profile: Any, components: list[Any]) -> bool:
    """
    Lightweight heuristic to decide whether to use implantable-cardiac (pacemaker-like)
    templates. Deterministic and purely based on user-entered context.
    """
    blob = " ".join(
        [
            str(getattr(profile, "intended_use", "") or ""),
            str(getattr(profile, "device_description", "") or ""),
            " ".join([str(getattr(c, "name", "") or "") for c in components]),
        ]
    ).lower()
    keywords = [
        "pacemaker",
        "cardiac",
        "bradycardia",
        "arrhythmia",
        "implant",
        "implantable",
        "pacing",
        "lead",
        "electrode",
        "telemetry",
    ]
    return any(k in blob for k in keywords)


def _traceability_header(*, project_id: str, profile: Any) -> str:
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    user_pop = (getattr(profile, "user_population", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""
    return (
        "DRAFT — Generated deterministically from ProjectProfile + Components\n"
        f"Project ID: {project_id}\n"
        f"Device description: {device_desc or 'TBD'}\n"
        f"Intended use: {intended_use or 'TBD'}\n"
        f"User population: {user_pop or 'TBD'}\n"
        f"Use environment: {use_env or 'TBD'}\n"
    )


def _draft_rmp(*, project_id: str, profile: Any, components: list[Any]) -> str:
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    user_pop = (getattr(profile, "user_population", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""

    comp_lines = []
    for c in components:
        comp_lines.append(f"- {c.name}{(': ' + c.description) if getattr(c, 'description', None) else ''}")
    if not comp_lines:
        comp_lines = ["- (No components defined yet)"]

    return (
        "Risk Management Plan (RMP) — Draft\n"
        "\n"
        + _traceability_header(project_id=project_id, profile=profile)
        + "\n"
        "1. Purpose and Scope\n"
        "- This Risk Management Plan defines the planned activities and responsibilities for risk management.\n"
        "- This draft is intended to be reviewed and tailored to the project.\n"
        "\n"
        "2. Device Description and Intended Use (from project profile)\n"
        f"- Device description: {device_desc or 'TBD'}\n"
        f"- Intended use: {intended_use or 'TBD'}\n"
        f"- User population: {user_pop or 'TBD'}\n"
        f"- Use environment: {use_env or 'TBD'}\n"
        "\n"
        "3. System / Components in Scope (from project components)\n"
        + "\n".join(comp_lines)
        + "\n\n"
        "4. Risk Management Process (draft)\n"
        "- Planned activities: hazard identification, risk estimation, risk evaluation, risk control, and evaluation of residual risk.\n"
        "- Risk control verification and production/post-production information shall be considered.\n"
        "- Note: This draft does not assign risk scores; scoring criteria should be defined and approved by the team.\n"
        "\n"
        "5. Roles and Responsibilities (draft)\n"
        "- Risk Management Lead: maintains this plan and ensures execution.\n"
        "- Design Engineering: provides design information and implements risk controls.\n"
        "- Quality / Regulatory: ensures process alignment and review support.\n"
        "- Clinical / Safety: supports hazard identification and clinical rationale.\n"
        "\n"
        "6. Review / Approval\n"
        "- This draft shall be reviewed and approved prior to formal use.\n"
    )


def _draft_hazard_analysis(*, project_id: str, profile: Any, components: list[Any]) -> str:
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""

    is_pace = _is_pacemaker_context(profile, components)
    header = (
        "Hazard Analysis — Draft\n\n"
        + _traceability_header(project_id=project_id, profile=profile)
        + "\n"
        "Important\n"
        "- DRAFT content. Deterministic starter hazards only.\n"
        "- No risk scoring is assigned in this draft.\n"
        "- Review and tailor to the specific design, intended use, and clinical context.\n\n"
    )

    if not components:
        return header + "Seeded Hazards\n- (No components defined yet. Add components to seed hazards.)\n"

    # Implantable-cardiac (pacemaker-like) hazard categories + component mapping.
    categories = [
        ("Electrical / Energy Delivery", ["power", "battery", "capacitor", "charger", "supply", "energy"]),
        ("Sensing / Detection", ["sense", "sensor", "electrode", "lead", "ecg"]),
        ("Therapy Delivery (Pacing Output)", ["pace", "output", "pulse", "stim"]),
        ("Software / Firmware / Algorithms", ["software", "firmware", "algorithm", "code", "app", "os"]),
        ("Cybersecurity / Connectivity", ["telemetry", "wireless", "rf", "bluetooth", "wifi", "cloud", "cyber"]),
        ("Mechanical / Structural", ["housing", "case", "seal", "connector", "header", "mechanical"]),
        ("Biological / Biocompatibility", ["bio", "tissue", "coating", "material", "sterile", "implant"]),
        ("EMI / Environmental", ["emi", "emc", "mri", "magnet", "environment"]),
        ("Usability / Human Factors / Clinical Workflow", ["user", "clinician", "procedure", "implantation", "programmer"]),
    ]

    def classify_component(c: Any) -> str:
        name = (getattr(c, "name", "") or "").lower()
        tags = " ".join(_normalize_tags(getattr(c, "tags", None))).lower()
        blob = f"{name} {tags}"
        for cat, hints in categories:
            if any(h in blob for h in hints):
                return cat
        return "General (System-level)"

    # Build per-category hazards, linked to components, with no scoring.
    grouped: Dict[str, List[Any]] = {}
    for c in components:
        cat = classify_component(c) if is_pace else "General (System-level)"
        grouped.setdefault(cat, []).append(c)

    # Deterministic ordering for stable drafts.
    for cat in list(grouped.keys()):
        grouped[cat] = sorted(grouped[cat], key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or "")))

    lines: List[str] = []
    lines.append("Seeded Hazard Categories and Hazards")
    lines.append(f"- Device context template: {'Implantable cardiac (pacemaker-like)' if is_pace else 'Generic medical device'}")
    lines.append("")

    def hazard_block(component_name: str, category: str) -> str:
        # Keep wording neutral and avoid implying quantified risk.
        return (
            f"Component: {component_name}\n"
            f"Category: {category}\n"
            f"Hazard (Draft): Potential harm due to {component_name} malfunction or misuse\n"
            f"Hazardous situation (Draft): During {intended_use or 'intended use'}, in {use_env or 'the intended environment'}, "
            f"{component_name} may fail, degrade, or behave unexpectedly.\n"
            "Possible harms (Draft): Injury to patient/user, therapy interruption, inappropriate therapy, infection, or other clinically relevant harm.\n"
            "Risk scoring: Not assigned in this draft.\n"
        )

    for cat in sorted(grouped.keys()):
        lines.append(f"\n== {cat} ==")
        for c in grouped[cat]:
            lines.append(hazard_block(c.name, cat))

    return header + "\n".join(lines).strip() + "\n"


def _ensure_fmea_rows_for_components(db: Session, *, project_id: str, components: list[Any]) -> int:
    existing = db.query(FMEARow).filter(FMEARow.project_id == project_id).count()
    if existing > 0:
        return 0
    if not components:
        return 0

    created = 0
    # Deterministic order
    for c in sorted(components, key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or ""))):
        fmea_crud.create_fmea_row(
            db,
            FMEARowCreate(
                project_id=project_id,
                component_id=c.id,
                # Draft placeholders; do not assign risk scores.
                failure_mode=f"[DRAFT] {c.name} — placeholder failure mode (to be refined)",
                effect="[DRAFT] Placeholder effect on therapy/system/user (to be refined)",
                cause="[DRAFT] Placeholder cause / mechanism (to be refined)",
                severity=None,
                probability=None,
                detection=None,
                mitigation="[DRAFT] Placeholder mitigation / control (to be refined)",
                ai_metadata={
                    "seeded_by": "initialize_from_profile",
                    "project_id": project_id,
                    "component_name": c.name,
                    "draft": True,
                },
            ),
        )
        created += 1
    return created


def _draft_fmea_table(db: Session, *, project_id: str, components: list[Any]) -> str:
    """
    Deterministic text table for the FMEA document draft.
    We keep it plain text to avoid time-based HTML differences and keep idempotency stable.
    """
    comp_name_by_id = {str(getattr(c, "id", "")): str(getattr(c, "name", "") or "") for c in components}
    rows = db.query(FMEARow).filter(FMEARow.project_id == project_id).all()
    if not rows:
        if not components:
            return (
                "FMEA — Draft\n\n"
                + _traceability_header(project_id=project_id, profile=None)
                + "\nNo components defined yet. Add components to seed starter FMEA rows.\n"
            )
        return (
            "FMEA — Draft\n\n"
            + _traceability_header(project_id=project_id, profile=None)
            + "\nNo FMEA rows exist yet.\n"
        )

    lines = [
        "FMEA — Draft",
        "",
        "Important",
        "- DRAFT placeholders. Do not treat as validated risk analysis.",
        "- Severity/Occurrence/Detection are intentionally left blank in this draft.",
        "",
        f"Project ID: {project_id}",
        "",
        "Seeded starter rows (one per component):",
        "",
        "component | failure_mode | effect | cause | S | O | D | mitigation",
        "-" * 92,
    ]
    # Deterministic ordering
    for r in sorted(rows, key=lambda x: (str(x.component_id or ""), str(x.id or ""))):
        comp_label = comp_name_by_id.get(str(r.component_id or ""), "") or (str(r.component_id or "")[:8] if r.component_id else "")
        lines.append(
            f"{comp_label} | {r.failure_mode or ''} | {r.effect or ''} | {r.cause or ''} | "
            f"{'' if r.severity is None else r.severity} | {'' if r.probability is None else r.probability} | {'' if r.detection is None else r.detection} | {r.mitigation or ''}"
        )
    return "\n".join(lines) + "\n"


def _draft_design_inputs(*, project_id: str, profile: Any, components: list[Any]) -> str:
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    is_pace = _is_pacemaker_context(profile, components)

    lines = [
        "Design Inputs Documentation — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Purpose",
        "- Deterministic starter design inputs derived from intended use + safety expectations.",
        "- This draft provides high-level inputs that must be refined into verifiable requirements and acceptance criteria.",
        "",
        f"Context summary: device={device_desc or 'TBD'}; intended_use={intended_use or 'TBD'}; use_environment={use_env or 'TBD'}",
        "",
        "Seeded High-Level Design Inputs (Draft)",
    ]

    # 5–10 high-level inputs (keep deterministic and neutral)
    inputs: List[str] = []
    base_context = f"for {intended_use or 'the intended use'} in {use_env or 'the intended environment'}"
    inputs.extend(
        [
            f"- DI-01 (Safety): The device shall be designed to minimize foreseeable harm {base_context}. [DRAFT]",
            f"- DI-02 (Performance): The device shall perform its intended function within specified limits {base_context}. [DRAFT]",
            "- DI-03 (Risk Controls): The device design shall include appropriate risk control measures and verification evidence. [DRAFT]",
            "- DI-04 (Alarms/Indicators): The device shall provide appropriate status indication for safe use (as applicable). [DRAFT]",
            "- DI-05 (Usability): The device shall support safe and effective use by the intended user population. [DRAFT]",
        ]
    )
    if is_pace:
        inputs.extend(
            [
                "- DI-06 (Therapy): The device shall deliver pacing therapy within defined output parameter tolerances. [DRAFT]",
                "- DI-07 (Sensing): The device shall reliably sense relevant cardiac signals to support correct therapy behavior. [DRAFT]",
                "- DI-08 (EMI/EMC): The device shall maintain safe behavior under reasonably foreseeable electromagnetic interference conditions. [DRAFT]",
                "- DI-09 (Longevity): The device shall meet a defined service life / battery longevity target under specified use profiles. [DRAFT]",
                "- DI-10 (Biocompatibility): Patient-contacting materials shall be biocompatible for intended duration of contact. [DRAFT]",
                "- DI-11 (Cybersecurity): The device shall incorporate security controls appropriate to its connectivity and threat model. [DRAFT]",
            ]
        )
    else:
        inputs.extend(
            [
                "- DI-06 (EMI/EMC): The device shall maintain safe behavior under reasonably foreseeable electromagnetic interference conditions. [DRAFT]",
                "- DI-07 (Software): If software is present, it shall be developed and verified commensurate with its safety impact. [DRAFT]",
                "- DI-08 (Biocompatibility): Patient-contacting materials shall be biocompatible for intended duration of contact (as applicable). [DRAFT]",
            ]
        )

    # Keep between 5 and 10 if possible; pacemaker template may add more, so trim deterministically.
    max_items = 10
    inputs = inputs[:max_items]
    lines.extend(inputs)

    if components:
        lines.append("")
        lines.append("Component Traceability (from project components)")
        for c in sorted(components, key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or ""))):
            lines.append(f"- {c.name} (component_id={c.id})")
    else:
        lines.append("")
        lines.append("Component Traceability")
        lines.append("- (No components defined yet.)")

    return "\n".join(lines).strip() + "\n"


def initialize_project_from_profile(db: Session, *, project_id: str) -> Dict[str, Any]:
    """
    Controlled initializer:
    - Idempotent
    - Never overwrites non-empty/non-placeholder content unless status == Not started
    - Creates a new document version when generating content (via update_document)
    """
    stats = InitFromProfileStats()

    created = initialize_project_required_docs(db, project_id)
    stats.created_required_docs = len(created)

    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)

    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}

    # 1) RMP
    rmp = by_type.get("rmp")
    if rmp and _should_populate(rmp):
        content = _draft_rmp(project_id=project_id, profile=profile, components=components)
        document_crud.update_document(db, rmp.id, DocumentUpdate(content=content, status="draft"), project_id)
        stats.updated_documents.append("rmp")

    # 2) Hazard Analysis
    ha = by_type.get("hazard_analysis")
    if ha and _should_populate(ha):
        content = _draft_hazard_analysis(project_id=project_id, profile=profile, components=components)
        document_crud.update_document(db, ha.id, DocumentUpdate(content=content, status="draft"), project_id)
        stats.updated_documents.append("hazard_analysis")

    # 3) FMEA
    fmea_doc = by_type.get("fmea")
    if fmea_doc and _should_populate(fmea_doc):
        stats.seeded_fmea_rows = _ensure_fmea_rows_for_components(db, project_id=project_id, components=components)
        content = _draft_fmea_table(db, project_id=project_id, components=components)
        document_crud.update_document(db, fmea_doc.id, DocumentUpdate(content=content, status="draft"), project_id)
        stats.updated_documents.append("fmea")

    # 4) Design Inputs doc
    di = by_type.get("design_inputs_doc")
    if di and _should_populate(di):
        content = _draft_design_inputs(project_id=project_id, profile=profile, components=components)
        document_crud.update_document(db, di.id, DocumentUpdate(content=content, status="draft"), project_id)
        stats.updated_documents.append("design_inputs_doc")

    return stats.as_dict()

