# routes/mastercontrol.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from integrations.mastercontrol import push_batch

router = APIRouter(prefix="/integrations/mastercontrol", tags=["integrations:mastercontrol"])

class FMEARow(BaseModel):
    component: str = Field(..., alias="COMPONENT")
    function: Optional[str] = Field(None, alias="FUNCTION")
    failure_mode: str = Field(..., alias="FAILURE MODE")
    effects: Optional[str] = Field(None, alias="EFFECTS")
    severity: Optional[int] = Field(None, alias="SEVERITY")
    causes: Optional[str] = Field(None, alias="CAUSES")
    occurrence: Optional[int] = Field(None, alias="OCCURRENCE")
    controls: Optional[str] = Field(None, alias="CONTROLS")
    detection: Optional[int] = Field(None, alias="DETECTION")
    rpn: Optional[int] = Field(None, alias="RPN")
    actions: Optional[str] = Field(None, alias="ACTIONS")
    owner: Optional[str] = Field(None, alias="OWNER")
    due_date: Optional[str] = Field(None, alias="DUE DATE")   # YYYY-MM-DD
    status: Optional[str] = Field(None, alias="STATUS")
    doc_link: Optional[str] = Field(None, alias="DOC LINK")

class ExportRequest(BaseModel):
    project_id: Optional[str] = None
    rows: Optional[List[FMEARow]] = None
    rate_limit_sec: float = 0.0

@router.post("/export")
def export_to_mastercontrol(req: ExportRequest):
    # Source rows: from DB or request
    if req.rows:
        rows = [r.model_dump(by_alias=True) for r in req.rows]
    elif req.project_id:
        # TODO: fetch from your DB by project_id; example stub:
        # rows = db.fetch_fmea_rows(project_id=req.project_id)
        raise HTTPException(501, "DB fetch not implemented in example")
    else:
        raise HTTPException(400, "Provide either 'rows' or 'project_id'.")

    # Debug: Log the first row payload that will be sent
    import logging
    logger = logging.getLogger(__name__)
    if rows:
        from integrations.mastercontrol import smart_risk_row_to_mc_payload
        try:
            test_payload = smart_risk_row_to_mc_payload(rows[0])
            logger.info(f"DEBUG: First row payload structure: {test_payload.get('serviceName')}, {test_payload.get('methodName')}")
            logger.info(f"DEBUG: ConnectionID in payload: {test_payload.get('arguments', {}).get('connectionID', 'NOT SET')}")
            logger.info(f"DEBUG: Number of fields: {len(test_payload.get('arguments', {}).get('processTask', {}).get('fields', []))}")
        except Exception as e:
            logger.error(f"DEBUG: Error creating payload: {e}")

    results = push_batch(rows, rate_limit_sec=req.rate_limit_sec)

    # Basic success metric
    success = sum(1 for r in results if r["error"] is None and r["status"] and 200 <= r["status"] < 300)
    fail = len(results) - success
    return {"summary": {"success": success, "fail": fail}, "results": results}
