from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import openai
import os
import logging
import re
logger = logging.getLogger(__name__)

router = APIRouter()

# Set your OpenAI API key (or use dotenv/env setup)
openai.api_key = os.getenv("OPENAI_API_KEY")

class TraceabilityRequest(BaseModel):
    component: str

class TraceabilityItem(BaseModel):
    user_need: str
    design_input: str
    design_output: str
    verification: str
    validation: str

class TraceabilityResponse(BaseModel):
    matrix: List[TraceabilityItem]
    mock: bool = False

@router.post("/ai/traceability/suggest", response_model=TraceabilityResponse)
async def suggest_traceability_matrix(request: TraceabilityRequest):
    prompt = (
        f"Given the component '{request.component}', generate a traceability matrix consisting of:\n"
        f"1. User Needs\n"
        f"2. Design Inputs\n"
        f"3. Design Outputs\n"
        f"4. Verification Methods\n"
        f"5. Validation Methods\n\n"
        f"Output in JSON array format with keys: user_need, design_input, design_output, verification, validation."
    )

    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            # No API key, return mock data
            return TraceabilityResponse(matrix=generate_mock_traceability_data(request.component), mock=True)
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in medical device development and regulatory compliance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        import json
        content = response.choices[0].message.content
        if content is None:
            raise HTTPException(status_code=500, detail="No content returned from OpenAI API.")
        # Extract JSON array from content using regex
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            matrix = json.loads(json_str)
            return TraceabilityResponse(matrix=matrix, mock=False)
        else:
            raise HTTPException(status_code=500, detail="Could not parse JSON from OpenAI response.")

    except Exception as e:
        logger.error(f"Traceability matrix generation failed: {e}", exc_info=True)
        # On error, return mock data
        return TraceabilityResponse(matrix=generate_mock_traceability_data(request.component), mock=True)

# Helper to generate mock data

def generate_mock_traceability_data(component: str) -> list:
    # Return 10 mock rows for demonstration
    return [
        {
            "user_need": f"User need {i+1} for {component}",
            "design_input": f"Design input {i+1} for {component}",
            "design_output": f"Design output {i+1} for {component}",
            "verification": f"Verification {i+1} for {component}",
            "validation": f"Validation {i+1} for {component}"
        }
        for i in range(10)
    ]
