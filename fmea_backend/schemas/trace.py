from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Literal
from datetime import datetime

# Canonical trace link types - SmartQS Connection Contract
FromType = Literal[
    "risk_item",
    "risk_item_version", 
    "risk_control",
    "design_input",
    "design_output",
    "vv_test",
    "capa",
    "change_control",
    "fmea_row",
    "pms_signal"
]

ToType = Literal[
    "risk_item",
    "risk_item_version",
    "risk_control",
    "design_input",
    "design_output",
    "vv_test",
    "capa",
    "change_control",
    "fmea_row",
    "pms_signal"
]

LinkType = Literal[
    "traces_to",
    "verified_by",
    "generated_from",
    "impacts",
    "mitigates",
    "links_to"
]

class TraceLinkBase(BaseModel):
    from_type: FromType
    from_id: str  # UUID
    to_type: ToType
    to_id: str  # UUID
    link_type: LinkType = "traces_to"  # Optional, defaults to traces_to

    @field_validator('from_type', 'to_type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Ensure canonical types are used"""
        valid_from_types = ["risk_item", "risk_item_version", "risk_control", "design_input", "design_output", "vv_test", "capa", "change_control", "fmea_row", "pms_signal"]
        valid_to_types = valid_from_types  # Same set
        if isinstance(v, str) and v not in valid_from_types:
            raise ValueError(f"Invalid type: {v}. Must be one of {valid_from_types}")
        return v

class TraceLinkCreate(TraceLinkBase):
    project_id: str  # UUID

class TraceLinkOut(TraceLinkBase):
    id: str  # UUID
    project_id: str  # UUID
    link_type: LinkType = "traces_to"
    created_at: datetime

    class Config:
        from_attributes = True

class TraceMatrixResponse(BaseModel):
    """Response for traceability matrix"""
    links: List[TraceLinkOut]
    graph: Dict[str, Any]  # Graph representation of trace links

