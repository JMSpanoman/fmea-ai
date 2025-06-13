import openai
import os
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ComponentInput(BaseModel):
    component: str

@app.post("/generate_fmea/")
async def generate_fmea(data: ComponentInput):
    prompt = f"""
    You are a senior risk management engineer. For the component "{data.component}", generate 3 to 5 FMEA rows in JSON list format.
    Each row should include these keys: "Failure Mode", "Effect", "Cause", "Severity", "Probability", "RPN",
    "Mitigation", "Post Severity", "Post Probability", "Post RPN".

    Severity and Probability scores range from 1 (low) to 10 (high). RPN = Severity × Probability. Post values are after mitigation.

    Example format:
    [
        {{
            "Failure Mode": "...",
            "Effect": "...",
            "Cause": "...",
            "Severity": 8,
            "Probability": 7,
            "RPN": 56,
            "Mitigation": "...",
            "Post Severity": 5,
            "Post Probability": 3,
            "Post RPN": 15
        }},
        ...
    ]
    Only return valid JSON.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an FMEA generation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        raw_output = response.choices[0].message.content.strip()
        fmea_rows = json.loads(raw_output)
        return {"fmea": fmea_rows}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")
