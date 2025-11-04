# integrations/mastercontrol.py
from typing import Dict, Any, List, Optional
import os, json, time
import requests
from tenacity import retry, wait_exponential, stop_after_attempt

MC_BASE = os.getenv("MC_BASE", "").rstrip("/")
MC_TOKEN = os.getenv("MC_TOKEN", "")  # This is the API key
MC_CONNECTION_ID = os.getenv("MC_CONNECTION_ID", "")
MC_RPN_CALCULATED = os.getenv("MC_RPN_CALCULATED", "false").lower() == "true"

HEADERS = {
    "Content-Type": "application/json"
}

def mc_debug_probe():
    base = os.getenv("MC_BASE", "").rstrip("/")
    token = os.getenv("MC_TOKEN", "")
    path = os.getenv("MC_OBJECT_PATH", "")

    assert base and token, "MC_BASE/MC_TOKEN missing"
    headers = {"Authorization": f"Bearer {token}"}

    # 1) Base + token check
    r = requests.get(f"{base}/objects", headers=headers, timeout=30)
    print("GET /objects ->", r.status_code)
    if r.status_code == 404:
        return {"ok": False, "hint": "Wrong base URL or missing /api."}
    if r.status_code in (401, 403):
        return {"ok": False, "hint": "Auth token invalid/expired or lacks scope."}

    # 2) If you already set MC_OBJECT_PATH, check it exists
    if path:
        r2 = requests.options(f"{base}/{path.lstrip('/')}", headers=headers, timeout=30)
        print(f"OPTIONS {path} ->", r2.status_code, r2.headers.get("Allow"))
        if r2.status_code == 404:
            return {"ok": False, "hint": f"Object path {path} likely wrong; discover the object key from /objects."}

    return {"ok": True, "hint": "Base URL & token look good. If import still fails, inspect payload/field names."}

def _connect_with_api_key() -> str:
    """
    Establish connection with MasterControl using API key.
    Returns the connectionID from the response.
    """
    if not (MC_BASE and MC_TOKEN):
        raise RuntimeError("Missing MC_BASE/MC_TOKEN configuration")
    
    # Extract base domain and construct correct endpoint URL
    # The correct endpoint is: https://sts009.mastercontrol.com/sts009/ws/jsonBridge.cfm
    if "/api" in MC_BASE:
        base_domain = MC_BASE.replace("/api", "").rstrip("/")
    else:
        base_domain = MC_BASE.rstrip("/")
    
    # MasterControl endpoint includes /sts009/ in the path
    url = f"{base_domain}/sts009/ws/jsonBridge.cfm"
    
    connect_payload = {
        "arguments": {
            "apiKey": MC_TOKEN,
            "logoutCurrentWebConnection": False
        },
        "methodName": "connectWithApiKey",
        "serviceName": "ConnectionService"
    }
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Connecting to MasterControl: {url}")
    
    resp = requests.post(url, headers=HEADERS, json=connect_payload, timeout=60)
    
    logger.info(f"ConnectionService response status: {resp.status_code}")
    logger.debug(f"ConnectionService response text: {resp.text[:500]}")
    
    if resp.status_code != 200:
        raise RuntimeError(f"ConnectionService failed: {resp.status_code} {resp.text[:200]}")
    
    try:
        # Log raw response for debugging
        logger.debug(f"ConnectionService raw response text: {resp.text[:1000]}")
        
        # Try to parse as JSON
        try:
            response_data = resp.json()
        except json.JSONDecodeError as json_err:
            # If not JSON, log and raise
            logger.error(f"ConnectionService returned non-JSON response: {resp.text[:500]}")
            raise RuntimeError(f"ConnectionService returned invalid response (not JSON): {resp.text[:200]}")
        
        logger.info(f"ConnectionService response type: {type(response_data)}")
        logger.info(f"ConnectionService response content: {str(response_data)[:500]}")
        
        # Handle if response is not a dict (e.g., string or list)
        if not isinstance(response_data, dict):
            logger.error(f"ConnectionService response is not a dict (type: {type(response_data)}): {response_data}")
            # If it's a string error message, raise it
            if isinstance(response_data, str):
                raise RuntimeError(f"ConnectionService returned string error: {response_data}")
            raise RuntimeError(f"ConnectionService returned unexpected response type {type(response_data)}: {response_data}")
        
        # Check if response contains an error
        if "error" in response_data:
            error_msg = response_data.get("error", {})
            if isinstance(error_msg, dict):
                error_msg = error_msg.get("message", str(error_msg))
            logger.error(f"ConnectionService returned error: {error_msg}")
            raise RuntimeError(f"ConnectionService error: {error_msg}")
        
        # Extract connectionID from response
        # MasterControl returns it as: {"result": "connectionID-string"} or {"arguments": {"connectionID": "..."}}
        connection_id = None
        
        if isinstance(response_data, dict):
            # Check if result is a string (the connectionID itself)
            if "result" in response_data:
                result_value = response_data.get("result")
                if isinstance(result_value, str):
                    # result is the connectionID string directly
                    connection_id = result_value
                elif isinstance(result_value, dict):
                    # result is a dict, check for connectionID inside it
                    connection_id = result_value.get("connectionID")
            
            # Also check other possible locations
            if not connection_id:
                # Check arguments.connectionID
                if "arguments" in response_data and isinstance(response_data.get("arguments"), dict):
                    connection_id = response_data.get("arguments", {}).get("connectionID")
                # Check top-level connectionID
                if not connection_id and "connectionID" in response_data:
                    connection_id = response_data.get("connectionID")
                # Check data.connectionID
                if not connection_id and "data" in response_data and isinstance(response_data.get("data"), dict):
                    connection_id = response_data.get("data", {}).get("connectionID")
        
        if not connection_id:
            # If connectionID not in response, log full response for debugging
            logger.error(f"ConnectionService response didn't contain connectionID. Full response: {json.dumps(response_data, indent=2)}")
            # Try to use provided MC_CONNECTION_ID as fallback
            if MC_CONNECTION_ID:
                logger.warning(f"Using provided MC_CONNECTION_ID as fallback: {MC_CONNECTION_ID}")
                return MC_CONNECTION_ID
            else:
                raise RuntimeError(f"Could not extract connectionID from ConnectionService response: {response_data}")
        
        logger.info(f"Successfully connected. ConnectionID obtained: {connection_id[:50]}...")
        return connection_id
        
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Error parsing ConnectionService response: {e}")
        logger.error(f"Response text was: {resp.text[:500]}")
        raise RuntimeError(f"Failed to parse connection response: {e}")

# Map Smart Risk fields → MasterControl field identifiers (from Postman)
FIELD_MAP = {
    "COMPONENT": "Component",
    "FUNCTION": "Function",
    "FAILURE MODE": "FailureMode",
    "EFFECTS": "Effects",
    "SEVERITY": "Severity",
    "CAUSES": "Causes",
    "OCCURRENCE": "Occurrence",
    "CONTROLS": "Controls",
    "DETECTION": "Detection",
    "RPN": "RPN",
    "ACTIONS": "Actions",
    "OWNER": "Owner",
    "DUE DATE": "DueDate",
    "STATUS": "Status",
    "DOC LINK": "DocLink"
}

def _str_or_empty(v: Optional[Any]) -> str:
    """Convert value to string, empty string if None"""
    if v is None:
        return ""
    return str(v).strip()

def smart_risk_row_to_mc_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Smart Risk FMEA row to MasterControl TaskService launchProcess payload format.
    Returns the complete payload structure matching the Postman format.
    """
    aliases = {
        "component": "COMPONENT", "function": "FUNCTION",
        "failure_mode": "FAILURE MODE", "effects": "EFFECTS",
        "severity": "SEVERITY", "causes": "CAUSES",
        "occurrence": "OCCURRENCE", "controls": "CONTROLS",
        "detection": "DETECTION", "rpn": "RPN", "actions": "ACTIONS",
        "owner": "OWNER", "due_date": "DUE DATE", "status": "STATUS", "doc_link": "DOC LINK"
    }

    # Normalize input keys to Smart Risk header names
    src = {}
    for k, v in row.items():
        K = k
        if K not in FIELD_MAP and K.lower() in aliases:
            K = aliases[K.lower()]
        src[K] = v

    # Build fields array matching MasterControl format
    fields = []
    
    # Map all known fields
    field_identifiers = {
        "Component": "Component",
        "Function": "Function",
        "FailureMode": "FailureMode",
        "Effects": "Effects",
        "Severity": "Severity",
        "Causes": "Causes",
        "Occurrence": "Occurrence",
        "Controls": "Controls",
        "Detection": "Detection",
        "RPN": "RPN",
        "Actions": "Actions",
        "Owner": "Owner",
        "DueDate": "DueDate",
        "Status": "Status",
        "DocLink": "DocLink"
    }
    
    # Add fields with values from input
    for src_key, identifier in FIELD_MAP.items():
        if src_key in src:
            value = _str_or_empty(src[src_key])
            fields.append({
                "custom": False,
                "label": identifier,
                "identifier": identifier,
                "value": value
            })
    
    # Add required empty fields that MasterControl expects
    required_empty_fields = [
        "CloseOut", "mastercontrol.route.stepnameat.step2", "mastercontrol.route.stepnameat.step1",
        "mastercontrol.route.stepnameat.step3", "mastercontrol.route.stepduedate", "Notes",
        "mastercontrol.attachments.Review", "Reviewed_Supervisor", "Reviewed_Trainer",
        "mastercontrol.route.esig.timestamps.step1", "mastercontrol.route.esig.users.step1",
        "mastercontrol.route.esig.sigstatus.step1", "mastercontrol.route.esig.timestamps.step2",
        "mastercontrol.route.esig.users.step2", "mastercontrol.route.esig.sigstatus.step2",
        "mastercontrol.route.esig.timestamps.step3", "mastercontrol.route.esig.users.step3",
        "mastercontrol.route.esig.sigstatus.step3", "headerText", "VerificationPoint",
        "Verified_Supervisor", "Verified_Trainer"
    ]
    
    # Create a set of already added identifiers to avoid duplicates
    added_identifiers = {field["identifier"] for field in fields}
    
    for identifier in required_empty_fields:
        if identifier not in added_identifiers:
            # Extract label from identifier for readability
            label = identifier.replace("mastercontrol.", "").replace("route.", "").replace(".", " ").title()
            fields.append({
                "custom": False,
                "label": label,
                "identifier": identifier,
                "value": ""
            })
    
    # Set headerText to "Test" as shown in Postman example
    header_text_field = next((f for f in fields if f["identifier"] == "headerText"), None)
    if header_text_field:
        header_text_field["value"] = "Test"

    # Build complete payload structure
    # Note: connectionID will be set when making the actual request via _post_one
    payload = {
        "arguments": {
            "processTask": {
                "formInfoCard": {},
                "message": "",
                "userSignoffSteps": [],
                "signoffStatuses": [],
                "routename": "SmartRisk_Workflow",
                "fields": fields,
                "name": "SmartRisk_Workflow",
                "type": "process",
                "originator": "",
                "allSignoffSteps": []
            }
        },
        "methodName": "launchProcess",
        "serviceName": "TaskService"
    }

    # Validation
    if not any(f["identifier"] == "Component" and f["value"] for f in fields):
        raise ValueError("Missing required field: Component")
    if not any(f["identifier"] == "FailureMode" and f["value"] for f in fields):
        raise ValueError("Missing required field: FailureMode")

    return payload

@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
def _post_one(payload: Dict[str, Any], connection_id: Optional[str] = None) -> requests.Response:
    """
    Post payload to MasterControl TaskService.
    If connection_id is provided, uses it; otherwise gets connectionID via API key.
    """
    if not (MC_BASE and MC_TOKEN):
        raise RuntimeError("Missing MC_BASE/MC_TOKEN configuration")
    
    # Get connection ID if not provided
    if not connection_id:
        connection_id = _connect_with_api_key()
    
    # Update payload with connection ID
    if "arguments" in payload and "connectionID" not in payload["arguments"]:
        payload["arguments"]["connectionID"] = connection_id
    
    # Extract base domain and construct correct endpoint URL
    # The correct endpoint is: https://sts009.mastercontrol.com/sts009/ws/jsonBridge.cfm
    if "/api" in MC_BASE:
        base_domain = MC_BASE.replace("/api", "").rstrip("/")
    else:
        base_domain = MC_BASE.rstrip("/")
    
    # MasterControl endpoint includes /sts009/ in the path
    url = f"{base_domain}/sts009/ws/jsonBridge.cfm"
    
    # Log for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Posting to MasterControl: {url}")
    logger.info(f"Headers: {HEADERS}")
    logger.info(f"Payload serviceName: {payload.get('serviceName')}, methodName: {payload.get('methodName')}")
    logger.info(f"ConnectionID: {payload.get('arguments', {}).get('connectionID', 'NOT SET')[:50]}...")
    logger.debug(f"Full payload: {json.dumps(payload, indent=2)}")
    
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=60)
    
    # Log response for debugging
    logger.info(f"MasterControl response status: {resp.status_code}")
    if resp.status_code != 200:
        logger.warning(f"MasterControl error response: {resp.text[:1000]}")
    else:
        logger.info(f"MasterControl success response: {resp.text[:500]}")
    
    # Retry only on 5xx
    if 500 <= resp.status_code < 600:
        raise RuntimeError(f"MasterControl 5xx: {resp.status_code} {resp.text[:200]}")
    return resp

def push_batch(rows: List[Dict[str, Any]], rate_limit_sec: float = 0.0) -> List[Dict[str, Any]]:
    """
    Returns per-row results:
    [{index, status, id, error, payload}]
    
    Establishes a new connection for each row to ensure fresh connectionID for each FMEA record.
    """
    results = []
    import logging
    logger = logging.getLogger(__name__)
    
    # Process each row with a fresh connection
    for i, row in enumerate(rows):
        connection_id = None
        try:
            # Establish connection for this row
            connection_id = _connect_with_api_key()
            logger.info(f"Row {i}: Established connection, ConnectionID: {connection_id[:50]}...")
            
            # Create payload for this row
            payload = smart_risk_row_to_mc_payload(row)
            
            # Update connectionID in payload
            payload["arguments"]["connectionID"] = connection_id
            
            # Send the TaskService.launchProcess request
            resp = _post_one(payload, connection_id=connection_id)
            
            # Extract record ID from response
            rec_id = None
            try:
                response_data = resp.json()
                logger.debug(f"Row {i} response: {json.dumps(response_data, indent=2)[:500]}")
                # Try to extract record ID from various possible response structures
                rec_id = (
                    response_data.get("result", {}).get("id") or
                    response_data.get("arguments", {}).get("id") or
                    response_data.get("id") or
                    response_data.get("data", {}).get("id")
                )
            except Exception as parse_error:
                logger.debug(f"Row {i}: Could not parse response as JSON: {parse_error}")
            
            results.append({"index": i, "status": resp.status_code, "id": rec_id, "error": None})
            
        except Exception as e:
            logger.error(f"Row {i}: Error processing row: {str(e)}")
            results.append({"index": i, "status": None, "id": None, "error": str(e)})
        
        # Rate limiting between rows
        if rate_limit_sec and i < len(rows) - 1:  # Don't sleep after last row
            time.sleep(rate_limit_sec)
    
    return results
