from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel
import openai
import os
import json
from dotenv import load_dotenv

from database import get_db
from auth.dependencies import verify_token

# Load environment variables from `.env` only in non-production environments.
if os.getenv("ENVIRONMENT", "").lower() not in ("production", "prod"):
    load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter()

# Add caching for date calculations
_date_cache = {}

def get_cached_date_calculation(timestamp: str, days_offset: int) -> str:
    """Get cached date calculation or compute and cache it"""
    cache_key = f"{timestamp}_{days_offset}"
    if cache_key not in _date_cache:
        try:
            if 'T' in timestamp:
                base_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                base_date = datetime.strptime(timestamp, "%Y-%m-%d")
            result_date = base_date + timedelta(days=days_offset)
            _date_cache[cache_key] = result_date.strftime("%Y-%m-%d")
        except ValueError:
            # Fallback to current date calculation
            result_date = datetime.now() + timedelta(days=days_offset)
            _date_cache[cache_key] = result_date.strftime("%Y-%m-%d")
    return _date_cache[cache_key]

def validate_due_date(due_date_str: str, analysis_timestamp: str = None) -> str:
    """Validate and ensure due date is 5 weeks after analysis_timestamp"""
    try:
        # Parse the due date
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        
        # If analysis_timestamp is provided, use it as reference
        if analysis_timestamp:
            try:
                # Use cached calculation for efficiency
                target_due_date_str = get_cached_date_calculation(analysis_timestamp, 35)  # 5 weeks = 35 days
                target_due_date = datetime.strptime(target_due_date_str, "%Y-%m-%d")
                
                # If the provided due date is less than 5 weeks after analysis_timestamp, adjust it
                if due_date < target_due_date:
                    return target_due_date_str
                
                return due_date_str
            except ValueError:
                # If analysis_timestamp parsing fails, fall back to current date logic
                pass
        
        # Fallback to current date logic (original behavior)
        current_date = datetime.now()
        min_due_date = current_date + timedelta(days=30)
        
        if due_date < min_due_date:
            adjusted_due_date = current_date + timedelta(days=45)
            return adjusted_due_date.strftime("%Y-%m-%d")
        
        return due_date_str
    except ValueError:
        # If date parsing fails, return a safe default
        if analysis_timestamp:
            try:
                return get_cached_date_calculation(analysis_timestamp, 35)
            except ValueError:
                pass
        return (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")

def validate_detection_date(detection_date_str: str, analysis_timestamp: str = None) -> str:
    """Validate and ensure detection date is 1 week before analysis_timestamp"""
    try:
        # Parse the detection date
        detection_date = datetime.strptime(detection_date_str, "%Y-%m-%d")
        
        # If analysis_timestamp is provided, use it as reference
        if analysis_timestamp:
            try:
                # Use cached calculation for efficiency
                target_detection_date_str = get_cached_date_calculation(analysis_timestamp, -7)  # 1 week before = -7 days
                target_detection_date = datetime.strptime(target_detection_date_str, "%Y-%m-%d")
                
                # If the provided detection date is not 1 week before analysis_timestamp, adjust it
                if detection_date != target_detection_date:
                    return target_detection_date_str
                
                return detection_date_str
            except ValueError:
                # If analysis_timestamp parsing fails, fall back to current date logic
                pass
        
        # Fallback to current date logic
        current_date = datetime.now()
        target_detection_date = current_date - timedelta(weeks=1)
        return target_detection_date.strftime("%Y-%m-%d")
    except ValueError:
        # If date parsing fails, return a safe default
        if analysis_timestamp:
            try:
                return get_cached_date_calculation(analysis_timestamp, -7)
            except ValueError:
                pass
        return (datetime.now() - timedelta(weeks=1)).strftime("%Y-%m-%d")

class CapaGenerateRequest(BaseModel):
    issue_description: str
    capa_type: str = "corrective"

class CapaData(BaseModel):
    id: str
    project_id: int
    user_id: str
    issue_description: str
    source: str
    detection_date: str
    severity: str
    root_cause: str
    corrective_action: str
    preventive_action: str
    action_owner: str
    due_date: str
    status: str
    effectiveness_check_plan: str
    fmea_link: str
    regulatory_impact: str
    closure_summary: str
    milestones: str
    risk_controls_update: str
    analysis_timestamp: str
    version: str

class CapaResponse(BaseModel):
    capa_data: List[CapaData]
    mock: bool = False

def generate_capa_with_ai(issue_description: str, capa_type: str = "corrective") -> List[CapaData]:
    """Generate CAPA data using AI for the given issue description."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise Exception("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Ultra-optimized prompt for speed
        prompt = f"""Generate 3 CAPA entries for: {issue_description}

JSON format with fields:
- id: "CAPA-001", "CAPA-002", "CAPA-003"
- project_id: 1
- user_id: "ai-assistant"
- issue_description: Brief issue description
- source: "Customer Complaint", "Internal Audit", or "Regulatory Finding"
- detection_date: YYYY-MM-DD (1 week before analysis_timestamp)
- severity: "Low", "Medium", "High", or "Critical"
- root_cause: Brief root cause
- corrective_action: Brief corrective action
- preventive_action: Brief preventive action
- action_owner: "Quality Manager", "Supply Chain Manager", or "Regulatory Manager"
- due_date: YYYY-MM-DD (5 weeks after analysis_timestamp)
- status: "Open", "In Progress", or "Closed"
- effectiveness_check_plan: Brief effectiveness plan
- fmea_link: "http://example.com/fmea/CAPA-XXX"
- regulatory_impact: Brief regulatory impact
- closure_summary: Brief closure summary
- milestones: Brief milestones
- risk_controls_update: Brief risk controls update
- analysis_timestamp: Current ISO timestamp
- version: "1.0"

Return JSON array with 3 objects. Keep all descriptions very brief."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Fastest model
            messages=[
                {"role": "system", "content": "Generate brief CAPA entries in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Very low temperature for consistent, fast output
            max_tokens=800,   # Further reduced token limit
            timeout=8,        # Reduced timeout
            stream=False      # Ensure no streaming for faster response
        )
        
        # Parse the AI response
        ai_response = response.choices[0].message.content
        logger.info(f"AI Response: {ai_response}")
        
        # Extract JSON from the response with optimized parsing
        try:
            # Try to find JSON array in the response
            start_idx = ai_response.find('[')
            end_idx = ai_response.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = ai_response[start_idx:end_idx]
                capa_entries = json.loads(json_str)
            else:
                # If JSON parsing fails, raise an exception instead of using mock data
                raise Exception("Failed to parse AI response as JSON")
            
            # Convert to CapaData objects with ultra-optimized processing
            capa_data = []
            current_timestamp = datetime.now().isoformat()
            
            # Pre-calculate all dates once for efficiency
            base_date = datetime.now()
            detection_dates = [
                get_cached_date_calculation(current_timestamp, -7),  # 1 week before
                get_cached_date_calculation(current_timestamp, -7),
                get_cached_date_calculation(current_timestamp, -7)
            ]
            due_dates = [
                get_cached_date_calculation(current_timestamp, 35),  # 5 weeks after
                get_cached_date_calculation(current_timestamp, 35),
                get_cached_date_calculation(current_timestamp, 35)
            ]
            
            # Pre-define common values
            sources = ["Customer Complaint", "Internal Audit", "Regulatory Finding"]
            severities = ["Low", "Medium", "High"]
            statuses = ["Open", "In Progress", "Closed"]
            owners = ["Quality Manager", "Supply Chain Manager", "Regulatory Manager"]
            
            for i, entry in enumerate(capa_entries):
                capa_entry = CapaData(
                    id=entry.get("id", f"CAPA-{str(i+1).zfill(3)}"),
                    project_id=entry.get("project_id", 1),
                    user_id=entry.get("user_id", "ai-assistant"),
                    issue_description=entry.get("issue_description", f"{issue_description} - Issue {i+1}"),
                    source=entry.get("source", sources[i % len(sources)]),
                    detection_date=detection_dates[i],
                    severity=entry.get("severity", severities[i % len(severities)]),
                    root_cause=entry.get("root_cause", f"Root cause for {capa_type} CAPA {i+1}"),
                    corrective_action=entry.get("corrective_action", f"Corrective action for {capa_type} issue {i+1}"),
                    preventive_action=entry.get("preventive_action", f"Preventive action for {capa_type} process {i+1}"),
                    action_owner=entry.get("action_owner", owners[i % len(owners)]),
                    due_date=due_dates[i],
                    status=entry.get("status", statuses[i % len(statuses)]),
                    effectiveness_check_plan=entry.get("effectiveness_check_plan", f"Effectiveness plan for {capa_type} controls"),
                    fmea_link=entry.get("fmea_link", f"http://example.com/fmea/CAPA-{str(i+1).zfill(3)}"),
                    regulatory_impact=entry.get("regulatory_impact", "Regulatory impact assessment"),
                    closure_summary=entry.get("closure_summary", f"Closure summary for {capa_type} CAPA {i+1}"),
                    milestones=entry.get("milestones", f"Milestones for {capa_type} CAPA {i+1}"),
                    risk_controls_update=entry.get("risk_controls_update", f"Risk controls for {capa_type} CAPA {i+1}"),
                    analysis_timestamp=entry.get("analysis_timestamp", current_timestamp),
                    version=entry.get("version", "1.0")
                )
                capa_data.append(capa_entry)
            
            logger.info(f"Generated {len(capa_data)} CAPA entries (AI-generated)")
            return capa_data
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error processing AI response: {e}")
            raise Exception(f"Failed to process AI response: {e}")
            
    except Exception as e:
        logger.error(f"Error generating CAPA with AI: {e}")
        raise Exception(f"AI generation failed: {e}")

@router.post("/capa/generate", response_model=CapaResponse)
async def generate_capa(request: CapaGenerateRequest):
    """Generate CAPA data for the given issue description."""
    logger.info(f"Received CAPA request: {request.issue_description}, type: {request.capa_type}")
    
    # Try AI generation with timeout
    try:
        # Use asyncio.wait_for to implement a timeout
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        # Create a thread pool for running the AI generation
        with ThreadPoolExecutor() as executor:
            # Submit the AI generation task
            future = executor.submit(generate_capa_with_ai, request.issue_description, request.capa_type)
            
            try:
                # Wait for the result with a 10-second timeout
                capa_data = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: future.result(timeout=10)
                )
                
                # Always return AI-generated data
                return CapaResponse(capa_data=capa_data, mock=False)
                
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"AI generation failed: {str(e)}. Please try again or check your OpenAI API key."
                )
                
    except Exception as e:
        logger.error(f"Error in CAPA generation: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"CAPA generation failed: {str(e)}"
        )

@router.get("/capa/health")
async def capa_health():
    """Health check for CAPA endpoints"""
    return {"status": "healthy", "message": "CAPA endpoints are working"} 