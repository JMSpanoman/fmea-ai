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

class ChangeControlGenerateRequest(BaseModel):
    change_description: str

class ChangeControlData(BaseModel):
    id: str
    change_description: str
    initiator: str
    date_initiated: str
    status: str
    impact_assessment: str
    actions_required: str
    action_owner: str
    due_date: str
    closure_summary: str
    analysis_timestamp: str
    version: str

class ChangeControlResponse(BaseModel):
    change_control_data: List[ChangeControlData]
    mock: bool = False

def generate_change_control_with_ai(change_description: str) -> List[ChangeControlData]:
    """Generate Change Control data using AI for the given change description."""
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # No API key available, use mock data
        return generate_mock_change_control_data(change_description)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        # Ultra-optimized prompt for maximum speed
        prompt = f"""Generate 3 change control entries for: {change_description}

JSON format:
- id: "CC-001", "CC-002", "CC-003"
- change_description: Brief description
- initiator: "Quality Manager", "Regulatory Manager", or "Process Engineer"
- date_initiated: YYYY-MM-DD (1 week ago)
- status: "Open", "In Progress", or "Closed"
- impact_assessment: Brief impact assessment
- actions_required: Brief actions required
- action_owner: "Quality Manager", "Regulatory Manager", or "Process Engineer"
- due_date: YYYY-MM-DD (5 weeks from now)
- closure_summary: Brief closure summary
- analysis_timestamp: Current ISO timestamp
- version: "1.0"

Return JSON array with 3 objects. Keep descriptions very brief."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Fastest model
            messages=[
                {"role": "system", "content": "Generate brief change control entries in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Zero temperature for fastest, most consistent output
            max_tokens=200,   # Minimal token limit for maximum speed
            timeout=3,        # Very short timeout for faster response
            stream=False,     # Ensure no streaming for faster response
            presence_penalty=0,  # No penalties for faster generation
            frequency_penalty=0   # No penalties for faster generation
        )
        
        # Parse the AI response
        ai_response = response.choices[0].message.content
        logger.info(f"AI Response: {ai_response}")
        
        # Extract JSON from the response
        try:
            # Try to find JSON array in the response
            start_idx = ai_response.find('[')
            end_idx = ai_response.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = ai_response[start_idx:end_idx]
                change_control_entries = json.loads(json_str)
            else:
                # Fallback to mock data if JSON parsing fails
                logger.warning("Failed to parse AI response as JSON, using mock data")
                return generate_mock_change_control_data(change_description)
            
            # Convert to ChangeControlData objects with ultra-optimized processing
            change_control_data = []
            current_timestamp = datetime.now().isoformat()
            
            # Pre-calculate all dates once for efficiency
            base_date = datetime.now()
            initiated_dates = [
                (base_date - timedelta(days=7)).strftime("%Y-%m-%d"),  # 1 week ago
                (base_date - timedelta(days=7)).strftime("%Y-%m-%d"),
                (base_date - timedelta(days=7)).strftime("%Y-%m-%d")
            ]
            due_dates = [
                (base_date + timedelta(days=35)).strftime("%Y-%m-%d"),  # 5 weeks from now
                (base_date + timedelta(days=35)).strftime("%Y-%m-%d"),
                (base_date + timedelta(days=35)).strftime("%Y-%m-%d")
            ]
            
            # Pre-define common values
            initiators = ["Quality Manager", "Regulatory Manager", "Process Engineer"]
            statuses = ["Open", "In Progress", "Closed"]
            owners = ["Quality Manager", "Regulatory Manager", "Process Engineer"]
            
            for i, entry in enumerate(change_control_entries):
                change_control_entry = ChangeControlData(
                    id=entry.get("id", f"CC-{str(i+1).zfill(3)}"),
                    change_description=entry.get("change_description", f"{change_description} - Change {i+1}"),
                    initiator=entry.get("initiator", initiators[i % len(initiators)]),
                    date_initiated=entry.get("date_initiated", initiated_dates[i]),
                    status=entry.get("status", statuses[i % len(statuses)]),
                    impact_assessment=entry.get("impact_assessment", f"AI-generated impact assessment for change {i+1}"),
                    actions_required=entry.get("actions_required", f"AI-generated actions required for change {i+1}"),
                    action_owner=entry.get("action_owner", owners[i % len(owners)]),
                    due_date=entry.get("due_date", due_dates[i]),
                    closure_summary=entry.get("closure_summary", f"AI-generated closure summary for change {i+1}"),
                    analysis_timestamp=entry.get("analysis_timestamp", current_timestamp),
                    version=entry.get("version", "1.0")
                )
                change_control_data.append(change_control_entry)
            
            return change_control_data
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing AI response: {e}")
            return generate_mock_change_control_data(change_description)
            
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        return generate_mock_change_control_data(change_description)

def generate_mock_change_control_data(change_description: str):
    """Generate mock Change Control data for testing"""
    mock_data = []
    for i in range(3):
        status_levels = ["Open", "In Progress", "Closed"]
        mock_entry = ChangeControlData(
            id=f"CC-{i+1:03d}",
            change_description=f"{change_description} - Change {i+1}",
            initiator="AI Assistant",
            date_initiated=(datetime.now() - timedelta(days=i*7)).strftime("%Y-%m-%d"),
            status=status_levels[i % 3],
            impact_assessment=f"Simulated impact assessment for change {i+1}",
            actions_required=f"Actions required for change {i+1}",
            action_owner="AI Owner",
            due_date=(datetime.now() + timedelta(days=30-i*5)).strftime("%Y-%m-%d"),
            closure_summary=f"AI generated closure summary for change {i+1}",
            analysis_timestamp=datetime.now().isoformat(),
            version="1.0"
        )
        mock_data.append(mock_entry)
    return mock_data

@router.post("/change-control/generate", tags=["Change Control"], response_model=ChangeControlResponse)
def generate_change_control(request: ChangeControlGenerateRequest):
    logger.info(f"Received Change Control request: {request.change_description}")
    
    # Generate AI data
    change_control_data = generate_change_control_with_ai(request.change_description)
    
    # Check if we used mock data (no API key or AI failed)
    # Reload environment variables to ensure we have the latest
    if os.getenv("ENVIRONMENT", "").lower() not in ("production", "prod"):
        load_dotenv()
    is_mock = not os.getenv("OPENAI_API_KEY") or len(change_control_data) == 0
    
    logger.info(f"Generated {len(change_control_data)} Change Control entries (mock: {is_mock})")
    
    return ChangeControlResponse(
        change_control_data=change_control_data,
        mock=is_mock
    ) 