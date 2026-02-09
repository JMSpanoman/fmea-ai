---
title: Risk Analysis (Template)
standard: ISO 14971-style
doc_type: risk_analysis
document_id: RA-TEMPLATE
project: "{{PROJECT_NAME}}"
owner: "{{DOCUMENT_OWNER}}"
version: "0.1"
status: draft
effective_date: "{{EFFECTIVE_DATE}}"
---

# Risk Analysis (ISO 14971-style)

## Document control

- **Product / system**: {{PRODUCT_NAME}}
- **Project**: {{PROJECT_NAME}}
- **Document ID**: {{DOCUMENT_ID}}
- **Owner**: {{DOCUMENT_OWNER}}
- **Approver(s)**: {{APPROVERS}}
- **Effective date**: {{EFFECTIVE_DATE}}
- **Related documents**:
  - Risk Management Plan (RMP): {{RMP_REFERENCE}}
  - Risk Acceptability Criteria: {{RISK_ACCEPTABILITY_REFERENCE}}
  - Hazard Analysis: {{HAZARD_ANALYSIS_REFERENCE}}
  - Risk Controls / Verification: {{VERIFICATION_REFERENCE}}
  - Benefit–risk analysis (if applicable): {{BENEFIT_RISK_REFERENCE}}

---

## 1) Purpose & Scope

### Purpose

This document identifies hazards and evaluates risks for {{PRODUCT_NAME}} in accordance with ISO 14971. It documents risk controls, verification, and residual risk evaluation.

### Scope

- **Included configurations / variants**: {{INCLUDED_CONFIGURATIONS}}
- **Included accessories / consumables**: {{INCLUDED_ACCESSORIES}}
- **Excluded use cases / out of scope**: {{OUT_OF_SCOPE}}
- **Lifecycle coverage**: {{LIFECYCLE_COVERAGE}}
- **Interfaces considered** (device / user / environment / external systems): {{INTERFACES_CONSIDERED}}

## 2) Intended Use, Users, Use Environment

- **Intended use**: {{INTENDED_USE}}
- **Intended users**: {{INTENDED_USERS}}
- **Use environment**: {{USE_ENVIRONMENT}}
- **User population / patient population** (if applicable): {{POPULATION}}
- **Key safety characteristics** (safety-related functions/outputs): {{KEY_SAFETY_CHARACTERISTICS}}

## 3) Foreseeable Misuse (top 5)

List the top reasonably foreseeable misuse scenarios that could lead to hazardous situations.

1. {{MISUSE_1}}
2. {{MISUSE_2}}
3. {{MISUSE_3}}
4. {{MISUSE_4}}
5. {{MISUSE_5}}

## 4) Risk Acceptability Framework (brief)

Summarize the risk acceptability framework and decision rules used for this analysis.

- **Framework summary**: {{RISK_ACCEPTABILITY_SUMMARY}}
- **Reference to RMP**: {{RMP_REFERENCE}}
- **Decision rules** (e.g., acceptable/ALARP/unacceptable regions; escalation/approval requirements): {{DECISION_RULES}}

### Decision Preconditions

The following must be completed and approved prior to final risk acceptance:

- Approved Risk Management Plan
- Completed Hazard Analysis
- Versioned Residual Risk Evaluation
- Verification of applicable risk controls

## 5) Hazard → Hazardous Situation → Harm mapping

Provide traceability from hazard identification through hazardous situation to harm.

### Mapping table

| Hazard ID | Hazard | Hazardous Situation ID | Hazardous Situation | Harm ID | Harm | Initiating events / notes |
|---|---|---|---|---|---|---|
| HZ-001 | {{HZ_001}} | HS-001 | {{HS_001}} | HM-001 | {{HM_001}} | {{NOTES_001}} |
| HZ-002 | {{HZ_002}} | HS-002 | {{HS_002}} | HM-002 | {{HM_002}} | {{NOTES_002}} |
| HZ-003 | {{HZ_003}} | HS-003 | {{HS_003}} | HM-003 | {{HM_003}} | {{NOTES_003}} |

## 6) Risk estimation: Initial (pre-control) vs Residual (post-control)

### Scoring assumptions

Define the scoring model used in this document.

- **Severity (S)** scale definition: {{SEVERITY_SCALE}}
- **Probability of harm (P)** scale definition: {{PROBABILITY_SCALE}}
- **Detectability (D)** *(if used)* scale definition: {{DETECTION_SCALE}}
- **Risk index calculation**: {{RISK_INDEX_DEFINITION}}  
  Examples: \(RPN = S \times P \times D\), or risk matrix category.

### Risk evaluation table (traceable)

| Risk ID | Hazard ID | Hazardous Situation ID | Harm ID | Initial S | Initial P | Initial D | Initial Risk Index | Risk controls (IDs) | Residual S | Residual P | Residual D | Residual Risk Index | Residual acceptable? | Benefit–risk needed? |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|---|
| RSK-001 | HZ-001 | HS-001 | HM-001 | {{S0_001}} | {{P0_001}} | {{D0_001}} | {{R0_001}} | {{RC_001_LIST}} | {{S1_001}} | {{P1_001}} | {{D1_001}} | {{R1_001}} | {{ACC_001}} | {{BR_001}} |
| RSK-002 | HZ-002 | HS-002 | HM-002 | {{S0_002}} | {{P0_002}} | {{D0_002}} | {{R0_002}} | {{RC_002_LIST}} | {{S1_002}} | {{P1_002}} | {{D1_002}} | {{R1_002}} | {{ACC_002}} | {{BR_002}} |

## 7) Risk control details (hierarchy + rationale)

Document each control with hierarchy and rationale (ISO 14971 preferred order):

1. **Inherent safety by design**
2. **Protective measures** (device or manufacturing process)
3. **Information for safety** (labeling, IFU, training)

### Risk controls register

| Control ID | Control description | Hierarchy (Inherent/Protective/Info) | Applies to (Risk IDs) | Rationale / why effective | Side effects / new hazards | Traceability (requirements/tests/labels) |
|---|---|---|---|---|---|---|
| RC-001 | {{RC_001_DESC}} | {{RC_001_HIER}} | {{RC_001_RISKS}} | {{RC_001_RATIONALE}} | {{RC_001_SIDE_EFFECTS}} | {{RC_001_TRACE}} |
| RC-002 | {{RC_002_DESC}} | {{RC_002_HIER}} | {{RC_002_RISKS}} | {{RC_002_RATIONALE}} | {{RC_002_SIDE_EFFECTS}} | {{RC_002_TRACE}} |

## 8) Verification of risk controls (method + reference IDs + status)

Provide objective evidence that risk controls are implemented and effective.

| Verification ID | Control ID(s) | Method (test/inspection/analysis) | Evidence / reference ID(s) | Acceptance criteria | Status (Planned/Pass/Fail) | Notes |
|---|---|---|---|---|---|---|
| VER-001 | RC-001 | {{VER_001_METHOD}} | {{VER_001_EVIDENCE}} | {{VER_001_CRITERIA}} | {{VER_001_STATUS}} | {{VER_001_NOTES}} |
| VER-002 | RC-002 | {{VER_002_METHOD}} | {{VER_002_EVIDENCE}} | {{VER_002_CRITERIA}} | {{VER_002_STATUS}} | {{VER_002_NOTES}} |

## 9) Residual Risk Summary + benefit–risk justification references

### Residual risk summary

- **Highest residual risks (Risk IDs)**: {{HIGHEST_RESIDUAL_RISKS}}
- **Residual risk acceptability conclusion**: {{RESIDUAL_RISK_CONCLUSION}}

### Benefit–risk justifications (if needed)

| Risk ID | Residual acceptable? | Benefit–risk required? | Reference (document/link) | Decision / approval |
|---|---|---|---|---|
| RSK-___ | ___ | ___ | {{BENEFIT_RISK_REFERENCE}} | {{DECISION_APPROVAL}} |

## 10) Production & Post-Production (PMS) feedback hooks

### PMS sources

- Complaints / customer feedback: {{PMS_SOURCE_COMPLAINTS}}
- Nonconformances / deviations: {{PMS_SOURCE_NC}}
- CAPA: {{PMS_SOURCE_CAPA}}
- Service/repair data: {{PMS_SOURCE_SERVICE}}
- Supplier quality issues: {{PMS_SOURCE_SUPPLIER}}
- Vigilance / regulatory reporting: {{PMS_SOURCE_VIGILANCE}}
- Literature / field safety notices: {{PMS_SOURCE_LITERATURE}}

### Review triggers

- {{PMS_TRIGGER_1}}
- {{PMS_TRIGGER_2}}
- {{PMS_TRIGGER_3}}

## 11) Revision history + change summary

| Version | Date | Author | Change summary | Approved by |
|---:|---|---|---|---|
| 0.1 | {{DATE}} | {{AUTHOR}} | Initial draft | {{APPROVER}} |

---

## System Integrity Checks (smartRisk)

- [ ] All residual risk evaluations are based on versioned, immutable risk records.
- [ ] No residual risk data is inferred or auto-generated without explicit entry.
- [ ] Report outputs accurately reflect available data (no silent assumptions).

## Open Items / TODO

- {{TODO_1}}
- {{TODO_2}}
- {{TODO_3}}

