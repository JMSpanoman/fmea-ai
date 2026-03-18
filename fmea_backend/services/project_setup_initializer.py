from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import json
import os
import re

from sqlalchemy.orm import Session

from business_logic.project_initializer import initialize_project_required_docs
from crud import component as component_crud
from crud import project_profile as profile_crud
from crud import risk_item as risk_item_crud
from crud import risk_item_version as version_crud
from crud import document as document_crud
from crud import fmea as fmea_crud
from crud import design_control as design_control_crud
from crud import traceability as traceability_crud
from models.fmea import FMEARow
from models.document import Document
from models.project import Project
from schemas.fmea import FMEARowCreate, FMEARowUpdate
from schemas.risk_item import RiskItemCreate, RiskItemVersionCreate
from schemas.design_control import DesignInputCreate
from schemas.design_control import DesignOutputCreate


@dataclass
class InitializeStats:
    created_required_docs: int = 0
    seeded_risk_items: int = 0
    seeded_fmea_rows: int = 0
    seeded_design_inputs: int = 0
    seeded_design_outputs: int = 0
    updated_documents: int = 0

    def as_dict(self) -> dict:
        return {
            "created_required_docs": self.created_required_docs,
            "seeded_risk_items": self.seeded_risk_items,
            "seeded_fmea_rows": self.seeded_fmea_rows,
            "seeded_design_inputs": self.seeded_design_inputs,
            "seeded_design_outputs": self.seeded_design_outputs,
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
    def _is_placeholder_seed_row(r: FMEARow) -> bool:
        try:
            md = getattr(r, "ai_metadata", None)
            if not isinstance(md, dict):
                return False
            if md.get("seeded_by") != "wizard_initialize":
                return False
            hazard = str(md.get("hazard") or "")
            hay = " ".join(
                [
                    str(getattr(r, "failure_mode", "") or ""),
                    str(getattr(r, "effect", "") or ""),
                    str(getattr(r, "cause", "") or ""),
                    str(getattr(r, "mitigation", "") or ""),
                    hazard,
                ]
            ).lower()
            return "tbd" in hay
        except Exception:
            return False

    def _clamp_1_10(v: Any, default: int) -> int:
        try:
            n = int(v)
        except Exception:
            return default
        return max(1, min(10, n))

    def _fallback_rows(component_name: str, *, count: int) -> List[Dict[str, Any]]:
        # Non-AI fallback: still avoid "TBD" strings so UI/export looks realistic.
        # Keep deterministic-ish and generic.
        base = [
            {
                "hazard": f"{component_name}: unintended operation leading to user harm",
                "failure_mode": f"{component_name}: fails to operate as intended",
                "effect": "Loss of intended function; potential unsafe state or degraded performance",
                "cause": "Manufacturing variation, wear-out, or environmental stress",
                "severity": 7,
                "probability": 3,
                "detection": 4,
                "mitigation": "Design verification testing; incoming inspection; preventive maintenance",
            },
            {
                "hazard": f"{component_name}: incorrect output leading to misuse",
                "failure_mode": f"{component_name}: output out of specification",
                "effect": "Incorrect system behavior; potential misinterpretation by user/operator",
                "cause": "Calibration drift, sensor offset, or software configuration error",
                "severity": 6,
                "probability": 4,
                "detection": 5,
                "mitigation": "Calibration procedure; plausibility checks; alarms/limits; labeling",
            },
            {
                "hazard": f"{component_name}: overheating or thermal runaway",
                "failure_mode": f"{component_name}: excessive heat generation",
                "effect": "Thermal damage; shutdown; burn risk; reduced lifespan",
                "cause": "Overcurrent, blocked airflow, short circuit, or inadequate heat sinking",
                "severity": 8,
                "probability": 2,
                "detection": 4,
                "mitigation": "Thermal design margin; temperature sensor; current limiting; fusing",
            },
            {
                "hazard": f"{component_name}: mechanical breakage causing sharp edges/parts release",
                "failure_mode": f"{component_name}: crack/fracture under load",
                "effect": "Loss of integrity; debris; injury risk; device failure",
                "cause": "Material defect, fatigue, impact loading, or incorrect assembly torque",
                "severity": 7,
                "probability": 2,
                "detection": 5,
                "mitigation": "Material qualification; stress analysis; assembly torque controls; inspection",
            },
            {
                "hazard": f"{component_name}: contamination or ingress causing malfunction",
                "failure_mode": f"{component_name}: seal/closure failure allowing ingress",
                "effect": "Intermittent operation; corrosion; electrical short; reduced reliability",
                "cause": "Seal wear, improper assembly, chemical exposure, or gasket compression set",
                "severity": 6,
                "probability": 3,
                "detection": 5,
                "mitigation": "Ingress protection testing; gasket material selection; assembly poka-yoke",
            },
        ]
        out: List[Dict[str, Any]] = []
        n = max(0, int(count))
        for i in range(n):
            item = dict(base[i % len(base)])
            # If we exceed the base set, make a small deterministic variation so
            # `failure_mode` remains unique and still reads naturally.
            if i >= len(base):
                variant = (i // len(base)) + 1
                item["failure_mode"] = f"{item.get('failure_mode','').strip()} (scenario {variant})".strip()
                item["hazard"] = f"{item.get('hazard','').strip()} (scenario {variant})".strip()
            out.append(item)
        return out

    def _ai_rows(component_name: str, *, count: int) -> List[Dict[str, Any]]:
        openai_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not openai_key:
            return []
        try:
            import openai  # type: ignore
        except Exception:
            return []

        n = max(1, min(20, int(count)))
        prompt = f"""
Generate {n} realistic starter FMEA rows for the component: {component_name}.

Return JSON array ONLY. Each object must have these keys:
- hazard (string)
- failure_mode (string)
- effect (string)
- cause (string)
- severity (int 1-10)
- probability (int 1-10)
- detection (int 1-10)
- mitigation (string)

Keep each string concise (1-2 sentences). Avoid placeholder text like "TBD".
Ensure all `failure_mode` values are unique (no duplicates).
"""
        client = openai.OpenAI(api_key=openai_key)
        models_to_try = ["gpt-4o", "gpt-3.5-turbo"]
        last_err: Optional[Exception] = None
        content: Optional[str] = None
        for m in models_to_try:
            try:
                resp = client.chat.completions.create(
                    model=m,
                    messages=[
                        {"role": "system", "content": "You are an expert FMEA analyst. Return valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.4,
                    max_tokens=900,
                )
                content = resp.choices[0].message.content if resp and resp.choices else None
                if content:
                    break
            except Exception as e:
                last_err = e
                continue
        if not content:
            # fail closed: no AI rows
            return []

        # Try strict JSON parse first; then extract array via regex.
        data = None
        try:
            data = json.loads(content)
        except Exception:
            m = re.search(r"\[[\s\S]*\]", content)
            if m:
                try:
                    data = json.loads(m.group(0))
                except Exception:
                    data = None
        if not isinstance(data, list):
            return []

        out: List[Dict[str, Any]] = []
        seen_modes: set[str] = set()
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                continue
            hazard = str(item.get("hazard") or "").strip()
            failure_mode = str(item.get("failure_mode") or "").strip()
            effect = str(item.get("effect") or "").strip()
            cause = str(item.get("cause") or "").strip()
            mitigation = str(item.get("mitigation") or "").strip()

            # Skip obviously empty rows
            if not (hazard and failure_mode and effect and cause):
                continue
            key = re.sub(r"\s+", " ", failure_mode.strip().lower())
            if not key or key in seen_modes:
                continue
            seen_modes.add(key)

            out.append(
                {
                    "hazard": hazard[:500],
                    "failure_mode": failure_mode[:500],
                    "effect": effect[:800],
                    "cause": cause[:800],
                    "severity": _clamp_1_10(item.get("severity"), 6),
                    "probability": _clamp_1_10(item.get("probability"), 3),
                    "detection": _clamp_1_10(item.get("detection"), 4),
                    "mitigation": (mitigation or "Design controls; verification testing; inspection")[:800],
                }
            )
            if len(out) >= n:
                break
        return out

    def _mode_key(s: Any) -> str:
        return re.sub(r"\s+", " ", str(s or "").strip().lower())

    components = component_crud.get_components_by_project(db, project_id)
    if not components:
        return 0

    seeded = 0
    for c in components:
        rows = db.query(FMEARow).filter(FMEARow.project_id == project_id, FMEARow.component_id == c.id).all()
        existing_for_component = len(rows)
        used_modes = {_mode_key(getattr(r, "failure_mode", None)) for r in rows if _mode_key(getattr(r, "failure_mode", None))}
        unique_mode_count = len(used_modes)

        placeholders = [r for r in rows if _is_placeholder_seed_row(r)]
        # Ensure at least 5 rows AND at least 5 unique failure modes for each component.
        to_create_for_min_rows = max(0, 5 - existing_for_component)
        to_create_for_unique = max(0, 5 - unique_mode_count)
        # If we already have >=5 rows but not enough unique modes, prefer adding new rows
        # rather than mutating non-placeholder existing content.
        to_create = max(to_create_for_min_rows, to_create_for_unique)

        target = max(5, to_create + len(placeholders))
        target = max(1, min(20, target))

        generated = _ai_rows(str(c.name), count=target)
        if not generated:
            generated = _fallback_rows(str(c.name), count=target)

        # Filter generated to unique failure modes that aren't already present for the component.
        filtered: List[Dict[str, Any]] = []
        seen_new: set[str] = set()
        for g in generated:
            fm = _mode_key(g.get("failure_mode"))
            if not fm:
                continue
            if fm in used_modes or fm in seen_new:
                continue
            seen_new.add(fm)
            filtered.append(g)
        generated = filtered

        # Upgrade placeholder rows first (only wizard-seeded placeholders).
        for idx, r in enumerate(placeholders):
            if idx >= len(generated):
                break
            g = generated[idx]
            md = r.ai_metadata if isinstance(r.ai_metadata, dict) else {}
            md_next = {
                **(md or {}),
                "seeded_by": "wizard_initialize",
                "seeded_mode": "ai_seed_v1" if os.getenv("OPENAI_API_KEY") else "fallback_seed_v1",
                "component_name": c.name,
                "hazard": g.get("hazard") or "",
            }
            updated = fmea_crud.update_fmea_row(
                db,
                r.id,
                FMEARowUpdate(
                    failure_mode=g.get("failure_mode"),
                    effect=g.get("effect"),
                    cause=g.get("cause"),
                    severity=g.get("severity"),
                    probability=g.get("probability"),
                    detection=g.get("detection"),
                    mitigation=g.get("mitigation"),
                    ai_metadata=md_next,
                ),
                project_id,
            )
            if updated:
                seeded += 1
                used_modes.add(_mode_key(g.get("failure_mode")))

        # Create missing rows to reach 5 per component.
        offset = len(placeholders)
        for i in range(to_create):
            g = generated[offset + i] if (offset + i) < len(generated) else None
            # If we ran out (or had too many duplicates), keep generating fallback
            # rows until we find a new unique failure mode.
            if not g:
                # try a few deterministic fallback variants
                candidate = None
                for k in range(1, 25):
                    cand = _fallback_rows(str(c.name), count=k)[-1]
                    fm = _mode_key(cand.get("failure_mode"))
                    if fm and fm not in used_modes:
                        candidate = cand
                        break
                g = candidate or _fallback_rows(str(c.name), count=1)[0
                ]
            fm_key = _mode_key(g.get("failure_mode"))
            if fm_key and fm_key in used_modes:
                # As a last resort, make the failure mode unique without changing meaning too much.
                suffix = 1
                base_fm = str(g.get("failure_mode") or "").strip()[:450]
                while _mode_key(f"{base_fm} (variant {suffix})") in used_modes and suffix < 50:
                    suffix += 1
                g["failure_mode"] = f"{base_fm} (variant {suffix})".strip()
            fmea_crud.create_fmea_row(
                db,
                FMEARowCreate(
                    project_id=project_id,
                    component_id=c.id,
                    failure_mode=g.get("failure_mode"),
                    effect=g.get("effect"),
                    cause=g.get("cause"),
                    severity=g.get("severity"),
                    probability=g.get("probability"),
                    detection=g.get("detection"),
                    mitigation=g.get("mitigation"),
                    ai_metadata={
                        "seeded_by": "wizard_initialize",
                        "seeded_mode": "ai_seed_v1" if os.getenv("OPENAI_API_KEY") else "fallback_seed_v1",
                        "component_name": c.name,
                        "hazard": g.get("hazard") or "",
                    },
                ),
            )
            seeded += 1
            used_modes.add(_mode_key(g.get("failure_mode")))

    return seeded


def _seed_design_inputs_from_profile_components(
    db: Session,
    *,
    project_id: str,
    user_id: str,
) -> int:
    """
    Create baseline Design Input records from ProjectProfile + Components (Wizard).
    Idempotent: only seeds if the project currently has zero design inputs.

    This ensures the "Design Inputs Documentation" and Design Inputs module are not blank
    immediately after completing the wizard.
    """
    try:
        existing = design_control_crud.get_design_inputs_by_project(db, project_id)
        if existing:
            return 0
    except Exception:
        # If the table doesn't exist / query fails, don't block the wizard initializer.
        return 0

    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)

    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    user_pop = (getattr(profile, "user_population", None) or "").strip() if profile else ""

    seeded = 0

    def _create(title: str, requirement_text: str) -> None:
        nonlocal seeded
        title_s = (title or "").strip()
        req_s = (requirement_text or "").strip()
        if not title_s or not req_s:
            return
        design_control_crud.create_design_input(
            db,
            DesignInputCreate(
                project_id=project_id,
                title=title_s[:240],
                requirement_text=req_s[:2000],
                status="draft",
                source="wizard_seed",
                linked_risk_ids=[],
                text=req_s[:2000],
                requirement=req_s[:2000],
            ),
            created_by=user_id,
        )
        seeded += 1

    # System-level (from profile)
    if intended_use:
        _create(
            "Intended use (system requirement)",
            f"The device shall support the intended use: {intended_use}.",
        )
    if device_desc:
        _create(
            "Device description (system requirement)",
            f"The device shall conform to the described system architecture and features: {device_desc}.",
        )
    if user_pop:
        _create(
            "User/patient population (system requirement)",
            f"The device shall be usable and safe for the intended user/patient population: {user_pop}.",
        )
    if use_env:
        _create(
            "Use environment (system requirement)",
            f"The device shall be designed to operate safely in the intended use environment: {use_env}.",
        )

    # Always include a few generic baseline requirements
    _create(
        "Safety (general)",
        "The device shall fail safely or enter a safe state upon detection of critical faults.",
    )
    _create(
        "Labeling / Instructions for Use (general)",
        "The device shall include labeling/IFU content sufficient to support safe use and to communicate residual risks.",
    )
    _create(
        "Data integrity / auditability (general)",
        "The system shall maintain integrity of safety-relevant configuration and shall record audit logs for critical changes.",
    )

    # Component-specific baseline requirements (from wizard components)
    for c in components or []:
        name = (getattr(c, "name", None) or "").strip()
        if not name:
            continue
        desc = (getattr(c, "description", None) or "").strip()
        role_hint = desc if desc else "its intended function"
        _create(
            f"{name}: functional requirement",
            f"The system shall ensure the component '{name}' performs {role_hint}.",
        )
        _create(
            f"{name}: monitoring / fault detection",
            f"The system shall detect loss/degradation of function in '{name}' and provide an appropriate response (alarm, mitigation, or safe state).",
        )

    return seeded


def _seed_design_outputs_from_design_inputs(
    db: Session,
    *,
    project_id: str,
    user_id: str,
) -> int:
    """
    Create baseline Design Output records from existing Design Inputs.
    Idempotent: only seeds if the project currently has zero design outputs.

    Also creates trace_links: design_input -> design_output (implements).
    """
    try:
        existing = design_control_crud.get_design_outputs_by_project(db, project_id)
        if existing:
            return 0
    except Exception:
        return 0

    try:
        design_inputs = design_control_crud.get_design_inputs_by_project(db, project_id)
    except Exception:
        design_inputs = []

    if not design_inputs:
        return 0

    seeded = 0

    for di in design_inputs:
        di_id = str(getattr(di, "id", "") or "")
        di_key = str(getattr(di, "di_key", "") or "")
        di_title = str(getattr(di, "title", "") or "").strip() or "Design Input"
        req = ""
        try:
            req = str(getattr(di, "requirement", None) or getattr(di, "text", None) or "").strip()
        except Exception:
            req = ""

        # Create a baseline output artifact placeholder (implementation idea), not a claim of completion.
        text = (
            f"Implementation artifact for {di_key or di_title}:\n"
            f"- Design Output Title: (draft)\n"
            f"- Description: Implement requirement '{di_title}'.\n"
            + (f"- Requirement: {req}\n" if req else "")
            + "- Document reference: TBD\n"
        ).strip()

        do = design_control_crud.create_design_output(
            db,
            DesignOutputCreate(
                project_id=project_id,
                text=text[:4000],
                source="wizard_seed",
                linked_input_id=di_id or None,
            ),
            created_by=user_id,
        )
        seeded += 1

        # Create trace link DI -> DO for traceability (best-effort).
        try:
            from schemas.trace import TraceLinkCreate

            traceability_crud.create_trace_link(
                db,
                TraceLinkCreate(
                    project_id=project_id,
                    from_type="design_input",
                    from_id=di_id,
                    to_type="design_output",
                    to_id=str(getattr(do, "id", "") or ""),
                    link_type="implements",
                    rationale="Auto-derived wizard seed: baseline Design Output created to implement seeded Design Input.",
                ),
            )
        except Exception:
            # Don't block initialization if trace link creation fails.
            pass

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
    from models.project_profile import ProjectProfile
    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    device_name = getattr(profile, "device_description", None) if profile else None
    intended_use = getattr(profile, "intended_use", None) if profile else None
    rendered_html = hazard_analysis_renderer.render_hazard_analysis_html(
        evidence, project_name, device_name=device_name, intended_use=intended_use
    )

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
    stats.seeded_design_inputs = _seed_design_inputs_from_profile_components(db, project_id=project_id, user_id=user_id)
    stats.seeded_design_outputs = _seed_design_outputs_from_design_inputs(db, project_id=project_id, user_id=user_id)
    stats.updated_documents = _update_hazard_analysis_document_if_empty(db, project_id=project_id)

    return stats.as_dict()

