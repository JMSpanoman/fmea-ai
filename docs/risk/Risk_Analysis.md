---
title: Risk Analysis
standard: ISO 14971-style (smartRisk)
document_id: RA-001
project: TBD
owner: TBD
effective_date: TBD
---

# Risk Analysis (ISO 14971-style)

## 1) Purpose & Scope

This Risk Analysis documents the identification and evaluation of hazards, hazardous situations, and harms associated with the product/system under analysis. It also documents the risk controls selected, verification of those controls, and the resulting residual risk.

- **Scope**: TBD (define product boundaries, intended configuration, included accessories, and excluded use cases)
- **Lifecycle coverage**: Concept → design → manufacturing → distribution → use → servicing → end-of-life (as applicable)
- **Interfaces considered**: TBD (software, electrical, mechanical, packaging, labeling, user workflow, external systems)

## 2) Intended Use, Users, Use Environment

Document the intended medical purpose and operational context.

- **Intended use**: TBD
- **Intended users**: TBD (e.g., clinician, patient, caregiver, technician)
- **Use environment**: TBD (e.g., hospital, home, EMS, lab; temperature/humidity/EMI constraints)
- **Patient population / user population**: TBD
- **Key safety characteristics**: TBD (list the key functions/outputs that are safety-relevant)

## 3) Foreseeable Misuse (top 5)

List the most likely, reasonably foreseeable misuses that could lead to hazardous situations.

1. TBD
2. TBD
3. TBD
4. TBD
5. TBD

## 4) Risk Acceptability Framework (brief)

This Risk Analysis evaluates risk against the project’s defined acceptability criteria.

- **Acceptability criteria**: TBD (briefly summarize thresholds/regions and decision rules)
- **Reference**: Risk Management Plan (RMP) — TBD (insert document ID/link/location)

### Decision Preconditions

The following must be completed and approved prior to final risk acceptance:

- Approved Risk Management Plan
- Completed Hazard Analysis
- Versioned Residual Risk Evaluation
- Verification of applicable risk controls

## 5) Hazard → Hazardous Situation → Harm mapping

This mapping establishes traceability from hazard identification through hazardous situation to harm.

### Mapping table

| Hazard ID | Hazard | Hazardous Situation ID | Hazardous Situation | Harm ID | Harm | Notes / Initiating Events |
|---|---|---|---|---|---|---|
| HZ-001 | TBD | HS-001 | TBD | HM-001 | TBD | TBD |
| HZ-002 | TBD | HS-002 | TBD | HM-002 | TBD | TBD |
| HZ-003 | TBD | HS-003 | TBD | HM-003 | TBD | TBD |

## 6) Risk estimation: Initial (pre-control) vs Residual (post-control)

### Scoring assumptions

Define the scoring scales used consistently throughout this document.

- **Severity (S)**: 1–10 (TBD: define qualitative anchors, e.g., 1 = negligible, 10 = catastrophic)
- **Probability of harm (P)**: 1–10 (TBD: define anchors and whether probability includes exposure)
- **Detectability (D)** *(optional)*: 1–10 (TBD: if used, define anchors; otherwise remove)
- **Risk index**: TBD (e.g., \( RPN = S \times P \times D \) or risk matrix bin)

### Risk table (traceable)

For each hazardous situation, document initial risk, controls, and residual risk.

| Risk ID | Hazard ID | Hazardous Situation ID | Harm ID | Initial S | Initial P | Initial D | Initial Risk Index | Risk Controls (IDs) | Residual S | Residual P | Residual D | Residual Risk Index | Residual Acceptable? | Benefit–Risk Needed? |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|---|
| RSK-001 | HZ-001 | HS-001 | HM-001 | TBD | TBD | TBD | TBD | RC-001, RC-002 | TBD | TBD | TBD | TBD | TBD | TBD |
| RSK-002 | HZ-002 | HS-002 | HM-002 | TBD | TBD | TBD | TBD | RC-003 | TBD | TBD | TBD | TBD | TBD | TBD |
| RSK-003 | HZ-003 | HS-003 | HM-003 | TBD | TBD | TBD | TBD | RC-004 | TBD | TBD | TBD | TBD | TBD | TBD |

## 7) Risk control details (hierarchy + rationale)

Risk controls should follow the ISO 14971 hierarchy where feasible:

1. **Inherent safety by design**
2. **Protective measures** (in the device or manufacturing process)
3. **Information for safety** (labeling, IFU, training, warnings)

### Risk controls register

| Control ID | Control description | Hierarchy (Inherent / Protective / Info) | Applied to (Risk IDs) | Rationale / why effective | Side effects / new hazards | Traceability refs |
|---|---|---|---|---|---|---|
| RC-001 | TBD | TBD | RSK-001 | TBD | TBD | TBD |
| RC-002 | TBD | TBD | RSK-001 | TBD | TBD | TBD |
| RC-003 | TBD | TBD | RSK-002 | TBD | TBD | TBD |
| RC-004 | TBD | TBD | RSK-003 | TBD | TBD | TBD |

## 8) Verification of risk controls (method + reference IDs + status)

Each risk control must have objective evidence of implementation and effectiveness.

| Verification ID | Control ID(s) | Verification method | Reference / Evidence ID(s) | Acceptance criteria | Status (Planned / Pass / Fail) | Notes |
|---|---|---|---|---|---|---|
| VER-001 | RC-001 | TBD (test/inspection/analysis) | TBD | TBD | TBD | TBD |
| VER-002 | RC-002 | TBD | TBD | TBD | TBD | TBD |
| VER-003 | RC-003 | TBD | TBD | TBD | TBD | TBD |
| VER-004 | RC-004 | TBD | TBD | TBD | TBD | TBD |

## 9) Residual Risk Summary + benefit–risk justification references

### Residual risk summary

- **Highest residual risks**: TBD (list Risk IDs)
- **Residual risk acceptability conclusion**: TBD

### Benefit–risk justifications (if needed)

If any residual risks remain unacceptable but are justified by benefits, document references:

| Risk ID | Residual acceptable? | Benefit–risk justification required? | Reference (document/link) | Decision / approval |
|---|---|---|---|---|
| RSK-001 | TBD | TBD | TBD | TBD |

## 10) Production & Post-Production (PMS) feedback hooks

Define what will be monitored post-release and what triggers re-review of the risk analysis.

### PMS sources

- Complaints / customer feedback (TBD system/source)
- Nonconformances / deviations (TBD)
- CAPA (TBD)
- Service/repair data (TBD)
- Supplier issues (TBD)
- Vigilance / regulatory reporting (TBD)
- Literature / field safety notices (TBD)

### Review triggers

- Trending increase in complaint rate for a hazard category (TBD threshold)
- CAPA opened related to a risk control failure (TBD)
- Design change impacting safety-related function (TBD)
- New hazard identified from PMS (TBD)

## 11) Revision history + change summary

| Version | Date | Author | Change summary | Approved by |
|---:|---|---|---|---|
| 0.1 | TBD | TBD | Initial draft created to meet smartRisk RA standard | TBD |

---

## System Integrity Checks (smartRisk)

- [ ] All residual risk evaluations are based on versioned, immutable risk records.
- [ ] No residual risk data is inferred or auto-generated without explicit entry.
- [ ] Report outputs accurately reflect available data (no silent assumptions).

## Open Items / TODO

- Define **Intended Use / Users / Use Environment** (Section 2).
- Replace all **TBD** in the **Hazard → Situation → Harm** mapping (Section 5).
- Define the **risk scoring assumptions** and acceptability framework + link to the **RMP** (Sections 4 and 6).
- Populate **risk control details** with hierarchy and rationale (Section 7).
- Add **verification evidence IDs** and statuses for each control (Section 8).
- Complete residual risk conclusions and any required benefit–risk justifications (Section 9).
- Confirm PMS sources and review triggers for this product (Section 10).

