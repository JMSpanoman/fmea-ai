from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
import hashlib

from business_logic.project_initializer import initialize_project_required_docs
from crud import document as document_crud
from crud import project_profile as profile_crud
from crud import component as component_crud
from crud import fmea as fmea_crud
from schemas.document import DocumentUpdate
from schemas.fmea import FMEARowCreate, FMEARowUpdate
from services.project_profile_initializer import build_project_setup_scaffolds


AI_DRAFT_FN = Callable[[str, str, Dict[str, Any]], str]
AI_FMEA_ROWS_FN = Callable[[str, Dict[str, Any]], List[Dict[str, Any]]]


@dataclass
class AIGenerateStats:
    created_required_docs: int = 0
    attempted: int = 0
    updated: List[str] = None
    skipped: List[str] = None

    def __post_init__(self):
        self.updated = self.updated or []
        self.skipped = self.skipped or []

    def as_dict(self) -> dict:
        return {
            "created_required_docs": self.created_required_docs,
            "attempted": self.attempted,
            "updated": self.updated,
            "skipped": self.skipped,
        }


def _status_is_not_started(status: Optional[str]) -> bool:
    if status is None:
        return False
    s = str(status).strip().lower()
    return s in {"not started", "not_started", "not-started"}


def _is_emptyish(content: Optional[str]) -> bool:
    return not (content or "").strip()


def _is_placeholder_for_type(doc_type: str, content: Optional[str]) -> bool:
    c = (content or "").strip().lower()
    if not c:
        return True
    # Mirror the starter strings in business_logic/project_initializer._default_content_for
    starters = [
        ("rmf", "rmf/rmr export configuration starter"),
        ("hazard_analysis", "hazard analysis export configuration starter"),
        ("residual_risk", "residual risk evaluation export configuration starter"),
        ("risk_controls_doc", "risk control measures documentation export configuration starter"),
        ("fmea", "fmea starter"),
        ("design_inputs_doc", "design inputs documentation starter"),
        ("design_outputs_doc", "design outputs documentation starter"),
        ("vv_plan", "v&v plan starter"),
        ("vv_evidence", "v&v evidence report starter"),
        ("traceability_matrix", "traceability matrix export configuration starter"),
        ("rmp", "rmp starter"),
        ("capa", "capa starter"),
    ]
    for t, needle in starters:
        if doc_type == t and needle in c:
            return True
    return False


def _should_ai_generate(
    *,
    doc_type: str,
    doc_content: Optional[str],
    doc_status: Optional[str],
    setup_scaffold: Optional[str],
) -> bool:
    """
    Audit-safe gating:
    - OK if empty / Not started / known starter placeholder
    - Also OK if the document exactly matches our deterministic setup scaffold (meaning it's system-generated and unedited)
    """
    if _status_is_not_started(doc_status):
        return True
    if _is_emptyish(doc_content):
        return True
    if _is_placeholder_for_type(doc_type, doc_content):
        return True
    if setup_scaffold is not None and (doc_content or "") == setup_scaffold:
        return True
    return False


def generate_capa_ai_assist(*, context: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI reviewer output ONLY for the CAPA controlled document (ai_assist block).
    Never returns a full CAPA scaffold or duplicates system structure.
    """
    import json
    import os
    from pathlib import Path

    from services.capa_document_builder import normalize_ai_assist_dict

    if os.getenv("SMARTQS_TEST_AI", "").strip() == "1":
        return normalize_ai_assist_dict(
            {
                "problem_review": "Stub AI review (SMARTQS_TEST_AI=1). Replace with real model output in production.",
                "root_cause_challenges": ["Confirm that the trigger reference is traceable to an authorized record."],
                "missing_information": ["Containment verification evidence (if required by procedure)."],
                "suggested_actions": ["Define measurable effectiveness criteria before implementation."],
            }
        )

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return {}

    import openai

    prompts_dir = Path(__file__).parent.parent.parent / "ai_prompts"
    system_prompt = ""
    try:
        system_prompt = (prompts_dir / "phase3_system_prompt.txt").read_text().strip()
    except Exception:
        system_prompt = (
            "You are a medical device quality systems reviewer. "
            "Provide concise critique and suggestions only. Output JSON only."
        )
    try:
        capa_ai = (prompts_dir / "capa_ai_assist_prompt.txt").read_text().strip()
    except Exception:
        capa_ai = (
            "Return JSON only: {\n"
            '  "ai_assist": {\n'
            '    "problem_review": "string or null",\n'
            '    "root_cause_challenges": ["string"],\n'
            '    "missing_information": ["string"],\n'
            '    "suggested_actions": ["string"]\n'
            "  }\n"
            "}\n"
            "Rules: Do NOT repeat CAPA structure. Do NOT invent complaint/NCR IDs or approvals."
        )

    user_prompt = (
        f"{capa_ai}\n\n"
        f"Context:\n{context}\n\n"
        f"Metadata (JSON): {json.dumps(meta)}\n"
    )

    def _extract_json_object(text: str) -> dict:
        try:
            return json.loads(text)
        except Exception:
            import re

            m = re.search(r"\{[\s\S]*\}", text or "")
            if not m:
                raise
            return json.loads(m.group(0))

    client = openai.OpenAI(api_key=openai_api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = resp.choices[0].message.content or ""
        data = _extract_json_object(content) if content else {}
    except Exception:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            content = resp.choices[0].message.content or ""
            data = _extract_json_object(content) if content else {}
        except Exception:
            return {}

    inner = data.get("ai_assist") if isinstance(data.get("ai_assist"), dict) else data
    return normalize_ai_assist_dict(inner)


def merge_capa_document_json(
    *,
    project_id: str,
    project_name: str,
    existing_content: Optional[str],
    context: str,
    meta: Dict[str, Any],
) -> str:
    """
    Single structured CAPA document JSON: deterministic base + merged ai_assist (never concatenated text blocks).
    """
    from services.capa_document_builder import (
        load_or_build_capa_record,
        merge_ai_assist_only,
        serialize_capa_document,
    )

    base = load_or_build_capa_record(existing_content, project_id=project_id, project_name=project_name)
    ai_assist = generate_capa_ai_assist(context=context, meta=meta)
    merged = merge_ai_assist_only(base, ai_assist)
    merged["legacy_format"] = False
    return serialize_capa_document(merged)


def _default_ai_draft_fn(doc_type: str, context: str, meta: Dict[str, Any]) -> str:
    """
    Default AI draft implementation. Uses OpenAI if configured.
    Kept as a small wrapper so tests can inject a stub.
    """
    import os
    import json
    import openai

    def _fallback_draft() -> str:
        """
        Dev-friendly fallback (mirrors legacy FMEA behavior): if OpenAI isn't configured,
        return a deterministic draft scaffold instead of erroring.
        """
        project_name = str(meta.get("project_name") or "Project").strip() or "Project"
        dt = (doc_type or "").strip().lower()
        if dt == "benefit_risk_analysis":
            # Pull a few high-signal fields from the provided context so we can populate
            # some "TBD" values even when OpenAI isn't configured.
            import re

            def _extract_profile_field(key: str) -> str:
                m = re.search(rf"^- {re.escape(key)}:\s*(.*)$", context or "", flags=re.MULTILINE)
                if not m:
                    return ""
                val = (m.group(1) or "").strip()
                if val.lower() in {"none", "null"}:
                    return ""
                return val

            intended_use = _extract_profile_field("intended_use") or "TBD"
            device_description = _extract_profile_field("device_description") or "TBD"
            use_env = _extract_profile_field("use_environment") or "TBD"
            user_pop = _extract_profile_field("user_population") or "TBD"

            # Extract top residual risks from the evidence snapshot (if present).
            risk_lines: list[str] = []
            in_block = False
            for line in (context or "").splitlines():
                if line.strip().lower().startswith("top fmea residual risks"):
                    in_block = True
                    continue
                if in_block and line.strip().startswith("- "):
                    risk_lines.append(line.strip()[2:])
                    if len(risk_lines) >= 6:
                        break
                if in_block and line.strip().startswith("-") is False and line.strip().endswith(":"):
                    break

            def _parse_kv(text: str) -> dict:
                parts = [p.strip() for p in text.split("|")]
                out: dict = {}
                for p in parts:
                    if ":" in p:
                        k, v = p.split(":", 1)
                        out[k.strip().lower()] = v.strip()
                return out

            if risk_lines:
                md_rows = []
                for rl in risk_lines:
                    kv = _parse_kv(rl)
                    hazard = kv.get("hazard", "") or "TBD"
                    cause = kv.get("cause", "") or ""
                    fm = kv.get("failure_mode", "") or "TBD"
                    eff = kv.get("effect", "") or "TBD"
                    comp = kv.get("component", "") or "—"
                    seq = cause or f"{comp}: {fm}"
                    mit = kv.get("mitigation", "") or "TBD"
                    rrpn = kv.get("residual_rpn", "") or kv.get("residual rpn", "") or "TBD"
                    md_rows.append(f"| {hazard} | {seq} | {eff} | TBD | TBD | {mit} | {rrpn} |")
                residual_risk_rows_md = "\n".join(md_rows)
            else:
                residual_risk_rows_md = "| TBD | TBD | TBD | TBD | TBD | TBD | TBD |"

            mitigations: list[str] = []
            for rl in risk_lines:
                kv = _parse_kv(rl)
                mit = kv.get("mitigation", "")
                if mit and mit.lower() not in {"tbd", "—"}:
                    mitigations.append(mit)
                if len(mitigations) >= 5:
                    break
            mitigation_bullets = "\n".join([f"- {m}" for m in mitigations]) if mitigations else "- TBD (derive from FMEA mitigations and risk controls)"

            return f"""# Benefit–Risk Analysis Report

## 1. Document Information

- Project Name: {project_name}
- Project ID: (TBD)
- Device Name: {project_name}
- Device Description: {device_description}
- Intended Use / Indications: {intended_use}
- Risk Management File Reference: (TBD)
- Version: 0.1
- Date: (TBD)
- Author(s): (TBD)
- Reviewer(s): (TBD)
- Approver(s): (TBD)

---

## 2. Purpose

This document provides a structured evaluation of whether the **overall residual risks** associated with the device are acceptable when weighed against the **anticipated clinical benefits**, in accordance with ISO 14971. This draft **does not** claim conclusions; populate with objective evidence from CER, Risk Management outputs, and post-market information.

---

## 3. Scope

This analysis applies to:
- Final design configuration of the device
- Approved risk management documentation
- Intended use population

---

## 4. Reference Documents

- Risk Management Plan
- Hazard Analysis / FMEA
- Risk Control Measures Documentation
- Residual Risk Evaluation Report
- Clinical Evaluation Report (CER) / Literature Review
- Usability Engineering File (if applicable)
- Post-Market Surveillance Plan

---

## 5. Device Overview

### 5.1 Device Description
{device_description}

### 5.2 Intended Use
{intended_use}

### 5.3 Target Population
{user_pop}

**Use environment:** {use_env}

---

## 6. Summary of Residual Risks

### 6.1 Residual Risk Evaluation Summary
(TBD — summarize results of residual risk assessment)

### 6.2 Top Residual Risks

| Hazard | Sequence of Events | Harm | Severity | Probability | Risk Control Measures | Residual Risk |
|--------|------------------|------|----------|------------|----------------------|---------------|
{residual_risk_rows_md}

### 6.3 Risk Control Effectiveness
From available project evidence (best-effort, draft):
{mitigation_bullets}

- Design controls: (TBD)
- Protective measures: (TBD)
- Information for safety: (TBD)

### 6.4 Overall Residual Risk Statement
(TBD — state whether individual residual risks are acceptable per criteria)

---

## 7. Anticipated Clinical Benefits

### 7.1 Primary Clinical Benefits
(TBD — list key intended clinical outcomes)

### 7.2 Secondary Benefits
(TBD — quality of life, efficiency, etc.)

### 7.3 Quantification of Benefits
- Clinical outcomes: (TBD)
- Performance metrics: (TBD)
- Literature references: (TBD)

### 7.4 Time to Benefit
(TBD)

---

## 8. Benefit–Risk Comparison

### 8.1 Qualitative Comparison

| Category | Benefits | Risks |
|----------|--------|------|
| Severity | (TBD) | (TBD) |
| Probability | (TBD) | (TBD) |
| Duration | (TBD) | (TBD) |
| Reversibility | (TBD) | (TBD) |

### 8.2 Quantitative Comparison (if applicable)
(TBD — optional scoring or modeling)

### 8.3 Key Considerations
- Severity of condition being treated: (TBD)
- Availability of alternatives: (TBD)
- Clinical necessity: (TBD)

---

## 9. State of the Art Comparison

### 9.1 Existing Alternatives
(TBD — list comparable devices or treatments)

### 9.2 Comparison to Current Standard of Care

| Aspect | Current Standard | This Device |
|--------|----------------|------------|
| Effectiveness | (TBD) | (TBD) |
| Risk Profile | (TBD) | (TBD) |
| Usability | (TBD) | (TBD) |

### 9.3 No-Treatment Scenario
(TBD)

---

## 10. Target Population Considerations

### 10.1 High-Risk Subpopulations
- Elderly: (TBD)
- Pediatric: (TBD)
- Patients with comorbidities: (TBD)

### 10.2 Use Limitations
(TBD — contraindications, warnings, precautions)

---

## 11. Uncertainty and Data Gaps

- Known limitations of data: (TBD)
- Assumptions made: (TBD)
- Areas requiring further evidence: (TBD)

---

## 12. Post-Market Surveillance Plan

### 12.1 Monitoring Activities
- Complaint handling
- Trending
- Adverse event reporting

### 12.2 PMCF Activities (if applicable)
(TBD)

### 12.3 Reassessment Triggers
- New hazards identified
- Increased complaint rates
- Regulatory updates

---

## 13. Overall Benefit–Risk Conclusion

### 13.1 Statement of Acceptability
(TBD — explicit statement required. Example: "The overall residual risks are considered acceptable when weighed against the anticipated clinical benefits for the intended use population.")

### 13.2 Conditions of Acceptability
(TBD)

### 13.3 Risk–Benefit Determination Basis
- Clinical data: (TBD)
- Risk analysis: (TBD)
- State of the art: (TBD)

---

## 14. Traceability

| Element | Source Document |
|--------|----------------|
| Hazards | Hazard Analysis |
| Risk Controls | Risk Management File |
| Residual Risks | Residual Risk Evaluation |
| Clinical Benefits | Clinical Evaluation |
| Conclusions | This Report |

---

## 15. Approval

| Role | Name | Signature | Date |
|------|------|----------|------|
| Author | (TBD) | | |
| Reviewer | (TBD) | | |
| Approver | (TBD) | | |

---

## 16. Revision History

| Version | Date | Description of Change | Author |
|--------|------|----------------------|--------|
| 0.1 | (TBD) | Initial draft | (TBD) |
"""

        if dt == "design_dev_plan":
            # Full deterministic DDP (same generator as Project Initialize from profile), not a one-line stub.
            pid = str(meta.get("project_id") or "").strip()
            if pid:
                try:
                    from database import SessionLocal
                    from crud import component as component_crud
                    from crud import document as document_crud
                    from crud import project_profile as profile_crud
                    from models.project import Project
                    from services.project_profile_initializer import _draft_design_dev_plan

                    db = SessionLocal()
                    try:
                        profile = profile_crud.get_project_profile(db, pid)
                        components = component_crud.get_components_by_project(db, pid)
                        docs = document_crud.get_documents_by_project(db, pid)
                        by_type = {(d.type or "").lower(): d for d in docs}
                        refs = {
                            "design_inputs_doc": by_type.get("design_inputs_doc"),
                            "design_outputs_doc": by_type.get("design_outputs_doc"),
                            "design_reviews": by_type.get("design_reviews"),
                            "design_change_record": by_type.get("design_change_record"),
                            "rmf": by_type.get("rmf"),
                            "vv_evidence": by_type.get("vv_evidence"),
                            "validation_summary": by_type.get("validation_summary"),
                            "traceability_matrix": by_type.get("traceability_matrix"),
                        }
                        proj = db.query(Project).filter(Project.id == pid).first()
                        pn = getattr(proj, "name", None) if proj else project_name
                        body = _draft_design_dev_plan(
                            project_id=pid,
                            profile=profile,
                            components=components or [],
                            refs=refs,
                            project_name=pn,
                        )
                    finally:
                        db.close()
                    return body
                except Exception:
                    pass

        if dt == "capa":
            # Single structured JSON CAPA document (deterministic base; ai_assist empty without OpenAI).
            pid = str(meta.get("project_id") or "").strip()
            pn = str(meta.get("project_name") or "Project").strip() or "Project"
            if pid:
                try:
                    from services.capa_document_builder import (
                        build_capa_document_record,
                        merge_ai_assist_only,
                        serialize_capa_document,
                    )

                    base = build_capa_document_record(project_id=pid, project_name=pn)
                    merged = merge_ai_assist_only(base.model_dump(mode="json"), {})
                    return serialize_capa_document(merged)
                except Exception:
                    pass

        # Generic fallback for other doc types
        return f"""## AI Draft Unavailable (OpenAI not configured)

OpenAI is not configured for this environment (`OPENAI_API_KEY` not set). This is a deterministic placeholder scaffold.

- Document type: {dt}
- Project: {project_name}

### Draft
TBD
"""

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        env = (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or os.getenv("ENV") or "development").lower()
        if env in ("production", "prod", "staging"):
            raise RuntimeError("AI service unavailable. Please configure OPENAI_API_KEY.")
        return _fallback_draft()

    # CAPA: OpenAI enriches ai_assist only; never emits a second full scaffold.
    if (doc_type or "").strip().lower() == "capa":
        pid = str(meta.get("project_id") or "").strip()
        pn = str(meta.get("project_name") or "Project").strip() or "Project"
        if pid:
            return merge_capa_document_json(
                project_id=pid,
                project_name=pn,
                existing_content=None,
                context=context,
                meta=meta,
            )

    # Use the existing Phase 3 system prompt + document drafting prompt files if present.
    from pathlib import Path

    prompts_dir = Path(__file__).parent.parent.parent / "ai_prompts"
    system_prompt = ""
    doc_prompt = ""
    try:
        system_prompt = (prompts_dir / "phase3_system_prompt.txt").read_text().strip()
    except Exception:
        system_prompt = (
            "You are SmartQS AI. Produce detailed, audit-ready QMS documentation drafts. "
            "Use deterministic project setup context provided. Return JSON only."
        )
    # Prefer a doc-specific prompt if it exists (e.g., rmf_prompt.txt), else fall back to the generic drafting prompt.
    try:
        specific = prompts_dir / f"{doc_type}_prompt.txt"
        if specific.exists():
            doc_prompt = specific.read_text().strip()
        else:
            doc_prompt = (prompts_dir / "document_drafting_prompt.txt").read_text().strip()
    except Exception:
        doc_prompt = "Create a complete document of the specified type given the context. Return JSON: {draft: 'text'}."

    # Stronger, explicit constraints for safety/auditability
    user_prompt = (
        f"{doc_prompt}\n\n"
        f"DocumentType: {doc_type}\n"
        "Instructions:\n"
        "- Generate as much detail as possible.\n"
        "- Must be clearly marked as DRAFT.\n"
        "- Include the Project ID and state: 'Generated with AI from Project Setup'.\n"
        "- Do NOT fabricate test results, approvals, or compliance claims.\n"
        "- If risk scoring is not provided, do not invent scores.\n"
        "- Keep placeholders where data is unknown.\n\n"
        f"Context:\n{context}\n\n"
        f"Metadata (JSON): {json.dumps(meta)}\n"
    )

    def _extract_json_object(text: str) -> dict:
        try:
            return json.loads(text)
        except Exception:
            import re
            m = re.search(r"\{[\s\S]*\}", text or "")
            if not m:
                raise
            return json.loads(m.group(0))

    client = openai.OpenAI(api_key=openai_api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        content = resp.choices[0].message.content or ""
        data = _extract_json_object(content) if content else {}
    except Exception as e:
        # Some models / accounts reject response_format or older model names; retry without response_format.
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
            )
            content = resp.choices[0].message.content or ""
            data = _extract_json_object(content) if content else {}
        except Exception as e2:
            raise RuntimeError(f"OpenAI draft generation failed: {e2}") from e2
    draft = data.get("draft") or ""
    if not isinstance(draft, str) or not draft.strip():
        raise RuntimeError("AI returned no draft content")
    return draft


def _default_ai_fmea_rows_fn(context: str, meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    AI generator for persisted FMEA rows.
    Returns a list of dicts, one per component, with hazard + failure mode + S/O/D.
    """
    import os
    import json
    import openai

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("AI service unavailable. Please configure OPENAI_API_KEY.")

    system_prompt = "You are SmartQS AI. Generate ISO 14971 oriented FMEA content. Output JSON only."
    user_prompt = (
        "Generate ONE FMEA row per component based on the project setup context.\n"
        "Return JSON only in this exact shape:\n"
        "{ \"rows\": [\n"
        "  {\n"
        "    \"component_id\": \"...\",\n"
        "    \"component_name\": \"...\",\n"
        "    \"hazard\": \"...\",\n"
        "    \"failure_mode\": \"...\",\n"
        "    \"effect\": \"...\",\n"
        "    \"cause\": \"...\",\n"
        "    \"occurrence\": 1,\n"
        "    \"severity\": 1,\n"
        "    \"detection\": 1,\n"
        "    \"mitigation\": \"...\"\n"
        "  }\n"
        "] }\n"
        "\nRules:\n"
        "- Provide realistic values 1–10 for severity/occurrence/detection.\n"
        "- Do NOT fabricate test results, approvals, or compliance claims.\n"
        "- Hazard should be a concise potential source of harm.\n"
        "- Keep content specific to implantable cardiac devices if context indicates pacemaker/cardiac.\n"
        "\nContext:\n"
        + context
        + "\n\nMetadata:\n"
        + json.dumps(meta)
    )

    def _extract_json_object(text: str) -> dict:
        try:
            return json.loads(text)
        except Exception:
            import re
            m = re.search(r"\{[\s\S]*\}", text or "")
            if not m:
                raise
            return json.loads(m.group(0))

    client = openai.OpenAI(api_key=openai_api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = resp.choices[0].message.content or ""
        data = _extract_json_object(content) if content else {}
    except Exception as e:
        # Retry without response_format for compatibility.
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            content = resp.choices[0].message.content or ""
            data = _extract_json_object(content) if content else {}
        except Exception as e2:
            raise RuntimeError(f"OpenAI FMEA scoring failed: {e2}") from e2
    rows = data.get("rows")
    if not isinstance(rows, list):
        raise RuntimeError("AI returned invalid FMEA rows payload")
    return rows


def _is_draft_placeholder_text(s: Optional[str]) -> bool:
    v = (s or "").strip()
    return (not v) or v.startswith("[DRAFT]")


def _safe_int_1_10(v: Any) -> Optional[int]:
    try:
        n = int(v)
        if 1 <= n <= 10:
            return n
    except Exception:
        return None
    return None


def _upsert_scored_fmea_rows_from_ai(
    db: Session,
    *,
    project_id: str,
    components: list[Any],
    rows_payload: List[Dict[str, Any]],
) -> Tuple[int, int]:
    """
    Writes to persisted FMEARow table in an audit-safe way:
    - Only fills fields that are empty or placeholder ([DRAFT]) for text fields
    - Only fills S/O/D if currently None
    - Stores 'hazard' under ai_metadata['hazard']

    Returns (created_count, updated_count)
    """
    existing = fmea_crud.get_fmea_rows_by_project(db, project_id)
    by_comp: Dict[str, Any] = {str(r.component_id or ""): r for r in existing if r.component_id}
    comp_name_by_id = {str(getattr(c, "id", "") or ""): str(getattr(c, "name", "") or "") for c in components}

    created = 0
    updated = 0

    for item in rows_payload:
        comp_id = str(item.get("component_id") or "").strip()
        if not comp_id:
            # Try to map by name if component_id missing
            cname = str(item.get("component_name") or "").strip()
            if cname:
                for cid, n in comp_name_by_id.items():
                    if n.strip().lower() == cname.lower():
                        comp_id = cid
                        break
        if not comp_id:
            continue

        hazard = str(item.get("hazard") or "").strip()
        fm = str(item.get("failure_mode") or "").strip()
        eff = str(item.get("effect") or "").strip()
        cause = str(item.get("cause") or "").strip()
        mit = str(item.get("mitigation") or "").strip()
        sev = _safe_int_1_10(item.get("severity"))
        occ = _safe_int_1_10(item.get("occurrence"))
        det = _safe_int_1_10(item.get("detection"))

        row = by_comp.get(comp_id)
        if not row:
            # Create only if we have at least the core fields
            new_meta = {"generated_with_ai": True, "source": "project_setup_ai", "project_id": project_id}
            if hazard:
                new_meta["hazard"] = hazard
            fmea_crud.create_fmea_row(
                db,
                FMEARowCreate(
                    project_id=project_id,
                    component_id=comp_id,
                    failure_mode=fm or None,
                    effect=eff or None,
                    cause=cause or None,
                    severity=sev,
                    probability=occ,
                    detection=det,
                    mitigation=mit or None,
                    ai_metadata=new_meta,
                ),
            )
            created += 1
            continue

        # Only update safe fields (never overwrite user-entered non-draft text, never overwrite existing scores).
        meta0 = row.ai_metadata if isinstance(row.ai_metadata, dict) else {}
        meta = dict(meta0)
        meta.update({"generated_with_ai": True, "source": "project_setup_ai", "project_id": project_id})
        if hazard and not str(meta.get("hazard") or "").strip():
            meta["hazard"] = hazard

        upd = FMEARowUpdate(ai_metadata=meta)

        if fm and _is_draft_placeholder_text(row.failure_mode):
            upd.failure_mode = fm
        if eff and _is_draft_placeholder_text(row.effect):
            upd.effect = eff
        if cause and _is_draft_placeholder_text(row.cause):
            upd.cause = cause
        if mit and _is_draft_placeholder_text(row.mitigation):
            upd.mitigation = mit

        if sev is not None and row.severity is None:
            upd.severity = sev
        if occ is not None and row.probability is None:
            upd.probability = occ
        if det is not None and row.detection is None:
            upd.detection = det

        # Only write if we actually changed anything meaningful
        if getattr(upd, "model_dump", None):
            changes = upd.model_dump(exclude_unset=True)
        else:
            changes = upd.dict(exclude_unset=True)
        if len(changes.keys()) > 1 or ("ai_metadata" in changes and len(changes.keys()) == 1 and meta != meta0):
            fmea_crud.update_fmea_row(db, row.id, upd, project_id)
            updated += 1

    return created, updated


def _fmea_needs_ai_rows(
    *,
    project_id: str,
    components: list[Any],
    existing_rows: list[Any],
) -> bool:
    """
    Idempotency guard:
    - If any component lacks a row => needs AI
    - If any draft/placeholder row is missing hazard or S/O/D => needs AI
    - Otherwise do nothing
    """
    comp_ids = [str(getattr(c, "id", "") or "") for c in components if getattr(c, "id", None)]
    row_by_comp = {str(r.component_id or ""): r for r in existing_rows if r.component_id}

    # Missing rows for components
    for cid in comp_ids:
        if cid and cid not in row_by_comp:
            return True

    # No rows at all
    if not existing_rows and comp_ids:
        return True

    for r in existing_rows:
        meta = r.ai_metadata if isinstance(getattr(r, "ai_metadata", None), dict) else {}
        hazard = str(meta.get("hazard") or "").strip()
        is_placeholder = _is_draft_placeholder_text(getattr(r, "failure_mode", None)) or bool(meta.get("draft")) or meta.get("seeded_by") == "initialize_from_profile"
        if not is_placeholder:
            continue
        if not hazard:
            return True
        if getattr(r, "severity", None) is None or getattr(r, "probability", None) is None or getattr(r, "detection", None) is None:
            return True

    return False


def generate_all_docs_with_ai_from_setup(
    db: Session,
    *,
    project_id: str,
    doc_types: Optional[List[str]] = None,
    ai_draft_fn: Optional[AI_DRAFT_FN] = None,
    ai_fmea_rows_fn: Optional[AI_FMEA_ROWS_FN] = None,
) -> Dict[str, Any]:
    """
    Generates detailed drafts with AI using Project Setup context (ProjectProfile + Components).

    Audit-safe rules:
    - NEVER overwrite user-edited content
    - Only generate if doc is empty, Not started, starter placeholder, or exactly equals the deterministic setup scaffold
    - Always writes Draft content (new document version via update_document)
    """
    stats = AIGenerateStats()

    created = initialize_project_required_docs(db, project_id)
    stats.created_required_docs = len(created)

    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}

    wanted = [t.lower() for t in (doc_types or list(by_type.keys()))]
    wanted = [t for t in wanted if t]  # sanitize

    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)
    scaffolds = build_project_setup_scaffolds(db, project_id=project_id)

    # Context pack: keep deterministic + structured for best generation.
    component_lines = [
        f"- {getattr(c, 'name', '')} (id={getattr(c, 'id', '')})" + (f": {getattr(c, 'description', '')}" if getattr(c, "description", None) else "")
        for c in components
    ]
    context = (
        f"Project ID: {project_id}\n"
        f"Profile:\n"
        f"- intended_use: {getattr(profile, 'intended_use', None)}\n"
        f"- device_description: {getattr(profile, 'device_description', None)}\n"
        f"- user_population: {getattr(profile, 'user_population', None)}\n"
        f"- use_environment: {getattr(profile, 'use_environment', None)}\n"
        f"- key_safety_characteristics: {getattr(profile, 'key_safety_characteristics', None)}\n\n"
        "Components:\n"
        + ("\n".join(component_lines) if component_lines else "- (none)\n")
        + "\n\n"
        "Deterministic Setup Scaffolds (for reference / structure):\n"
    )

    ai_draft_fn = ai_draft_fn or _default_ai_draft_fn
    ai_fmea_rows_fn = ai_fmea_rows_fn or _default_ai_fmea_rows_fn

    def _truncate(s: Optional[str], max_chars: int) -> str:
        v = (s or "")
        if len(v) <= max_chars:
            return v
        return v[: max_chars - 20] + "\n...\n[TRUNCATED]\n"

    def _content_hash(s: str) -> str:
        return hashlib.sha256((s or "").encode("utf-8")).hexdigest()[:16]

    def _append_rmf_addendum_if_needed(*, doc: Any, addendum: str, context_hash: str) -> bool:
        """
        Append-only mode for RMF:
        - Never overwrite existing content
        - Idempotent: don't append the same context hash twice
        - Stores hashes under ai_metadata["rmf_addendum_hashes"]
        Returns True if appended.
        """
        meta0 = doc.ai_metadata if isinstance(getattr(doc, "ai_metadata", None), dict) else {}
        hashes = meta0.get("rmf_addendum_hashes")
        if not isinstance(hashes, list):
            hashes = []
        if context_hash in hashes:
            return False

        marker = f"[AI ADDENDUM — Generated with AI from Project Setup — hash={context_hash}]"
        existing = doc.content or ""
        if marker in existing:
            # Defensive: if content already includes it, record hash and do not append again.
            hashes.append(context_hash)
            document_crud.update_document(
                db,
                doc.id,
                DocumentUpdate(
                    ai_metadata={**meta0, "rmf_addendum_hashes": hashes, "generated_with_ai": True, "source": "project_setup_ai_rmf_addendum"},
                ),
                project_id,
            )
            return False

        appended = (
            existing.rstrip()
            + "\n\n"
            + ("-" * 72)
            + "\n"
            + marker
            + "\n\n"
            + (addendum or "").strip()
            + "\n"
        )
        hashes.append(context_hash)
        document_crud.update_document(
            db,
            doc.id,
            DocumentUpdate(
                content=appended,
                status="draft",
                ai_metadata={**meta0, "rmf_addendum_hashes": hashes, "generated_with_ai": True, "source": "project_setup_ai_rmf_addendum"},
            ),
            project_id,
        )
        return True

    for t in wanted:
        doc = by_type.get(t)
        if not doc:
            continue
        scaffold = scaffolds.get(t)

        # Special case: FMEA is rendered from persisted FMEARow rows.
        # We can safely populate missing hazard + scores based on row-level placeholders,
        # even when the document content itself is user-edited (we will not overwrite the doc content in that case).
        if t == "fmea":
            existing_rows = fmea_crud.get_fmea_rows_by_project(db, project_id)
            if not _fmea_needs_ai_rows(project_id=project_id, components=components, existing_rows=existing_rows):
                stats.skipped.append("fmea_rows")
                continue

            try:
                fmea_context = context + f"\n--- Scaffold for fmea ---\n{scaffold or '(none)'}\n"
                rows_payload = ai_fmea_rows_fn(
                    fmea_context,
                    {"project_id": project_id, "doc_type": "fmea_rows", "source": "Project Setup"},
                )
                created_rows, updated_rows = _upsert_scored_fmea_rows_from_ai(
                    db, project_id=project_id, components=components, rows_payload=rows_payload
                )
            except Exception as e:
                # Surface OpenAI failures clearly so the UI/user can correct configuration.
                raise RuntimeError(f"FMEA AI scoring failed: {e}") from e

            # Update the FMEA document content ONLY if it is safe to do so (placeholder/scaffold/not-started).
            # The rendered FMEA document export comes from persisted rows, so content updates are optional.
            content_changed = False
            if _should_ai_generate(
                doc_type="fmea",
                doc_content=doc.content,
                doc_status=doc.status,
                setup_scaffold=scaffold,
            ):
                refreshed_scaffolds = build_project_setup_scaffolds(db, project_id=project_id)
                fmea_table = refreshed_scaffolds.get("fmea") or ""
                content_changed = (doc.content or "") != fmea_table

            if content_changed:
                document_crud.update_document(
                    db,
                    doc.id,
                    DocumentUpdate(
                        content=fmea_table,
                        status="draft",
                        ai_metadata={"generated_with_ai": True, "source": "project_setup_ai_fmea_rows"},
                    ),
                    project_id,
                )
            if created_rows or updated_rows or content_changed:
                stats.updated.append("fmea_rows")
                stats.attempted += 1
            else:
                stats.skipped.append("fmea_rows")
            continue

        can_overwrite = _should_ai_generate(
            doc_type=t,
            doc_content=doc.content,
            doc_status=doc.status,
            setup_scaffold=scaffold,
        )

        # RMF is a compilation/summary doc: include the key project setup + risk data to produce a meaningful draft.
        if t == "rmf":
            try:
                from crud import risk_item as risk_item_crud
                risk_items = risk_item_crud.get_risk_items_by_project(db, project_id)
            except Exception:
                risk_items = []

            existing_rows = fmea_crud.get_fmea_rows_by_project(db, project_id)
            fmea_summary_lines: List[str] = []
            for r in existing_rows[:50]:
                hz = ""
                try:
                    meta0 = r.ai_metadata if isinstance(getattr(r, "ai_metadata", None), dict) else {}
                    hz = str(meta0.get("hazard") or "").strip()
                except Exception:
                    hz = ""
                fmea_summary_lines.append(
                    f"- component_id={getattr(r, 'component_id', None)} hazard={hz!r} "
                    f"failure_mode={getattr(r, 'failure_mode', None)!r} "
                    f"S={getattr(r, 'severity', None)} O={getattr(r, 'probability', None)} D={getattr(r, 'detection', None)} RPN={getattr(r, 'rpn', None)}"
                )

            risk_lines: List[str] = []
            for ri in risk_items[:50]:
                risk_lines.append(
                    f"- {getattr(ri, 'risk_key', '') or getattr(ri, 'id', '')}: {getattr(ri, 'title', '')} "
                    f"(component={getattr(ri, 'component_name', None)}) status={getattr(ri, 'status', None)} "
                    f"risk_level={getattr(ri, 'risk_level', None)}"
                )

            # Include key deterministic scaffolds for structure.
            rmf_struct = scaffolds.get("rmf") or scaffold or "(none)"
            per_doc_context = (
                context
                + "\n--- RMF STRUCTURE (deterministic scaffold) ---\n"
                + rmf_struct
                + "\n\n--- RELATED SCAFFOLDS (for compilation) ---\n"
                + f"\n[RMP]\n{_truncate(scaffolds.get('rmp'), 4000)}"
                + f"\n[Hazard Analysis]\n{_truncate(scaffolds.get('hazard_analysis'), 4000)}"
                + f"\n[Risk Controls Doc]\n{_truncate(scaffolds.get('risk_controls_doc'), 4000)}"
                + f"\n[Residual Risk]\n{_truncate(scaffolds.get('residual_risk'), 3000)}"
                + f"\n[Traceability Matrix]\n{_truncate(scaffolds.get('traceability_matrix'), 4000)}"
                + "\n\n--- PERSISTED FMEA ROWS (for RMF summary) ---\n"
                + ("\n".join(fmea_summary_lines) if fmea_summary_lines else "- (none)\n")
                + "\n\n--- PERSISTED RISK ITEMS (for RMF summary) ---\n"
                + ("\n".join(risk_lines) if risk_lines else "- (none)\n")
                + "\n"
            )
        else:
            per_doc_context = context + f"\n--- Scaffold for {t} ---\n{scaffold or '(none)'}\n"
        meta = {"project_id": project_id, "doc_type": t, "source": "Project Setup"}

        # Special behavior for RMF:
        # - If it's safe to overwrite (placeholder/scaffold/not-started), generate the full RMF (normal path).
        # - If it's not safe to overwrite (user has content), still allow AI to ADD information via an append-only addendum.
        if t == "rmf" and not can_overwrite:
            stats.attempted += 1
            ctx_hash = _content_hash(per_doc_context)
            addendum = ai_draft_fn("rmf_addendum", per_doc_context, {**meta, "doc_type": "rmf_addendum"})
            if _append_rmf_addendum_if_needed(doc=doc, addendum=addendum, context_hash=ctx_hash):
                stats.updated.append("rmf")
            else:
                stats.skipped.append("rmf_addendum")
            continue

        if not can_overwrite:
            stats.skipped.append(t)
            continue

        stats.attempted += 1

        draft = ai_draft_fn(t, per_doc_context, meta)

        # Ensure the draft is clearly marked and traceable even if the model forgets.
        header = (
            "DRAFT — Generated with AI from Project Setup (ProjectProfile + Components)\n"
            f"Project ID: {project_id}\n"
            "Do not treat this as approved or executed evidence.\n\n"
        )
        final_content = draft
        if "project id:" not in (draft or "").lower():
            final_content = header + draft
        elif "draft" not in (draft or "").lower()[:200]:
            final_content = "DRAFT\n" + draft

        document_crud.update_document(
            db,
            doc.id,
            DocumentUpdate(content=final_content, status="draft", ai_metadata={"generated_with_ai": True, "source": "project_setup"}),
            project_id,
        )
        stats.updated.append(t)

    return stats.as_dict()

