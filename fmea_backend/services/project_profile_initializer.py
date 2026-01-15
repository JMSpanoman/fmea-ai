from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from business_logic.project_initializer import initialize_project_required_docs
from crud import component as component_crud
from crud import project_profile as profile_crud
from crud import document as document_crud
from crud import fmea as fmea_crud
from models.risk_item import RiskItem
from models.risk_control import RiskControl
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
    if doc_type == "design_outputs_doc" and c.startswith("design outputs documentation starter"):
        return True
    if doc_type == "vv_plan" and c.startswith("v&v plan starter"):
        return True
    if doc_type == "vv_evidence" and c.startswith("v&v evidence report starter"):
        return True
    if doc_type == "traceability_matrix" and c.startswith("traceability matrix export configuration starter"):
        return True
    if doc_type == "residual_risk" and c.startswith("residual risk evaluation export configuration starter"):
        return True
    if doc_type == "risk_controls_doc" and c.startswith("risk control measures documentation export configuration starter"):
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
        "DRAFT — Generated from Project Setup (ProjectProfile + Components)\n"
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


def _draft_rmf_scaffold(*, project_id: str, profile: Any, components: list[Any]) -> str:
    """
    Deterministic RMF scaffold (structure only).
    RMF is typically a compilation of RMP + hazard analysis + risk analysis (incl. FMEA) + risk controls + residual risk + traceability.
    """
    comp_lines = [f"- {c.name} (id={getattr(c, 'id', '')})" for c in components] or ["- (No components defined yet)"]
    return (
        "Risk Management File (RMF/RMR) — Draft\n\n"
        + _traceability_header(project_id=project_id, profile=profile)
        + "\n"
        "Overview\n"
        "- This is a DRAFT RMF structure generated from Project Setup.\n"
        "- It is a compilation shell; expand/verify before use.\n\n"
        "1. Device Overview\n"
        "- Device description: (from profile)\n"
        "- Intended use: (from profile)\n"
        "- User population: (from profile)\n"
        "- Use environment: (from profile)\n\n"
        "2. Components / System Breakdown (from project components)\n"
        + "\n".join(comp_lines)
        + "\n\n"
        "3. Risk Management Plan (RMP) Summary\n"
        "- (Draft summary to be generated)\n\n"
        "4. Hazard Identification / Hazard Analysis Summary\n"
        "- (Draft summary to be generated)\n\n"
        "5. Risk Analysis Summary (including FMEA)\n"
        "- (Draft summary to be generated)\n\n"
        "6. Risk Control Measures Summary\n"
        "- (Draft summary to be generated)\n\n"
        "7. Residual Risk Evaluation Summary\n"
        "- (Draft summary to be generated)\n\n"
        "8. Traceability Summary\n"
        "- (Draft summary to be generated)\n\n"
        "9. Production and Post-Production Information (PMS)\n"
        "- (Placeholders; do not treat as executed evidence)\n\n"
        "10. Review and Approval\n"
        "- Approvals: TBD\n"
    )


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
        "- Do not treat as validated risk analysis.",
        "- Scores may be blank until generated and/or reviewed.",
        "",
        f"Project ID: {project_id}",
        "",
        "Seeded starter rows (one per component):",
        "",
        "component | hazard | failure_mode | effect | cause | S | O | D | mitigation",
        "-" * 120,
    ]
    # Deterministic ordering
    for r in sorted(rows, key=lambda x: (str(x.component_id or ""), str(x.id or ""))):
        comp_label = comp_name_by_id.get(str(r.component_id or ""), "") or (str(r.component_id or "")[:8] if r.component_id else "")
        hazard = ""
        try:
            if isinstance(getattr(r, "ai_metadata", None), dict):
                hazard = str(r.ai_metadata.get("hazard") or "").strip()
        except Exception:
            hazard = ""
        lines.append(
            f"{comp_label} | {hazard} | {r.failure_mode or ''} | {r.effect or ''} | {r.cause or ''} | "
            f"{'' if r.severity is None else r.severity} | {'' if r.probability is None else r.probability} | {'' if r.detection is None else r.detection} | {r.mitigation or ''}"
        )
    return "\n".join(lines) + "\n"


def _slug(s: str) -> str:
    out = []
    for ch in (s or ""):
        if ch.isalnum():
            out.append(ch.upper())
    return "".join(out)[:10] or "COMP"


def _build_design_inputs(
    *, project_id: str, profile: Any, components: list[Any]
) -> tuple[str, list[dict[str, str]]]:
    """
    Returns (content, design_inputs) where design_inputs is a list of:
      {id, component_id, component_name, text}
    """
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    ksc = getattr(profile, "key_safety_characteristics", None) if profile else None
    ksc_list = [str(x).strip() for x in (ksc or []) if str(x).strip()] if isinstance(ksc, list) else []

    comps = sorted(
        components,
        key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or "")),
    )

    di_entries: list[dict[str, str]] = []
    lines: list[str] = [
        "Design Inputs Documentation — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Purpose",
        "- Draft, deterministic design inputs derived from Project Setup data.",
        "- Use these as traceability scaffolding; refine into verifiable requirements and acceptance criteria.",
        "",
        "Design Inputs (Draft)",
    ]

    if not comps:
        lines.append("- (No components defined yet.)")
        return "\n".join(lines) + "\n", di_entries

    safety_hint = "; ".join(ksc_list[:5]) if ksc_list else ""
    if safety_hint:
        lines.append(f"Key safety characteristics (from setup): {safety_hint}")
        lines.append("")

    for comp in comps:
        cname = str(getattr(comp, "name", "") or "").strip() or "Component"
        cid = str(getattr(comp, "id", "") or "")
        slug = _slug(cname)

        # Always 3, add up to 2 more derived from safety characteristics.
        base_texts = [
            f"The device shall provide the required function for {cname} as part of {device_desc or 'the device'} for {intended_use or 'the intended use'}. [DRAFT]",
            f"The device shall detect and handle foreseeable faults related to {cname} to maintain a safe state. [DRAFT]",
            f"The device shall support verification of {cname} requirements through defined acceptance criteria (TBD). [DRAFT]",
        ]
        extra_texts: list[str] = []
        for k in ksc_list:
            if len(extra_texts) >= 2:
                break
            extra_texts.append(f"The device shall address safety characteristic '{k}' with respect to {cname}. [DRAFT]")

        texts = base_texts + extra_texts
        texts = texts[:5]

        lines.append(f"\nComponent: {cname} (component_id={cid})")
        for i, txt in enumerate(texts, start=1):
            di_id = f"DI-{slug}-{i:02d}"
            lines.append(f"- {di_id}: {txt}")
            di_entries.append(
                {
                    "id": di_id,
                    "component_id": cid,
                    "component_name": cname,
                    "text": txt,
                }
            )

    return "\n".join(lines).strip() + "\n", di_entries


def _build_design_outputs(
    *, project_id: str, profile: Any, design_inputs: list[dict[str, str]]
) -> tuple[str, list[dict[str, str]]]:
    """
    Returns (content, design_outputs) where design_outputs entries are:
      {id, input_id, text}
    """
    lines: list[str] = [
        "Design Outputs Documentation — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Purpose",
        "- Draft, deterministic design outputs mapped to Design Inputs.",
        "- Outputs are placeholders to scaffold traceability; replace with real artifacts (drawings, schematics, code, specs).",
        "",
        "Design Outputs (Draft)",
    ]

    do_entries: list[dict[str, str]] = []
    if not design_inputs:
        lines.append("- (No Design Inputs available yet. Generate Design Inputs first.)")
        return "\n".join(lines) + "\n", do_entries

    for di in design_inputs:
        di_id = di["id"]
        do_id = di_id.replace("DI-", "DO-", 1)
        text = f"Design output to be defined for {di_id} (e.g., specification, schematic, software module, drawing). [DRAFT]"
        lines.append(f"- {do_id} (maps to {di_id}): {text}")
        do_entries.append({"id": do_id, "input_id": di_id, "text": text})

    return "\n".join(lines).strip() + "\n", do_entries


def _build_vv_plan(
    db: Session, *, project_id: str, profile: Any, design_inputs: list[dict[str, str]]
) -> tuple[str, list[dict[str, str]]]:
    """
    Returns (content, vv_items) where vv_items are:
      {id, input_id, text}
    """
    lines: list[str] = [
        "V&V Plan — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Definitions (Draft)",
        "- Verification: confirmation, through provision of objective evidence, that specified requirements have been fulfilled.",
        "- Validation: confirmation that the device meets user needs and intended use under actual or simulated use conditions.",
        "",
        "Strategy (Draft)",
        "- Verification methods may include inspection, analysis, testing, and demonstration.",
        "- Validation activities should evaluate intended use, use environment, and user population.",
        "",
        "Traceability Expectations (Draft)",
        "- Each Design Input shall map to at least one verification activity and associated evidence.",
        "- This draft does not assert compliance or acceptance; it establishes placeholders only.",
        "",
        "Planned Verification/Validation Items (Draft placeholders)",
    ]

    vv_items: list[dict[str, str]] = []
    if not design_inputs:
        lines.append("- (No Design Inputs available yet.)")
        return "\n".join(lines) + "\n", vv_items

    for di in design_inputs:
        di_id = di["id"]
        vv_id = di_id.replace("DI-", "VV-", 1)
        txt = f"Verification/validation activity placeholder for {di_id} (method TBD; acceptance criteria TBD). [DRAFT]"
        lines.append(f"- {vv_id} (covers {di_id}): {txt}")
        vv_items.append({"id": vv_id, "input_id": di_id, "text": txt})

    # Risk control verification activities (auto-created VV tests linked via TraceLink).
    try:
        from models.trace_link import TraceLink
        from models.risk_control import RiskControl
        from models.vv_test import VVTest

        links = (
            db.query(TraceLink)
            .filter(
                TraceLink.project_id == project_id,
                TraceLink.from_type == "risk_control",
                TraceLink.to_type == "vv_test",
            )
            .all()
        )
        if links:
            lines.append("")
            lines.append("Risk Control Verification Activities (Draft)")
            lines.append("- These are draft verification activities created from RiskControl.verification_method.")
            lines.append("- Do not treat as executed or complete until performed and reviewed.")

            # Deterministic ordering
            for link in sorted(links, key=lambda l: (str(l.from_id or ""), str(l.to_id or ""))):
                rc = db.query(RiskControl).filter(RiskControl.id == link.from_id).first()
                vt = db.query(VVTest).filter(VVTest.id == link.to_id).first()
                if not rc or not vt:
                    continue
                lines.append(f"- {vt.vv_key or ('V-' + vt.id[:8])}: {vt.name or 'Verification activity'}")
                lines.append(f"  - Linked control: {rc.control_key or ('RC-' + rc.id[:8])} — {rc.control_name}")
                lines.append(f"  - Verification method: {vt.test_method}")
                lines.append(f"  - Acceptance criteria: {vt.acceptance_criteria}")
                lines.append(f"  - Status: {vt.status}")
    except Exception:
        # Keep V&V plan generation robust even if trace tables are not present yet.
        pass

    return "\n".join(lines).strip() + "\n", vv_items


def _build_vv_evidence_report(
    *, project_id: str, profile: Any, vv_items: list[dict[str, str]]
) -> str:
    lines: list[str] = [
        "V&V Evidence Report — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Status",
        "- Draft / Not Executed",
        "",
        "Evidence Sections (aligned to V&V Plan placeholders)",
    ]
    if not vv_items:
        lines.append("- (No V&V Plan placeholders available yet.)")
        return "\n".join(lines).strip() + "\n"

    for item in vv_items:
        lines.append(f"\n{item['id']} (covers {item['input_id']})")
        lines.append("- Execution status: Not Executed [DRAFT]")
        lines.append("- Evidence reference(s): TBD [DRAFT]")
        lines.append("- Result summary: TBD [DRAFT]")
        lines.append("- Deviations / anomalies: TBD [DRAFT]")

    return "\n".join(lines).strip() + "\n"


def _build_risk_controls_doc(db: Session, *, project_id: str, profile: Any, components: list[Any]) -> str:
    comps = sorted(
        components,
        key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or "")),
    )
    lines: list[str] = [
        "Risk Control Measures Documentation — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Note",
        "- Draft structure only. Effectiveness assessment is intentionally left empty.",
        "",
    ]
    comp_name_by_id = {str(getattr(c, "id", "") or ""): str(getattr(c, "name", "") or "") for c in comps}

    # Gather structured RiskControls (preferred) + RiskItem free-text + FMEA mitigation as fallback.
    risk_items = db.query(RiskItem).filter(RiskItem.project_id == project_id).all()
    controls = db.query(RiskControl).filter(RiskControl.project_id == project_id).all()
    controls_by_risk_item: Dict[str, List[RiskControl]] = {}
    for rc in controls:
        controls_by_risk_item.setdefault(str(rc.risk_item_id), []).append(rc)

    # FMEA mitigation fallback
    fmea_rows = fmea_crud.get_fmea_rows_by_project(db, project_id)

    grouped: Dict[str, List[Dict[str, Any]]] = {}

    def add_entry(component_name: str, entry: Dict[str, Any]):
        grouped.setdefault(component_name or "Unknown", []).append(entry)

    # 1) Structured RiskControls, grouped by component_name from RiskItem/component fields
    for ri in risk_items:
        cname = (getattr(ri, "component_name", None) or comp_name_by_id.get(str(getattr(ri, "component_id", "") or ""), "") or "Unknown").strip()
        rcs = controls_by_risk_item.get(str(ri.id), [])
        if rcs:
            for rc in rcs:
                add_entry(
                    cname,
                    {
                        "source": "RiskControl",
                        "risk_key": getattr(ri, "risk_key", None) or f"R-{str(ri.id)[:8]}",
                        "control_key": getattr(rc, "control_key", None) or f"RC-{str(rc.id)[:8]}",
                        "control_name": getattr(rc, "control_name", None),
                        "control_description": getattr(rc, "control_description", None),
                        "control_type": getattr(rc, "control_type", None) or "TBD",
                        "verification_method": getattr(rc, "verification_method", None) or "TBD",
                        "effectiveness": getattr(rc, "effectiveness_notes", None) or "(blank)",
                    },
                )
        else:
            # 2) Free-text controls on RiskItem (existing data, but not structured yet)
            txts = []
            if getattr(ri, "mitigation_strategy", None):
                txts.append(("Mitigation strategy", str(ri.mitigation_strategy)))
            if getattr(ri, "control_measures", None):
                txts.append(("Control measures", str(ri.control_measures)))
            for label, txt in txts:
                if not (txt or "").strip():
                    continue
                add_entry(
                    cname,
                    {
                        "source": "RiskItem",
                        "risk_key": getattr(ri, "risk_key", None) or f"R-{str(ri.id)[:8]}",
                        "control_key": f"{label.replace(' ', '_').upper()}-{str(ri.id)[:8]}",
                        "control_name": f"{label} (from Risk Item)",
                        "control_description": txt.strip(),
                        "control_type": "TBD",
                        "verification_method": "TBD",
                        "effectiveness": "(blank)",
                    },
                )

    # 3) FMEA mitigation fallback controls
    for r in fmea_rows:
        mit = (getattr(r, "mitigation", None) or "").strip()
        if not mit:
            continue
        cid = str(getattr(r, "component_id", "") or "")
        cname = comp_name_by_id.get(cid, "") or "Unknown"
        add_entry(
            cname,
            {
                "source": "FMEA",
                "risk_key": f"FMEA-{str(r.id)[:8]}",
                "control_key": f"FMEA-MIT-{str(r.id)[:8]}",
                "control_name": "Mitigation (from FMEA row)",
                "control_description": mit,
                "control_type": "TBD",
                "verification_method": "TBD",
                "effectiveness": "(blank)",
            },
        )

    if not grouped:
        lines.append("(No risk controls found yet. Add Risk Controls or enter mitigations on FMEA rows.)")
        return "\n".join(lines).strip() + "\n"

    # Deterministic ordering for stable drafts
    for component_name in sorted(grouped.keys(), key=lambda x: (x or "").lower()):
        lines.append(f"\nComponent: {component_name}")
        lines.append("Controls (aggregated from existing data)")
        for e in grouped[component_name]:
            lines.append(
                f"- {e.get('control_key')}: {e.get('control_name')} "
                f"(source={e.get('source')}, risk={e.get('risk_key')})"
            )
            lines.append(f"  - Description: {e.get('control_description') or 'TBD'}")
            lines.append(f"  - Control type (inherent/protective/information): {e.get('control_type') or 'TBD'}")
            lines.append(f"  - Verification method: {e.get('verification_method') or 'TBD'}")
            lines.append(f"  - Effectiveness: {e.get('effectiveness') or '(blank)'}")

    return "\n".join(lines).strip() + "\n"


def _build_residual_risk_eval(*, project_id: str, profile: Any) -> str:
    return (
        "Residual Risk Evaluation — Draft\n\n"
        + _traceability_header(project_id=project_id, profile=profile)
        + "\n"
        "Structure\n"
        "- This draft provides placeholders only; no risk scoring is assigned.\n\n"
        "1) Pre-control risk summary (placeholder)\n"
        "- Summary: TBD [DRAFT]\n\n"
        "2) Post-control (residual) risk summary (placeholder)\n"
        "- Summary: TBD [DRAFT]\n\n"
        "3) Acceptability decision (placeholder)\n"
        "- Criteria applied: TBD [DRAFT]\n"
        "- Decision: TBD [DRAFT]\n"
        "- Rationale: TBD [DRAFT]\n"
    )


def _build_traceability_matrix(
    *,
    project_id: str,
    profile: Any,
    components: list[Any],
    design_inputs: list[dict[str, str]],
    design_outputs: list[dict[str, str]],
    vv_items: list[dict[str, str]],
    fmea_rows: list[FMEARow],
) -> str:
    # Component -> FMEA linkage summary
    fmea_by_comp: Dict[str, int] = {}
    for r in fmea_rows:
        cid = str(r.component_id or "")
        fmea_by_comp[cid] = fmea_by_comp.get(cid, 0) + 1

    lines: list[str] = [
        "Traceability Matrix — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Important",
        "- Draft trace links generated from Project Setup scaffolding.",
        "- No compliance claims are made in this draft.",
        "",
        "A) Components → FMEA Rows",
        "component_id | component_name | fmea_rows_count",
        "-" * 72,
    ]
    for c in sorted(components, key=lambda x: (str(getattr(x, 'name', '') or '').lower(), str(getattr(x, 'id', '') or ''))):
        cid = str(getattr(c, "id", "") or "")
        cname = str(getattr(c, "name", "") or "")
        lines.append(f"{cid} | {cname} | {fmea_by_comp.get(cid, 0)}")

    # DI -> DO -> VV
    do_by_input = {d["input_id"]: d["id"] for d in design_outputs}
    vv_by_input = {v["input_id"]: v["id"] for v in vv_items}

    lines.extend(
        [
            "",
            "B) Design Inputs → Design Outputs → V&V Plan",
            "design_input_id | design_output_id | vv_item_id",
            "-" * 72,
        ]
    )
    for di in design_inputs:
        di_id = di["id"]
        lines.append(f"{di_id} | {do_by_input.get(di_id, '')} | {vv_by_input.get(di_id, '')}")

    return "\n".join(lines).strip() + "\n"
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

    # Precompute deterministic DI/DO/VV placeholder lists for traceability scaffolding.
    di_content, di_entries = _build_design_inputs(project_id=project_id, profile=profile, components=components)
    do_content, do_entries = _build_design_outputs(project_id=project_id, profile=profile, design_inputs=di_entries)
    vv_plan_content, vv_items = _build_vv_plan(db, project_id=project_id, profile=profile, design_inputs=di_entries)

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
        document_crud.update_document(db, di.id, DocumentUpdate(content=di_content, status="draft"), project_id)
        stats.updated_documents.append("design_inputs_doc")

    # 5) Design Outputs doc
    do = by_type.get("design_outputs_doc")
    if do and _should_populate(do):
        document_crud.update_document(db, do.id, DocumentUpdate(content=do_content, status="draft"), project_id)
        stats.updated_documents.append("design_outputs_doc")

    # 6) V&V Plan
    vvp = by_type.get("vv_plan")
    if vvp and _should_populate(vvp):
        document_crud.update_document(db, vvp.id, DocumentUpdate(content=vv_plan_content, status="draft"), project_id)
        stats.updated_documents.append("vv_plan")

    # 7) V&V Evidence Report
    vve = by_type.get("vv_evidence")
    if vve and _should_populate(vve):
        vve_content = _build_vv_evidence_report(project_id=project_id, profile=profile, vv_items=vv_items)
        document_crud.update_document(db, vve.id, DocumentUpdate(content=vve_content, status="draft"), project_id)
        stats.updated_documents.append("vv_evidence")

    # 8) Risk Controls Documentation
    rcd = by_type.get("risk_controls_doc")
    if rcd and _should_populate(rcd):
        rcd_content = _build_risk_controls_doc(db, project_id=project_id, profile=profile, components=components)
        document_crud.update_document(db, rcd.id, DocumentUpdate(content=rcd_content, status="draft"), project_id)
        stats.updated_documents.append("risk_controls_doc")

    # 9) Residual Risk Evaluation
    rr = by_type.get("residual_risk")
    if rr and _should_populate(rr):
        rr_content = _build_residual_risk_eval(project_id=project_id, profile=profile)
        document_crud.update_document(db, rr.id, DocumentUpdate(content=rr_content, status="draft"), project_id)
        stats.updated_documents.append("residual_risk")

    # 10) Traceability Matrix
    tm = by_type.get("traceability_matrix")
    if tm and _should_populate(tm):
        fmea_rows = fmea_crud.get_fmea_rows_by_project(db, project_id)
        tm_content = _build_traceability_matrix(
            project_id=project_id,
            profile=profile,
            components=components,
            design_inputs=di_entries,
            design_outputs=do_entries,
            vv_items=vv_items,
            fmea_rows=fmea_rows,
        )
        document_crud.update_document(db, tm.id, DocumentUpdate(content=tm_content, status="draft"), project_id)
        stats.updated_documents.append("traceability_matrix")

    return stats.as_dict()


def build_project_setup_scaffolds(
    db: Session, *, project_id: str
) -> Dict[str, str]:
    """
    Pure helper (no side effects): build deterministic draft scaffolds from
    ProjectProfile + Components for comparison/tagging/upgrade flows.

    Note: This does NOT seed any DB rows (e.g., FMEA rows).
    """
    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)

    di_content, di_entries = _build_design_inputs(project_id=project_id, profile=profile, components=components)
    do_content, do_entries = _build_design_outputs(project_id=project_id, profile=profile, design_inputs=di_entries)
    vv_plan_content, vv_items = _build_vv_plan(db, project_id=project_id, profile=profile, design_inputs=di_entries)

    # FMEA content scaffold is based on whatever rows currently exist; no seeding.
    fmea_content = _draft_fmea_table(db, project_id=project_id, components=components)

    tm_content = _build_traceability_matrix(
        project_id=project_id,
        profile=profile,
        components=components,
        design_inputs=di_entries,
        design_outputs=do_entries,
        vv_items=vv_items,
        fmea_rows=fmea_crud.get_fmea_rows_by_project(db, project_id),
    )

    return {
        "rmp": _draft_rmp(project_id=project_id, profile=profile, components=components),
        "rmf": _draft_rmf_scaffold(project_id=project_id, profile=profile, components=components),
        "hazard_analysis": _draft_hazard_analysis(project_id=project_id, profile=profile, components=components),
        "fmea": fmea_content,
        "design_inputs_doc": di_content,
        "design_outputs_doc": do_content,
        "vv_plan": vv_plan_content,
        "vv_evidence": _build_vv_evidence_report(project_id=project_id, profile=profile, vv_items=vv_items),
        "risk_controls_doc": _build_risk_controls_doc(db, project_id=project_id, profile=profile, components=components),
        "residual_risk": _build_residual_risk_eval(project_id=project_id, profile=profile),
        "traceability_matrix": tm_content,
    }

