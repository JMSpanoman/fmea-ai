from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

class ComponentInput(BaseModel):
    name: str
    description: Optional[str] = None

class ReviewRole(BaseModel):
    role: str
    requirement: str  # required, optional

class RMPGenerateRequest(BaseModel):
    title: Optional[str] = None  # Auto-generated if not provided
    scope: str
    intended_use: str
    components: List[ComponentInput]
    acceptability_profile: str = "default_med_device"  # default_med_device, custom
    custom_acceptability_criteria: Optional[Dict[str, Any]] = None
    review_roles: Dict[str, str]  # role -> requirement
    ai_assistance_enabled: bool = True

class RMPUpdateRequest(BaseModel):
    title: Optional[str] = None
    scope: Optional[str] = None
    intended_use: Optional[str] = None
    components: Optional[List[ComponentInput]] = None
    acceptability_criteria_json: Optional[str] = None
    review_roles: Optional[Dict[str, str]] = None

class RMPOut(BaseModel):
    id: str
    project_id: str
    title: str
    scope: str
    intended_use: str
    components_json: str
    acceptability_criteria_json: str
    risk_methodology: str
    review_roles_json: str
    risk_control_categories_json: str
    benefit_risk_criteria: str
    lifecycle_linkage: str
    governance_rules: str
    rendered_html: str
    status: str
    current_version_no: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @property
    def components(self) -> List[Dict[str, Any]]:
        """Parse components_json to list"""
        try:
            return json.loads(self.components_json)
        except:
            return []

    @property
    def acceptability_criteria(self) -> Dict[str, Any]:
        """Parse acceptability_criteria_json to dict"""
        try:
            return json.loads(self.acceptability_criteria_json)
        except:
            return {}

    @property
    def review_roles(self) -> Dict[str, str]:
        """Parse review_roles_json to dict"""
        try:
            return json.loads(self.review_roles_json)
        except:
            return {}

    @property
    def risk_control_categories(self) -> List[str]:
        """Parse risk_control_categories_json to list"""
        try:
            return json.loads(self.risk_control_categories_json)
        except:
            return []

class RMPApprovalRequest(BaseModel):
    decision: str  # approved, rejected
    rationale: str

