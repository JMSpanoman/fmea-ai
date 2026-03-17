from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas.design_control import DesignControlsGenerateRequest, DesignControlsGenerateResponse
from schemas.vv import (
    VVGenerateRequest,
    VVGenerateResponse,
    VVFromRiskGenerateRequest,
    VVFromRiskGenerateResponse,
    VVFromRiskSaveRequest,
    VVFromRiskSaveResponse,
    CalculationItem,
    TraceabilityBlock,
)
from schemas.capa import CAPAGenerateRequest, CAPAGenerateResponse
from schemas.pms import PMSGenerateRequest, PMSGenerateResponse
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
import json
from pathlib import Path

router = APIRouter(prefix="/ai", tags=["AI Phase 2"], dependencies=[Depends(require_pro)])


def _ensure_openai_env_loaded() -> None:
    """Load OPENAI_API_KEY / OPENAI_KEY from backend ENV.local and .env when this endpoint is called."""
    try:
        from dotenv import load_dotenv
        backend_dir = Path(__file__).resolve().parent.parent  # fmea_backend
        load_dotenv(dotenv_path=backend_dir / "ENV.local", override=False)
        load_dotenv(dotenv_path=backend_dir / ".env", override=False)
    except Exception:
        pass


def _get_openai_api_key() -> Optional[str]:
    """Use OPENAI_API_KEY or OPENAI_KEY (same env as FMEA)."""
    return (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY") or "").strip() or None


def _stub_sample_size_rationale(severity: int, occurrence: int, rpn: int) -> str:
    """Protocol-style sample size rationale based on risk level (for stub response)."""
    if severity >= 4 or rpn >= 80:
        return "High risk: n ≥ 5 units for verification; n ≥ 3 for validation scenarios. Justified by severity and RPN; adjust per protocol."
    if severity >= 3:
        return "Medium risk: n ≥ 3 units for verification; at least one validation scenario. Align with risk level and protocol."
    return "Low risk: n ≥ 1 for bench verification; validation as needed per protocol."


def _stub_vv_from_risk_response(request: VVFromRiskGenerateRequest) -> VVFromRiskGenerateResponse:
    """Fallback V&V response when no API key (same pattern as FMEA suggest in ai_phase1)."""
    payload = request.to_payload()
    rpn = payload["severity"] * payload["occurrence"] * payload["detection"]
    comp = payload["component"]
    fm = payload["failure_mode"]
    mitigation = payload.get("mitigation") or ""
    return VVFromRiskGenerateResponse(
        verification_test_name=f"Verification: {comp} – {fm}",
        verification_objective=f"Verify that risk control for '{fm}' is implemented and effective.",
        verification_method="Perform test per approved procedure; record results and evidence.",
        validation_test_name=f"Validation: {comp} – {fm}",
        validation_objective=f"Confirm that in intended use the mitigation for '{fm}' meets user needs.",
        validation_method_or_scenario="Execute validation scenario per protocol; document pass/fail.",
        validation_scenario=None,
        acceptance_criteria=[
            f"All test steps completed as specified.",
            f"Results meet defined acceptance limits.",
            f"Traceability to risk item (component: {comp}, failure mode: {fm}) documented.",
        ],
        calculations=[
            CalculationItem(
                name="Percent Error",
                formula="|Measured - Target| / Target × 100",
                description="Relative error vs target (when applicable).",
                inputs=["Measured", "Target"],
                unit_or_threshold="%",
            ),
        ],
        worst_case_conditions=[
            "Minimum/maximum specified operating conditions.",
            "End-of-life or worst-case component tolerance.",
        ],
        sample_size_rationale=_stub_sample_size_rationale(payload["severity"], payload["occurrence"], rpn),
        traceability=TraceabilityBlock(
            source_component=comp,
            source_failure_mode=fm,
            source_mitigation=mitigation,
            source_effect=payload.get("effect") or None,
            source_cause=payload.get("cause") or None,
            source_severity=payload["severity"],
            source_occurrence=payload["occurrence"],
            source_detection=payload["detection"],
            source_rpn=rpn,
            source_residual_severity=payload.get("residual_severity"),
            source_residual_occurrence=payload.get("residual_occurrence"),
            source_residual_detection=payload.get("residual_detection"),
            source_residual_rpn=payload.get("residual_rpn"),
        ),
    )


# Load AI prompts
PROMPTS_DIR = Path(__file__).parent.parent.parent / "ai_prompts"

def load_prompt(filename: str) -> str:
    """Load prompt from file"""
    try:
        with open(PROMPTS_DIR / filename, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

SYSTEM_PROMPT = load_prompt("phase2_system_prompt.txt") or "You are Smart Risk Phase 2 AI. Generate design inputs, design outputs, V and V test cases, CAPA plans, and PMS assessments using ISO 13485, ISO 14971, IEC 60601-1, and FDA QSR best practices. Output JSON only."
DESIGN_CONTROLS_PROMPT = load_prompt("design_controls_prompt.txt") or "Given risks, failure modes, device purpose, and component description, generate design inputs that address those risks. Then generate design outputs that satisfy the inputs. Return JSON with arrays design_inputs, design_outputs, and trace_links."
DESIGN_INPUTS_PROMPT = load_prompt("design_inputs_prompt.txt") or "Given a component name, generate exactly 5 design inputs that are relevant, specific, and appropriate for medical device design control. Each design input should have a title and a detailed requirement. Return JSON with an array 'design_inputs' containing objects with 'title' and 'requirement' fields."
DESIGN_OUTPUTS_PROMPT = load_prompt("design_outputs_prompt.txt") or "Given a component name, generate exactly 5 design outputs that are relevant, specific, and appropriate for medical device design control. Each design output should have a title and a detailed specification. Design outputs should satisfy design inputs and demonstrate that design requirements have been met. Return JSON with an array 'design_outputs' containing objects with 'title' and 'specification' fields."
VV_PROMPT = load_prompt("vv_prompt.txt") or "Given a design output, generate a verification test method, acceptance criteria, and rationale. Return JSON only."
VV_FROM_RISK_PROMPT = load_prompt("vv_from_risk_prompt.txt") or "Generate V&V test logic from FMEA/risk row. Return JSON with verification_test_name, verification_objective, verification_method, validation_scenario, acceptance_criteria, calculations, worst_case_conditions, sample_size_rationale, traceability."
CAPA_PROMPT = load_prompt("capa_prompt.txt") or "Given risk data and failure information, generate CAPA content including root cause, CAPA plan, effectiveness check, and risk linkages. Return JSON."
PMS_PROMPT = load_prompt("pms_prompt.txt") or "Given a PMS signal (complaints, service data, trending, field failure), identify affected risks, propose updates, and predict future risk trends. Return JSON."

# Request/Response models for design inputs generation
class DesignInputsGenerateRequest(BaseModel):
    component_name: str
    count: Optional[int] = 5

class DesignInputItem(BaseModel):
    title: str
    requirement: str
    description: Optional[str] = None

class DesignInputsGenerateResponse(BaseModel):
    design_inputs: List[DesignInputItem]

# Request/Response models for design outputs generation
class DesignOutputsGenerateRequest(BaseModel):
    component_name: str
    count: Optional[int] = 5

class DesignOutputItem(BaseModel):
    title: str
    specification: str
    description: Optional[str] = None

class DesignOutputsGenerateResponse(BaseModel):
    design_outputs: List[DesignOutputItem]

@router.post("/design-controls/generate", response_model=DesignControlsGenerateResponse)
async def generate_design_controls(
    request: DesignControlsGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate design inputs and outputs using AI"""
    # Verify project ownership first
    from crud import project as project_crud
    project = project_crud.get_project(db, request.project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    openai_api_key = _get_openai_api_key()
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        # Get FMEA rows for context
        from crud import fmea as fmea_crud
        from crud import component as component_crud
        from models.fmea import FMEARow
        
        risk_context = []
        if request.risk_ids:
            for risk_id in request.risk_ids:
                fmea_row = fmea_crud.get_fmea_row(db, risk_id, request.project_id)
                if fmea_row:
                    risk_context.append({
                        "failure_mode": fmea_row.failure_mode,
                        "effect": fmea_row.effect,
                        "cause": fmea_row.cause,
                        "severity": fmea_row.severity,
                        "probability": fmea_row.probability,
                        "detection": fmea_row.detection
                    })
        
        component_info = ""
        if request.component_id:
            component = component_crud.get_component(db, request.component_id, request.project_id)
            if component:
                component_info = f"Component: {component.name}, Description: {component.description}"
        
        prompt = f"{DESIGN_CONTROLS_PROMPT}\n\nComponent Info: {component_info}\n\nRisks: {json.dumps(risk_context)}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 for better quality
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        # Create design inputs and outputs in database
        from crud import design_control as dc_crud
        from crud import traceability as trace_crud
        from schemas.design_control import DesignInputCreate, DesignOutputCreate
        
        design_inputs = []
        design_outputs = []
        trace_links = []
        
        # Create design inputs
        for input_data in data.get("design_inputs", []):
            di_create = DesignInputCreate(
                project_id=request.project_id,
                source="ai",
                text=input_data.get("text", ""),
                linked_risk_ids=input_data.get("linked_risk_ids", [])
            )
            di = dc_crud.create_design_input(db, di_create, created_by=current_user.id)
            design_inputs.append(di)
            
            # Create trace links from risks to inputs
            for risk_id in di.linked_risk_ids or []:
                trace_crud.create_trace_link_bidirectional(
                    db, request.project_id, "risk", risk_id, "input", di.id
                )
        
        # Create design outputs
        for output_data in data.get("design_outputs", []):
            do_create = DesignOutputCreate(
                project_id=request.project_id,
                source="ai",
                text=output_data.get("text", ""),
                linked_input_id=output_data.get("linked_input_id")
            )
            do = dc_crud.create_design_output(db, do_create, created_by=current_user.id)
            design_outputs.append(do)
            
            # Create trace link from input to output
            if do.linked_input_id:
                trace_crud.create_trace_link_bidirectional(
                    db, request.project_id, "input", do.linked_input_id, "output", do.id
                )
        
        # Convert to proper schema objects
        from schemas.design_control import DesignInputOut, DesignOutputOut
        
        design_inputs_out = [
            DesignInputOut(
                id=di.id,
                project_id=di.project_id,
                source=di.source,
                text=di.text,
                linked_risk_ids=di.linked_risk_ids or [],
                created_at=di.created_at
            ) for di in design_inputs
        ]
        
        design_outputs_out = [
            DesignOutputOut(
                id=do.id,
                project_id=do.project_id,
                source=do.source,
                text=do.text,
                linked_input_id=do.linked_input_id,
                created_at=do.created_at
            ) for do in design_outputs
        ]
        
        # Collect all trace links created
        all_trace_links = []
        for di in design_inputs:
            for risk_id in (di.linked_risk_ids or []):
                all_trace_links.append({
                    "from_type": "risk",
                    "to_type": "input",
                    "from_id": risk_id,
                    "to_id": di.id
                })
        for do in design_outputs:
            if do.linked_input_id:
                all_trace_links.append({
                    "from_type": "input",
                    "to_type": "output",
                    "from_id": do.linked_input_id,
                    "to_id": do.id
                })
        
        return DesignControlsGenerateResponse(
            design_inputs=design_inputs_out,
            design_outputs=design_outputs_out,
            trace_links=all_trace_links
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/vv/generate", response_model=VVGenerateResponse)
async def generate_vv_test(
    request: VVGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate V&V test case using AI"""
    openai_api_key = _get_openai_api_key()
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        # Verify design output exists and user has access
        from crud import design_control as dc_crud
        from crud import project as project_crud
        from models.design_output import DesignOutput
        
        design_output = db.query(DesignOutput).filter(DesignOutput.id == request.design_output_id).first()
        if not design_output:
            raise HTTPException(status_code=404, detail="Design output not found")
        
        # Verify project ownership
        project = project_crud.get_project(db, design_output.project_id, current_user.id)
        if not project:
            raise HTTPException(status_code=403, detail="Access denied to this design output")
        prompt = f"{VV_PROMPT}\n\nDesign Output: {design_output.text}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return VVGenerateResponse(
            test_method=data.get("test_method", ""),
            acceptance_criteria=data.get("acceptance_criteria", ""),
            rationale=data.get("rationale", ""),
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/vv/generate-from-risk", response_model=VVFromRiskGenerateResponse)
async def generate_vv_from_risk(
    request: VVFromRiskGenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate risk-based V&V test logic from an FMEA/risk row. Loads API key when called and uses it to call OpenAI when set."""
    _ensure_openai_env_loaded()  # load ENV.local / .env so key is available when this endpoint is called
    openai_api_key = _get_openai_api_key()
    if not openai_api_key:
        return _stub_vv_from_risk_response(request)

    payload = request.to_payload()
    rpn = payload["severity"] * payload["occurrence"] * payload["detection"]
    risk_context = (
        f"Risk row:\n"
        f"  component: {payload['component']}\n"
        f"  failure_mode: {payload['failure_mode']}\n"
        f"  effect: {payload['effect']}\n"
        f"  cause: {payload['cause']}\n"
        f"  severity: {payload['severity']}, occurrence: {payload['occurrence']}, detection: {payload['detection']}\n"
        f"  RPN: {rpn}\n"
        f"  mitigation: {payload['mitigation'] or '(none)'}"
    )
    user_message = f"{VV_FROM_RISK_PROMPT}\n\n{risk_context}"

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
        )
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")

        data = json.loads(content)

        # Normalize acceptance_criteria to list
        ac = data.get("acceptance_criteria")
        if isinstance(ac, str):
            ac = [ac] if ac.strip() else []
        elif not isinstance(ac, list):
            ac = []

        # Normalize calculations to list; each item may have name, formula, description, inputs, unit_or_threshold
        calcs = data.get("calculations") or []
        if isinstance(calcs, dict):
            calcs = [calcs]
        calculations = []
        for c in calcs:
            if not isinstance(c, dict):
                continue
            inp = c.get("inputs")
            if isinstance(inp, str):
                inp = [inp] if inp.strip() else []
            elif not isinstance(inp, list):
                inp = []
            calculations.append(
                CalculationItem(
                    name=str(c.get("name", "")),
                    formula=str(c.get("formula", "")),
                    description=str(c.get("description", "")) or None,
                    inputs=inp or None,
                    unit_or_threshold=str(c.get("unit_or_threshold", "")) or None,
                )
            )

        # Normalize worst_case_conditions to list
        wcc = data.get("worst_case_conditions")
        if isinstance(wcc, str):
            wcc = [wcc] if wcc.strip() else []
        elif not isinstance(wcc, list):
            wcc = []

        # Traceability: always populate from request if model omits fields
        def _safe_int(v, default: int) -> int:
            if v is None:
                return default
            try:
                return int(v)
            except (TypeError, ValueError):
                return default

        def _opt_int(v) -> Optional[int]:
            if v is None:
                return None
            try:
                return int(v)
            except (TypeError, ValueError):
                return None

        trace = data.get("traceability") or {}
        if not isinstance(trace, dict):
            trace = {}
        traceability = TraceabilityBlock(
            source_component=str(trace.get("source_component") or payload["component"]),
            source_failure_mode=str(trace.get("source_failure_mode") or payload["failure_mode"]),
            source_mitigation=str(trace.get("source_mitigation") or payload.get("mitigation") or ""),
            source_effect=str(trace.get("source_effect") or payload.get("effect") or "").strip() or None,
            source_cause=str(trace.get("source_cause") or payload.get("cause") or "").strip() or None,
            source_severity=_safe_int(trace.get("source_severity"), payload["severity"]),
            source_occurrence=_safe_int(trace.get("source_occurrence"), payload["occurrence"]),
            source_detection=_safe_int(trace.get("source_detection"), payload["detection"]),
            source_rpn=_safe_int(trace.get("source_rpn"), rpn),
            source_residual_severity=_opt_int(payload.get("residual_severity") if payload.get("residual_severity") is not None else trace.get("source_residual_severity")),
            source_residual_occurrence=_opt_int(payload.get("residual_occurrence") if payload.get("residual_occurrence") is not None else trace.get("source_residual_occurrence")),
            source_residual_detection=_opt_int(payload.get("residual_detection") if payload.get("residual_detection") is not None else trace.get("source_residual_detection")),
            source_residual_rpn=_opt_int(payload.get("residual_rpn") if payload.get("residual_rpn") is not None else trace.get("source_residual_rpn")),
        )

        # Validation: prefer new fields, fallback to validation_scenario
        validation_method_or_scenario = (
            data.get("validation_method_or_scenario")
            or data.get("validation_scenario")
            or ""
        )

        return VVFromRiskGenerateResponse(
            verification_test_name=data.get("verification_test_name", "V&V Test"),
            verification_objective=data.get("verification_objective", ""),
            verification_method=data.get("verification_method", ""),
            validation_test_name=data.get("validation_test_name") or None,
            validation_objective=data.get("validation_objective") or None,
            validation_method_or_scenario=validation_method_or_scenario or None,
            validation_scenario=data.get("validation_scenario") or None,
            acceptance_criteria=ac,
            calculations=calculations,
            worst_case_conditions=wcc,
            sample_size_rationale=data.get("sample_size_rationale"),
            traceability=traceability,
        )
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/vv/save-from-risk", response_model=VVFromRiskSaveResponse, status_code=201)
async def save_vv_from_risk(
    request: VVFromRiskSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save generated V&V from risk to the project for traceability."""
    from crud import project as project_crud
    from models.generated_vv import GeneratedVVRecord

    project = project_crud.get_project(db, request.project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    calc_list = [
        {
            "name": c.name,
            "formula": c.formula,
            "description": getattr(c, "description", None),
            "inputs": getattr(c, "inputs", None) or [],
            "unit_or_threshold": getattr(c, "unit_or_threshold", None),
        }
        for c in request.calculations
    ]
    t = request.traceability
    trace = {
        "source_component": t.source_component,
        "source_failure_mode": t.source_failure_mode,
        "source_mitigation": t.source_mitigation,
        "source_effect": getattr(t, "source_effect", None),
        "source_cause": getattr(t, "source_cause", None),
        "source_severity": getattr(t, "source_severity", None),
        "source_occurrence": getattr(t, "source_occurrence", None),
        "source_detection": getattr(t, "source_detection", None),
        "source_rpn": getattr(t, "source_rpn", None),
        "source_residual_severity": getattr(t, "source_residual_severity", None),
        "source_residual_occurrence": getattr(t, "source_residual_occurrence", None),
        "source_residual_detection": getattr(t, "source_residual_detection", None),
        "source_residual_rpn": getattr(t, "source_residual_rpn", None),
    }
    validation_scenario_text = (
        request.validation_method_or_scenario
        or request.validation_scenario
        or None
    )
    record = GeneratedVVRecord(
        project_id=request.project_id,
        fmea_row_id=request.fmea_row_id,
        risk_item_id=request.risk_item_id,
        verification_test_name=request.verification_test_name,
        verification_objective=request.verification_objective or None,
        verification_method=request.verification_method or None,
        validation_test_name=request.validation_test_name or None,
        validation_objective=request.validation_objective or None,
        validation_scenario=validation_scenario_text,
        acceptance_criteria=request.acceptance_criteria or None,
        calculations=calc_list or None,
        worst_case_conditions=request.worst_case_conditions or None,
        sample_size_rationale=request.sample_size_rationale,
        traceability=trace,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return VVFromRiskSaveResponse(
        id=record.id,
        project_id=record.project_id,
        created_at=record.created_at,
    )


@router.post("/capa/generate", response_model=CAPAGenerateResponse)
async def generate_capa(
    request: CAPAGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate CAPA using AI"""
    openai_api_key = _get_openai_api_key()
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        # Get FMEA rows for context and verify access
        from crud import fmea as fmea_crud
        from crud import project as project_crud
        from models.fmea import FMEARow
        
        risk_context = []
        verified_project_ids = set()
        
        for risk_id in request.risk_ids:
            fmea_row = db.query(FMEARow).filter(FMEARow.id == risk_id).first()
            if fmea_row:
                # Verify project ownership
                project = project_crud.get_project(db, fmea_row.project_id, current_user.id)
                if not project:
                    raise HTTPException(status_code=403, detail=f"Access denied to risk {risk_id}")
                
                verified_project_ids.add(fmea_row.project_id)
                risk_context.append({
                    "failure_mode": fmea_row.failure_mode or request.failure_mode,
                    "effect": fmea_row.effect or request.effect,
                    "cause": fmea_row.cause or request.cause,
                    "severity": fmea_row.severity,
                    "probability": fmea_row.probability,
                    "detection": fmea_row.detection
                })
        
        prompt = f"{CAPA_PROMPT}\n\nRisk Data: {json.dumps(risk_context)}\n\nFailure Mode: {request.failure_mode or 'N/A'}\nEffect: {request.effect or 'N/A'}\nCause: {request.cause or 'N/A'}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return CAPAGenerateResponse(
            root_cause=data.get("root_cause", ""),
            capa_plan=data.get("capa_plan", ""),
            effectiveness_check=data.get("effectiveness_check", ""),
            linked_risk_ids=request.risk_ids,
            ai_metadata=data.get("ai_metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/pms/generate", response_model=PMSGenerateResponse)
async def generate_pms_assessment(
    request: PMSGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate PMS assessment using AI"""
    openai_api_key = _get_openai_api_key()
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        # Get FMEA rows for context and verify access
        from crud import fmea as fmea_crud
        from crud import project as project_crud
        from models.fmea import FMEARow
        
        risk_context = []
        if request.linked_risk_ids:
            for risk_id in request.linked_risk_ids:
                fmea_row = db.query(FMEARow).filter(FMEARow.id == risk_id).first()
                if fmea_row:
                    # Verify project ownership
                    project = project_crud.get_project(db, fmea_row.project_id, current_user.id)
                    if not project:
                        raise HTTPException(status_code=403, detail=f"Access denied to risk {risk_id}")
                    
                    risk_context.append({
                        "failure_mode": fmea_row.failure_mode,
                        "effect": fmea_row.effect,
                        "severity": fmea_row.severity,
                        "probability": fmea_row.probability,
                        "detection": fmea_row.detection,
                        "rpn": fmea_row.rpn
                    })
        
        prompt = f"{PMS_PROMPT}\n\nSignal Type: {request.signal_type}\nDescription: {request.description}\n\nLinked Risks: {json.dumps(risk_context)}"
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        return PMSGenerateResponse(
            updated_risk_scores=data.get("updated_risk_scores"),
            recommended_actions=data.get("recommended_actions", []),
            risk_trend_flag=data.get("risk_trend_flag"),
            metadata=data.get("metadata")
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/design-inputs/generate", response_model=DesignInputsGenerateResponse)
async def generate_design_inputs(
    request: DesignInputsGenerateRequest
):
    """Generate design inputs for a component using AI"""
    openai_api_key = _get_openai_api_key()
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        count = request.count or 5
        prompt = f"{DESIGN_INPUTS_PROMPT}\n\nComponent Name: {request.component_name}\n\nGenerate exactly {count} design inputs. Each design input should be specific, measurable, and relevant to medical device design control standards (ISO 13485, ISO 14971, IEC 60601-1).\n\nReturn a JSON object with a 'design_inputs' array containing {count} objects, each with 'title' and 'requirement' fields."
        
        client = openai.OpenAI(api_key=openai_api_key)
        # Try with gpt-4o first (supports json_object), fallback to gpt-3.5-turbo if needed
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
        except Exception as model_error:
            # Fallback to gpt-3.5-turbo without response_format if gpt-4o fails
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + " Return JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        data = json.loads(content)
        
        # Extract design inputs from response
        design_inputs_data = data.get("design_inputs", [])
        if not design_inputs_data or len(design_inputs_data) == 0:
            raise HTTPException(status_code=500, detail="AI did not generate any design inputs")
        
        # Ensure we have exactly the requested count (or at least 5)
        if len(design_inputs_data) < count:
            # If AI returned fewer than requested, pad with generic ones
            while len(design_inputs_data) < count:
                design_inputs_data.append({
                    "title": f"Design Input {len(design_inputs_data) + 1}",
                    "requirement": f"Additional design input requirement for {request.component_name}"
                })
        
        # Limit to requested count
        design_inputs_data = design_inputs_data[:count]
        
        design_inputs = [
            DesignInputItem(
                title=item.get("title", f"Design Input {i+1}"),
                requirement=item.get("requirement", item.get("description", "")),
                description=item.get("description")
            )
            for i, item in enumerate(design_inputs_data)
        ]
        
        return DesignInputsGenerateResponse(design_inputs=design_inputs)
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/design-outputs/generate", response_model=DesignOutputsGenerateResponse)
async def generate_design_outputs(
    request: DesignOutputsGenerateRequest
):
    """Generate design outputs for a component using AI"""
    openai_api_key = _get_openai_api_key()
    
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please configure OPENAI_API_KEY.")
    
    try:
        count = request.count or 5
        prompt = f"{DESIGN_OUTPUTS_PROMPT}\n\nComponent Name: {request.component_name}\n\nGenerate exactly {count} design outputs. Each design output should be specific, measurable, and relevant to medical device design control standards (ISO 13485, ISO 14971, IEC 60601-1). Design outputs should demonstrate that design requirements have been met.\n\nReturn a JSON object with a 'design_outputs' array containing {count} objects, each with 'title' and 'specification' fields."
        
        client = openai.OpenAI(api_key=openai_api_key)
        # Try with gpt-4o first (supports json_object), fallback to gpt-3.5-turbo if needed
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
        except Exception as model_error:
            # Fallback to gpt-3.5-turbo without response_format if gpt-4o fails
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + " Return JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned no content")
        
        # Extract JSON from response (handles both json_object format and text responses)
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # If direct JSON parsing fails, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise HTTPException(status_code=500, detail="Failed to parse AI response as JSON")
        
        # Extract design outputs from response
        design_outputs_data = data.get("design_outputs", [])
        if not design_outputs_data or len(design_outputs_data) == 0:
            raise HTTPException(status_code=500, detail="AI did not generate any design outputs")
        
        # Ensure we have exactly the requested count (or at least 5)
        if len(design_outputs_data) < count:
            # If AI returned fewer than requested, pad with generic ones
            while len(design_outputs_data) < count:
                design_outputs_data.append({
                    "title": f"Design Output {len(design_outputs_data) + 1}",
                    "specification": f"Design output specification for {request.component_name}"
                })
        
        # Limit to requested count
        design_outputs_data = design_outputs_data[:count]
        
        design_outputs = [
            DesignOutputItem(
                title=item.get("title", f"Design Output {i+1}"),
                specification=item.get("specification", item.get("description", "")),
                description=item.get("description")
            )
            for i, item in enumerate(design_outputs_data)
        ]
        
        return DesignOutputsGenerateResponse(design_outputs=design_outputs)
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

