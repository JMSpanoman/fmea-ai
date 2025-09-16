from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

class Mitigation(BaseModel):
    id: int
    title: str
    description: str
    fda_reference: str
    category: str

router = APIRouter()

mitigations = [
    Mitigation(
        id=1,
        title="Redundant Sensors",
        description="Use redundant sensors to detect failures and ensure continued operation.",
        fda_reference="21 CFR 820.70",
        category="Design Control"
    ),
    Mitigation(
        id=2,
        title="Preventive Maintenance",
        description="Implement a preventive maintenance schedule to reduce the risk of failure.",
        fda_reference="21 CFR 820.200",
        category="Process Control"
    ),
    Mitigation(
        id=3,
        title="User Training",
        description="Provide comprehensive user training to minimize use errors.",
        fda_reference="21 CFR 820.25",
        category="Labeling & Training"
    ),
]

@router.get("/mitigations", response_model=List[Mitigation])
def get_mitigations():
    return mitigations 