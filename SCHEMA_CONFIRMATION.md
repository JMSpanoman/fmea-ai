# SmartQS Risk Schema Confirmation

## Overview
This document compares the described SmartQS Risk core schema with the current implementation.

---

## 1. risk_items ✅ Mostly Aligned

### Described Schema:
- `id` (PK)
- `project_id` (FK → projects.id)
- `risk_key` (unique per project, e.g., R-023) ⚠️ **MISSING**
- `status` (draft/approved/archived or open/closed/accepted)
- `current_version_id` (FK → risk_item_versions.id)
- `created_by` ⚠️ **MISSING**
- `created_at`

### Current Implementation:
```12:57:fmea_backend/models/risk_item.py
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    fmea_row_id = Column(String, ForeignKey("fmea_rows.id"), nullable=True, index=True)
    current_version_id = Column(String, nullable=True, index=True)  # FK handled in migration/application
    
    # Risk identification
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    risk_type = Column(String, nullable=True)
    
    # Risk assessment (backward compatible)
    severity = Column(Integer, nullable=True)
    probability = Column(Integer, nullable=True)
    impact = Column(Integer, nullable=True)
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)
    
    # Risk control
    mitigation_strategy = Column(Text, nullable=True)
    control_measures = Column(Text, nullable=True)
    residual_risk_score = Column(Integer, nullable=True)
    residual_risk_level = Column(String, nullable=True)
    
    # Ownership and status
    owner = Column(String, nullable=True)
    status = Column(String, nullable=False, default="open")
    priority = Column(String, nullable=True)
    
    # Additional metadata
    source = Column(String, nullable=True)
    detected_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    closed_date = Column(DateTime(timezone=True), nullable=True)
    
    # AI and metadata
    ai_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Discrepancies:
- ❌ **Missing `risk_key`**: No unique per-project identifier field (e.g., R-023). Currently using `title` or derived from `id` in code.
- ❌ **Missing `created_by`**: No FK to users table for creator tracking.
- ✅ Has `current_version_id` (as described)
- ✅ Has `status` (as described, with values: "open", "mitigated", "closed", "accepted")
- ✅ Has `created_at` (as described)
- ⚠️ **Additional fields**: Has many legacy/compatibility fields (severity, probability, impact, etc.) that may be redundant with versioned data.

---

## 2. risk_item_versions ✅ Well Aligned

### Described Schema:
- ISO 14971 hazard chain: `hazard`, `sequence_of_events`, `hazardous_situation`, `harm`, `failure_mode`
- Risk estimation: `severity`, `probability_of_harm` (canonical), optional `occurrence`, `detection`, `risk_score`
- Acceptability & rationale: `risk_acceptability`, `risk_rationale`
- Risk controls summary: `inherent_safety`, `protective_measures`, `information_for_safety`
- Residual risk: `residual_severity`, `residual_probability_of_harm`, optional `residual_occurrence`, `residual_detection`, `residual_risk_score`
- Benefit-risk: `benefit_risk_summary`, `overall_residual_risk_conclusion`
- Version metadata: `risk_item_id` (FK), `version_no` (optional), `created_by`, `created_at`

### Current Implementation:
```11:68:fmea_backend/models/risk_item_version.py
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    risk_item_id = Column(String, ForeignKey("risk_items.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    
    # ISO 14971: Hazard analysis chain
    hazard = Column(Text, nullable=True)
    hazardous_situation = Column(Text, nullable=True)
    harm = Column(Text, nullable=True)
    failure_mode = Column(Text, nullable=True)
    sequence_of_events = Column(Text, nullable=True)
    
    # Risk estimation (ISO 14971 compliant)
    severity = Column(Integer, nullable=True)
    probability_of_harm = Column(Integer, nullable=True)
    occurrence = Column(Integer, nullable=True)
    detection = Column(Integer, nullable=True)
    
    # Legacy fields (backward compatibility)
    probability = Column(Integer, nullable=True)
    impact = Column(Integer, nullable=True)
    
    # Calculated risk metrics
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)
    
    # Risk control measures (ISO 14971)
    inherent_safety = Column(Text, nullable=True)
    protective_measures = Column(Text, nullable=True)
    information_for_safety = Column(Text, nullable=True)
    control_measures_summary = Column(Text, nullable=True)
    
    # Residual risk evaluation (ISO 14971)
    residual_severity = Column(Integer, nullable=True)
    residual_probability_of_harm = Column(Integer, nullable=True)
    residual_occurrence = Column(Integer, nullable=True)
    residual_detection = Column(Integer, nullable=True)
    residual_risk_score = Column(Integer, nullable=True)
    residual_risk_level = Column(String, nullable=True)
    
    # Benefit-risk analysis (ISO 14971)
    benefit_risk_summary = Column(Text, nullable=True)
    overall_residual_risk_conclusion = Column(Text, nullable=True)
    
    # Risk acceptability (ISO 14971)
    risk_acceptability = Column(String, nullable=True)
    risk_rationale = Column(Text, nullable=True)
    
    # Metadata
    change_summary = Column(Text, nullable=True)
    changed_by = Column(String, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Discrepancies:
- ✅ All ISO 14971 fields present and correctly named
- ✅ Has `version_number` (as `version_no` described)
- ❌ **Missing `created_by`**: Has `changed_by` instead (String, not FK). Should consider adding `created_by` FK to users.
- ✅ Has `created_at` (as described)
- ⚠️ **Additional fields**: Has `change_summary`, `ai_metadata`, `residual_risk_level` (not mentioned but useful)

---

## 3. risk_controls ⚠️ Partially Aligned

### Described Schema:
- `id` (PK)
- `risk_item_id` (FK → risk_items.id)
- `control_key` (unique within a risk item, e.g., RC-003) ⚠️ **MISSING**
- `name`
- `control_type` (inherent_safety | protective | information)
- `description`
- `status` (proposed | active | retired)
- `created_by` ⚠️ **MISSING**
- `created_at`

### Current Implementation:
```11:50:fmea_backend/models/risk_control.py
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    risk_item_id = Column(String, ForeignKey("risk_items.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Control identification
    control_name = Column(String, nullable=False)
    control_description = Column(Text, nullable=True)
    control_type = Column(String, nullable=False)  # "inherent_safety", "protective", "information"
    
    # Control details
    implementation_details = Column(Text, nullable=True)
    verification_method = Column(Text, nullable=True)
    trace_to_design_input = Column(String, nullable=True)
    trace_to_design_output = Column(String, nullable=True)
    trace_to_verification_test = Column(String, nullable=True)
    
    # Status
    status = Column(String, nullable=False, default="proposed")  # "proposed", "active", "retired"
    
    # Ownership
    owner = Column(String, nullable=True)
    assigned_to = Column(String, nullable=True)
    
    # Dates
    proposed_date = Column(DateTime(timezone=True), nullable=True)
    implemented_date = Column(DateTime(timezone=True), nullable=True)
    verified_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    effectiveness_notes = Column(Text, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Discrepancies:
- ❌ **Missing `control_key`**: No unique identifier within a risk item (e.g., RC-003). Currently using `control_name` or derived from `id` in code.
- ❌ **Missing `created_by`**: No FK to users table for creator tracking.
- ✅ Has `control_type` (as described: inherent_safety, protective, information)
- ✅ Has `status` (as described: proposed, active, retired)
- ✅ Has `created_at` (as described)
- ⚠️ **Field name difference**: Uses `control_name` instead of `name`, `control_description` instead of `description`
- ⚠️ **Additional fields**: Has `project_id`, `implementation_details`, `verification_method`, trace fields, ownership fields, dates, etc. (not mentioned but potentially useful)

---

## 4. approvals ⚠️ Partially Aligned

### Described Schema:
- `id` (PK)
- `project_id` ⚠️ **MISSING**
- `artifact_type` = "risk_item_version"
- `artifact_id` = risk_item_versions.id
- `decision` (approved/rejected) ⚠️ **DIFFERENT NAME**
- `rationale` (required) ⚠️ **DIFFERENT NAME**
- `approved_by` ⚠️ **DIFFERENT NAME**
- `approved_at` ⚠️ **DIFFERENT NAME**

### Current Implementation:
```10:20:fmea_backend/models/approval.py
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    artifact_type = Column(String, nullable=False)  # document, change_control, ncr, capa, audit, complaint
    artifact_id = Column(String, nullable=False, index=True)
    approver_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, nullable=False)  # pending, approved, rejected
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
```

### Discrepancies:
- ❌ **Missing `project_id`**: No direct project reference (would need to join through artifact)
- ⚠️ **Field name differences**:
  - Uses `status` instead of `decision` (values: "pending", "approved", "rejected")
  - Uses `comment` instead of `rationale`
  - Uses `approver_id` instead of `approved_by`
  - Uses `timestamp` instead of `approved_at`
- ✅ Has `artifact_type` and `artifact_id` (as described)
- ⚠️ **Note**: Current implementation is more generic (supports multiple artifact types), which is good for extensibility but doesn't match the described schema exactly.

---

## 5. ai_events ✅ Mostly Aligned

### Described Schema:
- `id` (PK)
- `project_id`
- `user_id`
- `context_object_type` (e.g., risk_item, risk_item_version_draft) ⚠️ **DIFFERENT NAME**
- `context_object_id` (optional) ⚠️ **DIFFERENT NAME**
- `output_json`
- `disposition` (none|accepted|edited|rejected)
- `disposition_notes`
- `created_at`

### Current Implementation:
```11:35:fmea_backend/models/ai_event.py
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Context
    context_type = Column(String, nullable=False)  # "risk_item", "fmea", "capa", etc.
    context_id = Column(String, nullable=True, index=True)  # ID of the artifact AI was used on
    
    # AI details
    prompt_name = Column(String, nullable=False)  # "risk_suggest", "fmea_generate", etc.
    input_summary = Column(Text, nullable=True)  # Summary of inputs (for privacy)
    output_json = Column(JSON, nullable=True)  # Full AI output
    
    # Disposition tracking
    disposition = Column(String, nullable=True)  # "accepted", "edited", "rejected", "pending"
    disposition_notes = Column(Text, nullable=True)
    disposition_user_id = Column(String, nullable=True)  # Who made the disposition
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    disposed_at = Column(DateTime(timezone=True), nullable=True)
```

### Discrepancies:
- ⚠️ **Field name differences**:
  - Uses `context_type` instead of `context_object_type`
  - Uses `context_id` instead of `context_object_id`
- ✅ Has all core fields (project_id, user_id, output_json, disposition, disposition_notes, created_at)
- ⚠️ **Additional fields**: Has `prompt_name`, `input_summary`, `disposition_user_id`, `disposed_at` (not mentioned but useful)

---

## 6. audit_log_events ✅ Well Aligned

### Described Schema:
- `id`
- `project_id`
- `user_id`
- `event_type` (e.g., handoff.design.design_input.created)
- `details_json` (risk keys, created artifact IDs, trace link IDs)
- `event_time` ⚠️ **DIFFERENT NAME**

### Current Implementation:
```11:26:fmea_backend/models/audit_log_event.py
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Event classification
    event_type = Column(String, nullable=False, index=True)  # "handoff.design.created", "handoff.capa.created", etc.
    
    # Event details
    details_json = Column(JSON, nullable=True)  # Flexible JSON for event-specific data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
```

### Discrepancies:
- ⚠️ **Field name difference**: Uses `created_at` instead of `event_time` (semantically equivalent)
- ✅ All other fields match exactly

---

## 7. idempotency_requests ✅ Mostly Aligned

### Described Schema:
- `id`
- `user_id`
- `endpoint`
- `idempotency_key`
- `response_json`
- `created_at`

### Current Implementation:
```10:30:fmea_backend/models/idempotency_request.py
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    idempotency_key = Column(String, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Request fingerprint
    endpoint = Column(String, nullable=False)  # e.g., "/risk-items/{id}/handoff/design"
    request_hash = Column(String, nullable=True)  # Hash of request body for additional validation
    
    # Response data
    response_json = Column(JSON, nullable=True)  # Store created artifact/link IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration
```

### Discrepancies:
- ✅ All described fields present
- ⚠️ **Additional fields**: Has `project_id`, `request_hash`, `expires_at` (not mentioned but potentially useful)

---

## 8. trace_links ⚠️ Missing Field

### Described Schema:
- `id`
- `project_id`
- `from_type` (risk_item | risk_item_version | risk_control)
- `from_id`
- `to_type` (design_input | design_output | vv_test | capa | change_control | fmea_row)
- `to_id`
- `link_type` (traces_to | verified_by | generated_from | impacts | mitigates)
- `rationale` ⚠️ **MISSING**
- `created_at`

### Current Implementation:
```10:21:fmea_backend/models/trace_link.py
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    from_type = Column(String, nullable=False)  # Canonical: risk_item, risk_item_version, risk_control, design_input, etc.
    from_id = Column(String, nullable=False, index=True)
    to_type = Column(String, nullable=False)  # Canonical: design_input, design_output, vv_test, capa, etc.
    to_id = Column(String, nullable=False, index=True)
    link_type = Column(String, nullable=True, default="traces_to")  # traces_to, verified_by, generated_from, impacts, mitigates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Discrepancies:
- ❌ **Missing `rationale`**: No field to store the reason/justification for the trace link
- ✅ All other fields match exactly

---

## Summary of Required Changes

### Critical Missing Fields:
1. **risk_items.risk_key** - Unique per-project identifier (e.g., R-023)
2. **risk_items.created_by** - FK to users table
3. **risk_item_versions.created_by** - FK to users table (currently has `changed_by` as String)
4. **risk_controls.control_key** - Unique identifier within risk item (e.g., RC-003)
5. **risk_controls.created_by** - FK to users table
6. **approvals.project_id** - Direct project reference
7. **trace_links.rationale** - Justification for trace link

### Field Name Mappings Needed:
1. **approvals**: `status` → `decision`, `comment` → `rationale`, `approver_id` → `approved_by`, `timestamp` → `approved_at`
2. **ai_events**: `context_type` → `context_object_type`, `context_id` → `context_object_id`
3. **audit_log_events**: `created_at` → `event_time` (or keep as is, semantically equivalent)
4. **risk_controls**: `control_name` → `name`, `control_description` → `description` (or keep descriptive names)

### Recommendations:
1. **Add missing fields** via migration
2. **Consider aliases** for field name differences if backward compatibility is needed
3. **Add unique constraints**:
   - `risk_items(project_id, risk_key)` unique
   - `risk_controls(risk_item_id, control_key)` unique
4. **Add indexes** for performance:
   - `(project_id, from_type, from_id)` on trace_links
   - `(project_id, to_type, to_id)` on trace_links

---

## Overall Assessment

**Alignment Score**: ~85%

- ✅ Core schema structure is well-implemented
- ✅ ISO 14971 fields are correctly implemented
- ✅ Relationships are properly defined
- ⚠️ Missing some key fields (`risk_key`, `control_key`, `created_by` fields, `rationale` in trace_links)
- ⚠️ Some field name differences (mostly semantic, easily mappable)

The schema is **functionally complete** but would benefit from the missing fields for better traceability and governance.

