from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas.design_control import DesignControlsGenerateRequest, DesignControlsGenerateResponse
from schemas.vv import VVGenerateRequest, VVGenerateResponse
from schemas.capa import CAPAGenerateRequest, CAPAGenerateResponse
from schemas.pms import PMSGenerateRequest, PMSGenerateResponse
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
import json
from pathlib import Path

router = APIRouter(prefix="/ai", tags=["AI Phase 2"])

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
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
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
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
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

@router.post("/capa/generate", response_model=CAPAGenerateResponse)
async def generate_capa(
    request: CAPAGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate CAPA using AI"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
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
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
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
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
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
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
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

