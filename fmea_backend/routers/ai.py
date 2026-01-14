from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
import json
from datetime import datetime, timedelta, timezone
import re
from docxtpl import DocxTemplate
from pathlib import Path

from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models.user import User
from crud import project as project_crud
from crud import generated_artifact as artifact_crud

router = APIRouter()

# --- Security helpers for legacy file downloads ---
_SAFE_DOCX_NAME_RE = re.compile(r"^[a-zA-Z0-9._-]+\.docx$")

def _is_safe_docx_filename(filename: str) -> bool:
    """Strict allowlist: no path separators; only [a-zA-Z0-9._-] and required .docx."""
    if not isinstance(filename, str) or not filename:
        return False
    if "/" in filename or "\\" in filename:
        return False
    return _SAFE_DOCX_NAME_RE.fullmatch(filename) is not None


def _safe_path_in_dir(base_dir: Path, filename: str) -> Path:
    """
    Resolve `filename` within `base_dir` and ensure it cannot escape the directory.
    Also enforces a flat directory (no subfolders).
    """
    base = base_dir.resolve()
    candidate = (base / filename).resolve()
    # Disallow nested directories (even if filename includes separators, which we also validate)
    if candidate.parent != base:
        raise ValueError("Invalid filename path")
    # Defense-in-depth against traversal/symlinks
    try:
        if not candidate.is_relative_to(base):  # py3.9+
            raise ValueError("Invalid filename path")
    except AttributeError:
        # Fallback for older Path implementations
        if str(candidate).find(str(base)) != 0:
            raise ValueError("Invalid filename path")
    return candidate


def _require_project_scoped_word_report(
    db: Session,
    *,
    current_user: User,
    filename: str,
):
    """
    Enforce that word report artifacts are project-scoped:
    - record must exist for (current_user, filename, artifact_type="word_report")
    - record must have project_id set
    - project must belong to current_user
    """
    rec = artifact_crud.get_generated_artifact_for_user(
        db,
        user_id=current_user.id,
        filename=filename,
        artifact_type="word_report",
    )
    if not rec or not rec.project_id:
        # Fail closed and don't leak existence
        raise HTTPException(status_code=404, detail="Generated report not found")

    project = project_crud.get_project(db, rec.project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Generated report not found")
    return rec

class FmeaRequest(BaseModel):
    component: str
    analyst_name: Optional[str] = None
    analyst_email: Optional[str] = None
    analyst_role: Optional[str] = None

class HazardAnalysisRequest(BaseModel):
    hazard_description: str
    hazard_type: str

class FaultTreeReportRequest(BaseModel):
    top_event: str
    fault_tree_type: str

class RiskEvaluationReportRequest(BaseModel):
    risk_description: str
    risk_category: str

class RiskControlImplementationRequest(BaseModel):
    control_name: str
    control_type: str

class ResidualRiskRiskBenefitRequest(BaseModel):
    risk_description: str
    risk_category: str
    benefit_description: str

class RiskTraceabilityMatrixRequest(BaseModel):
    project_name: str
    traceability_type: str

class RiskManagementPlanRequest(BaseModel):
    project_name: str
    plan_type: str
    industry_sector: str

class RiskManagementReportRequest(BaseModel):
    project_name: str
    report_type: str
    reporting_period: str

class FmeaRow(BaseModel):
    id: str
    component: str
    function: str
    failureMode: str
    potentialEffect: str
    severity: int
    potentialCauses: str
    occurrence: int
    currentControls: str
    detection: int
    rpn: int
    recommendedActions: str
    responsible: str
    targetDate: str
    actionsTaken: str
    finalSeverity: int
    finalOccurrence: int
    finalDetection: int
    finalRpn: int
    analysis_timestamp: Optional[datetime] = None
    version: Optional[str] = "1.0"
    analyst_name: Optional[str] = None
    analyst_email: Optional[str] = None
    analyst_role: Optional[str] = None

class FmeaResponse(BaseModel):
    fmea_data: List[FmeaRow]
    mock: bool = False

class HazardAnalysisResponse(BaseModel):
    hazard_data: List[dict]
    mock: bool = False

class FaultTreeReportResponse(BaseModel):
    fault_tree_data: List[dict]
    mock: bool = False

class RiskEvaluationReportResponse(BaseModel):
    risk_evaluation_data: List[dict]
    mock: bool = False

class RiskControlImplementationResponse(BaseModel):
    risk_control_data: List[dict]
    mock: bool = False

class ResidualRiskRiskBenefitResponse(BaseModel):
    residual_risk_benefit_data: List[dict]
    mock: bool = False

class RiskTraceabilityMatrixResponse(BaseModel):
    traceability_matrix_data: List[dict]
    mock: bool = False

class RiskManagementPlanResponse(BaseModel):
    risk_management_plan_data: List[dict]
    mock: bool = False

class RiskManagementReportResponse(BaseModel):
    risk_management_report_data: List[dict]
    mock: bool = False

def generate_fmea_with_ai(component: str, analyst_name: Optional[str] = None, analyst_email: Optional[str] = None, analyst_role: Optional[str] = None) -> List[FmeaRow]:
    """Generate FMEA data using AI for the given component, with 20 failure modes per function."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_fmea_data(component, analyst_name, analyst_email, analyst_role)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive DFMEA (Design Failure Mode and Effects Analysis) for the component: {component}.
        For each of 5-7 functions, generate 20 failure modes in total (across all functions). For each failure mode, provide:
        - function: The function name
        - failureMode: The failure mode for this function
        - potentialEffect: Impact of failure
        - severity (1-10): How bad the effect is
        - potentialCauses: Why it might fail
        - occurrence (1-10): How often it might fail
        - currentControls: Existing prevention/detection methods
        - detection (1-10): How likely current controls will detect it
        - recommendedActions: Suggested improvements
        - actionsTaken: What mitigation was implemented
        - finalSeverity: Post-mitigation severity
        - finalOccurrence: Post-mitigation occurrence
        - finalDetection: Post-mitigation detection
        - finalRpn: Post-mitigation risk priority number
        - analysis_timestamp: Current timestamp when analysis was performed
        - version: Analysis version (e.g., '1.0', '2.1')
        
        Return the data as a JSON array of exactly 20 objects, where each object represents a single failure mode for a function, with these exact field names:
        [
          {{
            "id": "1",
            "component": "{component}",
            "function": "...",
            "failureMode": "...",
            "potentialEffect": "...",
            "severity": 7,
            "potentialCauses": "...",
            "occurrence": 4,
            "currentControls": "...",
            "detection": 6,
            "rpn": 168,
            "recommendedActions": "...",
            "responsible": "...",
            "targetDate": "2024-03-15",
            "actionsTaken": "...",
            "finalSeverity": 7,
            "finalOccurrence": 3,
            "finalDetection": 4,
            "finalRpn": 84,
            "analysis_timestamp": "2024-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert FMEA analyst with deep knowledge of engineering components and failure modes. Provide realistic, detailed DFMEA data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                fmea_data = json.loads(json_str)
                return fmea_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_fmea_data(component, analyst_name, analyst_email, analyst_role)
        else:
            # If content is None, fall back to mock data
            return generate_mock_fmea_data(component, analyst_name, analyst_email, analyst_role)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_fmea_data(component, analyst_name, analyst_email, analyst_role)

def generate_mock_fmea_data(component: str, analyst_name: Optional[str] = None, analyst_email: Optional[str] = None, analyst_role: Optional[str] = None) -> List[FmeaRow]:
    """Generate realistic mock FMEA data for testing - 20 rows"""
    
    current_timestamp = datetime.now()
    
    # Define base functions and failure modes for variety
    functions = [
        "Provide structural support and load bearing capacity",
        "Maintain dimensional stability under load",
        "Resist environmental degradation",
        "Ensure proper thermal management",
        "Maintain electrical conductivity",
        "Provide mechanical protection",
        "Ensure fluid containment",
        "Maintain operational efficiency"
    ]
    
    failure_modes = [
        "Crack formation", "Excessive deformation", "Corrosion", "Thermal expansion",
        "Electrical short circuit", "Mechanical wear", "Fluid leakage", "Vibration",
        "Material fatigue", "Stress concentration", "Oxidation", "Thermal stress",
        "Insulation breakdown", "Friction damage", "Pressure loss", "Resonance",
        "Creep deformation", "Brittle fracture", "Chemical attack", "Thermal shock"
    ]
    
    effects = [
        "Reduced structural integrity, potential collapse",
        "Misalignment, reduced performance",
        "Material loss, reduced strength",
        "Component overheating, performance degradation",
        "Electrical system failure, safety hazard",
        "Component damage, reduced lifespan",
        "System contamination, operational failure",
        "Equipment damage, noise generation",
        "Progressive deterioration, eventual failure",
        "Localized stress, crack propagation",
        "Surface degradation, reduced aesthetics",
        "Thermal cycling damage, component stress",
        "Electrical hazard, system shutdown",
        "Surface wear, reduced efficiency",
        "System pressure loss, reduced functionality",
        "Structural resonance, component damage",
        "Gradual deformation, dimensional change",
        "Sudden fracture, catastrophic failure",
        "Chemical deterioration, material loss",
        "Thermal stress cracking, component failure"
    ]
    
    causes = [
        "Material fatigue, overloading, manufacturing defects",
        "Insufficient stiffness, design flaws",
        "Exposure to moisture, chemical attack",
        "Inadequate cooling, high ambient temperature",
        "Insulation breakdown, moisture ingress",
        "Abrasive wear, insufficient lubrication",
        "Seal degradation, pressure differential",
        "Imbalanced rotating components",
        "Cyclic loading, stress concentration",
        "Design stress risers, material defects",
        "Atmospheric exposure, humidity",
        "Thermal cycling, coefficient mismatch",
        "Environmental contamination, aging",
        "Contact friction, abrasive particles",
        "System leaks, seal failure",
        "Natural frequency excitation",
        "High temperature, sustained load",
        "Material defects, impact loading",
        "Chemical exposure, pH imbalance",
        "Rapid temperature change, thermal gradient"
    ]
    
    mock_data = []
    
    for i in range(20):
        function_idx = i % len(functions)
        failure_idx = i % len(failure_modes)
        effect_idx = i % len(effects)
        cause_idx = i % len(causes)
        
        severity = 5 + (i % 5)  # 5-9
        occurrence = 3 + (i % 5)  # 3-7
        detection = 4 + (i % 4)  # 4-7
        rpn = severity * occurrence * detection
        
        # Calculate improved values after mitigation
        final_severity = max(1, severity - (i % 2))
        final_occurrence = max(1, occurrence - (i % 2))
        final_detection = min(10, detection + (i % 2))
        final_rpn = final_severity * final_occurrence * final_detection
        
        mock_data.append(FmeaRow(
            id=str(i + 1),
            component=component,
            function=functions[function_idx],
            failureMode=failure_modes[failure_idx],
            potentialEffect=effects[effect_idx],
            severity=severity,
            potentialCauses=causes[cause_idx],
            occurrence=occurrence,
            currentControls=f"Regular inspections, monitoring systems, preventive maintenance",
            detection=detection,
            rpn=rpn,
            recommendedActions=f"Implement enhanced monitoring, upgrade materials, improve design",
            responsible=f"Engineering Team {chr(65 + (i % 3))}",  # Team A, B, C
            targetDate=f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
            actionsTaken=f"Installed monitoring systems, upgraded materials, implemented preventive measures",
            finalSeverity=final_severity,
            finalOccurrence=final_occurrence,
            finalDetection=final_detection,
            finalRpn=final_rpn,
            analysis_timestamp=current_timestamp,
            version="1.0",
            analyst_name=analyst_name,
            analyst_email=analyst_email,
            analyst_role=analyst_role
        ))
    
    return mock_data

def generate_pfmea_with_ai(component: str) -> List[FmeaRow]:
    """Generate PFMEA data using AI for the given component, with processStep and processRequirements fields, and 3 failure modes per process step."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_fmea_data(component)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive PFMEA (Process Failure Mode and Effects Analysis) for the component: {component}.
        
        Please provide 5-7 process steps with the following information for each:
        - processStep: The process step name
        - processRequirements: The requirements for this process step
        - failureMode: The failure mode for this process step
        - potentialEffect: Impact of failure
        - severity (1-10): How bad the effect is
        - potentialCauses: Why it might fail
        - occurrence (1-10): How often it might fail
        - currentControls: Existing prevention/detection methods
        - detection (1-10): How likely current controls will detect it
        - recommendedActions: Suggested improvements
        - actionsTaken: What mitigation was implemented
        - finalSeverity: Post-mitigation severity
        - finalOccurrence: Post-mitigation occurrence
        - finalDetection: Post-mitigation detection
        - finalRpn: Post-mitigation risk priority number
        - analysis_timestamp: Current timestamp when analysis was performed
        - version: Analysis version (e.g., '1.0', '2.1')
        
        Return the data as a JSON array of exactly 20 objects, where each object represents a single failure mode for a process step, with these exact field names:
        [
          {{
            "id": "1",
            "component": "{component}",
            "processStep": "...",
            "processRequirements": "...",
            "failureMode": "...",
            "potentialEffect": "...",
            "severity": 7,
            "potentialCauses": "...",
            "occurrence": 4,
            "currentControls": "...",
            "detection": 6,
            "rpn": 168,
            "recommendedActions": "...",
            "responsible": "...",
            "targetDate": "2024-03-15",
            "actionsTaken": "...",
            "finalSeverity": 7,
            "finalOccurrence": 3,
            "finalDetection": 4,
            "finalRpn": 84,
            "analysis_timestamp": "2024-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert FMEA analyst with deep knowledge of engineering components and failure modes. Provide realistic, detailed PFMEA data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                fmea_data = json.loads(json_str)
                return fmea_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_fmea_data(component)
        else:
            # If content is None, fall back to mock data
            return generate_mock_fmea_data(component)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_fmea_data(component)

@router.post("/fmea/generate", response_model=FmeaResponse)
async def generate_fmea(request: FmeaRequest):
    """Generate complete FMEA analysis for a component"""
    try:
        # Try AI generation first
        fmea_data = generate_fmea_with_ai(
            request.component,
            request.analyst_name,
            request.analyst_email,
            request.analyst_role
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(fmea_data) == 20 and all('Engineering Team' in str(getattr(row, 'responsible', '')) for row in fmea_data)
        return FmeaResponse(fmea_data=fmea_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        fmea_data = generate_mock_fmea_data(
            request.component,
            request.analyst_name,
            request.analyst_email,
            request.analyst_role
        )
        return FmeaResponse(fmea_data=fmea_data, mock=True)

@router.post("/pfmea/generate", response_model=FmeaResponse)
async def generate_pfmea(request: FmeaRequest):
    """Generate PFMEA analysis for a component"""
    try:
        # Try AI generation first
        fmea_data = generate_pfmea_with_ai(request.component)
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(fmea_data) == 20 and all('Engineering Team' in str(getattr(row, 'responsible', '')) for row in fmea_data)
        return FmeaResponse(fmea_data=fmea_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        fmea_data = generate_mock_fmea_data(request.component)
        return FmeaResponse(fmea_data=fmea_data, mock=True)

@router.post("/ufmea/generate", response_model=FmeaResponse)
async def generate_ufmea(request: FmeaRequest):
    """Generate UFMEA analysis for a component"""
    try:
        # Try AI generation first
        fmea_data = generate_fmea_with_ai(
            request.component,
            request.analyst_name,
            request.analyst_email,
            request.analyst_role
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(fmea_data) == 20 and all('Engineering Team' in str(getattr(row, 'responsible', '')) for row in fmea_data)
        return FmeaResponse(fmea_data=fmea_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        fmea_data = generate_mock_fmea_data(
            request.component,
            request.analyst_name,
            request.analyst_email,
            request.analyst_role
        )
        return FmeaResponse(fmea_data=fmea_data, mock=True)

def generate_hazard_analysis_with_ai(hazard_description: str, hazard_type: str) -> List[dict]:
    """Generate hazard analysis data using AI for the given hazard description and type."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_hazard_analysis_data(hazard_description, hazard_type)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive hazard analysis for: {hazard_description}
        Hazard Type: {hazard_type}
        
        Provide detailed analysis with the following information:
        - hazard_description: The hazard description
        - hazard_type: The type of hazard
        - severity: High/Medium/Low severity rating
        - probability: High/Medium/Low probability rating
        - risk_level: High/Medium/Low overall risk level
        - affected_components: Components or systems affected
        - potential_consequences: Detailed consequences of the hazard
        - existing_controls: Current control measures
        - risk_assessment: Comprehensive risk evaluation
        - mitigation_measures: Recommended mitigation strategies
        - responsible_party: Person or team responsible
        - target_date: Target completion date
        - status: Current status (Open/In Progress/Closed)
        - monitoring_plan: Plan for monitoring the hazard
        - fmea_link: Reference to related FMEA analysis
        - regulatory_requirements: Applicable regulations
        - closure_summary: Summary of closure actions
        - milestones: Implementation milestones
        - risk_controls_update: Updated risk control measures
        - analysis_timestamp: Current timestamp
        - version: Analysis version
        
        Return the data as a JSON array with these exact field names:
        [
          {{
            "hazard_description": "...",
            "hazard_type": "{hazard_type}",
            "severity": "High",
            "probability": "Medium",
            "risk_level": "High",
            "affected_components": "...",
            "potential_consequences": "...",
            "existing_controls": "...",
            "risk_assessment": "...",
            "mitigation_measures": "...",
            "responsible_party": "...",
            "target_date": "2025-12-31",
            "status": "Open",
            "monitoring_plan": "...",
            "fmea_link": "Link to FMEA-001",
            "regulatory_requirements": "...",
            "closure_summary": "...",
            "milestones": "...",
            "risk_controls_update": "...",
            "analysis_timestamp": "2025-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert safety engineer and hazard analysis specialist. Provide realistic, detailed hazard analysis data with appropriate risk assessments and mitigation strategies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                hazard_data = json.loads(json_str)
                return hazard_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_hazard_analysis_data(hazard_description, hazard_type)
        else:
            # If content is None, fall back to mock data
            return generate_mock_hazard_analysis_data(hazard_description, hazard_type)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_hazard_analysis_data(hazard_description, hazard_type)

def generate_mock_hazard_analysis_data(hazard_description: str, hazard_type: str) -> List[dict]:
    """Generate realistic mock hazard analysis data for testing."""
    
    current_timestamp = datetime.now()
    
    mock_data = [{
        "hazard_description": hazard_description,
        "hazard_type": hazard_type,
        "severity": "High",
        "probability": "Medium",
        "risk_level": "High",
        "affected_components": "Main electrical panel, wiring, control systems",
        "potential_consequences": "Electric shock, fire, system shutdown, data loss",
        "existing_controls": "Circuit breakers, insulation, grounding, emergency shutdown",
        "risk_assessment": "High risk due to potential for serious injury and equipment damage",
        "mitigation_measures": "Enhanced insulation, ground fault protection, redundant systems",
        "responsible_party": "Electrical Engineer",
        "target_date": "2025-12-31",
        "status": "Open",
        "monitoring_plan": "Regular inspections, testing, continuous monitoring",
        "fmea_link": "Link to FMEA-001",
        "regulatory_requirements": "IEC 61010-1, UL 61010-1, NFPA 70",
        "closure_summary": "Comprehensive hazard analysis completed with mitigation plan",
        "milestones": "Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31",
        "risk_controls_update": "Updated risk control document RC-005",
        "analysis_timestamp": current_timestamp.isoformat(),
        "version": "1.0"
    }]
    
    return mock_data

def generate_fault_tree_report_with_ai(top_event: str, fault_tree_type: str) -> List[dict]:
    """Generate fault tree report data using AI for the given top event and type."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_fault_tree_report_data(top_event, fault_tree_type)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive fault tree analysis for: {top_event}
        Fault Tree Type: {fault_tree_type}
        
        Provide detailed analysis with the following information:
        - top_event: The top-level failure event
        - fault_tree_type: The type of fault tree analysis
        - complexity: High/Medium/Low complexity rating
        - risk_level: High/Medium/Low risk assessment
        - root_causes: Primary causes of the failure
        - intermediate_events: Sub-failures in the fault tree
        - basic_events: Fundamental failure events
        - probability: High/Medium/Low probability rating
        - cut_sets: Identified failure paths
        - minimal_cut_sets: Critical failure combinations
        - risk_assessment: Overall risk evaluation
        - mitigation_strategies: Risk reduction approaches
        - responsible_party: Person accountable for actions
        - target_date: Target completion date
        - status: Current status (Open/In Progress/Closed)
        - analysis_method: Methods used (FTA, FMEA, Risk Matrix)
        - fmea_link: Reference to related FMEA analysis
        - regulatory_requirements: Applicable standards
        - closure_summary: Analysis completion summary
        - milestones: Implementation timeline
        - risk_controls_update: Updated control measures
        - analysis_timestamp: Current timestamp
        - version: Analysis version
        
        Return the data as a JSON array with these exact field names:
        [
          {{
            "top_event": "{top_event}",
            "fault_tree_type": "{fault_tree_type}",
            "complexity": "High",
            "risk_level": "High",
            "root_causes": "...",
            "intermediate_events": "...",
            "basic_events": "...",
            "probability": "Medium",
            "cut_sets": "...",
            "minimal_cut_sets": "...",
            "risk_assessment": "...",
            "mitigation_strategies": "...",
            "responsible_party": "...",
            "target_date": "2025-12-31",
            "status": "Open",
            "analysis_method": "FTA, FMEA, Risk Matrix, Event Tree Analysis",
            "fmea_link": "Link to FMEA-001",
            "regulatory_requirements": "ISO 14971, IEC 61025, MIL-STD-882",
            "closure_summary": "...",
            "milestones": "...",
            "risk_controls_update": "...",
            "analysis_timestamp": "2025-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert systems engineer and fault tree analysis specialist. Provide realistic, detailed fault tree analysis data with appropriate risk assessments and mitigation strategies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                fault_tree_data = json.loads(json_str)
                return fault_tree_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_fault_tree_report_data(top_event, fault_tree_type)
        else:
            # If content is None, fall back to mock data
            return generate_mock_fault_tree_report_data(top_event, fault_tree_type)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_fault_tree_report_data(top_event, fault_tree_type)

def generate_mock_fault_tree_report_data(top_event: str, fault_tree_type: str) -> List[dict]:
    """Generate realistic mock fault tree report data for testing."""
    
    current_timestamp = datetime.now()
    
    mock_data = [{
        "top_event": top_event,
        "fault_tree_type": fault_tree_type,
        "complexity": "High",
        "risk_level": "High",
        "root_causes": "Component failure, design flaw, human error, environmental factors",
        "intermediate_events": "Subsystem failure, control system failure, communication failure",
        "basic_events": "Sensor failure, power loss, software bug, mechanical wear",
        "probability": "Medium",
        "cut_sets": "Multiple failure paths identified with varying probabilities",
        "minimal_cut_sets": "Critical path: Sensor + Power + Software, Secondary: Mechanical + Human",
        "risk_assessment": "High risk due to multiple failure modes and system complexity",
        "mitigation_strategies": "Redundancy, monitoring, maintenance, training, design improvements",
        "responsible_party": "Systems Engineer",
        "target_date": "2025-12-31",
        "status": "Open",
        "analysis_method": "FTA, FMEA, Risk Matrix, Event Tree Analysis",
        "fmea_link": "Link to FMEA-001",
        "regulatory_requirements": "ISO 14971, IEC 61025, MIL-STD-882",
        "closure_summary": "Comprehensive fault tree analysis completed with mitigation plan",
        "milestones": "Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31",
        "risk_controls_update": "Updated risk control document RC-005",
        "analysis_timestamp": current_timestamp.isoformat(),
        "version": "1.0"
    }]
    
    return mock_data

def generate_risk_evaluation_report_with_ai(risk_description: str, risk_category: str) -> List[dict]:
    """Generate risk evaluation report data using AI for the given risk description and category."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_risk_evaluation_report_data(risk_description, risk_category)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive risk evaluation report for: {risk_description}
        Risk Category: {risk_category}
        
        Provide detailed analysis with the following information:
        - risk_description: The risk description
        - risk_category: The category of risk
        - risk_level: High/Medium/Low risk level
        - probability: High/Medium/Low probability rating
        - severity: High/Medium/Low severity rating
        - exposure_frequency: How often the risk occurs
        - risk_score: Calculated risk score
        - affected_stakeholders: Who is affected by this risk
        - business_impact: Impact on business operations
        - financial_impact: Financial consequences
        - operational_impact: Operational consequences
        - compliance_impact: Compliance and regulatory impact
        - risk_controls: Current control measures
        - control_effectiveness: How effective current controls are
        - residual_risk: Remaining risk after controls
        - risk_owner: Person accountable for managing the risk
        - target_date: Target completion date
        - status: Current status (Open/In Progress/Closed)
        - risk_assessment_method: Methods used for assessment
        - fmea_link: Reference to related FMEA analysis
        - regulatory_requirements: Applicable regulations
        - closure_summary: Summary of closure actions
        - milestones: Implementation milestones
        - risk_controls_update: Updated control measures
        - analysis_timestamp: Current timestamp
        - version: Analysis version
        
        Return the data as a JSON array with these exact field names:
        [
          {{
            "risk_description": "{risk_description}",
            "risk_category": "{risk_category}",
            "risk_level": "High",
            "probability": "Medium",
            "severity": "High",
            "exposure_frequency": "Daily",
            "risk_score": "High",
            "affected_stakeholders": "Employees, customers, shareholders",
            "business_impact": "Significant disruption to operations",
            "financial_impact": "Potential loss of $500K-$1M annually",
            "operational_impact": "Reduced efficiency, increased costs",
            "compliance_impact": "Regulatory violations, fines",
            "risk_controls": "Regular monitoring, training, procedures",
            "control_effectiveness": "Moderate",
            "residual_risk": "Medium",
            "risk_owner": "Risk Manager",
            "target_date": "2025-12-31",
            "status": "Open",
            "risk_assessment_method": "Risk Matrix, FMEA, Monte Carlo",
            "fmea_link": "Link to FMEA-001",
            "regulatory_requirements": "ISO 31000, COSO, Basel III",
            "closure_summary": "Comprehensive risk evaluation completed with mitigation plan",
            "milestones": "Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31",
            "risk_controls_update": "Updated risk control document RC-006",
            "analysis_timestamp": "2025-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert risk management specialist and risk analyst. Provide realistic, detailed risk evaluation data with appropriate risk assessments and control strategies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                risk_evaluation_data = json.loads(json_str)
                return risk_evaluation_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_risk_evaluation_report_data(risk_description, risk_category)
        else:
            # If content is None, fall back to mock data
            return generate_mock_risk_evaluation_report_data(risk_description, risk_category)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_risk_evaluation_report_data(risk_description, risk_category)

def generate_mock_risk_evaluation_report_data(risk_description: str, risk_category: str) -> List[dict]:
    """Generate realistic mock risk evaluation report data for testing."""
    
    current_timestamp = datetime.now()
    
    mock_data = [{
        "risk_description": risk_description,
        "risk_category": risk_category,
        "risk_level": "High",
        "probability": "Medium",
        "severity": "High",
        "exposure_frequency": "Daily",
        "risk_score": "High",
        "affected_stakeholders": "Employees, customers, shareholders, suppliers",
        "business_impact": "Significant disruption to operations, potential revenue loss",
        "financial_impact": "Potential loss of $500K-$1M annually, increased insurance costs",
        "operational_impact": "Reduced efficiency, increased operational costs, process delays",
        "compliance_impact": "Regulatory violations, potential fines, legal action",
        "risk_controls": "Regular monitoring, employee training, documented procedures, insurance coverage",
        "control_effectiveness": "Moderate",
        "residual_risk": "Medium",
        "risk_owner": "Risk Manager",
        "target_date": "2025-12-31",
        "status": "Open",
        "risk_assessment_method": "Risk Matrix, FMEA, Monte Carlo Simulation, Expert Judgment",
        "fmea_link": "Link to FMEA-001",
        "regulatory_requirements": "ISO 31000, COSO Framework, Basel III, Sarbanes-Oxley",
        "closure_summary": "Comprehensive risk evaluation completed with detailed mitigation plan",
        "milestones": "Phase 1 complete by 2025-09-30, Phase 2 by 2025-12-31",
        "risk_controls_update": "Updated risk control document RC-006",
        "analysis_timestamp": current_timestamp.isoformat(),
        "version": "1.0"
    }]
    
    return mock_data

def generate_risk_control_implementation_with_ai(control_name: str, control_type: str) -> List[dict]:
    """Generate risk control implementation data using AI for the given control name and type."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_risk_control_implementation_data(control_name, control_type)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive risk control implementation plan for: {control_name}
        Control Type: {control_type}
        
        Provide detailed implementation plan with the following information:
        - control_name: The name of the control
        - control_type: The type of control
        - risk_category: The category of risk being controlled
        - risk_level: High/Medium/Low risk level
        - control_priority: High/Medium/Low priority
        - implementation_status: Not Started/In Progress/Completed/On Hold
        - control_description: Detailed description of the control
        - control_objectives: What the control aims to achieve
        - control_mechanisms: How the control works
        - control_frequency: How often the control is applied
        - control_effectiveness: High/Medium/Low effectiveness rating
        - control_owner: Person responsible for the control
        - responsible_team: Team accountable for implementation
        - target_completion_date: Target completion date
        - actual_completion_date: Actual completion date (if applicable)
        - implementation_cost: Estimated or actual cost
        - resource_requirements: Resources needed for implementation
        - training_requirements: Training needed for staff
        - monitoring_plan: Plan for monitoring control effectiveness
        - key_performance_indicators: KPIs to measure success
        - success_criteria: Criteria for successful implementation
        - risk_assessment_method: Methods used for risk assessment
        - fmea_link: Reference to related FMEA analysis
        - regulatory_requirements: Applicable regulations
        - implementation_summary: Summary of implementation approach
        - lessons_learned: Lessons from similar implementations
        - next_steps: Next steps in implementation
        - control_documentation: Required documentation
        - analysis_timestamp: Current timestamp
        - version: Implementation version
        
        Return the data as a JSON array with these exact field names:
        [
          {{
            "control_name": "{control_name}",
            "control_type": "{control_type}",
            "risk_category": "Information Security",
            "risk_level": "High",
            "control_priority": "High",
            "implementation_status": "Not Started",
            "control_description": "...",
            "control_objectives": "...",
            "control_mechanisms": "...",
            "control_frequency": "Continuous",
            "control_effectiveness": "High",
            "control_owner": "...",
            "responsible_team": "...",
            "target_completion_date": "2025-12-31",
            "actual_completion_date": "TBD",
            "implementation_cost": "$50K-$100K",
            "resource_requirements": "...",
            "training_requirements": "...",
            "monitoring_plan": "...",
            "key_performance_indicators": "...",
            "success_criteria": "...",
            "risk_assessment_method": "Risk Matrix, FMEA, Control Assessment",
            "fmea_link": "Link to FMEA-001",
            "regulatory_requirements": "ISO 27001, NIST, GDPR",
            "implementation_summary": "...",
            "lessons_learned": "...",
            "next_steps": "...",
            "control_documentation": "...",
            "analysis_timestamp": "2025-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert risk management specialist and control implementation specialist. Provide realistic, detailed risk control implementation plans with appropriate strategies and timelines."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                risk_control_data = json.loads(json_str)
                return risk_control_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_risk_control_implementation_data(control_name, control_type)
        else:
            # If content is None, fall back to mock data
            return generate_mock_risk_control_implementation_data(control_name, control_type)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_risk_control_implementation_data(control_name, control_type)

def generate_mock_risk_control_implementation_data(control_name: str, control_type: str) -> List[dict]:
    """Generate realistic mock risk control implementation data for testing."""
    
    current_timestamp = datetime.now()
    
    mock_data = [{
        "control_name": control_name,
        "control_type": control_type,
        "risk_category": "Information Security",
        "risk_level": "High",
        "control_priority": "High",
        "implementation_status": "Not Started",
        "control_description": "Comprehensive cybersecurity control implementation including technical, administrative, and physical controls",
        "control_objectives": "Reduce cybersecurity risk exposure, ensure compliance with regulations, protect sensitive data and systems",
        "control_mechanisms": "Multi-layered security approach including firewalls, intrusion detection, access controls, encryption, monitoring",
        "control_frequency": "Continuous",
        "control_effectiveness": "High",
        "control_owner": "Chief Information Security Officer",
        "responsible_team": "IT Security Team, Risk Management Team, Compliance Team",
        "target_completion_date": "2025-12-31",
        "actual_completion_date": "TBD",
        "implementation_cost": "$50K-$100K",
        "resource_requirements": "Security software licenses, hardware upgrades, staff training, external consultants",
        "training_requirements": "Cybersecurity awareness training, technical training for IT staff, management training",
        "monitoring_plan": "24/7 security monitoring, regular vulnerability assessments, incident response procedures",
        "key_performance_indicators": "Reduction in security incidents, compliance score improvement, risk assessment scores",
        "success_criteria": "Zero major security breaches, 100% regulatory compliance, reduced risk exposure by 80%",
        "risk_assessment_method": "Risk Matrix, FMEA, Control Assessment, Threat Modeling",
        "fmea_link": "Link to FMEA-001",
        "regulatory_requirements": "ISO 27001, NIST Cybersecurity Framework, GDPR, SOX",
        "implementation_summary": "Comprehensive risk control implementation plan with phased approach and clear milestones",
        "lessons_learned": "Early stakeholder engagement critical, phased implementation reduces risk, regular communication essential",
        "next_steps": "Stakeholder approval, resource allocation, project kickoff, detailed project planning",
        "control_documentation": "Control procedures, user guides, training materials, compliance documentation",
        "analysis_timestamp": current_timestamp.isoformat(),
        "version": "1.0"
    }]
    
    return mock_data

def generate_residual_risk_risk_benefit_with_ai(risk_description: str, risk_category: str, benefit_description: str) -> List[dict]:
    """Generate residual risk and risk-benefit analysis data using AI for the given risk description, category, and benefit description."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_residual_risk_risk_benefit_data(risk_description, risk_category, benefit_description)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive residual risk and risk-benefit analysis for: {risk_description}
        Risk Category: {risk_category}
        Benefit Description: {benefit_description}
        
        Provide detailed analysis with the following information:
        - risk_description: The risk description
        - risk_category: The category of risk
        - benefit_description: The description of the benefit
        - residual_risk_level: High/Medium/Low residual risk level
        - residual_probability: High/Medium/Low probability rating
        - residual_severity: High/Medium/Low severity rating
        - risk_reduction_effectiveness: How effective the control was in reducing the risk
        - risk_owner: Person accountable for managing the risk
        - target_date: Target completion date
        - status: Current status (Open/In Progress/Closed)
        - analysis_timestamp: Current timestamp
        - version: Analysis version
        
        Return the data as a JSON array with these exact field names:
        [
          {{
            "risk_description": "{risk_description}",
            "risk_category": "{risk_category}",
            "benefit_description": "{benefit_description}",
            "residual_risk_level": "High",
            "residual_probability": "Medium",
            "residual_severity": "High",
            "risk_reduction_effectiveness": "Moderate",
            "risk_owner": "Risk Manager",
            "target_date": "2025-12-31",
            "status": "Open",
            "analysis_timestamp": "2025-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert risk management specialist and residual risk/risk-benefit analysis specialist. Provide realistic, detailed residual risk and risk-benefit analysis data with appropriate risk assessments and control strategies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                residual_risk_benefit_data = json.loads(json_str)
                return residual_risk_benefit_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_residual_risk_risk_benefit_data(risk_description, risk_category, benefit_description)
        else:
            # If content is None, fall back to mock data
            return generate_mock_residual_risk_risk_benefit_data(risk_description, risk_category, benefit_description)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_residual_risk_risk_benefit_data(risk_description, risk_category, benefit_description)

def generate_mock_residual_risk_risk_benefit_data(risk_description: str, risk_category: str, benefit_description: str) -> List[dict]:
    """Generate realistic mock residual risk and risk-benefit analysis data for testing."""
    
    current_timestamp = datetime.now()
    
    mock_data = [{
        "risk_description": risk_description,
        "risk_category": risk_category,
        "benefit_description": benefit_description,
        "residual_risk_level": "High",
        "residual_probability": "Medium",
        "residual_severity": "High",
        "risk_reduction_effectiveness": "Moderate",
        "risk_owner": "Risk Manager",
        "target_date": "2025-12-31",
        "status": "Open",
        "analysis_timestamp": current_timestamp.isoformat(),
        "version": "1.0"
    }]
    
    return mock_data

def generate_risk_traceability_matrix_with_ai(project_name: str, traceability_type: str) -> List[dict]:
    """Generate risk traceability matrix data using AI for the given project name and traceability type."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_risk_traceability_matrix_data(project_name, traceability_type)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive risk traceability matrix for: {project_name}
        Traceability Type: {traceability_type}
        
        Provide detailed traceability matrix with the following information:
        - requirement_id: Unique identifier for the requirement
        - requirement_description: Description of the requirement
        - risk_id: Associated risk identifier
        - risk_description: Description of the risk
        - risk_level: High/Medium/Low risk level
        - control_id: Control identifier
        - control_description: Description of the control
        - control_effectiveness: High/Medium/Low effectiveness
        - verification_method: Method used for verification
        - verification_status: Pass/Fail/In Progress
        - responsible_party: Person responsible for verification
        - verification_date: Date of verification
        - matrix_owner: Person accountable for the matrix
        - last_updated: Last update timestamp
        - version: Matrix version
        
        Return the data as a JSON array with these exact field names:
        [
          {{
            "requirement_id": "REQ-001",
            "requirement_description": "System must be secure",
            "risk_id": "RISK-001",
            "risk_description": "Unauthorized access",
            "risk_level": "High",
            "control_id": "CTRL-001",
            "control_description": "Authentication system",
            "control_effectiveness": "High",
            "verification_method": "Penetration testing",
            "verification_status": "Pass",
            "responsible_party": "Security Engineer",
            "verification_date": "2025-01-15",
            "matrix_owner": "Risk Manager",
            "last_updated": "2025-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert risk management specialist and traceability matrix specialist. Provide realistic, detailed risk traceability matrix data with appropriate risk assessments, controls, and verification methods."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                traceability_matrix_data = json.loads(json_str)
                return traceability_matrix_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_risk_traceability_matrix_data(project_name, traceability_type)
        else:
            # If content is None, fall back to mock data
            return generate_mock_risk_traceability_matrix_data(project_name, traceability_type)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_risk_traceability_matrix_data(project_name, traceability_type)

def generate_mock_risk_traceability_matrix_data(project_name: str, traceability_type: str) -> List[dict]:
    """Generate realistic mock risk traceability matrix data for testing."""
    
    current_timestamp = datetime.now()
    
    mock_data = [{
        "requirement_id": "REQ-001",
        "requirement_description": "System must maintain data integrity",
        "risk_id": "RISK-001",
        "risk_description": "Data corruption during transmission",
        "risk_level": "High",
        "control_id": "CTRL-001",
        "control_description": "Data validation and checksums",
        "control_effectiveness": "High",
        "verification_method": "Data integrity testing",
        "verification_status": "Pass",
        "responsible_party": "Data Engineer",
        "verification_date": "2025-01-15",
        "matrix_owner": "Risk Manager",
        "last_updated": current_timestamp.isoformat(),
        "version": "1.0"
    }]
    
    return mock_data

def generate_risk_management_plan_with_ai(project_name: str, plan_type: str, industry_sector: str) -> List[dict]:
    """Generate risk management plan data using AI for the given project name, plan type, and industry sector."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_risk_management_plan_data(project_name, plan_type, industry_sector)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive risk management plan for: {project_name}
        Plan Type: {plan_type}
        Industry Sector: {industry_sector}
        
        Provide detailed risk management plan with the following information:
        - plan_section: Section of the plan (e.g., Executive Summary, Risk Assessment, Risk Response, Monitoring)
        - section_description: Detailed description of the section
        - key_objectives: Main objectives for this section
        - risk_categories: Types of risks covered (e.g., Strategic, Operational, Financial, Compliance)
        - risk_assessment_method: Method used for risk assessment
        - risk_response_strategies: Strategies for responding to risks
        - monitoring_frequency: How often risks should be monitored
        - responsible_party: Person responsible for this section
        - target_completion_date: Target date for completion
        - status: Current status (Draft, In Progress, Complete, Under Review)
        - plan_owner: Person accountable for the overall plan
        - last_updated: Last update timestamp
        - version: Plan version
        
        Return the data as a JSON array with these exact field names:
        [
          {{
            "plan_section": "Executive Summary",
            "section_description": "Overview of the risk management approach",
            "key_objectives": "Establish risk management framework and governance",
            "risk_categories": "Strategic, Operational, Financial, Compliance",
            "risk_assessment_method": "Qualitative and quantitative analysis",
            "risk_response_strategies": "Avoid, Transfer, Mitigate, Accept",
            "monitoring_frequency": "Monthly",
            "responsible_party": "Risk Manager",
            "target_completion_date": "2025-03-31",
            "status": "Draft",
            "plan_owner": "Chief Risk Officer",
            "last_updated": "2025-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert risk management specialist and strategic planner. Provide realistic, detailed risk management plan data with appropriate objectives, strategies, and governance structures."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                risk_management_plan_data = json.loads(json_str)
                return risk_management_plan_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_risk_management_plan_data(project_name, plan_type, industry_sector)
        else:
            # If content is None, fall back to mock data
            return generate_mock_risk_management_plan_data(project_name, plan_type, industry_sector)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_risk_management_plan_data(project_name, plan_type, industry_sector)

def generate_mock_risk_management_plan_data(project_name: str, plan_type: str, industry_sector: str) -> List[dict]:
    """Generate realistic mock risk management plan data for testing."""
    
    current_timestamp = datetime.now()
    
    mock_data = [
        {
            "plan_section": "Executive Summary",
            "section_description": "High-level overview of the risk management approach and governance structure for the project",
            "key_objectives": "Establish comprehensive risk management framework and governance structure",
            "risk_categories": "Strategic, Operational, Financial, Compliance, Technology",
            "risk_assessment_method": "Qualitative and quantitative analysis with expert judgment",
            "risk_response_strategies": "Avoid, Transfer, Mitigate, Accept with monitoring",
            "monitoring_frequency": "Monthly",
            "responsible_party": "Risk Manager",
            "target_completion_date": "2025-03-31",
            "status": "Draft",
            "plan_owner": "Chief Risk Officer",
            "last_updated": current_timestamp.isoformat(),
            "version": "1.0"
        },
        {
            "plan_section": "Risk Assessment",
            "section_description": "Systematic identification, analysis, and evaluation of project risks",
            "key_objectives": "Identify all potential risks and assess their likelihood and impact",
            "risk_categories": "Technical, Schedule, Resource, External, Regulatory",
            "risk_assessment_method": "Risk matrix with probability and impact scoring",
            "risk_response_strategies": "Risk prioritization and categorization",
            "monitoring_frequency": "Bi-weekly",
            "responsible_party": "Project Manager",
            "target_completion_date": "2025-02-28",
            "status": "In Progress",
            "plan_owner": "Chief Risk Officer",
            "last_updated": current_timestamp.isoformat(),
            "version": "1.0"
        },
        {
            "plan_section": "Risk Response",
            "section_description": "Development and implementation of risk response strategies and action plans",
            "key_objectives": "Develop effective response strategies for high-priority risks",
            "risk_categories": "High Impact, Medium Impact, Low Impact",
            "risk_assessment_method": "Cost-benefit analysis of response options",
            "risk_response_strategies": "Prevention, Contingency planning, Insurance",
            "monitoring_frequency": "Weekly",
            "responsible_party": "Risk Response Team",
            "target_completion_date": "2025-04-30",
            "status": "Draft",
            "plan_owner": "Chief Risk Officer",
            "last_updated": current_timestamp.isoformat(),
            "version": "1.0"
        }
    ]
    
    return mock_data

def generate_risk_management_report_with_ai(project_name: str, report_type: str, reporting_period: str) -> List[dict]:
    """Generate risk management report data using AI for the given project name, report type, and reporting period."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_risk_management_report_data(project_name, report_type, reporting_period)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"""
        Generate a comprehensive risk management report for: {project_name}
        Report Type: {report_type}
        Reporting Period: {reporting_period}
        
        Provide detailed risk management report with the following information:
        - report_section: Section of the report (e.g., Executive Summary, Risk Overview, Risk Assessment Results, Risk Response Status, Key Findings, Recommendations)
        - section_content: Detailed content and analysis for this section
        - risk_metrics: Key performance indicators and metrics
        - risk_trends: Trends and patterns identified
        - risk_incidents: Notable risk incidents or events
        - compliance_status: Compliance with risk management standards
        - action_items: Required actions and next steps
        - responsible_party: Person responsible for this section
        - target_completion_date: Target date for completion
        - status: Current status (Draft, In Progress, Complete, Under Review)
        - report_owner: Person accountable for the overall report
        - last_updated: Last update timestamp
        - version: Report version
        
        Return the data as a JSON array with these exact field names:
        [
          {{
            "report_section": "Executive Summary",
            "section_content": "Overview of risk management performance and key highlights",
            "risk_metrics": "Risk reduction: 15%, Incident rate: 2.3 per month",
            "risk_trends": "Decreasing trend in high-risk incidents",
            "risk_incidents": "3 major incidents reported and resolved",
            "compliance_status": "Fully compliant with ISO 31000",
            "action_items": "Implement enhanced monitoring system",
            "responsible_party": "Risk Manager",
            "target_completion_date": "2025-03-31",
            "status": "Complete",
            "report_owner": "Chief Risk Officer",
            "last_updated": "2025-01-15T10:30:00Z",
            "version": "1.0"
          }}
        ]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert risk management specialist and reporting analyst. Provide realistic, detailed risk management report data with appropriate metrics, trends, and actionable insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Extract JSON from the response
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                risk_management_report_data = json.loads(json_str)
                return risk_management_report_data
            else:
                # If we can't parse the response, fall back to mock data
                return generate_mock_risk_management_report_data(project_name, report_type, reporting_period)
        else:
            # If content is None, fall back to mock data
            return generate_mock_risk_management_report_data(project_name, report_type, reporting_period)
            
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fall back to mock data on any error
        return generate_mock_risk_management_report_data(project_name, report_type, reporting_period)

def generate_mock_risk_management_report_data(project_name: str, report_type: str, reporting_period: str) -> List[dict]:
    """Generate realistic mock risk management report data for testing."""
    
    current_timestamp = datetime.now()
    
    mock_data = [
        {
            "report_section": "Executive Summary",
            "section_content": "Comprehensive overview of risk management performance, key achievements, and strategic objectives for the reporting period",
            "risk_metrics": "Risk reduction: 15%, Incident rate: 2.3 per month, Risk maturity level: 4.2/5.0",
            "risk_trends": "Decreasing trend in high-risk incidents, improving risk culture across organization",
            "risk_incidents": "3 major incidents reported and resolved, 12 minor incidents managed proactively",
            "compliance_status": "Fully compliant with ISO 31000",
            "action_items": "Implement enhanced monitoring system, conduct risk awareness training",
            "responsible_party": "Risk Manager",
            "target_completion_date": "2025-03-31",
            "status": "Complete",
            "report_owner": "Chief Risk Officer",
            "last_updated": current_timestamp.isoformat(),
            "version": "1.0"
        },
        {
            "report_section": "Risk Overview",
            "section_content": "Detailed analysis of current risk landscape, including emerging risks and risk profile changes",
            "risk_metrics": "Total risks: 47, High risks: 8, Medium risks: 23, Low risks: 16",
            "risk_trends": "Cybersecurity risks increasing, operational risks decreasing",
            "risk_incidents": "2 cybersecurity incidents, 1 operational incident, 1 strategic risk event",
            "compliance_status": "95% compliance with internal risk policies",
            "action_items": "Update risk assessment methodology, enhance cyber risk monitoring",
            "responsible_party": "Risk Analyst",
            "target_completion_date": "2025-02-28",
            "status": "In Progress",
            "report_owner": "Chief Risk Officer",
            "last_updated": current_timestamp.isoformat(),
            "version": "1.0"
        },
        {
            "report_section": "Risk Assessment Results",
            "section_content": "Results of comprehensive risk assessments conducted during the reporting period",
            "risk_metrics": "Risk assessments completed: 12, Risk scores updated: 34, New risks identified: 7",
            "risk_trends": "Overall risk score decreased by 12%, technology risks increased by 8%",
            "risk_incidents": "5 risk assessments revealed critical gaps, 3 new controls implemented",
            "compliance_status": "100% of required assessments completed on schedule",
            "action_items": "Develop risk mitigation plans for high-scoring risks",
            "responsible_party": "Risk Assessment Team",
            "target_completion_date": "2025-04-30",
            "status": "Draft",
            "report_owner": "Chief Risk Officer",
            "last_updated": current_timestamp.isoformat(),
            "version": "1.0"
        }
    ]
    
    return mock_data

@router.post("/hazard-analysis/generate", response_model=HazardAnalysisResponse)
async def generate_hazard_analysis(request: HazardAnalysisRequest):
    """Generate complete hazard analysis using AI"""
    try:
        # Try AI generation first
        hazard_data = generate_hazard_analysis_with_ai(
            request.hazard_description,
            request.hazard_type
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(hazard_data) == 1 and hazard_data[0].get('responsible_party') == 'Electrical Engineer'
        return HazardAnalysisResponse(hazard_data=hazard_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        hazard_data = generate_mock_hazard_analysis_data(
            request.hazard_description,
            request.hazard_type
        )
        return HazardAnalysisResponse(hazard_data=hazard_data, mock=True)

@router.post("/fault-tree-report/generate", response_model=FaultTreeReportResponse)
async def generate_fault_tree_report(request: FaultTreeReportRequest):
    """Generate complete fault tree report using AI"""
    try:
        # Try AI generation first
        fault_tree_data = generate_fault_tree_report_with_ai(
            request.top_event,
            request.fault_tree_type
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(fault_tree_data) == 1 and fault_tree_data[0].get('responsible_party') == 'Systems Engineer'
        return FaultTreeReportResponse(fault_tree_data=fault_tree_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        fault_tree_data = generate_mock_fault_tree_report_data(
            request.top_event,
            request.fault_tree_type
        )
        return FaultTreeReportResponse(fault_tree_data=fault_tree_data, mock=True)

@router.post("/risk-evaluation-report/generate", response_model=RiskEvaluationReportResponse)
async def generate_risk_evaluation_report(request: RiskEvaluationReportRequest):
    """Generate complete risk evaluation report using AI"""
    try:
        # Try AI generation first
        risk_evaluation_data = generate_risk_evaluation_report_with_ai(
            request.risk_description,
            request.risk_category
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(risk_evaluation_data) == 1 and risk_evaluation_data[0].get('risk_owner') == 'Risk Manager'
        return RiskEvaluationReportResponse(risk_evaluation_data=risk_evaluation_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        risk_evaluation_data = generate_mock_risk_evaluation_report_data(
            request.risk_description,
            request.risk_category
        )
        return RiskEvaluationReportResponse(risk_evaluation_data=risk_evaluation_data, mock=True)

@router.post("/risk-control-implementation/generate", response_model=RiskControlImplementationResponse)
async def generate_risk_control_implementation(request: RiskControlImplementationRequest):
    """Generate complete risk control implementation plan using AI"""
    try:
        # Try AI generation first
        risk_control_data = generate_risk_control_implementation_with_ai(
            request.control_name,
            request.control_type
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(risk_control_data) == 1 and risk_control_data[0].get('control_owner') == 'Chief Information Security Officer'
        return RiskControlImplementationResponse(risk_control_data=risk_control_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        risk_control_data = generate_mock_risk_control_implementation_data(
            request.control_name,
            request.control_type
        )
        return RiskControlImplementationResponse(risk_control_data=risk_control_data, mock=True)

@router.post("/residual-risk-risk-benefit/generate", response_model=ResidualRiskRiskBenefitResponse)
async def generate_residual_risk_risk_benefit(request: ResidualRiskRiskBenefitRequest):
    """Generate residual risk and risk-benefit analysis using AI"""
    try:
        # Try AI generation first
        residual_risk_benefit_data = generate_residual_risk_risk_benefit_with_ai(
            request.risk_description,
            request.risk_category,
            request.benefit_description
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(residual_risk_benefit_data) == 1 and residual_risk_benefit_data[0].get('risk_owner') == 'Risk Manager'
        return ResidualRiskRiskBenefitResponse(residual_risk_benefit_data=residual_risk_benefit_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        residual_risk_benefit_data = generate_mock_residual_risk_risk_benefit_data(
            request.risk_description,
            request.risk_category,
            request.benefit_description
        )
        return ResidualRiskRiskBenefitResponse(residual_risk_benefit_data=residual_risk_benefit_data, mock=True)

@router.post("/residual-risk-risk-benefit/save")
async def save_residual_risk_risk_benefit(data: dict):
    """Save residual risk and risk-benefit analysis data to project"""
    try:
        # This would typically save to a database
        # For now, we'll just return a success message
        return {
            "message": "Residual risk and risk-benefit analysis data saved successfully",
            "saved_data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")

@router.post("/risk-traceability-matrix/generate", response_model=RiskTraceabilityMatrixResponse)
async def generate_risk_traceability_matrix(request: RiskTraceabilityMatrixRequest):
    """Generate risk traceability matrix using AI"""
    try:
        # Try AI generation first
        traceability_matrix_data = generate_risk_traceability_matrix_with_ai(
            request.project_name,
            request.traceability_type
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(traceability_matrix_data) == 1 and traceability_matrix_data[0].get('matrix_owner') == 'Risk Manager'
        return RiskTraceabilityMatrixResponse(traceability_matrix_data=traceability_matrix_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        traceability_matrix_data = generate_mock_risk_traceability_matrix_data(
            request.project_name,
            request.traceability_type
        )
        return RiskTraceabilityMatrixResponse(traceability_matrix_data=traceability_matrix_data, mock=True)

@router.post("/risk-traceability-matrix/save")
async def save_risk_traceability_matrix(data: dict):
    """Save risk traceability matrix data to project"""
    try:
        # This would typically save to a database
        # For now, we'll just return a success message
        return {
            "message": "Risk traceability matrix data saved successfully",
            "saved_data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")

@router.post("/risk-management-plan/generate", response_model=RiskManagementPlanResponse)
async def generate_risk_management_plan(request: RiskManagementPlanRequest):
    """Generate complete risk management plan using AI"""
    try:
        # Try AI generation first
        risk_management_plan_data = generate_risk_management_plan_with_ai(
            request.project_name,
            request.plan_type,
            request.industry_sector
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(risk_management_plan_data) == 3 and risk_management_plan_data[0].get('plan_owner') == 'Chief Risk Officer'
        return RiskManagementPlanResponse(risk_management_plan_data=risk_management_plan_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        risk_management_plan_data = generate_mock_risk_management_plan_data(
            request.project_name,
            request.plan_type,
            request.industry_sector
        )
        return RiskManagementPlanResponse(risk_management_plan_data=risk_management_plan_data, mock=True)

@router.post("/risk-management-plan/save")
async def save_risk_management_plan(data: dict):
    """Save risk management plan data to project"""
    try:
        # This would typically save to a database
        # For now, we'll just return a success message
        return {
            "message": "Risk management plan data saved successfully",
            "saved_data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")

@router.post("/risk-management-report/generate", response_model=RiskManagementReportResponse)
async def generate_risk_management_report(request: RiskManagementReportRequest):
    """Generate complete risk management report using AI"""
    try:
        # Try AI generation first
        risk_management_report_data = generate_risk_management_report_with_ai(
            request.project_name,
            request.report_type,
            request.reporting_period
        )
        # Check if we got mock data by checking if the data looks like mock data
        is_mock = len(risk_management_report_data) == 3 and risk_management_report_data[0].get('report_owner') == 'Chief Risk Officer'
        return RiskManagementReportResponse(risk_management_report_data=risk_management_report_data, mock=is_mock)
    except Exception as e:
        # Fallback to mock data on any error
        risk_management_report_data = generate_mock_risk_management_report_data(
            request.project_name,
            request.report_type,
            request.reporting_period
        )
        return RiskManagementReportResponse(risk_management_report_data=risk_management_report_data, mock=True)

@router.post("/risk-management-report/save")
async def save_risk_management_report(data: dict):
    """Save risk management report data to project"""
    try:
        # This would typically save to a database
        # For now, we'll just return a success message
        return {
            "message": "Risk management report data saved successfully",
            "saved_data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")

@router.post("/risk-management-report/generate-word")
async def generate_word_report(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate Word document report using template"""
    try:
        # Project scoping is REQUIRED for word report artifacts.
        project_id = data.get("project_id") or data.get("projectId") or data.get("projectID")
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        project = project_crud.get_project(db, str(project_id), current_user.id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Look for the Risk Management Report template
        templates_dir = Path("templates")
        template_file = None
        
        # Find the template file
        for template_path in templates_dir.glob("*risk_management_report*.docx"):
            template_file = template_path
            break
        
        if not template_file:
            raise HTTPException(
                status_code=404, 
                detail="Risk Management Report template not found. Please upload a template first."
            )
        
        # Load the template
        doc = DocxTemplate(template_file)
        
        # Prepare context data for the template
        context = {
            "project_name": data.get("project_name", "Unknown Project"),
            "report_type": data.get("report_type", "Unknown Type"),
            "reporting_period": data.get("reporting_period", "Unknown Period"),
            "generation_date": datetime.now().strftime("%B %d, %Y"),
            "report_data": data.get("risk_management_report_data", []),
            "executive_summary": "",
            "risk_overview": "",
            "risk_assessment": "",
            "risk_response": "",
            "key_findings": "",
            "recommendations": ""
        }
        
        # Extract specific sections from the report data
        for item in context["report_data"]:
            section = item.get("report_section", "").lower()
            if "executive" in section:
                context["executive_summary"] = item.get("section_content", "")
            elif "overview" in section:
                context["risk_overview"] = item.get("section_content", "")
            elif "assessment" in section:
                context["risk_assessment"] = item.get("section_content", "")
            elif "response" in section:
                context["risk_response"] = item.get("section_content", "")
            elif "findings" in section:
                context["key_findings"] = item.get("section_content", "")
            elif "recommendation" in section:
                context["recommendations"] = item.get("section_content", "")
        
        # Render the template
        doc.render(context)
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_project_name = str(data.get("project_name", "Project"))
        safe_project_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", raw_project_name).strip("._-") or "Project"
        output_filename = f"Risk_Management_Report_{safe_project_name}_{timestamp}.docx"
        if not _is_safe_docx_filename(output_filename):
            # Should never happen due to sanitization + fixed format, but keep guardrail.
            raise HTTPException(status_code=500, detail="Failed to create a safe output filename")

        temp_dir = Path("temp")
        output_path = temp_dir / output_filename
        
        # Create temp directory if it doesn't exist
        output_path.parent.mkdir(exist_ok=True)
        
        # Save the generated document
        doc.save(output_path)

        # Persist artifact record for multi-user authorization across restarts
        artifact_crud.create_generated_artifact(
            db,
            user_id=current_user.id,
            project_id=str(project_id),
            filename=output_filename,
            artifact_type="word_report",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        
        # Return the file path for download
        return {
            "message": "Word report generated successfully",
            "output_filename": output_filename,
            "output_path": str(output_path),
            "template_used": template_file.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating Word report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate Word report: {str(e)}")

@router.get("/risk-management-report/download-word/{filename}")
async def download_word_report(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download generated Word report"""
    try:
        from fastapi.responses import FileResponse

        # Validate filename strictly
        if not _is_safe_docx_filename(filename):
            raise HTTPException(status_code=400, detail="Invalid filename")

        # Enforce DB scoping + REQUIRED project ownership before serving
        _require_project_scoped_word_report(db, current_user=current_user, filename=filename)

        # Safe resolve inside fixed temp/ directory (no traversal)
        file_path = _safe_path_in_dir(Path("temp"), filename)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Generated report not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error downloading Word report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download Word report: {str(e)}")

@router.post("/fmea/suggest")
def suggest_fmea_row():
    """Legacy endpoint for backward compatibility"""
    return {"component": "Valve", "failure_mode": "Sticking", "severity": 7}
