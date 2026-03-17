# V&V from Risk – Calculation-Based Feature

This document describes the **calculation-based** V&V generation from FMEA/risk rows: sample request/response, schema, and local run instructions.

## Local run instructions

### Backend

```bash
cd fmea_backend
# Optional: use a local DB
export DATABASE_URL="sqlite:///./fmea.db"
# Optional: if port 8000 is in use
export PORT=8001
uvicorn main:app --reload --port ${PORT:-8000}
```

Ensure `OPENAI_API_KEY` is set for AI generation.

### Frontend

```bash
cd frontend
# If backend runs on 8001:
export VITE_API_BASE_URL=http://localhost:8001/api
npm run dev
```

### New DB columns (optional)

If the database was created before the calculation-based update, add the new columns for saved V&V:

```sql
-- SQLite
ALTER TABLE generated_vv_records ADD COLUMN validation_test_name VARCHAR(512);
ALTER TABLE generated_vv_records ADD COLUMN validation_objective TEXT;
```

If you use a fresh DB, tables are created with all columns automatically.

---

## Sample request (POST /api/ai/vv/generate-from-risk)

```json
{
  "component": "Battery management IC",
  "failure_mode": "Over-discharge below safe voltage",
  "effect": "Cell damage; reduced capacity; safety risk",
  "cause": "Missing or delayed low-voltage cutoff",
  "severity": 4,
  "occurrence": 2,
  "detection": 3,
  "mitigation": "Hardware UVLO + software monitoring with alarm and shutdown"
}
```

---

## Sample response (calculation-based schema)

```json
{
  "verification_test_name": "UVLO Verification – Threshold and Response Time",
  "verification_objective": "Verify that under-voltage lockout engages at or above the specified minimum cell voltage and that alarm/shutdown occur within the required time window.",
  "verification_method": "Apply programmable load to discharge cell; record voltage at which UVLO triggers and time from fault introduction to alarm and to shutdown. Use calibrated DMM and timer.",
  "validation_test_name": "Battery Protection Validation – User Scenario",
  "validation_objective": "Demonstrate that in intended use the device prevents over-discharge and provides clear alarm before shutdown.",
  "validation_method_or_scenario": "Simulate typical use until low-voltage condition; confirm alarm is presented and device shuts down before cell reaches minimum safe voltage; record response time and remaining capacity.",
  "acceptance_criteria": [
    "UVLO engages at or above 2.8 V per cell (measured).",
    "Alarm is presented within 5 s of crossing threshold.",
    "Shutdown occurs within 30 s of alarm or before cell reaches 2.5 V, whichever is earlier.",
    "Percent Error = |Measured Threshold - 2.8| / 2.8 × 100 ≤ 2%."
  ],
  "calculations": [
    {
      "name": "Percent Error",
      "formula": "|Measured - Target| / Target × 100",
      "description": "Relative error of UVLO threshold vs design target (2.8 V).",
      "inputs": ["Measured", "Target"],
      "unit_or_threshold": "%"
    },
    {
      "name": "Response Time",
      "formula": "Alarm Time - Fault Introduction Time",
      "description": "Time from crossing threshold to alarm presentation.",
      "inputs": ["Alarm Time", "Fault Introduction Time"],
      "unit_or_threshold": "seconds"
    }
  ],
  "worst_case_conditions": [
    "Minimum specified operating temperature",
    "Aged cell near end of life",
    "Maximum load current during test"
  ],
  "sample_size_rationale": "Per risk level: n=3 units for verification; n=5 for validation scenarios.",
  "traceability": {
    "source_component": "Battery management IC",
    "source_failure_mode": "Over-discharge below safe voltage",
    "source_effect": "Cell damage; reduced capacity; safety risk",
    "source_cause": "Missing or delayed low-voltage cutoff",
    "source_mitigation": "Hardware UVLO + software monitoring with alarm and shutdown",
    "source_severity": 4,
    "source_occurrence": 2,
    "source_detection": 3,
    "source_rpn": 24
  }
}
```

---

## Risk-based rigor (prompt logic)

- **Low risk** (severity ≤ 2 and occurrence ≤ 2): simple bench verification, brief acceptance criteria, calculations optional.
- **Medium risk** (severity ≥ 3): verification + validation scenario, at least one explicit quantitative calculation, measurable acceptance criteria.
- **High risk** (severity ≥ 4 or RPN above threshold): detailed V&V, worst-case conditions, at least one explicit formula, stronger measurable acceptance criteria, sample size rationale, protocol-like language.

---

## Response schema (summary)

| Field | Type | Notes |
|-------|------|--------|
| `verification_test_name` | string | Short test name |
| `verification_objective` | string | What verification must demonstrate |
| `verification_method` | string | How the test is performed |
| `validation_test_name` | string? | Short validation test name |
| `validation_objective` | string? | What validation must demonstrate |
| `validation_method_or_scenario` | string? | Validation scenario/method |
| `acceptance_criteria` | string[] | Measurable criteria |
| `calculations` | CalculationItem[] | name, formula, description?, inputs?, unit_or_threshold? |
| `worst_case_conditions` | string[] | Stress conditions |
| `sample_size_rationale` | string? | Rationale for n |
| `traceability` | TraceabilityBlock | source_component, source_failure_mode, source_effect?, source_cause?, source_mitigation, source_severity?, source_occurrence?, source_detection?, source_rpn? |

Backend normalizes missing or malformed fields (e.g. single string → array, traceability filled from request) so the UI does not crash on incomplete model output.
