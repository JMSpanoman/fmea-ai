from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas.fmea import (
    AIFMEASuggestRequest, 
    AIFMEASuggestResponse,
    AIConsistencyCheckRequest,
    AIConsistencyCheckResponse
)
import openai
import os
import json
import re
from decimal import Decimal

router = APIRouter(prefix="/ai/fmea", tags=["ai"])

# System prompt for Phase 1
SYSTEM_PROMPT = "You are the Smart Risk Phase 1 AI. Generate ISO 14971 compliant FMEA content. Output JSON only."

def _calculate_financial_impact(severity: int, probability: int) -> Decimal:
    """Calculate financial impact baseline if AI is unavailable"""
    return Decimal(severity * probability * 5000)

@router.post("/suggest", response_model=AIFMEASuggestResponse)
def suggest_fmea(
    request: AIFMEASuggestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI suggestions for FMEA row based on component, failure mode, effect, and cause. Uses OPENAI_API_KEY or OPENAI_KEY (same as V&V generate-from-risk)."""
    openai_api_key = (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY") or "").strip() or None

    if not openai_api_key:
        # Fallback: Use baseline calculation
        severity = 5  # Default
        probability = 5  # Default
        detection = 5  # Default
        rpn = severity * probability * detection
        financial_impact = _calculate_financial_impact(severity, probability)
        
        return AIFMEASuggestResponse(
            severity=severity,
            probability=probability,
            detection=detection,
            rpn=rpn,
            mitigation="Review design controls and implement preventive measures",
            financial_impact=financial_impact,
            residual_severity=max(1, severity - 1),
            residual_probability=max(1, probability - 1),
            residual_detection=min(10, detection + 1),
            residual_rpn=max(1, severity - 1) * max(1, probability - 1) * min(10, detection + 1)
        )
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        prompt = f"""Given component: {request.component}, failure mode: {request.failure_mode}, effect: {request.effect}, and cause: {request.cause}, generate severity (1–10), probability (1–10), detection (1–10), mitigation, residual scores, financial impact. Return JSON only.

Return a JSON object with these exact fields:
{{
  "severity": 7,
  "probability": 4,
  "detection": 6,
  "rpn": 168,
  "mitigation": "Detailed mitigation strategy",
  "financial_impact": 140000,
  "residual_severity": 6,
  "residual_probability": 3,
  "residual_detection": 5,
  "residual_rpn": 90
}}"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if content:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # Calculate RPN if not provided
                if "rpn" not in data:
                    data["rpn"] = data.get("severity", 1) * data.get("probability", 1) * data.get("detection", 1)
                if "residual_rpn" not in data:
                    data["residual_rpn"] = data.get("residual_severity", 1) * data.get("residual_probability", 1) * data.get("residual_detection", 1)
                
                return AIFMEASuggestResponse(
                    severity=data.get("severity", 5),
                    probability=data.get("probability", 5),
                    detection=data.get("detection", 5),
                    rpn=data.get("rpn", 125),
                    mitigation=data.get("mitigation", "Implement controls"),
                    financial_impact=Decimal(str(data.get("financial_impact", _calculate_financial_impact(data.get("severity", 5), data.get("probability", 5))))),
                    residual_severity=data.get("residual_severity", 4),
                    residual_probability=data.get("residual_probability", 4),
                    residual_detection=data.get("residual_detection", 6),
                    residual_rpn=data.get("residual_rpn", 96)
                )
    
    except Exception as e:
        print(f"AI suggestion failed: {e}")
    
    # Fallback response
    severity = 5
    probability = 5
    detection = 5
    return AIFMEASuggestResponse(
        severity=severity,
        probability=probability,
        detection=detection,
        rpn=severity * probability * detection,
        mitigation="Review design controls and implement preventive measures",
        financial_impact=_calculate_financial_impact(severity, probability),
        residual_severity=max(1, severity - 1),
        residual_probability=max(1, probability - 1),
        residual_detection=min(10, detection + 1),
        residual_rpn=max(1, severity - 1) * max(1, probability - 1) * min(10, detection + 1)
    )

@router.post("/check", response_model=AIConsistencyCheckResponse)
def check_consistency(
    request: AIConsistencyCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check FMEA row for consistency issues and provide recommendations"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        # Fallback: Basic consistency checks
        issues = []
        recommendations = []
        
        row = request.fmea_row
        
        # Check RPN calculation
        if row.severity and row.probability and row.detection:
            calculated_rpn = row.severity * row.probability * row.detection
            if row.rpn and row.rpn != calculated_rpn:
                issues.append(f"RPN mismatch: calculated {calculated_rpn} but stored {row.rpn}")
                recommendations.append("Update RPN to match calculated value")
        
        # Check residual RPN calculation
        if row.residual_severity and row.residual_probability and row.residual_detection:
            calculated_residual_rpn = row.residual_severity * row.residual_probability * row.residual_detection
            if row.residual_rpn and row.residual_rpn != calculated_residual_rpn:
                issues.append(f"Residual RPN mismatch: calculated {calculated_residual_rpn} but stored {row.residual_rpn}")
                recommendations.append("Update residual RPN to match calculated value")
        
        # Check severity range
        if row.severity and (row.severity < 1 or row.severity > 10):
            issues.append(f"Severity out of range: {row.severity} (should be 1-10)")
            recommendations.append("Adjust severity to valid range")
        
        return AIConsistencyCheckResponse(
            issues=issues,
            recommendations=recommendations
        )
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        prompt = f"""Review this FMEA row and return JSON listing issues and recommendations.

FMEA Row Data:
{json.dumps(request.fmea_row.dict(), indent=2)}

Return a JSON object with these exact fields:
{{
  "issues": ["Issue 1", "Issue 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"]
}}"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if content:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return AIConsistencyCheckResponse(
                    issues=data.get("issues", []),
                    recommendations=data.get("recommendations", [])
                )
    
    except Exception as e:
        print(f"AI consistency check failed: {e}")
    
    # Fallback response
    return AIConsistencyCheckResponse(
        issues=[],
        recommendations=["Review FMEA row for completeness and accuracy"]
    )

